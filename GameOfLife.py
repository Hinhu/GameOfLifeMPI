import sys
import random
import json
import os
import argparse
from mpi4py import MPI
from tkinter import Tk, Canvas

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
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
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
    return map, data['x'], data['y']


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

def parseArgs():
    parser = argparse.ArgumentParser(description='Game of Life MPI')
    parser.add_argument('-g', '--generations', help='number of generations', type=int, default=100)
    parser.add_argument('-b', '--benchmark', help='benchmark mode (no gui, no filesave)', action='store_true')
    parser.add_argument('--height', help='map height', type=int, default=100)
    parser.add_argument('--width', help='map width', type=int, default=100)
    parser.add_argument('--mapfile', help='input map file')
    parser.add_argument('--savelast', help='input map file', action='store_true')
    return parser.parse_args()


benchmark = False
saveLast = False
map = []
args = parseArgs()
n = args.generations
mapWidth = args.width
mapHeight = args.height
if args.mapfile:
    map, mapWidth, mapHeight = loadMap(args.mapfile)
else:
    map = generateRandom(mapWidth, mapHeight)
benchmark = args.benchmark
saveLast = args.savelast

mpi = MPI.COMM_WORLD
rank = mpi.Get_rank()
size = mpi.Get_size()
outputPath = "output/"

# print("N:{} G:{} mH:{} mW:{} ".format(size, n, mapHeight, mapWidth))

if rank == 0:
    if size > 2:
        part = mapHeight//(size-1)
        r = mapHeight % (size-1)

        for i in range(n):
            for j in range(1, size):
                p = part
                if r != 0:
                    p += 1

                if j != 1 and j != size-1:
                    mpi.send(map[(j-1)*p-1:j*p+1], dest=j, tag=n)
                elif j == 1:
                    mpi.send(map[0:p+1], dest=j, tag=n)
                else:
                    mpi.send(map[(j-1)*p-1:j*p], dest=j, tag=n)
                r -= 1
            for j in range(1, size):
                p = part
                if r != 0:
                    p += 1

                m = mpi.recv(source=j, tag=n)
                if j != 1 and j != size-1:
                    map[(j-1)*p:j*p] = m[1:-1]
                elif j == 1:
                    map[0:p] = m[:-1]
                else:
                    map[(j-1)*p:] = m[1:]
                r -= 1
            # zapisywanie do pliku, zeby potem moc wyswietlac
            # bedzie trzeba wylaczyc na potrzeby benchmarku
            if saveLast and i == (n-1):
                saveMap(map, outputPath + str(size) + "last.json")
            if not benchmark:
                saveMap(map, outputPath + str(i) + ".json")
    else:  # jednowatkowo
        for i in range(n):
            newMap = calculateNewMap(map)
            # zapisywanie do pliku, zeby potem moc wyswietlac
            # bedzie trzeba wylaczyc na potrzeby benchmarku
            if saveLast and i == (n - 1):
                saveMap(map, outputPath + str(size) + "last.json")
            if not benchmark:
                saveMap(newMap, outputPath + str(i) + ".json")
            map = newMap

    if not benchmark:
        master = Tk()
        canvasWidth = 800
        canvasHeight = 800

        w = Canvas(master, width=canvasWidth, height=canvasHeight)
        w.pack()

        cellSizeX = canvasWidth/len(map)
        cellSizeY = canvasHeight/len(map[0])

        for i in range(n):
            map, _, _ = loadMap(outputPath + str(i) + ".json")
            os.remove(outputPath + str(i) + ".json")
            drawMap(map, w, cellSizeX, cellSizeY)
            w.update()

else:
    if size == 2:  # jeśli uzytkownik poprosi o 2 procesy, to wszystko policzy glowny, ten moze skonczyc prace
        exit()
    for i in range(n):
        m = mpi.recv(source=0, tag=n)
        newM = calculateNewMap(m)
        mpi.send(newM, dest=0, tag=n)
