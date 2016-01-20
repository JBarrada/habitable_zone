from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy
import random
import colorsys
from copy import copy
from scipy.linalg import norm
from PIL import Image, ImageDraw


class Vertex:
    l_coords = numpy.zeros(3)
    t_coords = numpy.zeros(2)
    n_coords = numpy.zeros(3)

    def __init__(self, (x, y, z)=(0, 0, 0), (tx, ty)=(0, 0), (nx, ny, nz)=(0, 0, 0)):
        self.l_coords = numpy.array([x, y, z])
        self.t_coords = numpy.array([tx, ty])
        self.n_coords = numpy.array([nx, ny, nz])


class Triangle:
    vertices = [Vertex(), Vertex(), Vertex()]

    def __init__(self, (a, b, c)):
        self.vertices = a, b, c

    def calculate_normals(self, direction):
        a, b, c = self.vertices
        ab = b.l_coords - a.l_coords
        ac = c.l_coords - a.l_coords
        normal = numpy.zeros(3)
        if direction == 0:
            normal = numpy.cross(ab, ac)
        else:
            normal = numpy.cross(ac, ab)
        normal /= norm(normal)

        self.vertices[0].n_coords = normal
        self.vertices[1].n_coords = normal
        self.vertices[2].n_coords = normal


class Hexagon:
    triangles = []

    l_coords = []
    t_coords = []
    n_coords = []

    texture = 0

    height = 20.0
    radius = 1.0

    position = (0, 0, 0)

    def __init__(self, (x, y, z), height=20.0, radius=1.0):
        self.height = height
        self.radius = radius
        self.position = (x, y, z)

        self.generate_geometry()
        self.generate_texture()

    def draw(self):
        glVertexPointer(3, GL_FLOAT, 0, self.l_coords)
        glEnableClientState(GL_VERTEX_ARRAY)

        glNormalPointer(GL_FLOAT, 0, self.n_coords)
        glEnableClientState(GL_NORMAL_ARRAY)

        glTexCoordPointer(2, GL_FLOAT, 0, self.t_coords)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glActiveTexture(GL_TEXTURE0)

        glPushMatrix()

        x, y, z = self.position
        glTranslatef(x, y, z)

        glDrawElements(GL_TRIANGLES, 48, GL_UNSIGNED_INT, range(len(self.l_coords)))

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glPopMatrix()

    def generate_geometry(self):
        vertices = []
        self.l_coords = []
        self.t_coords = []
        self.n_coords = []

        self.triangles = []

        for i in range(6):
            x, y = self.radius*math.cos(i/6.0*2*math.pi), self.radius*math.sin(i/6.0*2*math.pi)
            tx, ty = (0.5*math.cos(i/6.0*2*math.pi))+0.5, (0.5*math.sin(i/6.0*2*math.pi))+0.5
            vertices += [Vertex((x, y, 0), (tx, ty)), Vertex((x, y, -self.height), (tx, ty))]

        for ai, bi, ci in [(0, 2, 4), (0, 4, 6), (0, 6, 10), (6, 8, 10)]:
            a, b, c = copy(vertices[ai]), copy(vertices[bi]), copy(vertices[ci])
            self.triangles += [Triangle((a, b, c))]

        for i in range(6):
            a, b, c = copy(vertices[0+(i*2)]), copy(vertices[1+(i*2)]), copy(vertices[(2+(i*2)) % 12])
            d, e, f = copy(vertices[(2+(i*2)) % 12]), copy(vertices[1+(i*2)]), copy(vertices[(3+(i*2)) % 12])
            self.triangles += [Triangle((a, b, c)), Triangle((d, e, f))]

        for triangle in self.triangles:
            triangle.calculate_normals(0)

            a, b, c = triangle.vertices
            self.l_coords += [a.l_coords, b.l_coords, c.l_coords]
            self.t_coords += [a.t_coords, b.t_coords, c.t_coords]
            self.n_coords += [a.n_coords, b.n_coords, c.n_coords]

        self.l_coords = numpy.array(self.l_coords).ravel()
        self.t_coords = numpy.array(self.t_coords).ravel()
        self.n_coords = numpy.array(self.n_coords).ravel()

    def generate_texture(self):
        t_size = 512
        image = Image.new('RGB', (t_size, t_size), '#ffffff')
        draw = ImageDraw.Draw(image)

        texr = 0.125*t_size
        base_hex = []
        for i in range(6):
            x, y = ((texr+0.001)*math.cos(i/6.0*2.0*math.pi)), ((texr+0.001)*math.sin(i/6.0*2.0*math.pi))
            base_hex += [(x, y)]
        base_hex = numpy.array(base_hex)

        w = (math.sqrt(3.0)*texr)
        for i in range(6):
            angle = float(i)*((math.pi*2.0)/6.0) + math.pi/6.0
            xo, yo = w*math.cos(angle), w*math.sin(angle)
            this_hex = numpy.add(base_hex, numpy.array([(xo+(t_size/2.0), yo+(t_size/2.0))]*6))
            r, g, b = colorsys.hsv_to_rgb((random.random()*0.33)+0.13, 0.58, 0.56)
            draw.polygon(this_hex.ravel().tolist(), (int(r*255.0), int(g*255.0), int(b*255.0), 255))

        for i in range(6):
            orr = texr*3.0
            angle = float(i)*((math.pi*2.0)/6.0)
            xo, yo = orr*math.cos(angle), orr*math.sin(angle)
            this_hex = numpy.add(base_hex, numpy.array([(xo+(t_size/2.0), yo+(t_size/2.0))]*6))

            r, g, b = colorsys.hsv_to_rgb((random.random()*0.33)+0.13, 0.58, 0.56)
            draw.polygon(this_hex.ravel().tolist(), (int(r*255.0), int(g*255.0), int(b*255.0), 255))

        del draw

        data = numpy.array(image.getdata()).ravel()

        self.texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self.texture)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glGenerateMipmap(GL_TEXTURE_2D)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, t_size, t_size, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
