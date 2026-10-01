"""
game/fruit.py
=============
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Defines the Fruit class and fruit types. Each fruit has physics properties
    (position, velocity, gravity, rotation), lifecycle states (active, sliced, missed),
    and slicing mechanics (splitting into two separate halves with juice particles).
"""

import math
import random
import cv2
import numpy as np


# ---------------------------------------------------------------------------
# Fruit Type Specifications
# ---------------------------------------------------------------------------
FRUIT_TYPES = {
    "watermelon": {
        "name": "Watermelon",
        "radius": 36,
        "points": 10,
        "color_rind": (34, 139, 34),       # BGR: Forest Green
        "color_flesh": (45, 45, 215),      # BGR: Red/Crimson
        "color_seed": (20, 20, 20),        # BGR: Dark
        "color_splash": (45, 45, 230),     # BGR: Red juice
        "is_bomb": False,
    },
    "apple": {
        "name": "Apple",
        "radius": 28,
        "points": 15,
        "color_rind": (25, 25, 210),       # BGR: Bright Red
        "color_flesh": (210, 245, 245),    # BGR: Pale Yellow/White
        "color_seed": (20, 20, 20),
        "color_splash": (30, 30, 220),
        "is_bomb": False,
    },
    "banana": {
        "name": "Banana",
        "radius": 26,
        "points": 20,
        "color_rind": (0, 215, 255),       # BGR: Bright Yellow
        "color_flesh": (180, 240, 250),    # BGR: Cream Yellow
        "color_seed": (80, 150, 180),
        "color_splash": (0, 220, 255),
        "is_bomb": False,
    },
    "orange": {
        "name": "Orange",
        "radius": 30,
        "points": 10,
        "color_rind": (0, 140, 255),       # BGR: Orange
        "color_flesh": (40, 175, 255),     # BGR: Light Orange
        "color_seed": (230, 230, 230),
        "color_splash": (0, 150, 255),
        "is_bomb": False,
    },
    "strawberry": {
        "name": "Strawberry",
        "radius": 24,
        "points": 25,
        "color_rind": (50, 50, 230),       # BGR: Ruby Red
        "color_flesh": (90, 90, 245),
        "color_seed": (0, 200, 100),       # BGR: Green leaves/seeds
        "color_splash": (50, 50, 240),
        "is_bomb": False,
    },
    "bomb": {
        "name": "Bomb",
        "radius": 30,
        "points": 0,
        "color_rind": (35, 35, 35),        # BGR: Charcoal/Black
        "color_flesh": (20, 20, 20),
        "color_seed": (0, 80, 255),        # BGR: Orange fuse
        "color_splash": (0, 69, 255),      # BGR: Fiery Orange/Red
        "is_bomb": True,
    },
}


class FruitHalf:
    """Represents one half of a sliced fruit separating and falling."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 radius: float, color_rind: tuple, color_flesh: tuple,
                 angle: float, rot_speed: float, is_left: bool):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color_rind = color_rind
        self.color_flesh = color_flesh
        self.angle = angle
        self.rot_speed = rot_speed
        self.is_left = is_left
        self.gravity = 0.45

    def update(self):
        """Update position and rotation of the half fruit."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.rot_speed

    def draw(self, frame: np.ndarray):
        """Draw half fruit on the OpenCV frame."""
        cx, cy = int(self.x), int(self.y)
        h, w = frame.shape[:2]
        if cx < -100 or cx > w + 100 or cy < -100 or cy > h + 100:
            return

        # Draw semicircle facing outward
        start_angle = int(self.angle + (90 if self.is_left else 270))
        end_angle = start_angle + 180
        r = int(self.radius)

        # Outer flesh/rind
        cv2.ellipse(frame, (cx, cy), (r, r), 0, start_angle, end_angle, self.color_rind, -1)
        # Inner flesh
        inner_r = max(4, int(r * 0.75))
        cv2.ellipse(frame, (cx, cy), (inner_r, inner_r), 0, start_angle, end_angle, self.color_flesh, -1)
        # Flat cut edge
        rad1 = math.radians(start_angle)
        rad2 = math.radians(end_angle)
        pt1 = (int(cx + r * math.cos(rad1)), int(cy + r * math.sin(rad1)))
        pt2 = (int(cx + r * math.cos(rad2)), int(cy + r * math.sin(rad2)))
        cv2.line(frame, pt1, pt2, (240, 240, 240), 2)


