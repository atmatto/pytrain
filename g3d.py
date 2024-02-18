"""
This module manages triangles in three dimensions and draws them
on screen.

Run this file as a script to see a simple demo - use WASD to move,
Q and E to move up and down, and the arrow keys to look around.
If used as a library, the setup() function must be called before
any other.

The properties of triangles are stored in several lists. They are
refered to by their indices. If a more structured way of refering
to a set of triangles is needed, meshes, which allow to refer to
triangles by arbitrary keys, can be used.

Because of performance limitations, a proper depth buffer cannot
be used for occlusion testing. Therefore all triangles must be
sorted by depth before rendering each frame. Because the scene
in this game is generally viewed from a rather static angle,
instead of using a sophisticated triangle sorting algorithm,
each triangle has its own sorting key according to which it is
sorted. The key has the form of a tuple, which allows for easy
separation of triangles into layers, and then ordering by depth
inside these layers.
"""
import sys
import pygame
import random
import math
import pygame.gfxdraw

from util import normalize_v3

# Configuration

FOV = 60  # Camera field of view in degrees
# Sun bias is added to the color of surfaces exposed to sunlight
SUN_BIAS = (20, 20, 20)


def world_to_camera(world):
    """
    Transform a 3D point from the world coordinates to the
    camera space, where the camera is positioned in the origin,
    and looking from it the x axis goes to the right, y goes up
    and z is the depth.
    """
    (x, y, z) = world
    yaw = -math.radians(camera_yaw + 180)
    pitch = -math.radians(camera_pitch + 90)

    # Undo translation
    x -= camera_position[0]
    y -= camera_position[1]
    z -= camera_position[2]
    x *= -1
    # Undo z rotation (yaw)
    xa = math.cos(yaw)*x - math.sin(yaw)*y
    ya = math.sin(yaw)*x + math.cos(yaw)*y
    za = z
    # Undo x rotation (pitch)
    xc = xa
    yc = math.cos(pitch)*ya - math.sin(pitch)*za
    zc = math.sin(pitch)*ya + math.cos(pitch)*za
    return (xc, yc, zc)


def camera_to_screen(camera):
    """
    Transform a 3D point from camera coordinates to 2D screen space.
    The returned vector has a third component, which corresponds to
    the depth.
    """
    (xc, yc, zc) = camera
    f = 2000  # far
    n = 1  # near
    S = 1/(math.tan(math.radians(FOV/2)))  # scale

    xc = S*xc
    yc = S*yc
    zc = -f/(f-n)*zc - (f*n)/(f-n)
    wc = -zc

    xc /= wc
    yc /= wc
    zc /= wc
    wc = math.copysign(1, wc)

    yc /= window_rect.height/window_rect.width  # Correct aspect ratio.
    return ((xc + 1)*window_rect.width/2, (1 - (yc+1)/2)*window_rect.height, wc)


def add_triangle(tri, color, depth):
    """
    Add a new triangle for rendering.
    Tri is a list of three points. Depth is the tuple for depth sorting.
    Return the index of the new triangle.
    """
    t = None
    # Find a free place in the triangle list
    for i, d in enumerate(descriptor):
        if not d:
            t = i
            break
    if t is None:
        # Extend the list
        t = len(descriptor)
        descriptor.append(True)
        triangle.append(tri)
        tri_color.append(color)
        tri_depth.append(depth)
    else:
        # Reuse a free index
        descriptor[t] = True
        triangle[t] = tri
        tri_color[t] = color
        tri_depth[t] = depth
    return t


def free_triangle(index):
    """
    Remove a triangle from the renderer. This leaves place for
    a new triangle in order to conserve memory without having
    to move the elements of all lists.
    """
    descriptor[index] = False


