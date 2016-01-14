from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random
import numpy
import math
import sys

G_WIDTH, G_HEIGHT = 256, 256

sys.setrecursionlimit((G_WIDTH*G_HEIGHT)*2)

cells = numpy.zeros((G_WIDTH, G_HEIGHT))

groups = []
group_colors = []


def random_fill_cells(seed, fill_percent):
    global cells
    random.seed(seed)

    for x in range(G_WIDTH):
        for y in range(G_HEIGHT):
            cells[x][y] = 1 if random.random() < fill_percent else 0


def get_cell_neighbor_count(x, y):
    global cells
    neighbors = 0
    neighbors += cells[(((x-1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y+1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x+0) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y+1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x+1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y+1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x-1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y+0) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x+1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y+0) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x-1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y-1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x+0) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y-1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    neighbors += cells[(((x+1) % G_WIDTH)+G_WIDTH) % G_WIDTH][(((y-1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT]
    return neighbors


def get_adjacent(x, y):
    global cells
    adjacent = []
    adjacent += [((((x+0) % G_WIDTH)+G_WIDTH) % G_WIDTH, (((y+1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT)]
    adjacent += [((((x-1) % G_WIDTH)+G_WIDTH) % G_WIDTH, (((y+0) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT)]
    adjacent += [((((x+1) % G_WIDTH)+G_WIDTH) % G_WIDTH, (((y+0) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT)]
    adjacent += [((((x+0) % G_WIDTH)+G_WIDTH) % G_WIDTH, (((y-1) % G_HEIGHT)+G_HEIGHT) % G_HEIGHT)]
    return adjacent


def xy_to_index(x, y):
    return y*G_WIDTH + x


def index_to_xy(index):
    return index % G_WIDTH, index / G_WIDTH


def smooth():
    global cells
    for x in range(G_WIDTH):
        for y in range(G_HEIGHT):
            neighbors = get_cell_neighbor_count(x, y)

            ypos = abs((y/float(G_HEIGHT))-0.5)*2.0

            neighbors += int(neighbors*math.pow(ypos, 8))

            if neighbors > 4:
                cells[x][y] = 1
            if neighbors < 4:
                cells[x][y] = 0


def is_cell_assigned(x, y):
    global groups
    cell_index = xy_to_index(x, y)
    for group in groups:
        if cell_index in group:
            return True
    return False


def flood_assign(x, y, group_num):
    assigned = 0
    for a_x, a_y in get_adjacent(x, y):
        if cells[a_x][a_y] == 1:
            if not is_cell_assigned(a_x, a_y):
                groups[group_num] += [xy_to_index(a_x, a_y)]
                assigned += 1 + flood_assign(a_x, a_y, group_num)
    return assigned


def find_groups():
    global groups, group_colors
    groups = []
    groups += [[]]
    group_num = 0

    group_colors = []
    group_colors += [(random.random(), random.random(), random.random())]

    for x in range(G_WIDTH):
        for y in range(G_HEIGHT):
            if cells[x][y] == 1:
                if not is_cell_assigned(x, y):
                    assigned = flood_assign(x, y, group_num)
                    if assigned != 0:
                        groups += [[]]
                        group_num += 1

                        group_colors += [(random.random(), random.random(), random.random())]


def create_tex():
    random_fill_cells(24, 0.45)
    smooth()
    # find_groups()

    global cells
    data = numpy.zeros((G_WIDTH, G_HEIGHT, 3))
    data.fill(100)
    # for group in groups:
    #     r, g, b = group_colors[groups.index(group)]
    #     for point_index in group:
    #         y, x = index_to_xy(point_index)
    #         data[x][y][0] = int(r*255)
    #         data[x][y][1] = int(g*255)
    #         data[x][y][2] = int(b*255)

    for x in range(G_WIDTH):
        for y in range(G_HEIGHT):
            r, g, b = (255, 255, 255) if cells[x][y] == 1 else (0, 0, 0)
            data[y][x][0] = r
            data[y][x][1] = g
            data[y][x][2] = b

    texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glGenerateMipmap(GL_TEXTURE_2D)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, G_WIDTH, G_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, numpy.array(data).ravel())

    return texture
