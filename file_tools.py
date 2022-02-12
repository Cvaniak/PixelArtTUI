import os
from rich.color import Color


def save_pxl(matrix, file_name):
    with open(file_name, "w") as file:
        for row in matrix:
            for rgb in row:
                t = str(tuple(rgb.get_truecolor())).replace(" ", "")
                t = t[1:-1]
                # r, g, b = t[0], t[1], t[2]
                file.write(f"{t} ")
            file.write(f"\n")


def load_pxl(matrix, file_name):
    if not os.path.exists(file_name):
        return
    with open(file_name, "r") as file:
        r = file.read().splitlines()
        for iidx, i in enumerate(r):
            j = i.split()
            for jidx, k in enumerate(j):
                tri = eval(k)
                r, g, b = tri
                matrix[iidx][jidx] = Color.from_rgb(red=r, green=g, blue=b)


def save_pal(matrix, file_name):
    with open(file_name, "w") as file:
        for rgb in matrix:
            t = str(tuple(rgb.get_truecolor())).replace(" ", "")
            t = t[1:-1]
            file.write(f"{t} ")
        file.write(f"\n")


def load_pal(matrix, file_name):
    if not os.path.exists(file_name):
        return
    with open(file_name, "r") as file:
        r = file.read().splitlines()
        for i in r:
            j = i.split()
            for jidx, k in enumerate(j):
                tri = eval(k)
                r, g, b = tri
                matrix[jidx] = Color.from_rgb(red=r, green=g, blue=b)
