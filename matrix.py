import random

def generateRandom(x, y):
    return [[random.randint(0, 1) for i in range(x)] for j in range(y)]


def zeros(x, y):
    return [[0 for i in range(x)] for j in range(y)]
