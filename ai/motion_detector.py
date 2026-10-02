"""
ai/motion_detector.py
=====================
AI / Hand Tracking Module — Member 1
AI Fruit Cutter Game

Description:
    Processes a stream of index fingertip positions from HandTracker and:
      - Maintains a rolling trajectory buffer of recent positions.
      - Computes movement distance, direction, and speed per frame.
      - Detects a "cutting / slashing" gesture when speed exceeds a threshold.
      - Provides a clean data structure consumable by the Game module.

Usage:
    detector = MotionDetector()

    # Each game frame:
    motion_data = detector.update(tracking_data)

    # motion_data keys:
    #   hand_detected      (bool)
    #   finger_x           (int)
    #   finger_y           (int)
    #   previous_x         (int)
    #   previous_y         (int)
    #   movement_distance  (float)  pixels moved since last frame
    #   movement_speed     (float)  pixels/ms  (uses frame timestamps)
    #   movement_direction (float)  angle in degrees (0=right, 90=down, etc.)
    #   trajectory         (list)   last N (x, y) positions
    #   is_cutting         (bool)   True if a slash was detected this frame
"""

import math
import time
from collections import deque


# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------
TRAJECTORY_MAX_LEN   = 20      # How many recent points to keep
CUT_SPEED_THRESHOLD  = 0.2     # px/ms  — minimum speed to count as a cut
CUT_DISTANCE_MIN     = 10      # px     — minimum single-frame movement for a cut
HAND_LOST_RESET_SEC  = 0.5     # seconds without a hand before trajectory resets


class MotionDetector:
    """
    Stateful motion analyser for index fingertip positions.

    Feed it one tracking_data dict per frame (from HandTracker.get_tracking_data)
    and it returns enriched motion_data including trajectory and cut detection.

    Parameters
    ----------
    trajectory_len   : int   — Number of recent positions to store.
    cut_speed_px_ms  : float — Speed threshold (px/ms) that triggers is_cutting.
    cut_distance_min : float — Minimum pixel distance per frame to consider a cut.
    """

    def __init__(
        self,
        trajectory_len:   int   = TRAJECTORY_MAX_LEN,
        cut_speed_px_ms:  float = CUT_SPEED_THRESHOLD,
        cut_distance_min: float = CUT_DISTANCE_MIN,
    ):
        self._trajectory:       deque = deque(maxlen=trajectory_len)
        self._cut_speed_thresh: float = cut_speed_px_ms
        self._cut_dist_min:     float = cut_distance_min

        self._prev_x:        int   = -1
        self._prev_y:        int   = -1
        self._prev_time:     float = 0.0
        self._last_seen:     float = 0.0   # timestamp of last valid hand frame

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, tracking_data: dict) -> dict:
        """
        Process one frame's tracking data and return enriched motion data.

        Parameters
        ----------
        tracking_data : dict
            Output from HandTracker.get_tracking_data().

        Returns
        -------
        dict — Full motion data for this frame (see module docstring).
        """
        now = time.time()

        if not tracking_data["hand_detected"]:
            # Check if hand has been absent long enough to reset trajectory
            if self._last_seen > 0 and (now - self._last_seen) > HAND_LOST_RESET_SEC:
                self._reset()
            return self._build_output(
                hand_detected=False,
                fx=-1, fy=-1,
                distance=0.0, speed=0.0, direction=0.0,
                is_cutting=False,
            )

        fx = tracking_data["finger_x"]
        fy = tracking_data["finger_y"]
        self._last_seen = now
        previous_x = self._prev_x
        previous_y = self._prev_y

        # --- Compute movement ---
        if self._prev_x == -1:
            # First frame with a hand — no movement yet
            distance  = 0.0
            speed     = 0.0
            direction = 0.0
        else:
            dx       = fx - self._prev_x
            dy       = fy - self._prev_y
            distance = math.hypot(dx, dy)

            dt_ms = (now - self._prev_time) * 1000.0  # seconds → ms
            speed = distance / dt_ms if dt_ms > 0 else 0.0

            # Angle: 0° = right, 90° = down (screen coords, Y grows downward)
            direction = math.degrees(math.atan2(dy, dx))

        # --- Update trajectory ---
        self._trajectory.append((fx, fy))

        # --- Cut detection ---
        is_cutting = (
            distance >= self._cut_dist_min
            and speed >= self._cut_speed_thresh
        )

        # --- Store state for next frame ---
        self._prev_x    = fx
        self._prev_y    = fy
        self._prev_time = now

        return self._build_output(
            hand_detected=True,
            fx=fx, fy=fy,
            previous_x=previous_x, previous_y=previous_y,
            distance=distance,
            speed=speed,
            direction=direction,
            is_cutting=is_cutting,
        )

    def get_trajectory(self) -> list:
        """Return the current trajectory as a list of (x, y) tuples."""
        return list(self._trajectory)

    def reset(self):
        """Manually reset all state (e.g. between game rounds)."""
        self._reset()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_output(
        self, *, hand_detected, fx, fy,
        previous_x=-1, previous_y=-1,
        distance, speed, direction, is_cutting
    ) -> dict:
        return {
            "hand_detected":      hand_detected,
            "finger_x":           fx,
            "finger_y":           fy,
            "previous_x":         previous_x if hand_detected else -1,
            "previous_y":         previous_y if hand_detected else -1,
            "movement_distance":  round(distance, 2),
            "movement_speed":     round(speed, 4),
            "movement_direction": round(direction, 2),
            "trajectory":         list(self._trajectory),
            "is_cutting":         is_cutting,
        }

    def _reset(self):
        """Reset all internal tracking state."""
        self._trajectory.clear()
        self._prev_x    = -1
        self._prev_y    = -1
        self._prev_time = 0.0
        self._last_seen = 0.0


# ---------------------------------------------------------------------------
# Standalone test — run: python -m ai.motion_detector
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import cv2
    from ai.hand_tracker import HandTracker

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        sys.exit(1)

    tracker  = HandTracker()
    detector = MotionDetector()
    print("[INFO] Motion Detector started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame  = cv2.flip(frame, 1)
        t_data = tracker.get_tracking_data(frame)
        m_data = detector.update(t_data)
        frame  = tracker.draw_landmarks(frame, t_data)

        # Draw trajectory
        traj = m_data["trajectory"]
        for i in range(1, len(traj)):
            alpha = int(255 * i / len(traj))
            cv2.line(frame, traj[i - 1], traj[i], (0, alpha, 255 - alpha), 2)

        # Overlay info
        lines = [
            f"Hand: {'YES' if m_data['hand_detected'] else 'NO'}",
            f"Pos : ({m_data['finger_x']}, {m_data['finger_y']})",
            f"Dist: {m_data['movement_distance']:.1f} px",
            f"Speed: {m_data['movement_speed']:.3f} px/ms",
            f"Dir : {m_data['movement_direction']:.1f} deg",
            f"CUT : {'*** YES ***' if m_data['is_cutting'] else 'no'}",
        ]
        for i, line in enumerate(lines):
            color = (0, 0, 255) if "YES" in line and "CUT" in lines[i] else (200, 200, 200)
            cv2.putText(frame, line, (10, 30 + i * 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        cv2.imshow("Motion Detector — AI Module (Member 1)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Motion Detector stopped.")