class Fruit:
    """
    Represents a game fruit or bomb.

    Parameters
    ----------
    fruit_type : str
        Type of fruit ('watermelon', 'apple', 'banana', 'orange', 'strawberry', 'bomb')
    x : float
        Initial X coordinate
    y : float
        Initial Y coordinate
    vx : float
        Horizontal velocity
    vy : float
        Vertical velocity (negative for upward launch)
    gravity : float
        Downward gravitational acceleration (default 0.38)
    """

    def __init__(
        self,
        fruit_type: str = "watermelon",
        x: float = 320.0,
        y: float = 500.0,
        vx: float = 0.0,
        vy: float = -15.0,
        gravity: float = 0.38,
    ):
        if fruit_type not in FRUIT_TYPES:
            fruit_type = "watermelon"

        info = FRUIT_TYPES[fruit_type]
        self.fruit_type = fruit_type
        self.name = info["name"]
        self.radius = info["radius"]
        self.points = info["points"]
        self.is_bomb = info["is_bomb"]
        self.color_rind = info["color_rind"]
        self.color_flesh = info["color_flesh"]
        self.color_seed = info["color_seed"]
        self.color_splash = info["color_splash"]

        # Physics
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.gravity = float(gravity)

        # Rotation
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-4.0, 4.0)

        # State: 'active', 'sliced', 'missed', 'removed'
        self.state = "active"
        self.halves = []

        # Bomb spark animation
        self._spark_phase = 0.0

    @property
    def is_active(self) -> bool:
        """True if the fruit is actively flyable and cuttable."""
        return self.state == "active"

    @property
    def is_sliced(self) -> bool:
        """True if fruit has been cut."""
        return self.state == "sliced"

    def slice(self, cut_angle: float = 0.0):
        """
        Slice the fruit into two halves.

        Parameters
        ----------
        cut_angle : float
            Direction angle of the slice in degrees.
        """
        if self.state != "active":
            return

        self.state = "sliced"

        if self.is_bomb:
            return  # Bombs explode rather than splitting cleanly

        # Direction of separation perpendicular to cut
        rad = math.radians(cut_angle + 90)
        sep_speed = 3.5

        # Left half
        left_vx = self.vx - math.cos(rad) * sep_speed
        left_vy = self.vy - math.sin(rad) * sep_speed - 1.5
        # Right half
        right_vx = self.vx + math.cos(rad) * sep_speed
        right_vy = self.vy + math.sin(rad) * sep_speed - 1.5

        self.halves = [
            FruitHalf(self.x, self.y, left_vx, left_vy,
                      self.radius, self.color_rind, self.color_flesh,
                      self.angle, -6.0, is_left=True),
            FruitHalf(self.x, self.y, right_vx, right_vy,
                      self.radius, self.color_rind, self.color_flesh,
                      self.angle, 6.0, is_left=False),
        ]

    def update(self, bounds_width: int = 640, bounds_height: int = 480):
        """
        Advance physics by one frame.

        Parameters
        ----------
        bounds_width : int
            Screen width in pixels.
        bounds_height : int
            Screen height in pixels.
        """
        if self.state == "active":
            self.x += self.vx
            self.y += self.vy
            self.vy += self.gravity
            self.angle = (self.angle + self.rot_speed) % 360

            # Check if active fruit fell below bottom of screen
            if self.y > bounds_height + 50 and self.vy > 0:
                self.state = "missed"

        elif self.state == "sliced":
            for half in self.halves:
                half.update()
            # If both halves have fallen off-screen, mark as removed
            if all(h.y > bounds_height + 80 for h in self.halves) or len(self.halves) == 0:
                self.state = "removed"

    def is_out_of_bounds(self, bounds_width: int = 640, bounds_height: int = 480) -> bool:
        """Check if fruit is completely out of play area."""
        if self.state == "active":
            return self.y > bounds_height + 50 and self.vy > 0
        elif self.state == "sliced":
            if self.is_bomb:
                return True
            return all(h.y > bounds_height + 80 for h in self.halves)
        return True

    def draw(self, frame: np.ndarray):
        """
        Draw the fruit or its split halves onto an OpenCV BGR frame.

        Parameters
        ----------
        frame : np.ndarray
            BGR image to draw on.
        """
        if self.state == "sliced":
            for half in self.halves:
                half.draw(frame)
            return

        if self.state != "active":
            return

        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)
        h, w = frame.shape[:2]

        if cx < -50 or cx > w + 50 or cy < -50 or cy > h + 50:
            return

        if self.is_bomb:
            self._draw_bomb(frame, cx, cy, r)
        else:
            self._draw_fruit(frame, cx, cy, r)

    def _draw_fruit(self, frame: np.ndarray, cx: int, cy: int, r: int):
        """Draw circular fruit with rind, highlight, and stem."""
        # 1. Outer rind / peel
        cv2.circle(frame, (cx, cy), r, self.color_rind, -1)

        # 2. Inner flesh (subtle depth)
        inner_r = max(4, int(r * 0.78))
        cv2.circle(frame, (cx, cy), inner_r, self.color_flesh, -1)

        # 3. Seed / core detailing
        if self.fruit_type == "watermelon":
            for offset in [(-6, -4), (6, -4), (-4, 6), (4, 6)]:
                sx = cx + int(offset[0] * (r / 36))
                sy = cy + int(offset[1] * (r / 36))
                cv2.circle(frame, (sx, sy), 2, self.color_seed, -1)
        elif self.fruit_type == "orange":
            # Orange segments
            for i in range(6):
                seg_angle = math.radians(self.angle + i * 60)
                px = int(cx + (inner_r * 0.7) * math.cos(seg_angle))
                py = int(cy + (inner_r * 0.7) * math.sin(seg_angle))
                cv2.line(frame, (cx, cy), (px, py), (255, 255, 255), 1)

        # 4. Specular highlight (top-left shiny gloss)
        hx = cx - int(r * 0.3)
        hy = cy - int(r * 0.3)
        hr = max(2, int(r * 0.22))
        cv2.circle(frame, (hx, hy), hr, (255, 255, 255), -1)

        # 5. Outer border for crisp visibility against webcam backgrounds
        cv2.circle(frame, (cx, cy), r, (15, 15, 15), 2)

    def _draw_bomb(self, frame: np.ndarray, cx: int, cy: int, r: int):
        """Draw bomb body with fuse and glowing animated spark."""
        # Bomb body (charcoal sphere)
        cv2.circle(frame, (cx, cy), r, (35, 35, 35), -1)
        cv2.circle(frame, (cx, cy), r, (10, 10, 10), 2)

        # Specular shine
        cv2.circle(frame, (cx - int(r * 0.3), cy - int(r * 0.3)),
                   max(2, int(r * 0.2)), (100, 100, 100), -1)

        # Fuse (curved line on top)
        fuse_base = (cx, cy - r)
        fuse_tip = (cx + 12, cy - r - 14)
        cv2.line(frame, fuse_base, fuse_tip, (40, 90, 140), 3)

        # Glowing spark at fuse tip
        self._spark_phase = (self._spark_phase + 0.3) % (2 * math.pi)
        spark_r = int(5 + 2 * math.sin(self._spark_phase))
        cv2.circle(frame, fuse_tip, spark_r + 2, (0, 140, 255), -1)   # Orange glow
        cv2.circle(frame, fuse_tip, spark_r, (0, 240, 255), -1)       # Yellow core
        cv2.circle(frame, fuse_tip, 2, (255, 255, 255), -1)           # White center

        # Hazard skull / cross icon on bomb
        cv2.putText(frame, "X", (cx - 7, cy + 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 220), 2)
