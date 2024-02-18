"""
This module is used to procedurally generate the railway.
"""
import random
import math
from util import normalize_v2

# Configuration

WINDOW_SIZE = (1280, 720)
FPS = 60  # Upper frames per second limit

# Constants

# railway_type, extension_railway_type
RT_MIXED = 0     # single two-way
RT_DOUBLE = 1    # double two-way
RT_FORWARD = 2   # single one-way forward
RT_BACKWARD = 3  # single one-way backward

# extension_type
ET_BRANCH = 0    # track turns out of the field of vision
ET_STATION = 1

# extension_direction
ED_IN_LEFT = 0
ED_IN_RIGHT = 1
ED_OUT_LEFT = 2
ED_OUT_RIGHT = 3

# signal_aspect
SA_PROCEED = 0  # 120 km/h
SA_LIMITED = 1  # 60 km/h
SA_CAUTION = 2  # 40 km/h
SA_STOP = 3

# signal_type
ST_MAIN = 0    # 3 lights, mainly for setting speed limit
# ST_BRANCH = 1  # like main, but also has distant signals
# ST_BLOCK = 2   # 2 lights, before a single track segment

SEGMENT_LENGTH = 100
STATION_LENGTH = 900


def add_extension(ext_type, rail_type, ext_direction):
    """
    Add a new extension and return its index.
    """
    extension_type.append(ext_type)
    extension_railway_type.append(rail_type)
    extension_direction.append(ext_direction)
    return len(extension_type) - 1


def railway_append(angle, rail_type, extension=None):
    """
    Add a new railway segment.
    """
    railway_angle.append(angle)
    railway_type.append(rail_type)
    railway_extension.append(extension)
    railway_speed.append(0)
    railway_signal.append(None)


def railway_set_speeds(station_index):
    """
    Set speed limits. This goes backward from the given index, which
    must be the railway index of a station, and sets only unset limits.
    """
    for i in range(station_index, -1, -1):
        if railway_speed[i] != 0:
            break
        if station_index - i < 20:
            railway_speed[i] = 40
        elif station_index - i < 90:
            railway_speed[i] = 60
        else:
            railway_speed[i] = 120


def railway_add_signals():
    """
    Add signals to the track. This function resumes the work from the
    last added signal and adds new signals where the speed limit changes.
    """
    start_i = 1
    if len(signal_index) != 0:
        start_i = signal_index[-1] + 1
    for i in range(start_i, len(railway_angle) - 2):
        if railway_speed[i] == 0:
            break
        st = None
        if railway_speed[i] != railway_speed[i - 1]:
            st = ST_MAIN
        # elif (railway_type[i + 1] == RT_MIXED
        #       and railway_type[i] == RT_DOUBLE):
        #     st = ST_BLOCK
        # elif (railway_extension[i + 2] is not None
        #       and extension_type[railway_extension[i + 2]] == ET_BRANCH):
        #     st = ST_BRANCH
        aspect = None
        if railway_speed[i] >= 120:
            aspect = SA_PROCEED
        elif railway_speed[i] >= 60:
            aspect = SA_LIMITED
        elif railway_speed[i] >= 40:
            aspect = SA_CAUTION
        if (railway_extension[i - 1] is not None
                and extension_type[railway_extension[i - 1]] == ET_STATION):
            aspect = SA_STOP
        if st is not None:
            railway_signal[i] = len(signal_index)
            signal_index.append(i)
            signal_aspect.append(aspect)
            signal_type.append(st)


