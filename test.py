from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy
import random
from scipy.spatial import Delaunay, distance
from scipy.linalg import norm

rotation = 0.0

tri = 0
normals = 0

light_position = [1.0, 1.0, 1.0, 0.0]
light_theta = 0.0

view_theta = 0
view_phi = 0
view_radius = 6

vt_mom = 0
vp_mom = 0
vr_mom = 0

stars = []


def init():
    global light_position
    light_diffuse = [0.8, 0.8, 0.8, 0.8]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)

    # glClearColor(0.8, 0.0, 0.1, 0.0)
    glClearColor(0.1, 0.1, 0.1, 0.0)
    glColor3f(0.4, 0.4, 0.4)
    glPointSize(4.0)

    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)

    #glLoadIdentity()
    gluPerspective(45.0, float(640)/float(480), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(6.0, 0.0, 0.0,
              0.0, 0.0, 0.0,
              0.0, 0.0, 1.0)


def sphere_points():
    global tri, normals
    tri = 0
    normals = []
    points = []

    for t in range(15):
        theta = (t/15.0) * (math.pi*2)
        for i in range(8):
            u = random.randint(-1000, 1000)
            u /= 1000.0

            x = math.sqrt(1.0 - math.pow(u, 2)) * math.cos(theta)
            y = math.sqrt(1.0 - math.pow(u, 2)) * math.sin(theta)
            z = u

            points += [(x, y, z)]

    np_points = numpy.array(points)
    tri = Delaunay(np_points)

    for pi1, pi2, pi3 in tri.convex_hull:
        p1 = tri.points[pi1]
        p2 = tri.points[pi2]
        p3 = tri.points[pi3]
        cross = numpy.cross(p2-p1, p3-p1)

        plus_norm = p1 + cross
        if norm(plus_norm) < norm(p1):
            cross = numpy.cross(p3-p1, p2-p1)

        mag = norm(cross)
        cross /= mag
        normals += [cross]


def calc_stars():
    global stars

    for t in range(100):
        theta = random.random()*(math.pi*2)
        u = random.randint(-1000, 1000)
        u /= 1000.0

        x = math.sqrt(1.0 - math.pow(u, 2)) * math.cos(theta)
        y = math.sqrt(1.0 - math.pow(u, 2)) * math.sin(theta)
        z = u

        radius = 10*random.random()

        x *= 80+radius
        y *= 80+radius
        z *= 80+radius

        stars += [(x, y, z)]


def display():
    global rotation, tri, normals, light_position, light_theta, view_theta, view_phi, view_radius, stars, vt_mom, vp_mom, vr_mom
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # view_x = 6*math.cos(view_theta)
    # view_y = 6*math.sin(view_theta)
    view_theta += vt_mom
    view_phi += vp_mom
    view_radius += vr_mom

    if -0.0003 < vt_mom < 0.0003:
        vt_mom = 0

    if vt_mom < 0.0:
        vt_mom += 0.0002
    elif vt_mom > 0.0:
        vt_mom -= 0.0002

    if -0.0003 < vp_mom < 0.0003:
        vp_mom = 0

    if vp_mom < 0.0:
        vp_mom += 0.0002
    elif vp_mom > 0.0:
        vp_mom -= 0.0002

    if -0.0006 < vr_mom < 0.0006:
        vr_mom = 0

    if vr_mom < 0.0:
        vr_mom += 0.0003
    elif vr_mom > 0.0:
        vr_mom -= 0.0003

    view_x = view_radius*math.cos(view_theta)*math.sin(view_phi)
    view_y = view_radius*math.sin(view_theta)*math.sin(view_phi)
    view_z = view_radius*math.cos(view_phi)

    glLoadIdentity()

    gluLookAt(view_x, view_y, view_z,
              0.0, 0.0, 0.0,
              0.0, 0.0, 1.0)

    # glLoadIdentity()
    # glTranslatef(0.0, 0.0, -6.0)
    # glRotatef(rotation, 0.5, 0.5, 0.2)
    rotation += 0.2

    light_theta += 0.002
    light_position[0] = 12*math.cos(light_theta)
    light_position[1] = 12*math.sin(light_theta)

    glDisable(GL_LIGHTING)

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(light_position[0], light_position[1], light_position[2])

    # stars
    glColor3f(0.7, 0.7, 0.7)
    for x, y, z in stars:
        glVertex3f(x, y, z)

    glEnd()

    glEnable(GL_LIGHTING)

    glColorMaterial(GL_FRONT, GL_DIFFUSE)
    glEnable(GL_COLOR_MATERIAL)
    glColor3f(1.0, 1.0, 1.0)
    facet_num = 0
    for facet in tri.convex_hull:
        glBegin(GL_TRIANGLES)
        glNormal3f(normals[facet_num][0], normals[facet_num][1], normals[facet_num][2])

        facet_num += 1

        for point in facet:
            x, y, z = tri.points[point]
            glVertex3f(x, y, z)
        glEnd()

    glutSwapBuffers()


def keyboard(key, x, y):
    if key == 'r':
        sphere_points()


def special_keyboard(key, x, y):
    global vt_mom, vp_mom, vr_mom
    if key == 100:
        vt_mom -= 0.01
    if key == 102:
        vt_mom += 0.01
    if key == 101:
        vp_mom -= 0.01
    if key == 103:
        vp_mom += 0.01

    if key == 104:
        vr_mom += 0.05
    if key == 105:
        vr_mom -= 0.05

    vp_mom = numpy.clip(vp_mom, -0.06, 0.06)
    vt_mom = numpy.clip(vt_mom, -0.06, 0.06)
    vr_mom = numpy.clip(vr_mom, -0.06, 0.06)


def main():
    sphere_points()
    calc_stars()

    glutInit()
    glutInitWindowSize(640, 480)
    glutCreateWindow("!!!")
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keyboard)
    init()
    glutMainLoop()

main()
