from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import math

import hexagon

view_theta, view_phi, view_radius = -math.pi/2.0, 0.0001, 12.0
vtd, vpd, vrd = 0.0, 0.0, 0.0


def view_handler():
    global vtd, vpd, vrd, view_theta, view_phi, view_radius
    vtd = numpy.clip(vtd, -0.06, 0.06)
    vpd = numpy.clip(vpd, -0.06, 0.06)
    vrd = numpy.clip(vrd, -0.06, 0.06)

    view_theta += numpy.clip((view_radius-1.1)*vtd, -0.01, 0.01)
    view_phi += numpy.clip((view_radius-1.1)*vpd, -0.01, 0.01)
    view_radius += numpy.clip((view_radius-1.1)*vrd, -0.01, 0.01)

    vtd = 0.0 if abs(vtd) < 0.002 else vtd
    vpd = 0.0 if abs(vpd) < 0.002 else vpd
    vrd = 0.0 if abs(vrd) < 0.002 else vrd

    view_x = view_radius*math.cos(view_theta)*math.sin(view_phi)
    view_y = view_radius*math.sin(view_theta)*math.sin(view_phi)
    view_z = view_radius*math.cos(view_phi)

    vtd *= 0.95
    vpd *= 0.95
    vrd *= 0.95

    glLoadIdentity()
    gluLookAt(view_x, view_y, view_z, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    view_handler()

    glEnable(GL_LIGHTING)

    for h in hexes:
        h.draw()

    glutSwapBuffers()


def init():
    glClearColor(0.1, 0.1, 0.1, 0)
    glPointSize(4.0)
    glLineWidth(2.0)

    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    fog_color = [0.1, 0.1, 0.1, 1]

    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogf(GL_FOG_START, 8.0)
    glFogf(GL_FOG_END, 15.0)
    glEnable(GL_FOG)

    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 1])
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    gluPerspective(45.0, float(640)/float(480), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(6.0, 0.0, 0.0,
              0.0, 0.0, 0.0,
              0.0, 0.0, 1.0)


def keyboard(key, x, y):
    global vtd, vpd, vrd

    if key == 100:
        vtd -= 0.01
    if key == 102:
        vtd += 0.01
    if key == 101:
        vpd -= 0.01
    if key == 103:
        vpd += 0.01

    if key == 104:
        vrd += 0.05
    if key == 105:
        vrd -= 0.05


def main():
    global hexes
    glutInit()
    glutInitWindowSize(640, 480)
    glutCreateWindow("!!!")
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboard)
    init()

    width = (math.sqrt(3.0)*1.0)
    hexes = [hexagon.Hexagon((0, 0, 0)),
             hexagon.Hexagon((0, width, 0)),
             hexagon.Hexagon((width*math.cos(math.pi/6.0), width*math.sin(math.pi/6.0), 0))]

    glutMainLoop()

hexes = []
main()
