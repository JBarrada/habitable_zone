from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from scipy.spatial import ConvexHull
from scipy.linalg import norm
import math
import numpy
import random


class TerrainType:
    op, tu, de, fo, ma, sw, so, do = range(8)
    values = numpy.zeros(8)

    def __init__(self):
        self.values = numpy.zeros(8)

    def get_max_index(self):
        return numpy.argmax(self.values)


class WorldType:
    terrain_type = TerrainType()


class Geometry:
    points = []
    cells = []
    neighbors = []
    areas = []
    positions = []

    points_unwrapped = []

    def reset_geometry(self):
        self.points = []
        self.cells = []
        self.neighbors = []
        self.areas = []
        self.positions = []

        self.points_unwrapped = []


class World:
    univ_position = [0, 0, 0]
    
    terrain_geom = Geometry()
    atmosphere_geom = Geometry()

    terrain_cell_types = []
    atmosphere_cell_types = []

    terrain_texture = 0

    atmosphere_angle = 0.0

    world_size = 1.0
    world_seed = 0.0
    world_fill = 0.50
    world_smooth = 5
    world_type = WorldType()

    def __init__(self, size, seed, fill, smooth, worldtype):
        self.world_size = size
        self.world_seed = seed
        # self.world_fill = fill
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

    create_geometry(w.terrain_geom, int(500*size), seed)
    create_geometry(w.atmosphere_geom, int(400*size), seed)

    create_terrain(w)
    create_atmosphere(w)

    return w


def unwrap_geometry(geometry):
    geometry.points_unwrapped = numpy.zeros((len(geometry.points), 2))
    for i in range(len(geometry.points)):
        x, y, z = geometry.points[i]

        r = math.sqrt(math.pow(x, 2)+math.pow(y, 2)+math.pow(z, 2))
        t = math.atan2(y, x)
        p = math.acos(z / r)

        geometry.points_unwrapped[i] = (t/(math.pi*2.0), p/math.pi)


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

    unwrap_geometry(geometry)


def create_terrain(world):
    world.reset_terrain()

    random.seed(world.world_seed)

    world.terrain_cell_types = [0]*len(world.terrain_geom.cells)
    for cell in range(len(world.terrain_geom.cells)):
        world.terrain_cell_types[cell] = TerrainType()
        for i in range(8):
            world.terrain_cell_types[cell].values[i] = random.random()*float(world.world_type.terrain_type.values[i])

    for smooth in range(world.world_smooth):
        for cell in range(len(world.terrain_geom.cells)):
            perimeter_type = TerrainType()

            for neighbor in world.terrain_geom.neighbors[cell]:
                terrain_area_weight = world.terrain_cell_types[neighbor].values*world.terrain_geom.areas[neighbor]
                perimeter_type.values = numpy.add(perimeter_type.values, terrain_area_weight)

            max_index = perimeter_type.get_max_index()
            world.terrain_cell_types[cell].values[max_index] *= 1.5


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
    terrain_vertex_array = (world.terrain_geom.points*world.world_size).ravel()
    glVertexPointer(3, GL_FLOAT, 0, terrain_vertex_array)

    palette = [(0.4, 0.8, 0.2),
               (0.8, 0.8, 0.8),
               (0.7, 0.6, 0.1),
               (0.2, 0.5, 0.4),
               (0.0, 0.5, 0.4),
               (0.4, 0.3, 0.3),
               (0.4, 0.4, 0.6),
               (0.2, 0.2, 0.3)]

    glEnableClientState(GL_VERTEX_ARRAY)

    for i in range(8):
        terrain_index_array = []
        for cell in range(len(world.terrain_geom.cells)):
            if world.terrain_cell_types[cell].get_max_index() == i:
                terrain_index_array.append(world.terrain_geom.cells[cell])

        glColor3f(palette[i][0], palette[i][1], palette[i][2])
        tio = numpy.array(terrain_index_array).ravel()
        glDrawElements(GL_TRIANGLES, len(tio), GL_UNSIGNED_INT, tio)

    glDisableClientState(GL_VERTEX_ARRAY)

    # glBegin(GL_LINES)
    # for i in range(len(world.terrain_geom.cells)):
    #     a, b, c = world.terrain_geom.points_unwrapped[world.terrain_geom.cells[i]]
    #
    #     if norm(b-a) < 0.5:
    #         glVertex2f(a[0], a[1])
    #         glVertex2f(b[0], b[1])
    #
    #     if norm(a-c) < 0.5:
    #         glVertex2f(c[0], c[1])
    #         glVertex2f(a[0], a[1])
    #
    #     if norm(c-b) < 0.5:
    #         glVertex2f(b[0], b[1])
    #         glVertex2f(c[0], c[1])
    # glEnd()
