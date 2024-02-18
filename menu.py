"""
This module implements the user interface of the main menu,
all submenus accessed by it, and the in-game pause screen.
"""
import pygame
import math
import sys

import ui

MARGIN = 60
BUTTON_SIZE = (300, 100)
SMALL_BUTTON_SIZE = (270, 70)

COLOR_NEUTRAL = "#cad6e6"
COLOR_BRIGHT = "#e5e5e5"

# menu_state
MS_WELCOME = 0
MS_MAIN = 1
MS_SCORES = 2
MS_PLAY = 3
MS_SUMMARY = 4
MS_MANUAL = 5


def draw_button(text, rect, small=False):
    """
    Draw a button with the specified label. The button's top left
    corner is the same as that of the given rectangle. Return True
    if the button was clicked by the user, otherwise False.
    """
    global last_clicked

    if small:
        rect.size = SMALL_BUTTON_SIZE
    else:
        rect.size = BUTTON_SIZE

    color = COLOR_BRIGHT
    clicked = False
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = COLOR_NEUTRAL
        if pygame.mouse.get_pressed()[0]:
            clicked = True

    pygame.draw.rect(window, color, rect, border_radius=8)

    label = font_normal.render(text, True, "black")
    label_rect = label.get_rect()
    label_rect.bottomleft = rect.bottomleft
    label_rect.left += 20
    label_rect.bottom -= 20
    window.blit(label, label_rect)

    if clicked:
        if last_clicked:
            clicked = False
        last_clicked = True
    elif not pygame.mouse.get_pressed()[0]:
        last_clicked = False
    return clicked


def draw_menu():
    """
    Draw the main menu and handle user interactions.
    """
    global menu_state, scores_page
    logo_rect = logo.get_rect().move(MARGIN, MARGIN - 20)
    window.blit(logo, logo_rect)

    rect_left = logo_rect.move(0, 400)
    rect_right = rect_left.move(BUTTON_SIZE[0] + 20, 0)
    if draw_button("Play", rect_left):
        menu_state = MS_PLAY
    if draw_button("Ride history", rect_right):
        menu_state = MS_SCORES
        scores_page = 0

    rect_left = rect_left.move(0, BUTTON_SIZE[1] + 20)
    rect_right = rect_right.move(0, BUTTON_SIZE[1] + 20)
    if draw_button("Quit", rect_left):
        pygame.quit()
        sys.exit(0)
    if draw_button("Manual", rect_right):
        menu_state = MS_MANUAL


def draw_splash():
    """
    Draw the splash screen displayed when starting the game.
    """
    logo_rect = logo_big.get_rect()
    logo_rect.center = window_rect.center
    logo_rect.top -= 40
    window.blit(logo_big, logo_rect)
    label = font_normal.render("atmatto", True, "black")
    label_rect = label.get_rect()
    label_rect.midtop = logo_rect.midbottom
    label_rect.top += 50
    window.blit(label, label_rect)


def draw_pause():
    """
    Draw the pause screen. Return True if the user decides to end the game,
    False if they unpause it, or None if no action has been made.
    """
    global menu_state
    rect = logo.get_rect().move(MARGIN, 250)
    if draw_button("Resume", rect):
        return False
    rect = rect.move(0, BUTTON_SIZE[1] + 20)
    if draw_button("End game", rect):
        return True


def draw_score(score):
    """
    Draw a card with a session score.
    """
    title = font_large.render("Final score", True, "black")
    title_rect = title.get_rect().move(0, 15)

    stars_rect = ui.draw_stars()
    stars_rect.top = title_rect.bottom + 30
    if score.score == 5:
        text = "Perfect"
    elif score.score == 4:
        text = "Excellent"
    elif score.score == 3:
        text = "Fair"
    elif score.score == 2:
        text = "Tolerable"
    elif score.score == 1:
        text = "Mediocre"
    elif score.score == 0:
        text = "Catastrophic"
    else:
        text = ""
    label = font_normal.render(text, True, "black")
    label_rect = label.get_rect()
    label_rect.midleft = stars_rect.midright
    label_rect.left += 20

    points = font_giant.render(str(math.ceil(score.points)), True, "black")
    points_rect = points.get_rect()
    points_rect.midtop = stars_rect.midbottom
    points_rect.top += 30

    rect = title_rect.copy()
    rect.width = max(label_rect.right, points_rect.right) + 30
    rect.height = points_rect.bottom + 15

    rect = ui.draw_dialog(rect, False)
    title_rect.centerx = rect.centerx
    title_rect.y += rect.y
    stars_rect.x += rect.x + 15
    stars_rect.y += rect.y
    label_rect.x += rect.x + 15
    label_rect.y += rect.y
    points_rect.centerx = rect.centerx
    points_rect.y += rect.y

    window.blit(title, title_rect)
    ui.draw_stars(score.score, stars_rect)
    window.blit(label, label_rect)
    window.blit(points, points_rect)


def draw_summary():
    """
    Draw the final score of the ended session. If no stations have been
    visited, no score is shown. Handle the transition to the main menu.
    """
    global menu_state
    title = font_big.render("Game finished", True, "black")
    title_rect = title.get_rect().move(MARGIN, MARGIN)
    window.blit(title, title_rect)
    rect = pygame.Rect(
        window_rect.width - MARGIN - BUTTON_SIZE[0],
        window_rect.height - MARGIN - BUTTON_SIZE[1],
        0, 0)
    if draw_button("Return to menu", rect):
        menu_state = MS_MAIN
    if not sess_score.empty:
        draw_score(sess_score)


