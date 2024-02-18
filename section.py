"""
This module provides a class used to manage the gameplay.
"""

import railway
import meshes
import game_time
import train

import math
import pygame
import scores


def predict_time(distance):
    """
    Get the predicted transit time in seconds for the specified
    distance between two stations given in metres.
    """
    if distance < 0:
        return 0
    return math.ceil(1.45952667485293 * distance ** 0.559513460213026) + 6


# Section.stage
S_NORMAL = 0  # Train goes forward to the next sation
S_APPROACH = 1  # Train goes over the station railway segment
S_BADSTOP = 2  # Train stopped at a station but too early
S_STOPPED = 3  # Train stopped properly at the station
S_OVERRUN = 4  # Train didn't stop at the station


class Section:
    """
    The Section class is used to store game data
    related to the ride between two adjacent stations.
    The section must be advanced before the train is allowed
    to leave the station.

    Attributes:
        start_time
        start_offset
        end_offset
        station_to: Index of the end station
        predicted_time: Predicted arrival time (game_time)
        distance: Distance between the stations
        stage: Current stage based on the position of the train
        stage_update: Timestamp (pygame) of the last stage change
        new_stage: True if stage was updated this frame
        speeding_time: Number of seconds above the speed limit
        speeding_last: Timestamp (game_time) of the last speeding tick
        score: Section score, may be None
    """

    def __init__(self, station_from, extend=False):
        """
        station_from is the index of the starting station.
        If it's the beginning of the game and there is no previous
        station, None should be passed instead.
        """
        if not extend:
            self.start_time = game_time.now()
            self.start_offset = 0
            if station_from is not None:
                self.start_offset = railway.station_distance[station_from] / 30
                self.station_to = station_from + 1
            else:
                self.station_to = 0
            self.score = None
            self.max_score = 5
            self.speeding_time = 0
            self.speeding_last = None
        else:
            self.station_to += 1
        self.end_offset = railway.station_distance[self.station_to] / 30
        self.distance = self.end_offset - self.start_offset
        self.predicted_time = self.start_time + predict_time(self.distance)*1000
        self.stage = S_NORMAL
        self.stage_update = pygame.time.get_ticks()
        self.new_stage = True
        if not extend:
            print(f"Section: {station_from} -> {self.station_to}")

    def advance(self):
        """
        Advance to the next section.
        """
        self.__init__(self.station_to)

    def extend(self):
        """
        Extend the section by skipping current end station
        and selecting the next station as the target. This
        function should be called after an overrun.
        """
        self.__init__(0, True)
        self.penalty()
        print(f"Section extended: -> {self.station_to}")

    def penalty(self):
        """
        Decrease the maximum score as a punishment.
        """
        self.max_score //= 2

    def remaining_time(self):
        """
        Get the time remaining to the predicted arrival
        time. If the train is late, return the delay as
        a negative number.
        """
        return self.predicted_time - game_time.now()

    def remaining_distance(self, train_offset):
        """
        Get the signed distance from the
        specified offset to the station.
        """
        return self.end_offset - train_offset

    def approach_distances(self, train_offset):
        """
        Returns 3 signed distance values and a boolen value (all regarding
        the target station):
        distance_back: from the rear of the train to the rear station end
        distance_front: from the head of the train to the front station end
        approach_distance: from the head of the train to the target position
        before_station: True if the train hasn't yet reached the station
        """
        station_back = self.end_offset + meshes.STATION_OFFSET/30
        station_front = (
            self.end_offset + railway.STATION_LENGTH/30
            - meshes.STATION_OFFSET/30)
        distance_back = train_offset - train.train_length/30 - station_back
        distance_front = station_front - train_offset
        approach_distance = distance_front - 4
        before_station = train_offset < station_back
        return distance_back, distance_front, approach_distance, before_station

    def update_stage(self, train_offset, train_velocity):
        """
        Update the current stage. Return the new stage
        or None if it didn't change. This function must
        be called each time the train state changes.
        Calculates the score when the train stops.
        """
        stage = None
        back, front, _, before = self.approach_distances(train_offset)
        if before:
            stage = S_NORMAL
        else:
            stage = S_APPROACH
            if back <= 0 and train_velocity == 0:
                stage = S_BADSTOP
            elif front >= 0 and train_velocity == 0:
                stage = S_STOPPED
                if self.score is None:
                    self.calculate_score(train_offset)
            elif front < 0:
                stage = S_OVERRUN
        self.new_stage = False
        if stage != self.stage:
            self.new_stage = True
            print(f"stage = {stage}")
            self.stage = stage
            self.stage_update = pygame.time.get_ticks()
            return stage

    def tick_speeding(self, value):
        """
        Increase the counter of time spent above the speed limit
        if the value is True. This function must be called even
        when the value is False, for it to function correctly.
        """
        if value == 0:
            self.speeding_last = None
        else:
            now = game_time.now()
            if self.speeding_last is not None:
                self.speeding_time += now - self.speeding_last
            self.speeding_last = now

    def calculate_score(self, train_offset):
        """
        Calculate the score of this section.
        """
        self.score = scores.SectionScore(self, train_offset)
        self.score.overall_score = min(self.score.overall_points,
                                       self.max_score)
        self.score.overall_points /= 5 / self.max_score
