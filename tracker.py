from dataclasses import dataclass

from geometry import Coordinate, Line, calculate_average_coordinate


@dataclass
class Tracked:
    current: Coordinate
    id: int
    start: Coordinate


class ObjectTracker:
    """
    Tracks passing object using a start line from which it starts tracking.
    Tracking is done with the assumption that the coordinate of a moving
    object in one frame, should always be closest to its coordinate in the next
    frame.
    """

    def __init__(self, starting_line: Line) -> None:
        self.starting_line = starting_line
        self.tracked_objects = []
        self.passed_objects = 0

    def track(self, obj_coo):
        closest = min(
            self.tracked_objects + [Tracked(self.starting_line, 0, None)],
            key=lambda obj: obj.current.distance(obj_coo),
        )

        if isinstance(closest.current, Line):
            self.passed_objects += 1
            self.tracked_objects = self.tracked_objects[-20:]

            self.tracked_objects = [
                Tracked(
                    obj_coo,
                    self.passed_objects,
                    obj_coo,
                )
            ] + self.tracked_objects

            print(self.passed_objects, closest.current.distance(obj_coo))
        else:
            closest.current = obj_coo

        return closest

    def reorient(self):
        """adjusts the starting line's slope. can be used to improve accuarcy in some streams"""
        aver_start_point = calculate_average_coordinate(
            obj.current for obj in self.tracked_objects[:-1]
        )
        aver_end_point = calculate_average_coordinate(
            obj.start for obj in self.tracked_objects[:-1]
        )

        x1, y1 = aver_start_point
        x2, y2 = aver_end_point

        if x2 - x1:
            aver_slope = (y2 - y1) / ((x2 - x1))
        else:
            aver_slope = float("inf")

        self.starting_line.slope = -1 / aver_slope

        return self.starting_line.slope