def clip(tri):
    """
    For proper rendering, parts of the triangles which are behind
    the camera have to be removed. This function accepts a list
    of three points in camera space and clips them. It returns
    a list containing the resulting triangles, still in camera
    space. From 0 to 2 resulting triangles can be returned.
    """
    front = []  # Indices of vertices in front of the camera
    behind = []  # Indices of vertices behind the camera
    for i in range(3):
        if tri[i][2] < 0:
            behind.append(i)
        else:
            front.append(i)

    if len(front) == 0:
        # Whole triangle behind the camera
        return []
    if len(behind) == 0:
        # Whole triangle in front of the camera
        return [[tri[0], tri[1], tri[2]]]
    if len(front) == 1:
        # Will get one triangle
        w0 = tri[front[0]][2] / (tri[front[0]][2] - tri[behind[0]][2])
        w1 = tri[front[0]][2] / (tri[front[0]][2] - tri[behind[1]][2])
        p0 = list(tri[front[0]])
        p0[0] += w0 * (tri[behind[0]][0] - p0[0])
        p0[1] += w0 * (tri[behind[0]][1] - p0[1])
        p0[2] += w0 * (tri[behind[0]][2] - p0[2])
        p1 = list(tri[front[0]])
        p1[0] += w1 * (tri[behind[1]][0] - p1[0])
        p1[1] += w1 * (tri[behind[1]][1] - p1[1])
        p1[2] += w1 * (tri[behind[1]][2] - p1[2])
        pf = list(tri[front[0]])
        return [[pf, p0, p1]]
    if len(front) == 2:
        # Will get a rectangle (two triangles)
        w0 = tri[front[0]][2] / (tri[front[0]][2] - tri[behind[0]][2])
        w1 = tri[front[1]][2] / (tri[front[1]][2] - tri[behind[0]][2])
        p0 = list(tri[behind[0]])
        p0[0] += (1 - w0) * (tri[front[0]][0] - p0[0])
        p0[1] += (1 - w0) * (tri[front[0]][1] - p0[1])
        p0[2] += (1 - w0) * (tri[front[0]][2] - p0[2])
        p1 = list(tri[behind[0]])
        p1[0] += (1 - w1) * (tri[front[1]][0] - p1[0])
        p1[1] += (1 - w1) * (tri[front[1]][1] - p1[1])
        p1[2] += (1 - w1) * (tri[front[1]][2] - p1[2])
        pf0 = list(tri[front[0]])
        pf1 = list(tri[front[1]])
        return [[pf0, pf1, p1], [pf0, p1, p0]]


def clip_window(poly):
    """
    Pygame's polygon rasterization slows down (and can even
    freeze the game) when the polygon extends far beyond the
    screen. This function accepts a list of at least three
    2D points and returns a new list of points representing
    a polygon entirely contained inside the game window.
    This is an implementation of the Sutherland–Hodgman algorithm.
    """
    input = None
    output = poly

    clip_edge = None  # The middle point of the edge
    clip_direction = None  # Vector pointing inside from the edge
    clips = (  # Pairs (edge, direction)
        (window_rect.midleft, (1, 0)),
        (window_rect.midtop, (0, 1)),
        (window_rect.midright, (-1, 0)),
        (window_rect.midbottom, (0, -1))
    )

    for (clip_edge, clip_direction) in clips:
        input = output
        output = []
        for i, p0 in enumerate(input):
            p1 = input[(i - 1) % len(input)]  # Previous point
            p0_inside = (
                (p0[0] - clip_edge[0]) * clip_direction[0]
                + (p0[1] - clip_edge[1]) * clip_direction[1]) > 0
            p1_inside = (
                (p1[0] - clip_edge[0]) * clip_direction[0]
                + (p1[1] - clip_edge[1]) * clip_direction[1]) > 0

            if not (p0_inside and p1_inside):
                # Calculate intersection of the line p0-p1 with the clip edge
                if clip_direction[0] == 0:
                    # Clip edge is horizontal
                    if p1[1] == p0[1]:
                        w = 0.5
                    else:
                        w = (clip_edge[1] - p0[1])/(p1[1] - p0[1])
                    intersection = [p0[0] + w * (p1[0] - p0[0]), clip_edge[1]]
                else:
                    # Clip edge is vertical
                    if p1[0] == p0[0]:
                        w = 0.5
                    else:
                        w = (clip_edge[0] - p0[0])/(p1[0] - p0[0])
                    intersection = [clip_edge[0], p0[1] + w * (p1[1] - p0[1])]

            if p0_inside:
                if not p1_inside:
                    output.append(intersection)
                output.append(p0)
            elif p1_inside:
                output.append(intersection)
    return output


def fill_triangle(tri, color):
    """
    Draw a filled triangle on the screen.
    """
    points = clip_window(tri)
    if len(points) > 2:
        pygame.draw.polygon(window, color, points)


