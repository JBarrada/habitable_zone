from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from scipy.spatial import Delaunay
import random
import numpy
import sys

G_WIDTH, G_HEIGHT = 100, 50
W_WIDTH, W_HEIGHT = 600, 300

sys.setrecursionlimit((G_WIDTH*G_HEIGHT)*2)

cells = numpy.zeros((G_WIDTH, G_HEIGHT))

groups = []
group_colors = []

fill = 0.46

x_start, y_start = 0.0, 0.0


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


def draw_cell(x, y, width, height, (r, g, b)=(1, 1, 1)):
    glColor3f(r, g, b)
    glBegin(GL_POLYGON)
    glVertex2f(x, y)
    glVertex2f(x+width, y)
    glVertex2f(x+width, y+height)
    glVertex2f(x, y+height)
    glEnd()


def display():
    global cells, x_start, y_start, groups, group_colors
    glClear(GL_COLOR_BUFFER_BIT)

    cell_size = 1

    for group in groups:
        r, g, b = group_colors[groups.index(group)]
        for point_index in group:
            x, y = index_to_xy(point_index)
            draw_cell(x*cell_size, y*cell_size, cell_size, cell_size, (r, g, b))

    glDisable(GL_DEPTH_TEST)

    glutSwapBuffers()


def keyboard(key, x, y):
    global fill

    if key == 's':
        smooth()
        find_groups()
    if key == 'r':
        random_fill_cells(random.random(), fill)
        smooth()
        find_groups()
    if key == '-':
        fill -= 0.02
        random_fill_cells(random.random(), fill)
        smooth()
        find_groups()
    if key == '=':
        fill += 0.02
        random_fill_cells(random.random(), fill)
        smooth()
        find_groups()


def init():
    glutInit()
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutCreateWindow("!!!")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboard)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, G_WIDTH, 0.0, G_HEIGHT)

    glutMainLoop()

random_fill_cells(24, fill)
smooth()
find_groups()
init()