def setup_summary(session_score):
    """
    Save internally the score to be displayed in the session summary screen.
    """
    global menu_state, sess_score
    menu_state = MS_SUMMARY
    sess_score = session_score
    sess_score.calculate()


def draw_small_score(rect, score):
    """
    Draw a row in the score history table, representing a past session score.
    The given rectangle's top left corner is used for positioning. The score
    argument is a tuple of three elements: (date, points, stars).
    """
    stars_rect = ui.draw_stars()
    stars_rect.topleft = rect.topleft

    label = font_normal.render(str(math.ceil(float(score[1]))), True, "black")
    label_rect = label.get_rect()
    label_rect.midleft = stars_rect.midright
    label_rect.left += 30

    date = font_normal.render(score[0], True, "black")
    date_rect = date.get_rect()
    date_rect.midleft = stars_rect.midright
    date_rect.right = rect.left + 530

    ui.draw_stars(float(score[2]), stars_rect)
    window.blit(label, label_rect)
    window.blit(date, date_rect)


def draw_scores():
    """
    Draw the score history screen. Handle user interactions.
    """
    global menu_state, scores_page

    rect = pygame.Rect(
        window_rect.width - MARGIN - SMALL_BUTTON_SIZE[0], MARGIN, 0, 0)
    if draw_button("Return to menu", rect, True):
        menu_state = MS_MAIN
    rect = rect.move(-SMALL_BUTTON_SIZE[0] - 20, 0)
    if draw_button("Next page", rect, True):
        scores_page += 1
    rect = rect.move(-SMALL_BUTTON_SIZE[0] - 20, 0)
    if draw_button("Previous page", rect, True):
        scores_page -= 1

    scores = list(reversed(score_hist.session_scores))
    pages = len(scores) // 14
    if len(scores) % 14 == 0:
        pages = max(0, pages - 1)
    scores_page = max(0, min(scores_page, pages))
    start_index = scores_page * 14

    title = font_big.render(
        f"Score history {str(scores_page + 1)}/{str(pages + 1)}",
        True, "black")
    title_rect = title.get_rect().move(MARGIN, MARGIN)
    window.blit(title, title_rect)

    # First column
    rect = title_rect.move(0, 140)
    line_start = list(rect.topleft)
    line_start[1] -= 20
    line_end = line_start.copy()
    line_end[0] += 530
    pygame.draw.line(window, "black", line_start, line_end, 2)
    for score in scores[start_index+0:start_index+7]:
        draw_small_score(rect, score)
        rect = rect.move(0, 70)
        line_start = list(rect.topleft)
        line_start[1] -= 20
        line_end = line_start.copy()
        line_end[0] += 530
        pygame.draw.line(window, "black", line_start, line_end, 2)
    # Second column
    rect = title_rect.move(600, 140)
    line_start = list(rect.topleft)
    line_start[1] -= 20
    line_end = line_start.copy()
    line_end[0] += 530
    pygame.draw.line(window, "black", line_start, line_end, 2)
    for score in scores[start_index+7:start_index+14]:
        draw_small_score(rect, score)
        rect = rect.move(0, 70)
        line_start = list(rect.topleft)
        line_start[1] -= 20
        line_end = line_start.copy()
        line_end[0] += 530
        pygame.draw.line(window, "black", line_start, line_end, 2)


def draw_manual():
    """
    Draw the game manual and handle the transition back to the main menu.
    """
    global menu_state
    window.blit(manual_image, manual_rect)
    rect = window_rect.move(MARGIN, MARGIN)
    if draw_button("Return to menu", rect, True):
        menu_state = MS_MAIN


def draw():
    """
    Draw the appropriate user interface for the current menu state.
    Return True if the player starts the game, otherwise False.
    """
    global menu_state
    if menu_state == MS_MAIN:
        draw_menu()
    elif menu_state == MS_SCORES:
        draw_scores()
    elif menu_state == MS_WELCOME:
        draw_splash()
        if pygame.time.get_ticks() > 3500:
            menu_state = MS_MAIN
    elif menu_state == MS_SUMMARY:
        draw_summary()
    elif menu_state == MS_MANUAL:
        draw_manual()
    elif menu_state == MS_PLAY:
        return True
    return False


def setup(surface, window_rectangle, score_history):
    """
    Initialize global variables.
    """
    global font_normal, font_large, font_big, font_giant, window_rect, window
    global logo, menu_state, score_hist, logo_big, scores_page, last_clicked
    global manual_image, manual_rect
    font_normal = pygame.font.Font("fonts/Inter-Medium.ttf", 26)
    font_big = pygame.font.Font("fonts/Inter-Bold.ttf", 24)
    font_large = pygame.font.Font("fonts/Inter-Medium.ttf", 32)
    font_giant = pygame.font.Font("fonts/Inter-Bold.ttf", 64)
    window_rect = window_rectangle
    window = surface
    logo = pygame.image.load("logo/logo-small.png").convert_alpha(window)
    logo_big = pygame.image.load("logo/logo.png").convert_alpha(window)
    menu_state = MS_WELCOME
    scores_page = 0
    score_hist = score_history
    last_clicked = False

    manual_image = pygame.image.load("manual/manual.png").convert_alpha(surface)
    manual_rect = manual_image.get_rect()
    manual_rect.center = window_rectangle.center