def render():
    """
    Draw all triangles on screen.
    """
    render_queue.clear()  # Invalidate previous render queue

    # Transform and clip all existing triangles and add them to the queue
    for i in range(len(descriptor)):
        if not descriptor[i]:
            continue
        p1 = world_to_camera(triangle[i][0])
        p2 = world_to_camera(triangle[i][1])
        p3 = world_to_camera(triangle[i][2])
        tris = clip([p1, p2, p3])
        for tri in tris:
            (q1, q2, q3) = tri
            tri[0] = camera_to_screen(q1)
            tri[1] = camera_to_screen(q2)
            tri[2] = camera_to_screen(q3)
            # Although the depth order is specified by the depth tuples,
            # it often isn't sufficient and this is used for tie-breaking.
            depth = (min(p1[2], p2[2], p3[2]), (p1[2] + p2[2] + p3[2])/3)
            render_queue.append([
                tri_depth[i], depth, i, [tri[0][0:2], tri[1][0:2], tri[2][0:2]]
            ])

    # Determine the order ("Painter's algorithm")
    render_queue.sort(
        reverse=True
    )

    # Draw the triangles to screen.
    for [_, _, i, tri] in render_queue:
        if render_solid:
            fill_triangle(tri, tri_color[i])
            if render_wireframe:
                pygame.draw.polygon(window, "black", tri, 1)
        else:
            pygame.draw.polygon(window, tri_color[i], tri, 1)


def toggle_debug_render():
    """
    Toggle special rendering modes used for debug purposes.
    """
    global render_solid, render_wireframe
    if render_solid and render_wireframe:
        render_solid = True
        render_wireframe = False
    elif render_solid:
        render_solid = False
        render_wireframe = True
    elif render_wireframe:
        render_solid = True
    render_solid = not render_solid


