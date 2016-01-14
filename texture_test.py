from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy
import math
import random

view_theta, view_phi, view_radius = 0.0, math.pi, 12.0
vtd, vpd, vrd = 0.0, 0.0, 0.0


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

    vtd *= 0.95
    vpd *= 0.95
    vrd *= 0.95

    glLoadIdentity()
    gluLookAt(view_x, view_y, view_z, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)


def create_tex():
    data = [100, 100, 100, 100, 100, 100, 20, 20, 50, 20, 20, 50]

    texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    # gluBuild2DMipmaps(GL_TEXTURE_2D, 3, 32, 32, GL_RGB, GL_UNSIGNED_BYTE, numpy.array(data).ravel())
    glGenerateMipmap(GL_TEXTURE_2D)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 2, 2, 0, GL_RGB, GL_UNSIGNED_BYTE, numpy.array(data).ravel())

    return texture


def display():
    global mytex
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    view_handler()

    glEnable(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, mytex)

    glActiveTexture(GL_TEXTURE0)

    vertex_array = [0, 0, 0,
                    0, 1, 0,
                    1, 1, 0,
                    1, 0, 0]

    # texture_array = [0, 0,
    #                  0, 1,
    #                  1, 1,
    #                  1, 0]
    texture_array = [0, 0,
                     0, 0,
                     1, 1,
                     1, 1]

    glVertexPointer(3, GL_FLOAT, 0, vertex_array)
    glEnableClientState(GL_VERTEX_ARRAY)

    glTexCoordPointer(2, GL_FLOAT, 0, texture_array)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    index_array = [0, 3, 2,
                   2, 1, 0]

    glDrawElements(GL_TRIANGLES, len(index_array), GL_UNSIGNED_INT, index_array)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

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

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
    global mytex
    glutInit()
    glutInitWindowSize(640, 480)
    glutCreateWindow("!!!")
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboard)
    init()

    mytex = create_tex()

    glutMainLoop()


mytex = 0

main()
