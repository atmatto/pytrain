"""
This module is used to handle in-game time tracking, allowing
to freeze or reset the clock.

Global variables must not be modified directly.
"""
import pygame


def now():
    """
    Return current game time in milliseconds.
    """
    if frozen:
        return freeze_start - skip_time
    return pygame.time.get_ticks() - skip_time


def freeze():
    """
    Freeze time.
    """
    global frozen, freeze_start
    print("Time freezed.")
    if frozen is False:
        freeze_start = pygame.time.get_ticks()
    frozen = True


def unfreeze():
    """
    Unfreeze time.
    """
    global skip_time, frozen
    print("Time unfreezed.")
    skip_time += pygame.time.get_ticks() - freeze_start
    frozen = False


def toggle_freeze(value):
    """
    Toggle the clock freeze state based
    on the passed boolean value.
    """
    if value:
        freeze()
    else:
        unfreeze()


def reset():
    """
    Reset the clock by setting current time to 0.
    """
    global skip_time
    skip_time = pygame.time.get_ticks()


skip_time = 0  # How many ms from the start of the game passed during a pause
freeze_start = 0  # When did the last pause start
frozen = False  # Is the time paused
