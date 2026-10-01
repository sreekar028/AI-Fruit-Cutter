"""
game/effects.py
===============
Game Logic Module — Member 2
AI Fruit Cutter Game

Description:
    Visual feedback and particle effects:
    - Juice splatter particles (colored per fruit)
    - Bomb explosion smoke and fire burst
    - Floating text effects (+10, COMBO 3x!, MISS!, BOMB!)
    - Smooth neon blade trail rendering
"""

import math
import random
import cv2
import numpy as np


class Particle:
    """Represents a single splash or spark particle."""

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: tuple, radius: float = 4.0, lifetime: float = 0.6):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.radius = float(radius)
        self.lifetime = float(lifetime)
        self.age = 0.0
        self.gravity = 0.35

    def update(self, dt: float = 0.033):
        self.age += dt
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def draw(self, frame: np.ndarray):
        if not self.is_alive:
            return
        progress = self.age / self.lifetime
        current_r = max(1, int(self.radius * (1.0 - progress)))
        cx, cy = int(self.x), int(self.y)
        h, w = frame.shape[:2]
        if 0 <= cx < w and 0 <= cy < h:
            cv2.circle(frame, (cx, cy), current_r, self.color, -1)


class FloatingText:
    """Represents a rising, fading text message."""

    def __init__(self, text: str, x: int, y: int, color: tuple,
                 scale: float = 0.75, lifetime: float = 0.8):
        self.text = text
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.scale = scale
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float = 0.033):
        self.age += dt
        self.y -= 1.8  # float upwards

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    def draw(self, frame: np.ndarray):
        if not self.is_alive:
            return
        cx, cy = int(self.x), int(self.y)
        h, w = frame.shape[:2]
        if 0 <= cx < w and 0 <= cy < h:
            # Black shadow border for readability
            cv2.putText(frame, self.text, (cx + 1, cy + 1),
                        cv2.FONT_HERSHEY_DUPLEX, self.scale, (0, 0, 0), 2)
            cv2.putText(frame, self.text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, self.scale, self.color, 2)


class EffectsManager:
    """Manages particles, floating score labels, and blade trails."""

    def __init__(self):
        self.particles = []
        self.texts = []

    def spawn_fruit_splash(self, x: float, y: float, color_splash: tuple, count: int = 16):
        """Spawn juice droplets bursting from cut location."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3.0, 8.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1.5
            radius = random.uniform(3.0, 6.0)
            lifetime = random.uniform(0.4, 0.75)
            self.particles.append(
                Particle(x, y, vx, vy, color_splash, radius, lifetime)
            )

    def spawn_bomb_explosion(self, x: float, y: float, count: int = 30):
        """Spawn fiery sparks and smoke burst for bomb detonation."""
        colors = [
            (0, 140, 255),    # Bright Orange
            (0, 240, 255),    # Yellow
            (0, 60, 255),     # Red
            (100, 100, 100),  # Smoke Gray
        ]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4.0, 12.0)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.0
            color = random.choice(colors)
            radius = random.uniform(4.0, 9.0)
            lifetime = random.uniform(0.5, 0.9)
            self.particles.append(
                Particle(x, y, vx, vy, color, radius, lifetime)
            )

    def spawn_floating_text(self, text: str, x: int, y: int, color: tuple = (0, 255, 255), scale: float = 0.75):
        """Add a floating score or notification label."""
        self.texts.append(FloatingText(text, x, y, color, scale))

    def update(self, dt: float = 0.033):
        """Update physics of all active effects."""
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive]

        for t in self.texts:
            t.update(dt)
        self.texts = [t for t in self.texts if t.is_alive]

    def draw(self, frame: np.ndarray):
        """Draw particles and floating texts onto the frame."""
        for p in self.particles:
            p.draw(frame)
        for t in self.texts:
            t.draw(frame)

    def draw_blade_trail(self, frame: np.ndarray, trajectory: list, is_cutting: bool):
        """
        Draw an enhanced glowing sword slash along Member 1's trajectory points.
        """
        n = len(trajectory)
        if n < 2:
            return

        core_color = (255, 255, 255)  # White core
        glow_color = (0, 255, 255) if is_cutting else (0, 200, 100)  # Cyan/Yellow slash

        for i in range(1, n):
            # Alpha gradient: oldest point is thin/transparent, newest is thick/glowing
            progress = i / float(n)
            width = max(1, int(progress * (7 if is_cutting else 3)))

            pt1 = (int(trajectory[i - 1][0]), int(trajectory[i - 1][1]))
            pt2 = (int(trajectory[i][0]), int(trajectory[i][1]))

            # Outer glow
            cv2.line(frame, pt1, pt2, glow_color, width + 3)
            # Inner sharp core
            cv2.line(frame, pt1, pt2, core_color, max(1, width - 1))

    def reset(self):
        """Clear all active particles and texts."""
        self.particles.clear()
        self.texts.clear()
