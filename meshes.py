"""
This module is used to generate 3D geometry used in the game.

The variables used for storing point coordinates often have short
names starting with 'p'. The following conventions are used:
- the number usually corresponds to the altitude (with 0 being the lowest)
- i - inner
- r/l - right/left
- f/b - front/back
"""
import pygame
import random
import math

import g3d
import railway

from util import parper2

# Depth order:
D_TRAIN = 0
D_SIGNAL = 0
D_STATION = 1
D_PROP = 2
D_RAIL = 3
D_GROUND = 4

# Mesh parameters:

TRAIN_HEIGHT = 25
TRAIN_WIDTH_HALF = 10
TRAIN_OVERLENGTH_HALF = 10
TRAIN_LEVEL = 2
TRAIN_COLOR = (65, 128, 176)

TRACK_WIDTH_HALF = 5
RAIL_WIDTH = 1
RAIL_COLOR = "#7e6649"
RAILWAY_BASE_COLOR = "#c0ac8e"

SIGNAL_POST_HEIGHT = TRAIN_LEVEL + TRAIN_HEIGHT + 6
SIGNAL_HEAD_HEIGHT = 18
SIGNAL_WIDTH = 3
SIGNAL_HEAD_WIDTH = 5
SIGNAL_POST_COLOR = (210, 210, 210)
SIGNAL_HEAD_COLOR = (50, 50, 50)

STATION_BASE_COLOR = (186, 176, 173)
PLATFORM_HEIGHT = TRAIN_LEVEL + 7
STATION_ROOF_COLOR = (179, 145, 96)
STATION_ROOF_LEVEL = TRAIN_LEVEL + TRAIN_HEIGHT + 5
STATION_ROOF_SLANT = 3
STATION_OFFSET = 200  # Station is shorter than the adjacent track by 2 offsets

TREE_COLOR1 = (69, 110, 45)
TREE_COLOR2 = (100, 176, 55)
HOUSE_COLOR1 = (248, 248, 246)
HOUSE_COLOR2 = (230, 230, 209)
ROOF_COLOR1 = (229, 186, 121)
ROOF_COLOR2 = (184, 144, 84)


def random_color(color1, color2):
    """
    Sample a random color which is a linear interpolation of the
    two given RGB tuples.
    """
    w = random.random()
    return [
        pygame.math.lerp(color1[0], color2[0], w),
        pygame.math.lerp(color1[1], color2[1], w),
        pygame.math.lerp(color1[2], color2[2], w)
    ]


def generate_tree(index, pos, depth):
    """
    Generate a tree at pos and associate it with the given index.
    The depth tuples for the generated triangles are the same
    as the given base depth tuple.
    """
    color = random_color(TREE_COLOR1, TREE_COLOR2)
    p0 = [pos[0], pos[1], 0]
    p1 = [pos[0], pos[1], random.uniform(80, 280)]
    radius = random.uniform(30, 55)
    base_angle = random.random() * 360
    angles = [0]
    while 360 - angles[-1] > 40:
        angles.append(angles[-1] + random.uniform(40, 80))
    angles[-1] = min(angles[-1], 350)
    prev_angle = angles[-1] + base_angle
    for angle in angles:
        angle += base_angle
        pa = p0.copy()
        pa[0] += radius * math.sin(math.radians(angle))
        pa[1] += radius * math.cos(math.radians(angle))
        pb = p0.copy()
        pb[0] += radius * math.sin(math.radians(prev_angle))
        pb[1] += radius * math.cos(math.radians(prev_angle))
        normal = [
            math.sin(math.radians(angle)), math.cos(math.radians(angle)), 0.5
        ]
        tri = g3d.add_triangle([pa, pb, p1], g3d.sunlight(color, normal), depth)
        railway_triangles[index].append(tri)
        prev_angle = angle


