"""
This module provides classes used for game score management.
"""
import math
from datetime import date


SCORES_FILE = ".scores"


class SectionScore():
    """
    Score of a section (from one stop to the next).

    Attributes:
        time: Remaining time in seconds (negative if late)
        time_score
        time_points
        distance: Remaining distance to the perfect stop in cm
        distance_score
        distance_points
        speeding: Time spent speeding in seconds
        speeding_score
        speeding_points
        overall_score
        overall_points
    Score is the number of stars (0-5) and points is a big numeric value.
    """

    def __init__(self, sect, train_offset):
        """
        Calculate the score of the given section, based on the specified
        train offset. This should be called after the train finally stops.
        """
        self.time = sect.remaining_time() / 1000
        late = max(0, -self.time)
        time_points = max(0, self.time + 10) * 10
        if late < 8:
            self.time_score = 5
        elif late < 12:
            self.time_score = 4
        elif late < 15:
            self.time_score = 3
        elif late < 20:
            self.time_score = 2
        elif late < 30:
            self.time_score = 1
        else:
            self.time_score = 0

        self.distance = sect.approach_distances(train_offset)[2] * 100
        dist = abs(self.distance/100)  # metres
        dist_points = 400 / max(0.5, dist + 0.5)
        if dist < 0.5:
            self.distance_score = 5
        elif dist < 1.5:
            self.distance_score = 4
        elif dist < 4:
            self.distance_score = 3
        elif dist < 6:
            self.distance_score = 2
        elif dist < 8.5:
            self.distance_score = 1
        else:
            self.distance_score = 0

        self.speeding = sect.speeding_time / 1000
        speeding_points = 200 / max(1, self.speeding + 1)
        if self.speeding < 1:
            self.speeding_score = 5
        elif self.speeding < 3:
            self.speeding_score = 4
        elif self.speeding < 8:
            self.speeding_score = 3
        elif self.speeding < 14:
            self.speeding_score = 2
        elif self.speeding < 20:
            self.speeding_score = 1
        else:
            self.speeding_score = 0

        self.overall_points = time_points + dist_points + speeding_points
        self.overall_score = math.ceil(
            (self.speeding_score + self.distance_score + self.time_score) / 3
        )

        print("Section score:", self.overall_points, self.overall_score)

    def __repr__(self):
        """
        Return a string representation of the object.
        """
        return (f"SectionScore(points={self.overall_points}, "
                + f"score={self.overall_score})")


class SessionScore():
    """
    Score of a session (consisting of consecutive sections).

    Attributes:
        scores: A list of section scores
        empty: Boolean value, are there no scores saved?
        score: Final number of stars
        points: Total number of points
    """

    def __init__(self):
        """
        Initialize a new session.
        """
        self.scores = []
        self.calculate()
        self.empty = True
        print("New session initialized")

    def __repr__(self):
        """
        Return a string representation of the object.
        """
        return f"SessionScore(points={self.points}, score={self.score})"

    def add(self, sect):
        """
        Add a section score to the session.
        """
        self.empty = False
        self.scores.append(sect)
        print("Added section score to the session", sect)

    def calculate(self):
        """
        Calculate the final number of points and the score.
        """
        points = [s.overall_points for s in self.scores]
        scores = [s.overall_score for s in self.scores]
        if len(points) == 0:
            self.points = 0
        else:
            self.points = sum(points)
        if len(scores) == 0:
            self.score = 0
        else:
            self.score = sum(scores) / len(scores)


class ScoreHistory():
    """
    All historic session scores. Saved to and loaded from the disk.

    Attributes:
        session_scores: List of tuples (date, points, score)
        section_scores: List of tuples (session index, points, score)
    """

    def __init__(self):
        """
        Initialize the score history. Tries to load saved scores from the file.
        """
        self.current_session = None
        self.session_scores = []
        self.section_scores = []
        print("New score history")
        self.load_file(SCORES_FILE)

    def add_score(self, sess_score):
        """
        Add a session score to the history. Saves the history to the file.
        """
        i = len(self.session_scores)
        today = date.today().isoformat()
        self.session_scores.append(
            (today, sess_score.points, sess_score.score))
        for sect_score in sess_score.scores:
            self.section_scores.append(
                (i, sect_score.overall_points, sect_score.overall_score))
        print("Added session to score history", sess_score)
        self.save_file(SCORES_FILE)

    def new_session(self):
        """
        Begin a new session. Returns the associated session score object.
        The previous session is saved.
        """
        print("New session in session history")
        self.end_session()
        self.current_session = SessionScore()
        return self.current_session

    def end_session(self):
        """
        End a session and save it, if the score wasn't empty.
        """
        if self.current_session is not None:
            if self.current_session.points != 0:
                print("Session ended, score added to history",
                      self.current_session)
                self.add_score(self.current_session)

    def load_file(self, path):
        """
        Load scores from the given file.
        """
        assert len(self.session_scores) == 0 and len(self.section_scores) == 0
        try:
            with open(path, "r") as f:
                for line in f:
                    if line == "":
                        continue
                    elements = line.split()
                    if len(elements) != 4:
                        print("Invalid save data:", line)
                        continue
                    e_type = elements[0]
                    if e_type not in ("sess", "sect"):
                        print("Invalid save type:", line)
                        continue
                    if e_type == "sess":
                        self.session_scores.append(
                            (elements[1], elements[2], elements[3])
                        )
                    elif e_type == "sect":
                        self.section_scores.append(
                            (elements[1], elements[2], elements[3])
                        )
            print("Loaded score history from", path)
        except FileNotFoundError:
            print("No scores file", path)

    def save_file(self, path):
        """
        Save scores to the given file.
        """
        with open(path, "w") as f:
            for s in self.session_scores:
                f.write(f"sess {s[0]} {s[1]} {s[2]}\n")
            for s in self.section_scores:
                f.write(f"sect {s[0]} {s[1]} {s[2]}\n")
        print("Saved score history to", path)
