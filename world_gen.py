from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from scipy.spatial import ConvexHull
from scipy.linalg import norm
import math
import numpy
import random


class WorldType:
    Normal, Desert, Ice, Land, Water = range(5)


class Geometry:
    points = []
    cells = []
    neighbors = []
    areas = []
    positions = []

    def reset_geometry(self):
        self.points = []
        self.cells = []
        self.neighbors = []
        self.areas = []
        self.positions = []


class World:
    univ_position = [0, 0, 0]
    
    terrain_geom = Geometry()
    atmosphere_geom = Geometry()

    terrain_cell_types = []
    atmosphere_cell_types = []

    atmosphere_angle = 0.0

    world_size = 1.0
    world_seed = 0.0
    world_fill = 0.50
    world_smooth = 5
    world_type = WorldType.Normal

    def __init__(self, size, seed, fill, smooth, worldtype):
        self.world_size = size
        self.world_seed = seed
        self.world_fill = fill
        self.world_smooth = smooth
        self.world_type = worldtype

    def reset_geometry(self):
        self.terrain_geom.reset_geometry()
        self.atmosphere_geom.reset_geometry()

    def reset_terrain(self):
        self.terrain_cell_types = []
    
    def reset_atmosphere(self):
        self.atmosphere_cell_types = []


def create_world(size, seed, fill, smooth, worldtype):
    w = World(size, seed, fill, smooth, worldtype)

    create_geometry(w.terrain_geom, 1500*size, seed)
    create_geometry(w.atmosphere_geom, 1000*size, seed)

    create_terrain(w)
    create_atmosphere(w)

    return w


def create_geometry(geometry, point_count, seed):
    geometry.reset_geometry()

    random.seed(seed)

    temp_points = []
    for i in range(point_count):
        theta = random.random()*(math.pi*2)
        u = random.random()*2.0 - 1.0

        x = math.sqrt(1.0-math.pow(u, 2))*math.cos(theta)
        y = math.sqrt(1.0-math.pow(u, 2))*math.sin(theta)
        z = u

        temp_points += [(x, y, z)]

    hull = ConvexHull(temp_points)

    geometry.points = hull.points
    geometry.cells = hull.simplices
    geometry.neighbors = hull.neighbors
    geometry.areas = numpy.zeros(len(geometry.cells))
    geometry.positions = numpy.zeros((len(geometry.cells), 3))

    for cell in range(len(geometry.cells)):
        a, b, c = geometry.points[geometry.cells[cell]]
        geometry.areas[cell] = norm(numpy.cross(b-a, c-a))/2.0
        geometry.positions[cell] = (a+b+c)/3.0


def create_terrain(world):
    world.reset_terrain()

    random.seed(world.world_seed)

    world.terrain_cell_types = [0]*len(world.terrain_geom.cells)
    for cell in range(len(world.terrain_geom.cells)):
        world.terrain_cell_types[cell] = 1 if random.random() < world.world_fill else 0

    for smooth in range(world.world_smooth):
        for cell in range(len(world.terrain_geom.cells)):
            live_area = 0.0
            dead_area = 0.0

            for neighbor in world.terrain_geom.neighbors[cell]:
                if world.terrain_cell_types[neighbor] == 0:
                    dead_area += world.terrain_geom.areas[neighbor]
                else:
                    live_area += world.terrain_geom.areas[neighbor]

            live_area *= (0.8 + math.pow(world.terrain_geom.positions[cell][2], 4)*2.0)

            if live_area > dead_area:
                world.terrain_cell_types[cell] = 1
            else:
                world.terrain_cell_types[cell] = 0
                

def create_atmosphere(world):
    world.reset_atmosphere()

    random.seed(world.world_seed+1)

    world.atmosphere_cell_types = [0]*len(world.atmosphere_geom.cells)
    for cell in range(len(world.atmosphere_geom.cells)):
        world.atmosphere_cell_types[cell] = 1 if random.random() < world.world_fill else 0

    for smooth in range(world.world_smooth):
        for cell in range(len(world.atmosphere_geom.cells)):
            live_area = 0.0
            dead_area = 0.0

            for neighbor in world.atmosphere_geom.neighbors[cell]:
                if world.atmosphere_cell_types[neighbor] == 0:
                    dead_area += world.atmosphere_geom.areas[neighbor]
                else:
                    live_area += world.atmosphere_geom.areas[neighbor]

            live_area *= (0.8 + math.pow(world.atmosphere_geom.positions[cell][2], 4)*2.0)

            if live_area > dead_area:
                world.atmosphere_cell_types[cell] = 1
            else:
                world.atmosphere_cell_types[cell] = 0


def draw_world(world):
    terrain_vertex_array = world.terrain_geom.points.ravel()

    live_index_array = []
    dead_index_array = []
    for cell in range(len(world.terrain_geom.cells)):
        if world.terrain_cell_types[cell] == 1:
            live_index_array += [world.terrain_geom.cells[cell]]
        else:
            dead_index_array += [world.terrain_geom.cells[cell]]

    lio = numpy.array(live_index_array).ravel()
    dio = numpy.array(dead_index_array).ravel()

    glVertexPointer(3, GL_FLOAT, 0, terrain_vertex_array)

    glEnableClientState(GL_VERTEX_ARRAY)

    glColor3f(0.8, 0.8, 0.8)
    glDrawElements(GL_TRIANGLES, len(lio), GL_UNSIGNED_INT, lio)

    glColor3f(0.2, 0.2, 0.3)
    glDrawElements(GL_TRIANGLES, len(dio), GL_UNSIGNED_INT, dio)

    glDisableClientState(GL_VERTEX_ARRAY)

    # atmosphere
    glRotatef(world.atmosphere_angle, 0, 0, 1)
    world.atmosphere_angle += 0.005

    atmosphere_vertex_array = (world.atmosphere_geom.points*1.015).ravel()

    atmosphere_index_array = []
    for cell in range(len(world.atmosphere_geom.cells)):
        if world.atmosphere_cell_types[cell] == 1:
            atmosphere_index_array += [world.atmosphere_geom.cells[cell]]

    aio = numpy.array(atmosphere_index_array).ravel()

    glVertexPointer(3, GL_FLOAT, 0, atmosphere_vertex_array)

    glEnableClientState(GL_VERTEX_ARRAY)

    glColor4f(0.5, 0.5, 0.5, 0.1)
    glDrawElements(GL_TRIANGLES, len(aio), GL_UNSIGNED_INT, aio)

    glDisableClientState(GL_VERTEX_ARRAY)