def display_stats():
    """
    Display a framerate counter and number of triangles.
    The FPS are averaged out over multiple frames.
    """
    global stats_ticks, stats_fps, stats_frames

    # Calculate FPS
    stats_frames += 1
    ticks = pygame.time.get_ticks()
    if stats_frames % 10 == 0:
        stats_fps = str(1000 // max(1, (ticks - stats_ticks)/10))
        stats_ticks = ticks

    tris = str(sum(1 for _ in filter(lambda d: d, descriptor)))

    # Draw
    t = font.render(f"FPS: {stats_fps} Tris: {tris}", True, "white", "black")
    r = t.get_rect().move(10, 10)
    window.blit(t, r)


def mesh_new():
    """
    Return a new empty mesh.
    """
    return {}


def mesh_triangle(mesh, tri_key):
    """
    Return the index of a triangle belonging to the mesh
    by its key. The key can be arbitrary hashable object.
    If the triangle with this key doesn't exist, it will
    be created.
    """
    if tri_key in mesh:
        return mesh[tri_key]
    tri = add_triangle([[0, 0, 0], [0, 0, 0], [0, 0, 0]], "purple", (-10000))
    mesh[tri_key] = tri
    return tri


def mesh_triangle_set(mesh, tri_key, new_tri, depth):
    """
    A helper function which wraps mesh_triangle() and
    allows to easily overwrite the triangle with a new
    one and update its depth tuple.
    """
    tri = mesh_triangle(mesh, tri_key)
    for i in range(3):
        for j in range(3):
            triangle[tri][i][j] = new_tri[i][j]
    tri_depth[tri] = depth


def mesh_free(mesh):
    """
    Free all triangles belonging to the mesh.
    The mesh is ready to be reused afterwards.
    """
    for tri in mesh.values():
        free_triangle(tri)
    mesh.clear()


def sunlight(base_color, normal):
    """
    Supplied with the color of a triangle, and its
    normal vector, this function returns a new color
    influenced by the sunlight. The given color must
    be an iterable of 3 elements.
    """
    normalize_v3(normal)
    dot = normal[0] * sun_direction[0]
    dot += normal[1] * sun_direction[1]
    dot += normal[2] * sun_direction[2]
    dot = -min(0, dot)
    return [
        min(255, base_color[0] + SUN_BIAS[0] * dot),
        min(255, base_color[1] + SUN_BIAS[1] * dot),
        min(255, base_color[2] + SUN_BIAS[2] * dot)
    ]


def demo():
    """
    Run a demonstration of the library.
    """
    global camera_pitch, camera_yaw
    clock = pygame.time.Clock()

    # Generate the world

    N = 20
    SIZE = 20
    heights = [[20*math.sin(i)*math.cos(j) for i in range(N)]
               for j in range(N)]
    for i in range(1, N):
        for j in range(1, N):
            x = SIZE * i
            y = SIZE * j
            r = random.uniform(-50, 20)
            add_triangle([[x, y, heights[i-1][j-1]],
                          [x + SIZE, y + SIZE, heights[i][j]],
                          [x + SIZE, y, heights[i][j-1]]],
                         (180+r, 180+r, 230+r),
                         (x, y))
            r = random.uniform(-5, 5)
            add_triangle([[x, y, heights[i-1][j-1]],
                          [x + SIZE, y + SIZE, heights[i][j]],
                          [x, y + SIZE, heights[i-1][j]]],
                         (180+r, 180+r, 230+r),
                         (x, y))
    print(len(descriptor))

    while True:
        # Handle user input

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.dict["key"] == pygame.K_z:
                    toggle_debug_render()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            camera_pitch -= 1
        if keys[pygame.K_DOWN]:
            camera_pitch += 1
        if keys[pygame.K_RIGHT]:
            camera_yaw += 1
        if keys[pygame.K_LEFT]:
            camera_yaw -= 1
        if keys[pygame.K_w]:
            camera_position[0] += math.sin(math.radians(camera_yaw))
            camera_position[1] += math.cos(math.radians(camera_yaw))
        if keys[pygame.K_a]:
            camera_position[0] -= math.cos(math.radians(camera_yaw))
            camera_position[1] += math.sin(math.radians(camera_yaw))
        if keys[pygame.K_s]:
            camera_position[0] -= math.sin(math.radians(camera_yaw))
            camera_position[1] -= math.cos(math.radians(camera_yaw))
        if keys[pygame.K_d]:
            camera_position[0] += math.cos(math.radians(camera_yaw))
            camera_position[1] -= math.sin(math.radians(camera_yaw))
        if keys[pygame.K_q]:
            camera_position[2] -= 1
        if keys[pygame.K_e]:
            camera_position[2] += 1
        camera_pitch = pygame.math.clamp(camera_pitch, -90, 90)

        # Update geometry

        heights = [[20*math.sin(i + pygame.time.get_ticks()/1000)
                    * math.cos(j + pygame.time.get_ticks()/1000)
                    + 30*math.sin(i/10 + pygame.time.get_ticks()/20000)
                    for i in range(N)] for j in range(N)]
        ti = 0
        for i in range(1, N):
            for j in range(1, N):
                x = SIZE * i
                y = SIZE * j
                triangle[ti][0][2] = heights[i-1][j-1]
                triangle[ti][1][2] = heights[i][j]
                triangle[ti][2][2] = heights[i][j-1]
                ti += 1
                triangle[ti][0][2] = heights[i-1][j-1]
                triangle[ti][1][2] = heights[i][j]
                triangle[ti][2][2] = heights[i-1][j]
                ti += 1

        # Draw

        window.fill((240, 240, 255))
        render()
        display_stats()
        pygame.display.flip()
        clock.tick(FPS)


def setup(surface, window_rectangle):
    """
    Initialize all needed global variables
    """
    global font, window_rect, window, stats_ticks, stats_fps, stats_frames
    global render_queue
    font = pygame.font.Font("freesansbold.ttf", 18)
    window_rect = window_rectangle
    window = surface
    stats_ticks = 0
    stats_fps = ""
    stats_frames = 0
    render_queue = []


def reset():
    """
    Delete all triangles. Calling this function invalidates
    all existing meshes.
    """
    descriptor.clear()
    triangle.clear()
    tri_color.clear()
    tri_depth.clear()


camera_position = [0, 0, 10]
camera_pitch = 0
camera_yaw = 0

sun_direction = [1, 1, -2]
normalize_v3(sun_direction)

render_wireframe = False  # Draw the wireframe of each triangle
render_solid = True  # Set to False in order to draw the wireframe only

descriptor = []  # True for existing tris, False for vacant slots
triangle = []  # Each triangle is an iterable of three 3D points
tri_color = []  # Triangle color
tri_depth = []  # The key used for depth sorting, must be a tuple

if __name__ == "__main__":
    WINDOW_SIZE = (1280, 720)
    FPS = 60  # Upper frames per second limit

    random.seed()
    pygame.init()

    window = pygame.display.set_mode(WINDOW_SIZE)
    window_rect = window.get_rect()

    setup(window, window_rect)

    demo()
