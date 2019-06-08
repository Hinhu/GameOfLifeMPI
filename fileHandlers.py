import json, os
from matrix import zeros

def saveMap(map, name):
    f = open(name, "w")
    data = {
        'y': len(map),
        'x': len(map[0]),
        'cells': []
    }
    for x in range(len(map)):
        for y in range(len(map[0])):
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