import sys
import random
import json
import os
from mpi4py import MPI
from Tkinter import Tk, Canvas


def calculateNewMap(map):
    newMap = zeros(len(map[0]), len(map))
    for x in range(len(newMap)):
        for y in range(len(newMap[0])):
            count = countNeighbours(map, x, y)
            if map[x][y] == 1:
                if count < 2 or count > 3:
                    newMap[x][y] = 0
                else:
                    newMap[x][y] = 1
            else:
                if count == 3:
                    newMap[x][y] = 1
    return newMap


def saveMap(map, name):
    f = open(name, "w")
    data = {
        'y': len(map),
        'x': len(map[0]),
        'cells': []
    }
    for x in range(len(map)):
        for y in range(len(map)):
            if map[x][y] == 1:
                data['cells'].append([x, y])
    f.write(json.dumps(data))


def loadMap(filename):
    f = open(filename)
    data = json.loads(f.read())
    cells = data['cells']
    map = zeros(data['x'], data['y'])
    for cell in cells:
        map[cell[0]][cell[1]] = 1
    return map


def generateRandom(x, y):
    return [[random.randint(0, 1) for i in range(x)] for j in range(y)]


def zeros(x, y):
    return [[0 for i in range(x)] for j in range(y)]


def countNeighbours(m, x, y):
    count = 0
    if x > 0:
        count += m[x - 1][y]
    if len(m) > x + 1:
        count += m[x + 1][y]
    if y > 0:
        count += m[x][y - 1]
    if len(m[0]) > y + 1:
        count += m[x][y + 1]
    if x > 0 and y > 0:
        count += m[x - 1][y - 1]
    if x > 0 and len(m[0]) > y + 1:
        count += m[x - 1][y + 1]
    if len(m) > x + 1 and len(m[0]) > y + 1:
        count += m[x + 1][y + 1]
    if y > 0 and len(m) > x + 1:
        count += m[x + 1][y - 1]
    return count


def drawMap(m, w, cellSizeX, cellSizeY):
    for x in range(len(m)):
        for y in range(len(m[0])):
            if m[x][y] == 1:
                f = "#000000"
            else:
                f = "#ffffff"
            w.create_rectangle(cellSizeX*x, cellSizeY*y, cellSizeX *
                               x+cellSizeX, cellSizeY*y+cellSizeY, fill=f,
                               outline="")


mpi = MPI.COMM_WORLD
rank = mpi.Get_rank()
size = mpi.Get_size()
outputPath = "output/"

# ilosc generacji do obliczenia
n = int(sys.argv[1])

if rank == 0:

    try:
        mapWidth = int(sys.argv[2])
    except IndexError:
        mapWidth = 100

    try:
        mapHeight = int(sys.argv[3])
    except IndexError:
        mapHeight = 100

    try:
        map = loadMap(sys.argv[4])
    except IndexError:
        map = generateRandom(mapWidth, mapHeight)

    part = mapHeight/(size-1)

    for i in range(n):
        for j in range(1, size):
            if j != 1 and j != size-1:
                mpi.send(map[(j-1)*part-1:j*part+1], dest=j, tag=n)
            elif j == 1:
                mpi.send(map[(j-1)*part:j*part+1], dest=j, tag=n)
            else:
                mpi.send(map[(j-1)*part-1:j*part], dest=j, tag=n)
        for j in range(1, size):
            m = mpi.recv(source=j, tag=n)
            if j != 1 and j != size-1:
                map[(j-1)*part:j*part] = m[1:-1]
            elif j == 1:
                map[(j-1)*part:j*part] = m[:-1]
            else:
                map[(j-1)*part:j*part] = m[1:]
        # zapisywanie do pliku, zeby potem moc wyswietlac
        # bedzie trzeba wylaczyc na potrzeby benchmarku
        saveMap(map, outputPath + str(i) + ".json")

    # wyswietlanie, tez bedzie trzeba wylaczyc
    master = Tk()

    canvasWidth = 800
    canvasHeight = 800
    w = Canvas(master,
               width=canvasWidth,
               height=canvasHeight)
    w.pack()

    cellSizeX = canvasWidth/len(map)
    cellSizeY = canvasHeight/len(map[0])

    for i in range(n):
        map = loadMap(outputPath + str(i) + ".json")
        os.remove(outputPath + str(i) + ".json")
        drawMap(map, w, cellSizeX, cellSizeY)
        w.update()

else:
    for i in range(n):
        m = mpi.recv(source=0, tag=n)
        newM = calculateNewMap(m)
        mpi.send(newM, dest=0, tag=n)
