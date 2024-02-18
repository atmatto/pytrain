"""
This module provides functions related to the management
of the position of the train.

A train_position variable is a list consisting of a number and a deque.
The deque contains railway graph vertex indices. The first vertex from
the right is the one that the train is currently heading to, and the
previous ones represent the previously visited vertices. The number in
the train_position list is the current offset of the front of the train
from the vertex deque[-2] to deque[-1].
"""

import collections
import math

import railway
from meshes import STATION_OFFSET


def place_train(start_vertex=0):
    """
    Construct the initial train_position list.
    """
    next_vertex = None
    for (v2, draw, is_main) in railway.graph_connections[start_vertex]:
        next_vertex = v2
        if is_main:
            break
    return [0, collections.deque((start_vertex, next_vertex))]


def advance_train(train_position, delta):
    """
    Advance the position of the train by the given delta units. If needed,
    new vertices will be added to the deque, but unneeded vertices are not
    deleted by this function.
    """
    train_position[0] += delta
    v1 = train_position[1][-1]
    v2 = train_position[1][-2]
    v1p = railway.graph_vertex[v1]
    v2p = railway.graph_vertex[v2]
    distance_sq = (v1p[0] - v2p[0])**2 + (v1p[1] - v2p[1])**2
    while train_position[0]**2 > distance_sq:
        train_position[0] -= math.sqrt(distance_sq)
        next_vertex = None
        for (v3, draw, is_main) in railway.graph_connections[v1]:
            if is_main:
                next_vertex = v3
                break
        train_position[1].append(next_vertex)
        v1 = train_position[1][-1]
        v2 = train_position[1][-2]
        v1p = railway.graph_vertex[v1]
        v2p = railway.graph_vertex[v2]
        distance_sq = (v1p[0] - v2p[0])**2 + (v1p[1] - v2p[1])**2


def car_positions(train_position, deltas=None):
    """
    Return a list of 2D points from the front to the back of the train.
    Deltas[i] is the distance between (i-1)th and (i)th point.
    The 0-th delta must be equal to 0. This function removes unneeded
    vertices from the deque in train_position.
    """
    # This is accurate only for small angles™
    if deltas is None:
        deltas = train_deltas
    ans = []
    offset = train_position[0]
    segment_front = railway.graph_vertex[train_position[1][-1]]
    segment_back = railway.graph_vertex[train_position[1][-2]]
    unit = [
        segment_back[0] - segment_front[0],
        segment_back[1] - segment_front[1]
    ]
    length = math.sqrt(unit[0]**2 + unit[1]**2)
    unit[0] /= length
    unit[1] /= length
    next_point = len(train_position[1]) - 3
    for delta in deltas:
        offset -= delta
        while offset < 0:
            if next_point < 0:
                offset += length
                length += length
            else:
                segment_front = segment_back
                segment_back = railway.graph_vertex[
                    train_position[1][next_point]]
                unit = [
                    segment_back[0] - segment_front[0],
                    segment_back[1] - segment_front[1]
                ]
                length = math.sqrt(unit[0]**2 + unit[1]**2)
                unit[0] /= length
                unit[1] /= length
                offset += length
                next_point -= 1
        dv = unit.copy()
        dv[0] *= length - offset
        dv[1] *= length - offset
        ans.append([segment_front[0] + dv[0], segment_front[1] + dv[1]])
    # Remove unneeded vertices from the deque
    next_point -= 1
    while next_point >= 0:
        train_position[1].popleft()
        next_point -= 1
    return ans


def setup(cars, cars_sep):
    """
    Initialize the module. Cars is a list of the lengths of the cars
    of the train, starting from the front. Cars_sep is the distance
    between cars.
    """
    global train, train_sep, train_deltas, train_length
    train = cars
    train_sep = cars_sep
    train_deltas = [0, train[0]]
    for car in train[1:]:
        train_deltas.append(train_sep)
        train_deltas.append(car)
    train_length = sum(train_deltas)
    railway.STATION_LENGTH = train_length * 1.9 + 2 * STATION_OFFSET
