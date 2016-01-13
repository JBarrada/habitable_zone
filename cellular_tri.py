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

triangulated = []
alive_simplex = []
simplex_areas = []

fill = 0.45


def generate_cells(seed, fill_percent):
    global triangulated, alive_simplex, simplex_areas
    random.seed(seed)

    p_count = 2000

    points = []
    for point in range(p_count):
        points += [(random.random()*float(G_WIDTH), random.random()*float(G_HEIGHT))]

    for point in range(p_count/10):
        points += [(0, random.random()*float(G_HEIGHT))]
        points += [(G_WIDTH, random.random()*float(G_HEIGHT))]
        points += [(random.random()*float(G_WIDTH), 0)]
        points += [(random.random()*float(G_WIDTH), G_HEIGHT)]

    points += [(0, 0)]
    points += [(G_WIDTH, 0)]
    points += [(G_WIDTH, G_HEIGHT)]
    points += [(0, G_HEIGHT)]

    triangulated = Delaunay(points)

    alive_simplex = [0]*len(triangulated.simplices)
    for simplex in range(len(triangulated.simplices)):
        alive_simplex[simplex] = 1 if random.random() < fill_percent else 0

    simplex_areas = [0]*len(triangulated.simplices)
    for simplex in range(len(triangulated.simplices)):
        a, b, c = triangulated.simplices[simplex]
        ax, ay = triangulated.points[a]
        bx, by = triangulated.points[b]
        cx, cy = triangulated.points[c]
        simplex_areas[simplex] = abs(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))/2.0


def smooth():
    global triangulated, alive_simplex, simplex_areas
    for i in range(len(alive_simplex)):
        self_area = simplex_areas[i]
        alive_neighbor_area = 0
        dead_neighbor_area = 0
        for neighbor_simplex in triangulated.neighbors[i]:
            if alive_simplex[neighbor_simplex] == 1:
                alive_neighbor_area += simplex_areas[neighbor_simplex]
            else:
                dead_neighbor_area += simplex_areas[neighbor_simplex]

        if alive_neighbor_area > dead_neighbor_area:
            alive_simplex[i] = 1
        else:
            alive_simplex[i] = 0

        # if (neighbor_area/1.0) > self_area:
        #     alive_simplex[i] = 1
        # elif (neighbor_area/1.0) < self_area:
        #     alive_simplex[i] = 0

        # neighbors_alive = 0
        # for neighbor_simplex in triangulated.neighbors[i]:
        #     neighbors_alive += alive_simplex[neighbor_simplex]
#
        # if neighbors_alive >= 2:
        #     alive_simplex[i] = 1
        # elif neighbors_alive < 2:
        #     alive_simplex[i] = 0


def display():
    global triangulated, alive_simplex
    glClear(GL_COLOR_BUFFER_BIT)

    glColor3f(0.5, 0.5, 0.5)
    for i in range(len(alive_simplex)):
        if alive_simplex[i] == 1:
            glBegin(GL_POLYGON)
            for p_index in triangulated.simplices[i]:
                x, y = triangulated.points[p_index]
                glVertex2f(x, y)
            glEnd()

    # glColor3f(0, 0, 0)
    # for simplex in triangulated.simplices:
    #     glBegin(GL_LINES)
    #     for p_index in simplex:
    #         x, y = triangulated.points[p_index]
    #         glVertex2f(x, y)
    #     x, y = triangulated.points[simplex[0]]
    #     glVertex2f(x, y)
    #     glEnd()

    glutSwapBuffers()


def keyboard(key, x, y):
    global fill
    if key == 's':
        smooth()
    if key == 'r':
        generate_cells(random.random(), fill)
        smooth()
    if key == '-':
        fill -= 0.02
        generate_cells(random.random(), fill)
        smooth()
    if key == '=':
        fill += 0.02
        generate_cells(random.random(), fill)
        smooth()


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

generate_cells(22, fill)
init()
