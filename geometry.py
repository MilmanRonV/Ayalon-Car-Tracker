import math
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Coordinate:
    x: int
    y: int

    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        hypo_len = (dx**2 + dy**2) ** 0.5
        return abs(hypo_len)

    def __iter__(self):
        yield int(self.x)
        yield int(self.y)


class Line:
    def __init__(self, coordinate: Coordinate, slope: float):
        self.coordinate = coordinate
        self.slope = slope

    def distance(self, coo: Coordinate):
        if self.slope == 0:
            x1, y1 = self.coordinate
            x2, y2 = coo
            return abs(y2 - y1)
        elif math.isinf(self.slope):
            x1, y1 = self.coordinate
            x2, y2 = coo
            return abs(x2 - x1)

        slope = -1 / self.slope
        perpendicular = Line(coo, slope)
        closest_point = self.calculate_intersection(perpendicular)
        return closest_point.distance(coo)

    def calculate_intersection(self, other_line):
        x1, y1 = self.coordinate
        x2, y2 = other_line.coordinate

        if self.slope == other_line.slope:
            return None

        if math.isinf(self.slope):
            x_intersection = x1
            y_intersection = y2 + ((x1 - x2) * other_line.slope)
        elif math.isinf(other_line.slope):
            x_intersection = x2
            y_intersection = y1 + ((x2 - x1) * self.slope)
        else:
            x_intersection = (y2 - y1 + self.slope * x1 - other_line.slope * x2) / (
                self.slope - other_line.slope
            )
            y_intersection = self.slope * (x_intersection - x1) + y1

        return Coordinate(x_intersection, y_intersection)


def calculate_average_coordinate(coordinates):
    x_sum, y_sum = 0, 0
    for i, coo in enumerate(coordinates):
        x, y = coo
        y_sum += y
        x_sum += x

    avg_x = int(x_sum / i)
    avg_y = int(y_sum / i)
    return Coordinate(avg_x, avg_y)


def draw_line(frame: np.ndarray, line: Line):
    height, width, _ = frame.shape

    left_y_axis = Line(Coordinate(0, 0), float("inf"))
    right_y_axis = Line(Coordinate(width, 0), float("inf"))
    top_x_axis = Line(Coordinate(0, height), 0)
    bottom_x_axis = Line(Coordinate(0, 0), 0)

    intersections = [
        line.calculate_intersection(left_y_axis),
        line.calculate_intersection(right_y_axis),
        line.calculate_intersection(top_x_axis),
        line.calculate_intersection(bottom_x_axis),
    ]

    inner_intersections = set(
        tuple(intersection)
        for intersection in filter(
            lambda coo: coo is not None
            and 0 <= coo.x <= width
            and 0 <= coo.y <= height,
            intersections,
        )
    )

    cv2.line(frame, *inner_intersections, (0, 0, 255), 2)


def get_center_coordinate(contour):
    x, y, w, h = cv2.boundingRect(contour)
    return Coordinate(x + int(w / 2), y + int(h / 2))
