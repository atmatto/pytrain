"""
This module is used to render the user interface.
"""
import pygame
import math

from railway import SA_PROCEED, SA_LIMITED, SA_CAUTION, SA_STOP

MARGIN = 30

COLOR_NEUTRAL = "#cad6e6"
COLOR_ACCENT = "#3489f7"
COLOR_BRIGHT = "#e5e5e5"
POWER_TEXT = "black"
POWER_PADDING = 5
POWER_TRIANGLE = 10  # height
POWER_LEVELS = [  # [group, level, description, height]
    (-1, -3, "Brake", 35),
    (-1, -2, "Brake", 30),
    (-1, -1, "Brake", 25),
    (0, 0, "Neutral", 22),
    (1, 1, "Cruise", 15),
    (1, 2, "Accelerate", 30),
    (1, 3, "Accelerate", 38),
]
POWER_GROUPS = {
    -1: "B",
    0: "N",
    1: "D"
}

STAR_SIZE = 30
STAR_COLOR = "gold"

COLOR_TEXT = "black"
COLOR_DISTANT = "#353535"
COLOR_SIGNAL = "#202020"
COLOR_WARNING = "red"


def draw_signal(distance, aspect):
    """
    Draw a signal showing the given aspect and being located distance
    metres in front of the train.
    """
    if distance > 300:
        return
    lights = [
        "green" if (
            aspect == SA_PROCEED or aspect == SA_LIMITED
        ) else "black",
        "yellow" if (
            aspect == SA_LIMITED or aspect == SA_CAUTION
        ) else "black",
        "red" if (
            aspect == SA_STOP
        ) else "black",
    ]
    pos = [window_rect.right - 30 - MARGIN, window_rect.top + 300]
    dist = font_small.render(str(math.ceil(distance)) + "m", True, COLOR_TEXT)
    dist_rect = dist.get_rect()
    dist_rect.midbottom = pos.copy()
    dist_rect.bottom -= 40
    if distance > 10:
        window.blit(dist, dist_rect)
    for i, light in enumerate(lights):
        if i == 3:
            pos[1] += 15
        if i != 4 and i != 2:
            pygame.draw.rect(window, COLOR_SIGNAL,
                             (pos[0] - 30, pos[1], 60, 50))
        pygame.draw.circle(window, COLOR_SIGNAL, pos, 30)
        pygame.draw.circle(window, light, pos, 20)
        pygame.draw.circle(window, "#555555", pos, 20, 2)
        pos[1] += 50
    pos[1] -= 50
    status = ""
    status2 = ""

    if aspect == SA_PROCEED:
        status = "120 km/h"
    elif aspect == SA_LIMITED:
        status = "60 km/h"
    elif aspect == SA_CAUTION:
        status = "40 km/h"
        status2 = "STOP"
    elif aspect == SA_STOP:
        status = "STOP"
    stat = font_small.render(status, True, COLOR_TEXT)
    stat_rect = stat.get_rect()
    stat_rect.midtop = pos.copy()
    stat_rect.top += 40
    window.blit(stat, stat_rect)
    if status2 != "":
        then = font_small.render("THEN", True, COLOR_DISTANT)
        then_rect = then.get_rect()
        then_rect.midtop = stat_rect.midbottom
        then_rect.top += 15
        stat2 = font_small.render(status2, True, COLOR_DISTANT)
        stat2_rect = stat2.get_rect()
        stat2_rect.midtop = then_rect.midbottom
        window.blit(then, then_rect)
        window.blit(stat2, stat2_rect)


def draw_approach(distance, time, now):
    """
    Draw approach indicators. Distance is the signed distance to the perfect
    stop location (in metres), time is the planned arrival time (ms) and now
    is the current time.
    """
    pos = list(window_rect.center)
    pos[0] -= 200

    dist = str(abs(math.floor(distance))) + " m"
    if abs(distance) < 5:
        dist = str(math.floor(abs(distance)*100)) + " cm"
    dist_text = font_giant.render(dist, True, COLOR_TEXT)
    dist_rect = dist_text.get_rect()
    dist_rect.center = pos
    window.blit(dist_text, dist_rect)

    vert = -math.copysign(1, distance)

    for d in (0, 20):
        p1 = [pos[0], pos[1] + vert*(70+d)]
        p2 = [p1[0] + 60, p1[1] - vert*25]
        p3 = [p1[0] - 60, p1[1] - vert*25]
        pygame.draw.lines(window, "black", False, [p3, p1, p2], 10)

    pos[0] += 2*200
    remaining = str(abs(math.ceil((time - now) / 1000))) + " s"
    time_text = font_giant.render(remaining, True, COLOR_TEXT)
    time_rect = time_text.get_rect()
    time_rect.center = pos
    window.blit(time_text, time_rect)


