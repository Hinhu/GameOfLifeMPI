import os
from mpi4py import MPI
from parser import parseArgs
from fileHandlers import loadMap, saveMap
from matrix import zeros, generateRandom
from renderer import render
from cellCalculators import calculateNewMap, countNeighbours


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
if not os.path.exists(outputPath):
    os.makedirs(outputPath)


if rank == 0:
    if size > 2:
        part = mapHeight//(size-1)
        r = mapHeight % (size-1)

        for i in range(n):
            slices = []
            for j in range(1, size):
                p = part
                if r > 0:
                    p += 1

                if j == 1:
                    mpi.send(map[0:p+1], dest=j, tag=n)
                    slices.append([0, p])
                    past = p+1
                elif j != 1 and j != size-1:
                    mpi.send(map[past-2:past+p], dest=j, tag=n)
                    slices.append([past-1, past+p-1])
                    past += p
                else:
                    mpi.send(map[past-2:], dest=j, tag=n)
                    slices.append([past-1, len(map)])

                r -= 1
            for j in range(1, size):
                p = part
                if r > 0:
                    p += 1

                m = mpi.recv(source=j, tag=n)

                if j == 1:
                    map[slices[j-1][0]:slices[j-1][1]] = m[:-1]
                    past = p
                elif j != 1 and j != size-1:
                    map[slices[j-1][0]:slices[j-1][1]] = m[1:-1]
                else:
                    map[slices[j-1][0]:slices[j-1][1]] = m[1:]

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
            map = newMap
            # zapisywanie do pliku, zeby potem moc wyswietlac
            # bedzie trzeba wylaczyc na potrzeby benchmarku
            if saveLast and i == (n - 1):
                saveMap(map, outputPath + str(size) + "last.json")
            if not benchmark:
                saveMap(newMap, outputPath + str(i) + ".json")


    if not benchmark:
        render(len(map), len(map[0]), n, outputPath)

else:
    if size == 2:  # jesli uzytkownik poprosi o 2 procesy, to wszystko policzy glowny, ten moze skonczyc prace
        exit()
    for i in range(n):
        m = mpi.recv(source=0, tag=n)
        newM = calculateNewMap(m)
        mpi.send(newM, dest=0, tag=n)