def generate_railway():
    """
    A generator function for creating an intial description
    of the railway. Each time next() is used on the returned
    iterator, one new segment is generated. No value is yielded,
    everything is saved to global arrays.
    """
    rt = RT_DOUBLE  # railway type
    # Counters for enforcing some pause between changes:
    rt_counter = 12
    st_counter = 7
    ext_counter = 7
    ext = None
    while True:
        angle = random.uniform(-1, 1)
        # For smoothing, the same angle is used for multiple segments:
        num = 1
        if abs(angle) < 0.05:
            num = random.randint(20, 35)
        elif abs(angle) < 0.15:
            num = random.randint(10, 45)
        elif abs(angle) < 0.30:
            num = random.randint(7, 15)
        elif abs(angle) < 0.50:
            num = random.randint(6, 10)
        else:
            num = random.randint(5, 8)
        for _ in range(num):
            # Either change the railway type or add an extension
            if rt_counter <= 0:
                rt = random.choices([RT_DOUBLE, RT_MIXED], [3, 1])[0]
                rt_counter = random.randint(60, 120)
                ext_counter += 20
            else:
                ext_rt = ext_dir = 0
                ext = 0
                if ext_counter <= 0 and st_counter <= 0:
                    ext_type = ET_STATION
                    ext_counter = 30
                    rt_counter += 10
                    st_counter = random.randint(70, 700)
                elif ext_counter <= 0:
                    ext_type = ET_BRANCH
                    ext_counter = random.randint(70, 120)
                    if rt == RT_DOUBLE:
                        ext_rt = random.choice(
                            (RT_DOUBLE, RT_FORWARD, RT_BACKWARD))
                    else:
                        ext_rt = random.choice((RT_FORWARD, RT_BACKWARD))
                    if angle > 0:
                        ext_dir = random.choice((ED_IN_LEFT, ED_OUT_LEFT))
                    else:
                        ext_dir = random.choice((ED_IN_RIGHT, ED_OUT_RIGHT))
                else:
                    ext = None

                if ext is not None:
                    ext = add_extension(ext_type, ext_rt, ext_dir)
            # commit
            railway_append(angle, rt, ext)
            if ext is not None and ext_type == ET_STATION:
                railway_set_speeds(len(railway_angle) - 1)
            yield
            # post-commit
            rt_counter -= 1
            ext_counter -= 1
            st_counter -= 1
            ext = None


def get_railway_vertex(index, track=0):
    """
    Given a railway index, this function returns the corresponding
    graph vertex. The track number 0 is the forward track, -1 is the
    first on the left, going backward.
    """
    for rv in railway_vertices[index]:
        if rv[0] == track:
            return rv[1]


def graph_add(pos, index, station=None):
    """
    Add a vertex to the graph.
    """
    graph_vertex.append(pos)
    graph_connections.append([])
    graph_incoming.append([])
    graph_index.append(index)
    graph_station.append(station)
    return len(graph_vertex) - 1


def graph_connect(v1, v2, bidi=False, is_main=False):
    """
    Connect to graph vertices.
    """
    graph_connections[v1].append([v2, True, is_main])
    graph_incoming[v2].append([v1, True, is_main])
    if bidi:
        graph_connections[v2].append([v1, False, False])
        graph_incoming[v1].append([v2, False, False])


