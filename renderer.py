import os
from Tkinter import Tk, Canvas
from fileHandlers import loadMap


def drawMap(m, w, cellSize):
    for x in range(len(m[0])):
        for y in range(len(m)):
            if m[y][x] == 1:
                f = "#000000"
            else:
                f = "#ffffff"
            w.create_rectangle(cellSize*x, cellSize*y, cellSize *
                               x+cellSize, cellSize*y+cellSize, fill=f,
                               outline="")


def render(width, height, n, outputPath):
    master = Tk()
    canvasWidth = 800
    canvasHeight = 800

    w = Canvas(master, width=canvasWidth, height=canvasHeight)
    w.pack()

    cellSize = canvasWidth / \
        width if width > height else (canvasWidth/height)

    for i in range(n):
        map, _, _ = loadMap(outputPath + str(i) + ".json")
        os.remove(outputPath + str(i) + ".json")
        drawMap(map, w, cellSize)
        w.update()
