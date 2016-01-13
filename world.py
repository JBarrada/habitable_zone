from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy
import random
from scipy.spatial import ConvexHull, distance
from scipy.linalg import norm

tring = []
smplx_types = []
smplx_areas = []


view_theta, view_phi, view_radius = 0.0, 0.0, 6.0
vtd, vpd, vrd = 0.0, 0.0, 0.0

world_seed = 0.0
world_fill = 0.45


def calc_sphere():
    global tring
    points = []
    for t in range(1000):
        theta = random.random()*(math.pi*2)
        u = random.randint(-1000, 1000)
        u /= 1000.0

        x = math.sqrt(1.0 - math.pow(u, 2)) * math.cos(theta)
        y = math.sqrt(1.0 - math.pow(u, 2)) * math.sin(theta)
        z = u

        points += [(x, y, z)]

    tring = ConvexHull(points)


def init_cell_types(seed, fill_percent):
    global tring, smplx_types
    random.seed(seed)
    smplx_types = [0]*len(tring.simplices)
    for simplex in range(len(tring.simplices)):
        smplx_types[simplex] = 1 if random.random() < fill_percent else 0


def init_cell_areas():
    global tring, smplx_areas
    smplx_areas = [0]*len(tring.simplices)
    for simplex in range(len(tring.simplices)):
        a, b, c = tring.simplices[simplex]
        ab = tring.points[b]-tring.points[a]
        ac = tring.points[c]-tring.points[a]
        smplx_areas[simplex] = norm(numpy.cross(ab, ac))/2.0


def smooth():
    global tring, smplx_areas, smplx_types
    for i in range(len(smplx_types)):
        alive_neighbor_area = 0
        dead_neighbor_area = 0
        for neighbor_simplex in tring.neighbors[i]:
            if smplx_types[neighbor_simplex] == 1:
                alive_neighbor_area += smplx_areas[neighbor_simplex]
            else:
                dead_neighbor_area += smplx_areas[neighbor_simplex]

        avg_points = numpy.zeros(3)
        for pindex in tring.simplices[i]:
            avg_points += tring.points[pindex]
        avg_points /= 3

        alive_neighbor_area *= (0.8 + (math.pow(avg_points[2], 4)*2.0))

        if alive_neighbor_area > dead_neighbor_area:
            smplx_types[i] = 1
        else:
            smplx_types[i] = 0


def view_handler():
    global vtd, vpd, vrd, view_theta, view_phi, view_radius
    vtd = numpy.clip(vtd, -0.06, 0.06)
    vpd = numpy.clip(vpd, -0.06, 0.06)
    vrd = numpy.clip(vrd, -0.06, 0.06)

    view_theta += vtd
    view_phi += vpd
    view_radius += vrd

    vtd = 0.0 if abs(vtd) < 0.002 else vtd
    vpd = 0.0 if abs(vpd) < 0.002 else vpd
    vrd = 0.0 if abs(vrd) < 0.002 else vrd

    view_x = view_radius*math.cos(view_theta)*math.sin(view_phi)
    view_y = view_radius*math.sin(view_theta)*math.sin(view_phi)
    view_z = view_radius*math.cos(view_phi)

    vtd *= 0.9
    vpd *= 0.9
    vrd *= 0.9

    glLoadIdentity()
    gluLookAt(view_x, view_y, view_z, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)


def display():
    global tring
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    view_handler()

    glBegin(GL_TRIANGLES)
    for i in range(len(tring.simplices)):
        if smplx_types[i] != 0:
            glColor3f(0.8, 0.8, 0.8)
        else:
            glColor3f(0.1, 0.2, 0.4)
        for pindex in tring.simplices[i]:
            x, y, z = tring.points[pindex]
            glVertex3f(x, y, z)
    glEnd()

    glutSwapBuffers()


def init():
    glClearColor(0.1, 0.1, 0.1, 0.0)
    glPointSize(4.0)
    glLineWidth(2.0)

    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)

    gluPerspective(45.0, float(640)/float(480), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(6.0, 0.0, 0.0,
              0.0, 0.0, 0.0,
              0.0, 0.0, 1.0)


def keyboard(key, x, y):
    global world_seed, world_fill, vtd, vpd, vrd
    if key == 's':
        smooth()
    if key == 'r':
        world_seed = random.random()
        calc_sphere()
        init_cell_types(world_seed, world_fill)
        init_cell_areas()
        for i in range(5):
            smooth()

    if key == '-':
        world_fill -= 0.02
        calc_sphere()
        init_cell_types(world_seed, world_fill)
        init_cell_areas()
        for i in range(5):
            smooth()
    if key == '=':
        world_fill += 0.02
        calc_sphere()
        init_cell_types(world_seed, world_fill)
        init_cell_areas()
        for i in range(5):
            smooth()

    if key == 100:
        vtd -= 0.01
    if key == 102:
        vtd += 0.01
    if key == 101:
        vpd -= 0.01
    if key == 103:
        vpd += 0.01


def main():
    glutInit()
    glutInitWindowSize(640, 480)
    glutCreateWindow("!!!")
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboard)
    init()
    glutMainLoop()

calc_sphere()
init_cell_types(22, 0.45)
init_cell_areas()
main()
