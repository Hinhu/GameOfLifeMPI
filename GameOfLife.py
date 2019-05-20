import sys
import random
from tkinter import *
from time import sleep


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
    if len(m[x]) > y + 1:
        count += m[x][y + 1]
    if x > 0 and y > 0:
        count += m[x - 1][y - 1]
    if x > 0 and len(m[x]) > y + 1:
        count += m[x - 1][y + 1]
    if len(m) > x + 1 and len(m[x]) > y + 1:
        count += m[x + 1][y + 1]
    if y > 0 and len(m) > x + 1:
        count += m[x + 1][y - 1]
    return count


def drawMap(m, w, cellSizeX, cellSizeY):

    for y in range(len(m)):
        for x in range(len(m[0])):
            if m[x][y] == 1:
                f = "#000000"
            else:
                f = "#ffffff"
            w.create_rectangle(cellSizeX*x, cellSizeY*y, cellSizeX *
                               x+cellSizeX, cellSizeY*y+cellSizeY, fill=f)


n = int(sys.argv[1])

try:
    mapWidth = int(sys.argv[2])
except IndexError:
    mapWidth = 100

try:
    mapHeight = int(sys.argv[3])
except IndexError:
    mapHeight = 100

try:
    map = sys.argv[4]
except IndexError:
    map = generateRandom(mapWidth, mapHeight)

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
    newMap = zeros(mapWidth, mapHeight)
    for y in range(len(newMap)):
        for x in range(len(newMap[0])):
            count = countNeighbours(map, x, y)
            if map[x][y] == 1:
                if count < 2 or count > 3:
                    newMap[x][y] = 0
                else:
                    newMap[x][y] = 1
            else:
                if count == 3:
                    newMap[x][y] = 1
    map = newMap
    drawMap(map, w, cellSizeX, cellSizeY)
    w.update()

mainloop()
