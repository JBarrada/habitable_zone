from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import numpy
import random
import colorsys
from PIL import Image, ImageDraw


class Hexagon:
    points = []
    triangles = []

    texture_coords = []
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
        glVertexPointer(3, GL_FLOAT, 0, self.points)
        glEnableClientState(GL_VERTEX_ARRAY)

        glTexCoordPointer(2, GL_FLOAT, 0, self.texture_coords)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glPushMatrix()

        x, y, z = self.position
        glTranslatef(x, y, z)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glActiveTexture(GL_TEXTURE0)

        glDrawElements(GL_TRIANGLES, len(self.triangles[0:4*3]), GL_UNSIGNED_INT, self.triangles[0:4*3])

        glDisable(GL_TEXTURE_2D)
        glDrawElements(GL_TRIANGLES, len(self.triangles[4*3:]), GL_UNSIGNED_INT, self.triangles[4*3:])

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glPopMatrix()

    def generate_geometry(self):
        self.points = []
        self.triangles = []

        for i in range(6):
            x, y = self.radius*math.cos(i/6.0*2*math.pi), self.radius*math.sin(i/6.0*2*math.pi)
            self.points += [(x, y, 0), (x, y, -self.height)]

        self.triangles = [(0, 2, 4), (0, 4, 6), (0, 6, 10), (6, 8, 10)]
        for i in range(6):
            self.triangles += [(0+(i*2), 1+(i*2), (2+(i*2)) % 12), ((2+(i*2)) % 12, 1+(i*2), (3+(i*2)) % 12)]

        self.points = numpy.array(self.points).ravel()
        self.triangles = numpy.array(self.triangles).ravel()

    def generate_texture(self):
        self.texture_coords = []
        for i in range(6):
            x, y = (0.5*math.cos(i/6.0*2*math.pi))+0.5, (0.5*math.sin(i/6.0*2*math.pi))+0.5
            self.texture_coords += [(x, y), (x, y)]
        self.texture_coords = numpy.array(self.texture_coords).ravel()

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
