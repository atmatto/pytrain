"""
This module provides commonly used utility functions.
"""
import math


def normalize_v2(vec):
    """
    Given a two-dimensional vector, replace it in-place
    with a vector of the same direction but length 1.
    """
    if len(vec) != 2:
        raise TypeError
    mag = math.sqrt(vec[0]**2 + vec[1]**2)
    if mag != 0:
        vec[0] /= mag
        vec[1] /= mag


def normalize_v3(vec):
    """
    Given a three-dimensional vector, replace it in-place
    with a vector of the same direction but length 1.
    """
    if len(vec) != 3:
        raise TypeError
    mag = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    if mag != 0:
        vec[0] /= mag
        vec[1] /= mag
        vec[2] /= mag


def parper2(p1, p2):
    """
    Given two two-dimensional points, return two normalized
    vectors. The first returned vector points in the direction
    from p1 to p2, and the second is perpendicular and points
    to the right of the first vector.
    """
    par = [p2[0] - p1[0], p2[1] - p1[1]]
    mag = math.sqrt(par[0]**2 + par[1]**2)
    par[0] /= mag
    par[1] /= mag
    per = [par[1], -par[0]]
    mag = math.sqrt(per[0]**2 + per[1]**2)
    per[0] /= mag
    per[1] /= mag
    return par, per
