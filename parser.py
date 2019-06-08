import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description='Game of Life MPI')
    parser.add_argument('-g', '--generations',
                        help='number of generations', type=int, default=100)
    parser.add_argument(
        '-b', '--benchmark', help='benchmark mode (no gui, no filesave)', action='store_true')
    parser.add_argument('--height', help='map height', type=int, default=100)
    parser.add_argument('--width', help='map width', type=int, default=100)
    parser.add_argument('--mapfile', help='input map file')
    parser.add_argument('--savelast', help='input map file',
                        action='store_true')
    return parser.parse_args()