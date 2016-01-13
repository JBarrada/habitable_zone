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


class World:
    univ_position = [0, 0, 0]

    geom_points = []
    geom_cells = []
    geom_neighbors = []
    geom_cell_areas = []
    geom_cell_positions = []

    terrain_cell_types = []

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
        self.geom_points = []
        self.geom_cells = []
        self.geom_neighbors = []
        self.geom_cell_areas = []
        self.geom_cell_positions = []

    def reset_terrain(self):
        self.terrain_cell_types = []


def create_world(size, seed, fill, smooth, worldtype):
    w = World(size, seed, fill, smooth, worldtype)

    create_geometry(w)

    create_terrain(w)

    return w


def create_geometry(world):
    world.reset_geometry()

    random.seed(world.world_seed)

    temp_points = []
    for i in range(800*world.world_size):
        theta = random.random()*(math.pi*2)
        u = random.random()*2.0 - 1.0

        x = math.sqrt(1.0-math.pow(u, 2))*math.cos(theta)
        y = math.sqrt(1.0-math.pow(u, 2))*math.sin(theta)
        z = u

        temp_points += [(x, y, z)]

    hull = ConvexHull(temp_points)

    world.geom_points = hull.points
    world.geom_cells = hull.simplices
    world.geom_neighbors = hull.neighbors
    world.geom_cell_areas = numpy.zeros(len(world.geom_cells))
    world.geom_cell_positions = numpy.zeros((len(world.geom_cells), 3))

    for cell in range(len(world.geom_cells)):
        a, b, c = world.geom_points[world.geom_cells[cell]]
        world.geom_cell_areas[cell] = norm(numpy.cross(b-a, c-a))/2.0
        world.geom_cell_positions[cell] = (a+b+c)/3.0


def create_terrain(world):
    world.reset_terrain()

    random.seed(world.world_seed)

    world.terrain_cell_types = [0]*len(world.geom_cells)
    for cell in range(len(world.geom_cells)):
        world.terrain_cell_types[cell] = 1 if random.random() < world.world_fill else 0

    for smooth in range(world.world_smooth):
        for cell in range(len(world.geom_cells)):
            live_area = 0.0
            dead_area = 0.0

            for neighbor in world.geom_neighbors[cell]:
                if world.terrain_cell_types[neighbor] == 0:
                    dead_area += world.geom_cell_areas[neighbor]
                else:
                    live_area += world.geom_cell_areas[neighbor]

            live_area *= (0.8 + math.pow(world.geom_cell_positions[cell][2], 4)*2.0)

            if live_area > dead_area:
                world.terrain_cell_types[cell] = 1
            else:
                world.terrain_cell_types[cell] = 0


def draw_world(world):
    color_array = [0.2, 0.2, 0.3, 0.8, 0.8, 0.8]
    vertex_array = world.geom_points.ravel()
    index_array = world.geom_cells.ravel()

    # glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    # glColorPointer(3, GL_FLOAT, 0, color_array)
    glVertexPointer(3, GL_FLOAT, 0, vertex_array)
    glDrawElements(GL_TRIANGLES, len(index_array), GL_UNSIGNED_INT, index_array)
    # glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)

    # glBegin(GL_TRIANGLES)
    # for i in range(len(world.geom_cells)):
    #     if world.terrain_cell_types[i] != 0:
    #         glColor3f(0.8, 0.8, 0.8)
    #     else:
    #         glColor3f(0.2, 0.2, 0.3)
#
    #     for pindex in world.geom_cells[i]:
    #         x, y, z = (world.geom_points[pindex]*world.world_size)+world.univ_position
#
    #         glVertex3f(x, y, z)
    # glEnd()
