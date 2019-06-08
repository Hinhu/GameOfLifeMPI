from matrix import zeros

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