def generate_graph():
    """
    A generator function for creating a 2D graph of the railway network.
    Each time next() is used on the returned iterator, all railway segments
    not yet added to the graph are processed.
    No value is yielded, everything is saved to global arrays.
    This design makes it possible to extend the railway at
    any point in time.
    """
    start_i = 0
    rt_previous = railway_type[0]
    station = None
    station_id = 0
    angle = 0  # Absolute angle of the main track
    distance = 0  # Total distance from the beginning
    length = 0
    # Position of the last main track vertex
    last_vertex = [0, 0]
    while True:
        while start_i >= len(railway_angle) - 1:
            yield
        railway_add_signals()
        for i in range(start_i, len(railway_angle) - 1):
            ext = railway_extension[i]
            # Vertex
            angle -= railway_angle[i]
            real_angle = angle
            length_previous = length
            length = SEGMENT_LENGTH
            if railway_type[i] != rt_previous:
                length *= 7
                if rt_previous == RT_DOUBLE:
                    real_angle += 1.35
                else:
                    real_angle -= 1.35
            if station is not None:
                length = STATION_LENGTH
            station = None
            if ext is not None and extension_type[ext] == ET_STATION:
                station = station_id
                station_id += 1
                station_distance.append(distance + length_previous)
            pos = last_vertex.copy()
            pos[0] += length * math.sin(math.radians(real_angle))
            pos[1] -= length * math.cos(math.radians(real_angle))
            railway_vertices.append([[0, len(graph_vertex)]])
            if railway_type[i] != RT_DOUBLE:
                railway_vertices[i].append([-1, len(graph_vertex)])
            graph_add(pos, i, station)
            last_vertex = pos.copy()
            distance += length
            railway_distance.append(distance)
            # Edge
            if i != 0:
                graph_connect(
                    get_railway_vertex(i - 1), get_railway_vertex(i),
                    railway_type[i] == RT_MIXED and rt_previous == RT_MIXED,
                    True)
            # Normal
            middle = graph_vertex[get_railway_vertex(i)]
            forward_end = middle.copy()
            forward_end[0] += length * math.sin(
                math.radians(angle - railway_angle[i + 1]))
            forward_end[1] -= length * math.cos(math.radians(
                angle - railway_angle[i + 1]))
            forward = [forward_end[0] - middle[0],
                       forward_end[1] - middle[1]]
            normalize_v2(forward)
            if i == 0:
                backward = [-forward[0], -forward[1]]
            else:
                backward_end = graph_vertex[get_railway_vertex(i - 1)]
                backward = [backward_end[0] - middle[0],
                            backward_end[1] - middle[1]]
                normalize_v2(backward)
            n = [forward[1] - backward[1], -forward[0] + backward[0]]
            normalize_v2(n)
            normal.append(n)
            # Backward track
            if railway_type[i] == RT_DOUBLE and i < len(normal):
                pos2 = pos.copy()
                pos2[0] -= normal[i][0] * 24
                pos2[1] -= normal[i][1] * 24
                railway_vertices[i].append([-1, len(graph_vertex)])
                graph_add(pos2, i)
                if i > 0:
                    if rt_previous == RT_DOUBLE:
                        graph_connect(get_railway_vertex(i, -1),
                                      get_railway_vertex(i - 1, -1))
                    else:
                        graph_connect(get_railway_vertex(i, -1),
                                      get_railway_vertex(i - 1))
            elif railway_type[i] != RT_DOUBLE and rt_previous == RT_DOUBLE:
                graph_connect(get_railway_vertex(i),
                              get_railway_vertex(i - 1, -1))
            # Branch
            if ext is not None and extension_type[ext] == ET_BRANCH:
                direction = extension_direction[ext]
                if extension_railway_type[ext] == RT_DOUBLE:
                    tracks = [RT_FORWARD, RT_BACKWARD]
                else:
                    tracks = [extension_railway_type[ext]]
                for track in tracks:
                    if track == RT_BACKWARD:
                        vx = get_railway_vertex(i, -1)
                    else:
                        vx = get_railway_vertex(i, 0)
                    posb = graph_vertex[vx].copy()
                    branch_angle = angle
                    delta_angle = -10
                    if direction == ED_IN_LEFT or direction == ED_IN_RIGHT:
                        branch_angle -= 180
                        delta_angle *= -1
                    if direction == ED_IN_LEFT or direction == ED_OUT_LEFT:
                        delta_angle *= -1
                    for m in range(8):
                        if m < 7:
                            branch_angle += delta_angle
                        ba_rad = math.radians(branch_angle)
                        len_fact = 0.6
                        if m >= 7:
                            len_fact = 14
                        posb[0] += SEGMENT_LENGTH * len_fact * math.sin(ba_rad)
                        posb[1] -= SEGMENT_LENGTH * len_fact * math.cos(ba_rad)
                        graph_add(posb.copy(), None)
                        if ((track == RT_FORWARD and direction == ED_OUT_LEFT)
                                or (track == RT_FORWARD
                                    and direction == ED_OUT_RIGHT)
                                or (track == RT_BACKWARD
                                    and direction == ED_IN_RIGHT)
                                or (track == RT_BACKWARD
                                    and direction == ED_IN_LEFT)):
                            graph_connect(vx, len(graph_vertex) - 1)
                        else:
                            graph_connect(len(graph_vertex) - 1, vx)
                        vx = len(graph_vertex) - 1
            rt_previous = railway_type[i]
        start_i = len(railway_angle) - 1


def reset():
    """
    Reset the generated railway and make the module ready to generate
    a new railway for the next playthrough.
    """
    railway_angle.clear()
    railway_type.clear()
    railway_extension.clear()
    railway_vertices.clear()
    railway_distance.clear()
    railway_speed.clear()
    railway_signal.clear()

    extension_type.clear()
    extension_railway_type.clear()
    extension_direction.clear()

    graph_vertex.clear()
    graph_connections.clear()
    graph_incoming.clear()
    graph_index.clear()
    graph_station.clear()
    normal.clear()

    signal_index.clear()
    signal_aspect.clear()
    signal_type.clear()

    station_distance.clear()


railway_angle = []  # angle of the next forward edge relative to the previous
railway_type = []
railway_extension = []  # extension index
railway_vertices = []  # element: [track_number, vertex]
railway_distance = []  # distance from the begining to this node
railway_speed = []  # speed limit
railway_signal = []  # signal index or None

# extensions represent branching tracks and stations
extension_type = []
extension_railway_type = []
extension_direction = []

graph_vertex = []  # position of each vertex
graph_connections = []  # outgoing edges: pairs (target, draw?, main?)
graph_incoming = []  # incoming edges
graph_index = []  # railway index for the vertex, None for extensions
graph_station = []  # station id or None
normal = []  # vector pointing to the right

signal_index = []  # railway index of the location of the signal
signal_aspect = []
signal_type = []

station_distance = []  # Distance to this station from the beginning