def draw_next(distance, time, now):
    """
    Draw information about the next stop. Distance is the remaining distance
    (in metres), time is the planned arrival time (ms) and now is the current
    time.
    """
    rect = pygame.Rect(405, 0, 280, 36)
    rect.bottom = window_rect.bottom - MARGIN - 3

    label = font_small.render("NEXT STATION", True, COLOR_TEXT)
    label_rect = label.get_rect()
    label_rect.midleft = rect.midleft
    label_rect.left += 18

    distance = max(0, distance)
    dist = str(math.ceil(distance)) + " m"
    if distance == 0:
        dist = "Here"
    elif distance > 500:
        distance /= 100
        distance = math.ceil(distance) / 10
        dist = str(distance) + " km"

    dist_text = font_small_bold.render(dist, True, COLOR_TEXT)
    dist_rect = dist_text.get_rect()
    dist_rect.midright = rect.midright
    dist_rect.right -= 18

    pygame.draw.rect(window, COLOR_BRIGHT, rect, border_radius=100)
    window.blit(dist_text, dist_rect)
    window.blit(label, label_rect)

    rect.bottom = rect.top - 5

    text = "ARRIVAL TIME" if time - now >= 0 else "LATE"
    label = font_small.render(text, True, COLOR_TEXT)
    label_rect = label.get_rect()
    label_rect.midleft = rect.midleft
    label_rect.left += 18

    remaining = abs(math.ceil((time - now) / 1000))
    seconds = str(remaining % 60)
    minutes = str(remaining // 60)
    if len(seconds) <= 1:
        seconds = "0" + seconds

    arrival = minutes + ":" + seconds
    arrival_text = font_small_bold.render(arrival, True, COLOR_TEXT)
    arrival_rect = arrival_text.get_rect()
    arrival_rect.midright = rect.midright
    arrival_rect.right -= 18

    pygame.draw.rect(window, COLOR_BRIGHT, rect, border_radius=100)
    window.blit(arrival_text, arrival_rect)
    window.blit(label, label_rect)


def draw_power_triangle(rectangle, direction, color):
    """
    Draw a triangle in the specified rectangle, pointing
    up if the direction is negative and down otherwise.
    """
    left = list(rectangle.bottomleft)
    right = list(rectangle.bottomright)
    top = list(rectangle.midbottom)
    if direction < 0:  # up
        top[1] -= POWER_TRIANGLE
    else:  # down
        left[1] -= POWER_TRIANGLE
        right[1] -= POWER_TRIANGLE
    rectangle.top -= POWER_TRIANGLE
    pygame.draw.polygon(window, color, [left, top, right])


def power_level_selected(selection, level):
    """
    Return True if the specified level should be drawn with
    emphasis, given the currently selected level.
    """
    if level == 0:
        return True
    elif level > 0:
        return selection >= level
    else:
        return selection <= level


def power_level_color(selected):
    """
    Return the color to be used to draw a power level indicator.
    """
    if selected:
        return COLOR_ACCENT
    else:
        return COLOR_NEUTRAL


def draw_power_level(selection):
    """
    Draw the power level indicator, given the selected level.
    """
    rectangle = pygame.Rect(MARGIN, 0, 80, 40)
    rectangle.bottom = window_rect.bottom - MARGIN
    last_group = None
    group_text = None
    group_text_rect = None
    draw_power_triangle(
        rectangle, 1,
        power_level_color(power_level_selected(selection, -3)))
    for (group, level, _, height) in POWER_LEVELS:
        if last_group != group:
            group_rect = pygame.Rect(0, 0, 15, 0)
            group_rect.left = rectangle.right + POWER_PADDING
            group_rect.bottom = rectangle.bottom
            group_text = font_small2.render(
                POWER_GROUPS[group], True, POWER_TEXT)
            group_text_rect = group_text.get_rect()

        rectangle.top = rectangle.bottom - height
        rectangle.height = height
        pygame.draw.rect(
            window, power_level_color(power_level_selected(selection, level)),
            rectangle)

        group_rect.height += height
        group_rect.top -= height
        pygame.draw.rect(window, COLOR_BRIGHT, group_rect)
        group_text_rect.center = group_rect.center
        window.blit(group_text, group_text_rect)

        rectangle.bottom -= POWER_PADDING + rectangle.height
        group_rect.height += POWER_PADDING
        group_rect.top -= POWER_PADDING
        last_group = group
    rectangle.bottom += POWER_PADDING
    draw_power_triangle(
        rectangle, -1,
        power_level_color(power_level_selected(selection, 3)))

    rectangle.width += POWER_PADDING + 15
    rectangle.bottom -= 2*POWER_PADDING
    pygame.draw.rect(window, COLOR_BRIGHT, rectangle, border_radius=50)
    text = font_small2.render(POWER_LEVELS[selection-4][2], True, POWER_TEXT)
    text_rect = text.get_rect()
    text_rect.center = rectangle.center
    window.blit(text, text_rect)


def draw_disk(pos, value, max_value, limit):
    """
    Draw a speedometer disk, with the current speed equal to value,
    the range of the speedometer equal to max_value, and the specified
    speed limit.
    """
    subdivisions = 320
    radius_in = 70
    radius_out = 90
    point_inner = [0, 0]
    last_inner = point_inner.copy()
    point_outer = [0, 0]
    last_outer = point_outer.copy()
    for i in range(subdivisions + 1):
        angle = (i)/subdivisions * 360
        angle_r = math.radians(angle)
        angle = (angle + 120) % 360
        direction = [math.sin(angle_r), -math.cos(angle_r)]
        point_inner = [
            pos[0] + radius_in * direction[0],
            pos[1] + radius_in * direction[1]
        ]
        point_outer = [
            pos[0] + radius_out * direction[0],
            pos[1] + radius_out * direction[1]
        ]
        if i != 0 and angle <= 2*120:
            color = COLOR_BRIGHT
            if angle < 240 * value / max_value:
                color = COLOR_ACCENT
                if value > limit + 5:
                    color = "red"
            pygame.draw.polygon(
                window, color,
                [last_inner, point_inner, point_outer, last_outer]
            )
        last_inner = point_inner
        last_outer = point_outer
    angle = 240 * limit / max_value - 120
    angle_r = math.radians(angle)
    direction = [math.sin(angle_r), -math.cos(angle_r)]
    per = [-direction[1], direction[0]]
    point1 = [
        pos[0] + (radius_out + 5) * direction[0],
        pos[1] + (radius_out + 5) * direction[1]
    ]
    point2 = [
        pos[0] + (radius_out + 15) * direction[0] + 10 * per[0],
        pos[1] + (radius_out + 15) * direction[1] + 10 * per[1]
    ]
    point3 = [
        pos[0] + (radius_out + 15) * direction[0] - 10 * per[0],
        pos[1] + (radius_out + 15) * direction[1] - 10 * per[1]
    ]
    pygame.draw.aalines(window, "black", True, [point1, point2, point3])
    lim = font_small.render(str(limit), True, COLOR_TEXT)
    lim_rect = lim.get_rect()
    lim_rect.centerx = point1[0] + 32 * direction[0]
    lim_rect.centery = point1[1] + 32 * direction[1]
    window.blit(lim, lim_rect)


def draw_velocity(velocity, limit):
    """
    Draw the speed indicator.
    """
    color = COLOR_TEXT
    if velocity > limit + 5 and pygame.time.get_ticks() % 1000 < 500:
        color = COLOR_WARNING
    center = list(window_rect.bottomleft)
    center[0] += 260
    center[1] -= 80
    vel = font_giant.render(str(math.floor(velocity)), True, color)
    kmh = font_small.render("km/h", True, COLOR_TEXT)

    vel_rect = vel.get_rect()
    vel_rect.center = center
    vel_rect.bottom -= 8

    kmh_rect = kmh.get_rect()
    kmh_rect.top = vel_rect.bottom - 5
    kmh_rect.centerx = vel_rect.centerx

    draw_disk(center, velocity, 125, limit)
    window.blit(vel, vel_rect)
    window.blit(kmh, kmh_rect)


def show_notification(start_time, duration, text):
    """
    Draw a notification. The time is given in seconds.
    """
    dt = pygame.time.get_ticks() - start_time
    y_start = dt/100 * MARGIN
    y_end = (duration - dt)/100 * MARGIN
    y = min(y_start, y_end, MARGIN)
    label = font_normal.render(text, True, COLOR_TEXT)
    label_rect = label.get_rect()
    label_rect.centerx = window_rect.centerx
    label_rect.top = y
    rect = label_rect.copy()
    rect.x -= 18
    rect.width += 36
    rect.y -= 9
    rect.height += 18
    pygame.draw.rect(window, COLOR_BRIGHT, rect, border_radius=18)
    window.blit(label, label_rect)


def push_notification(text):
    """
    Set the text of a new notification. It will be displayed for the
    next 7 seconds.
    """
    global n_start, n_duration, n_text
    if n_text == text:
        return
    n_start = pygame.time.get_ticks()
    n_duration = 7000
    n_text = text


def display_pushed_notification():
    """
    Display the current notification.
    """
    show_notification(n_start, n_duration, n_text)


def draw_stars(n=0, rect=None):
    """
    Draw stars (actually squares) representing a score n. The score
    is in the range 0-5. If rect is None then the size is calculated
    and a rectangle is returned, without drawing. Otherwise, the
    given rectangle is used to determine the position of the top left
    corner.
    """
    xpos = 0
    for i in range(5):
        xpos = i * (STAR_SIZE + 5)
        if rect is not None:
            x = rect.left + xpos
            pygame.draw.rect(
                window, STAR_COLOR,
                (x, rect.y, STAR_SIZE, STAR_SIZE),
                0 if i < n else 4
            )
    return pygame.Rect(0, 0, xpos + STAR_SIZE, STAR_SIZE)


def draw_dialog(rect, prompt=True):
    """
    Draw a dialog window background. The window will be the size of the given
    rectangle. The rectangle will be appropriately positioned on the screen
    and returned. Then the elements to be displayed inside the dialog can be
    drawn. If prompt is True, a prompt with the instruction to click the
    spacebar is displayed.
    """
    rect.center = window_rect.center
    rect.height += 20
    rect.width += 36
    rect2 = rect.copy()
    label = font_small.render("Click space to continue", True, COLOR_TEXT)
    label_rect = label.get_rect()
    label_rect.top = rect.bottom + 5
    label_rect.left = rect.left + 18
    rect2.height += label_rect.height + 10
    if prompt:
        pygame.draw.rect(window, COLOR_NEUTRAL, rect2, border_radius=18)
        window.blit(label, label_rect)
    pygame.draw.rect(window, COLOR_BRIGHT, rect, border_radius=18)
    rect.top += 10
    rect.left += 18
    rect.width -= 36
    return rect


def display_sigviol():
    """
    Display a notice that a stop signal has been violated.
    """
    label = font_normal.render(
        "You passed a stop signal! You cannot continue driving.",
        True, COLOR_TEXT)
    rect = draw_dialog(label.get_rect())
    window.blit(label, rect)


def display_passengers():
    """
    Display a notice that passengers are entering the train.
    """
    label = font_normal.render("Passengers are entering the train.",
                               True, COLOR_TEXT)
    rect = draw_dialog(label.get_rect(), False)
    window.blit(label, rect)


def draw_score(score):
    """
    Draw a dialog summarising the given section score.
    """
    title = font_big.render("Station stop complete", True, COLOR_TEXT)
    title_rect = title.get_rect()

    sp_stars_rect = draw_stars()
    sp_stars_rect.top = title_rect.bottom + 10
    sp_text = font_normal.render(
        "Speeding " + str(math.ceil(score.speeding)) + "s", True, COLOR_TEXT)
    sp_rect = sp_text.get_rect()
    sp_rect.midleft = sp_stars_rect.midright
    sp_rect.left += 30

    tm_value = math.ceil(score.time)
    if tm_value > 1:
        tm_type = str(abs(tm_value)) + "s early"
    elif tm_value < -1:
        tm_type = str(abs(tm_value)) + "s late"
    else:
        tm_type = "perfect"
    tm_stars_rect = draw_stars()
    tm_stars_rect.top = sp_rect.bottom + 10
    tm_text = font_normal.render("Time " + tm_type, True, COLOR_TEXT)
    tm_rect = tm_text.get_rect()
    tm_rect.midleft = tm_stars_rect.midright
    tm_rect.left += 30

    ps_stars_rect = draw_stars()
    ps_stars_rect.top = tm_rect.bottom + 10
    ps_text = font_normal.render(
        "Stop accuracy " + str(math.floor(abs(score.distance))) + "cm",
        True, COLOR_TEXT)
    ps_rect = ps_text.get_rect()
    ps_rect.midleft = ps_stars_rect.midright
    ps_rect.left += 30

    oah = font_big.render("Overall score", True, COLOR_TEXT)
    oah_rect = oah.get_rect()
    oah_rect.top = ps_rect.bottom + 30

    oa_stars_rect = draw_stars()
    oa_stars_rect.top = oah_rect.bottom + 10
    oa_text = font_giant.render(str(math.ceil(score.overall_points)),
                                True, COLOR_TEXT)
    oa_rect = oa_text.get_rect()
    oa_rect.midtop = oa_stars_rect.midbottom
    oa_rect.top += 10

    rect = title_rect.copy()
    rect.width = max(sp_rect.right, tm_rect.right, ps_rect.right)
    rect.height = oa_rect.bottom

    rect = draw_dialog(rect)
    title_rect.x += rect.x
    title_rect.y += rect.y
    sp_stars_rect.x += rect.x
    sp_stars_rect.y += rect.y
    sp_rect.x += rect.x
    sp_rect.y += rect.y
    tm_stars_rect.x += rect.x
    tm_stars_rect.y += rect.y
    tm_rect.x += rect.x
    tm_rect.y += rect.y
    ps_stars_rect.x += rect.x
    ps_stars_rect.y += rect.y
    ps_rect.x += rect.x
    ps_rect.y += rect.y
    oa_stars_rect.centerx = rect.centerx
    oa_stars_rect.y += rect.y
    oah_rect.centerx = rect.centerx
    oah_rect.y += rect.y
    oa_rect.centerx = rect.centerx
    oa_rect.y += rect.y

    window.blit(title, title_rect)
    draw_stars(score.speeding_score, sp_stars_rect)
    window.blit(sp_text, sp_rect)
    draw_stars(score.time_score, tm_stars_rect)
    window.blit(tm_text, tm_rect)
    draw_stars(score.distance_score, ps_stars_rect)
    window.blit(ps_text, ps_rect)
    window.blit(oah, oah_rect)
    draw_stars(score.overall_score, oa_stars_rect)
    window.blit(oa_text, oa_rect)

    keys = pygame.key.get_pressed()

    return keys[pygame.K_SPACE] or keys[pygame.K_ESCAPE]


def setup(surface, window_rectangle):
    """
    Initialize global variables used by the module.
    """
    global font_small, font_small2, font_normal, font_big, font_giant
    global window_rect, window, font_small_bold
    font_small = pygame.font.Font("fonts/Inter-Regular.ttf", 22)
    font_small2 = pygame.font.Font("fonts/Inter-Regular.ttf", 18)
    font_normal = pygame.font.Font("fonts/Inter-Medium.ttf", 24)
    font_big = pygame.font.Font("fonts/Inter-Bold.ttf", 24)
    font_small_bold = pygame.font.Font("fonts/Inter-Bold.ttf", 22)
    font_giant = pygame.font.Font("fonts/Inter-Bold.ttf", 64)
    window_rect = window_rectangle
    window = surface
    reset()


def reset():
    """
    Reset the state of the user interface.
    """
    global n_start, n_duration, n_text
    n_start = -36000
    n_duration = 0
    n_text = ""