def generate_house(index, pos, depth):
    """
    Generate a house at pos and associate it with the given index.
    The depth tuples for the generated triangles are determined by
    appending additional elements to the given base depth tuple.
    """
    color = random_color(HOUSE_COLOR1, HOUSE_COLOR2)
    roof_color = random_color(ROOF_COLOR1, ROOF_COLOR2)
    length = random.uniform(40, 80)
    height = random.uniform(30, 60)
    roof_height = random.uniform(15, 25)
    angle = math.radians(random.random() * 360)
    par = [math.sin(angle), math.cos(angle)]
    per = [par[1], -par[0]]
    par[0] *= length
    par[1] *= length
    per[0] *= length
    per[1] *= length

    pos = pos.copy()
    pos[0] -= 0.5*(par[0] + per[0])
    pos[1] -= 0.5*(par[1] + per[1])

    p0a = [pos[0], pos[1], 0]
    p0b = [pos[0]+par[0], pos[1]+par[1], 0]
    p0c = [pos[0]+par[0]+per[0], pos[1]+par[1]+per[1], 0]
    p0d = [pos[0]+per[0], pos[1]+per[1], 0]
    pr = [pos[0]+0.5*par[0]+0.5*per[0], pos[1]+0.5*par[1]+0.5*per[1], 0]
    p1a = p0a.copy()
    p1a[2] += height
    p1b = p0b.copy()
    p1b[2] += height
    p1c = p0c.copy()
    p1c[2] += height
    p1d = p0d.copy()
    p1d[2] += height
    pr[2] += height + roof_height
    normal = [0, 0, -1]  # TODO House normals

    # Walls
    tri = g3d.add_triangle([p0a, p0b, p1b], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0a, p1a, p1b], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0b, p0c, p1c], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0b, p1b, p1c], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0c, p0d, p1d], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0c, p1c, p1d], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0d, p0a, p1a], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0d, p1d, p1a], g3d.sunlight(color, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)

    # Roof
    tri = g3d.add_triangle([p1a, p1b, pr], g3d.sunlight(roof_color, normal),
                           depth + (0,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1b, p1c, pr], g3d.sunlight(roof_color, normal),
                           depth + (0,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1c, p1d, pr], g3d.sunlight(roof_color, normal),
                           depth + (0,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1d, p1a, pr], g3d.sunlight(roof_color, normal),
                           depth + (0,))
    railway_triangles[index].append(tri)


