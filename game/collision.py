"""
game/collision.py
=================
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Performs high-precision collision detection between Member 1's hand tracking
    cutting trajectory and active fruit bounding circles using continuous
    line-segment to circle intersection algorithms.
"""

import math
from typing import List, Tuple
from game.fruit import Fruit


class CollisionDetector:
    """
    Detects collisions between Member 1's hand cutting trajectory and active fruits.

    Parameters
    ----------
    blade_thickness : float
        Additional tolerance radius around the cutting line in pixels (default 12.0).
    """

    def __init__(self, blade_thickness: float = 12.0):
        self.blade_thickness = blade_thickness

    def check_collisions(
        self,
        motion_data: dict,
        active_fruits: List[Fruit],
    ) -> List[Fruit]:
        """
        Check for collisions between the cutting gesture and active fruits.

        Parameters
        ----------
        motion_data : dict
            Member 1's motion data output containing:
            - hand_detected (bool)
            - finger_x, finger_y (int)
            - previous_x, previous_y (int)
            - trajectory (list of (x, y))
            - is_cutting (bool)
            - movement_direction (float)
        active_fruits : List[Fruit]
            List of currently active, sliceable fruits.

        Returns
        -------
        List[Fruit]
            List of fruits that were sliced in this frame.
        """
        if not motion_data.get("hand_detected", False):
            return []

        # Only cut if player is performing a cutting gesture or moving with speed
        is_cutting = motion_data.get("is_cutting", False)
        speed = motion_data.get("movement_speed", 0.0)

        # Allow slicing if is_cutting is True or speed is above modest threshold (0.28 px/ms)
        if not (is_cutting or speed >= 0.28):
            return []

        fx, fy = motion_data.get("finger_x", -1), motion_data.get("finger_y", -1)
        px, py = motion_data.get("previous_x", -1), motion_data.get("previous_y", -1)
        trajectory = motion_data.get("trajectory", [])
        direction = motion_data.get("movement_direction", 0.0)

        if fx < 0 or fy < 0:
            return []

        # Build list of line segments to test
        # 1. Primary segment: previous position -> current position
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        if px >= 0 and py >= 0 and (px != fx or py != fy):
            segments.append(((float(px), float(py)), (float(fx), float(fy))))

        # 2. Recent trajectory segments (last 4 points) to catch fast multi-frame slashes
        if len(trajectory) >= 2:
            recent_points = trajectory[-5:]
            for i in range(len(recent_points) - 1):
                p1 = (float(recent_points[i][0]), float(recent_points[i][1]))
                p2 = (float(recent_points[i + 1][0]), float(recent_points[i + 1][1]))
                if p1 != p2 and (p1, p2) not in segments:
                    segments.append((p1, p2))

        # If no valid segment, test fingertip point directly
        if not segments:
            segments.append(((float(fx), float(fy)), (float(fx), float(fy))))

        sliced_fruits: List[Fruit] = []

        for fruit in active_fruits:
            if not fruit.is_active:
                continue

            hit = False
            fruit_center = (fruit.x, fruit.y)
            effective_radius = fruit.radius + self.blade_thickness

            for p1, p2 in segments:
                dist = self._dist_point_to_segment(fruit_center, p1, p2)
                if dist <= effective_radius:
                    hit = True
                    break

            if hit:
                fruit.slice(cut_angle=direction)
                sliced_fruits.append(fruit)

        return sliced_fruits

    @staticmethod
    def _dist_point_to_segment(
        pt: Tuple[float, float],
        seg_start: Tuple[float, float],
        seg_end: Tuple[float, float],
    ) -> float:
        """
        Calculate shortest Euclidean distance between a point pt and a line segment seg_start->seg_end.
        """
        px, py = pt
        x1, y1 = seg_start
        x2, y2 = seg_end

        dx = x2 - x1
        dy = y2 - y1

        # Degenerate segment (point)
        if dx == 0.0 and dy == 0.0:
            return math.hypot(px - x1, py - y1)

        # Vector projection factor t clamped to [0, 1]
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        t = max(0.0, min(1.0, t))

        # Closest point on segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        return math.hypot(px - closest_x, py - closest_y)