def generate_props(index, pos1, pos2, low, high, reverse=False):
    """
    Generate trees and houses to the right of the track from pos1 to pos2,
    and associate them with the given index. The distance from the track
    to the props is bounded by low and high. Reverse can be set to True
    to generate the props to the left of the track.
    """
    par, per = parper2(pos1, pos2)
    if index not in railway_triangles:
        railway_triangles[index] = []
    last_positions = []
    length = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    n = 3 * (1 + length//railway.SEGMENT_LENGTH)  # Maximum number of props
    for _ in range(random.randint(0, n)):
        radius = random.uniform(low, high)  # Distance perpendicular to track
        offset = random.uniform(30, length - 30)  # Parallel to the track
        pos = pos1.copy()
        pos[0] += offset * par[0]
        pos[1] += offset * par[1]
        pos[0] += radius * per[0]
        pos[1] += radius * per[1]

        # Try not to make the prop overlap with another one
        skip = False
        for last in last_positions:
            distance_sq = (last[0] - pos[0])**2 + (last[1] - pos[1])**2
            if distance_sq < 3600:
                skip = True
                break
        if skip:
            continue
        last_positions.append(pos)

        if reverse:
            depth = (D_PROP, index, - offset**2 - radius**2)
        else:
            depth = (D_PROP, index, offset**2 + radius**2)

        if random.random() < 0.05:
            generate_house(index, pos, depth)
        else:
            generate_tree(index, pos, depth)


def generate_station(index, pos1, pos2, roof=True):
    """
    Generate a station mesh, to the right of the track from pos1 to pos2,
    and associate it with the given index.
    """
    par, per = parper2(pos1, pos2)
    # Ground
    pg1l = [pos1[0], pos1[1], 0]
    pg2l = [pos2[0], pos2[1], 0]
    pg1l[0] += +STATION_OFFSET * par[0] + 12 * per[0]
    pg1l[1] += +STATION_OFFSET * par[1] + 12 * per[1]
    pg2l[0] += -STATION_OFFSET * par[0] + 12 * per[0]
    pg2l[1] += -STATION_OFFSET * par[1] + 12 * per[1]
    pg1r = pg1l.copy()
    pg2r = pg2l.copy()
    pg1r[0] += 30 * per[0]
    pg1r[1] += 30 * per[1]
    pg2r[0] += 30 * per[0]
    pg2r[1] += 30 * per[1]
    # Platform
    pp1l = pg1l.copy()
    pp1l[2] = PLATFORM_HEIGHT
    pp2l = pg2l.copy()
    pp2l[2] = PLATFORM_HEIGHT
    pp1r = pg1r.copy()
    pp1r[2] = PLATFORM_HEIGHT
    pp2r = pg2r.copy()
    pp2r[2] = PLATFORM_HEIGHT
    # Roof
    pr1l = pg1l.copy()
    pr1l[2] = STATION_ROOF_LEVEL
    pr2l = pg2l.copy()
    pr2l[2] = STATION_ROOF_LEVEL
    pr1r = pg1r.copy()
    pr1r[2] = STATION_ROOF_LEVEL + STATION_ROOF_SLANT
    pr2r = pg2r.copy()
    pr2r[2] = STATION_ROOF_LEVEL + STATION_ROOF_SLANT

    if index not in railway_triangles:
        railway_triangles[index] = []

    depth = (D_STATION, index)

    # Platform top
    normal = [0, 0, 1]
    tri = g3d.add_triangle([pp1l, pp2l, pp2r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pp1l, pp2r, pp1r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (1,))
    railway_triangles[index].append(tri)
    # Left
    normal = [-per[0], -per[1], 0]
    tri = g3d.add_triangle([pg1l, pg2l, pp2l],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pg1l, pp1l, pp2l],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    # Right
    normal = [per[0], per[1], 0]
    tri = g3d.add_triangle([pg1r, pg2r, pp2r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pg1r, pp1r, pp2r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    # Near
    normal = [-par[0], -par[1], 0]
    tri = g3d.add_triangle([pg1l, pg1r, pp1r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pg1l, pp1l, pp1r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    # Far
    normal = [par[0], par[1], 0]
    tri = g3d.add_triangle([pg2l, pg2r, pp2r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pg2l, pp2l, pp2r],
                           g3d.sunlight(STATION_BASE_COLOR, normal),
                           depth + (2,))
    railway_triangles[index].append(tri)
    # Roof
    if roof:
        normal = [-per[0], -per[1], 2]
        tri = g3d.add_triangle([pr1l, pr2l, pr2r],
                               g3d.sunlight(STATION_ROOF_COLOR, normal),
                               depth + (0,))
        railway_triangles[index].append(tri)
        tri = g3d.add_triangle([pr1l, pr2r, pr1r],
                               g3d.sunlight(STATION_ROOF_COLOR, normal),
                               depth + (0,))
        railway_triangles[index].append(tri)


def generate_signal(index, pos1, pos2):
    """
    Generate a signal mesh positioned to the right of the track from
    pos1 to pos2, and associate it with the given index.
    """
    par, per = parper2(pos1, pos2)
    if index not in railway_triangles:
        railway_triangles[index] = []
    p0 = [pos1[0], pos1[1], 0]
    p0[0] += (12 + SIGNAL_WIDTH) * per[0] + 12 * par[0]
    p0[1] += (12 + SIGNAL_WIDTH) * per[1] + 12 * par[1]
    p0i = p0.copy()
    p0i[0] -= SIGNAL_WIDTH * per[0]
    p0i[1] -= SIGNAL_WIDTH * per[1]
    p1 = p0.copy()
    p1i = p0i.copy()
    depth = (D_SIGNAL, index)
    for i in range(5):
        p1[2] += SIGNAL_POST_HEIGHT / 5
        p1i[2] += SIGNAL_POST_HEIGHT / 5
        tri = g3d.add_triangle([p0, p0i, p1i], SIGNAL_POST_COLOR, depth)
        railway_triangles[index].append(tri)
        tri = g3d.add_triangle([p0, p1, p1i], SIGNAL_POST_COLOR, depth)
        railway_triangles[index].append(tri)
        p0 = p0.copy()
        p1 = p1.copy()
        p0i = p0i.copy()
        p1i = p1i.copy()
        p0[2] = p1[2]
        p0i[2] = p1i[2]
    p1[2] += SIGNAL_HEAD_HEIGHT
    p1i[2] += SIGNAL_HEAD_HEIGHT
    p0[0] += (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[0]
    p0[1] += (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[1]
    p0i[0] -= (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[0]
    p0i[1] -= (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[1]
    p1[0] += (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[0]
    p1[1] += (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[1]
    p1i[0] -= (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[0]
    p1i[1] -= (SIGNAL_HEAD_WIDTH - SIGNAL_WIDTH) / 2 * per[1]
    tri = g3d.add_triangle([p0, p0i, p1i], SIGNAL_HEAD_COLOR, depth)
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p0, p1, p1i], SIGNAL_HEAD_COLOR, depth)
    railway_triangles[index].append(tri)


def generate_track(index, pos1, pos2):
    """
    Generate railway track from pos1 to pos2 and associate the mesh
    with the specified railway index.
    """
    global railway_triangles

    # Rails

    par, per = parper2(pos1, pos2)
    p1l = [pos1[0], pos1[1], 0]
    p2l = [pos2[0], pos2[1], 0]
    p1r = [pos1[0], pos1[1], 0]
    p2r = [pos2[0], pos2[1], 0]
    p1l[0] -= per[0] * TRACK_WIDTH_HALF
    p1l[1] -= per[1] * TRACK_WIDTH_HALF
    p2l[0] -= per[0] * TRACK_WIDTH_HALF
    p2l[1] -= per[1] * TRACK_WIDTH_HALF
    p1r[0] += per[0] * TRACK_WIDTH_HALF
    p1r[1] += per[1] * TRACK_WIDTH_HALF
    p2r[0] += per[0] * TRACK_WIDTH_HALF
    p2r[1] += per[1] * TRACK_WIDTH_HALF
    p1li = p1l.copy()
    p2li = p2l.copy()
    p1ri = p1r.copy()
    p2ri = p2r.copy()
    p1li[0] += per[0] * RAIL_WIDTH
    p1li[1] += per[1] * RAIL_WIDTH
    p2li[0] += per[0] * RAIL_WIDTH
    p2li[1] += per[1] * RAIL_WIDTH
    p1ri[0] -= per[0] * RAIL_WIDTH
    p1ri[1] -= per[1] * RAIL_WIDTH
    p2ri[0] -= per[0] * RAIL_WIDTH
    p2ri[1] -= per[1] * RAIL_WIDTH

    depth = (D_RAIL,)

    if index not in railway_triangles:
        railway_triangles[index] = []
    tri = g3d.add_triangle([p1l, p2l, p2li], RAIL_COLOR, depth)
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1l, p1li, p2li], RAIL_COLOR, depth)
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1r, p2r, p2ri], RAIL_COLOR, depth)
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([p1r, p1ri, p2ri], RAIL_COLOR, depth)
    railway_triangles[index].append(tri)

    # Ground under the rails

    pb1l = p1l.copy()
    pb1l[0] -= per[0] * 7 + par[0] * 5
    pb1l[1] -= per[1] * 7 + par[1] * 5
    pb1l[2] -= 0.1
    pb2l = p2l.copy()
    pb2l[0] -= per[0] * 7 - par[0] * 5
    pb2l[1] -= per[1] * 7 - par[1] * 5
    pb2l[2] -= 0.1
    pb1r = p1r.copy()
    pb1r[0] += per[0] * 7 - par[0] * 5
    pb1r[1] += per[1] * 7 - par[1] * 5
    pb1r[2] -= 0.1
    pb2r = p2r.copy()
    pb2r[0] += per[0] * 7 + par[0] * 5
    pb2r[1] += per[1] * 7 + par[1] * 5
    pb2r[2] -= 0.1

    depth = (D_GROUND,)

    tri = g3d.add_triangle([pb1l, pb2l, pb2r], RAILWAY_BASE_COLOR, depth)
    railway_triangles[index].append(tri)
    tri = g3d.add_triangle([pb1l, pb1r, pb2r], RAILWAY_BASE_COLOR, depth)
    railway_triangles[index].append(tri)


def generate_train(cars, train_mesh):
    """
    Update the specified train mesh based on the given cars data.
    Cars is a list containing an even number of 2D points, where
    even index corresponds to the front of a car, and odd to the
    back.
    """
    for i in range(0, len(cars), 2):
        front = cars[i]
        back = cars[i + 1]
        par, per = parper2(back, front)
        front[0] += par[0]*TRAIN_OVERLENGTH_HALF
        front[1] += par[1]*TRAIN_OVERLENGTH_HALF
        back[0] -= par[0]*TRAIN_OVERLENGTH_HALF
        back[1] -= par[1]*TRAIN_OVERLENGTH_HALF

        pfl1 = [front[0], front[1], TRAIN_LEVEL]
        pbl1 = [back[0], back[1], TRAIN_LEVEL]
        pfr1 = pfl1.copy()
        pfr1[0] += per[0]*TRAIN_WIDTH_HALF
        pfr1[1] += per[1]*TRAIN_WIDTH_HALF
        pbr1 = pbl1.copy()
        pbr1[0] += per[0]*TRAIN_WIDTH_HALF
        pbr1[1] += per[1]*TRAIN_WIDTH_HALF
        pfl1[0] -= per[0]*TRAIN_WIDTH_HALF
        pfl1[1] -= per[1]*TRAIN_WIDTH_HALF
        pbl1[0] -= per[0]*TRAIN_WIDTH_HALF
        pbl1[1] -= per[1]*TRAIN_WIDTH_HALF

        pfl2 = pfl1.copy()
        pfl2[2] += TRAIN_HEIGHT
        pbl2 = pbl1.copy()
        pbl2[2] += TRAIN_HEIGHT
        pfr2 = pfr1.copy()
        pfr2[2] += TRAIN_HEIGHT
        pbr2 = pbr1.copy()
        pbr2[2] += TRAIN_HEIGHT

        depth = (D_TRAIN,)

        # Top
        g3d.mesh_triangle_set(train_mesh, (i, 0), [pfl2, pfr2, pbl2],
                              depth + (-i, 0))
        g3d.mesh_triangle_set(train_mesh, (i, 1), [pfr2, pbl2, pbr2],
                              depth + (-i, 0))
        normal = [0, 0, 1]
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 0))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 1))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        # Front
        g3d.mesh_triangle_set(train_mesh, (i, 2), [pfl1, pfr1, pfl2],
                              depth + (-i, 3))
        g3d.mesh_triangle_set(train_mesh, (i, 3), [pfr1, pfr2, pfl2],
                              depth + (-i, 3))
        normal = [par[0], par[1], 0]
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 2))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 3))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        # Back
        g3d.mesh_triangle_set(train_mesh, (i, 4), [pbl1, pbr1, pbl2],
                              depth + (-i, 1))
        g3d.mesh_triangle_set(train_mesh, (i, 5), [pbr1, pbr2, pbl2],
                              depth + (-i, 1))
        normal = [-par[0], -par[1], 0]
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 4))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 5))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        # Left
        g3d.mesh_triangle_set(train_mesh, (i, 6), [pfl1, pbl1, pbl2],
                              depth + (-i, 2))
        g3d.mesh_triangle_set(train_mesh, (i, 7), [pfl1, pfl2, pbl2],
                              depth + (-i, 2))
        normal = [-per[0], -per[1], 0]
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 6))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 7))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        # Right
        g3d.mesh_triangle_set(train_mesh, (i, 8), [pfr1, pbr1, pbr2],
                              depth + (-i, 2))
        g3d.mesh_triangle_set(train_mesh, (i, 9), [pfr1, pfr2, pbr2],
                              depth + (-i, 2))
        normal = [per[0], per[1], 0]
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 8))] = (
            g3d.sunlight(TRAIN_COLOR, normal))
        g3d.tri_color[g3d.mesh_triangle(train_mesh, (i, 9))] = (
            g3d.sunlight(TRAIN_COLOR, normal))


def setup():
    """
    Initialize the library.
    """
    global railway_triangles
    # Maps railway index to a list of triangle indices.
    # Used for garbage collection of unneeded meshes.
    railway_triangles = {}
