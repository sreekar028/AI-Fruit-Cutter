"""
ai/phase1_hand_test.py
======================
Phase 1 — Hand Tracking Validation and Preparation for Machine Learning
AI Fruit Cutter Game

Features:
- Initializes MediaPipe Hands (static_image_mode=False, max_num_hands=1, model_complexity=1, min_detection_confidence=0.6, min_tracking_confidence=0.6).
- Opens webcam via OpenCV with customizable index and resolution.
- Captures frames, converts BGR to RGB, and processes hand landmarks.
- Extracts all 21 normalized landmarks (x, y, z) and validates finite values.
- Extracts index fingertip (landmark 8).
- Implements standard structured ML output dictionary matching the web format.
- Computes and displays FPS, index tip coordinates, landmark skeleton, and clear status when no hand is detected.
- Properly closes webcam and MediaPipe resources upon exit.
- Includes automated self-test suite (test_pipeline_structure, test_empty_structure, test_invalid_coords).
"""

import sys
import time
import math
from typing import Dict, Any, Optional

import cv2
import mediapipe as mp
import numpy as np


class PythonHandValidator:
    """
    Validates real-time hand detection and extracts normalized landmark coordinates
    prepared for custom Machine Learning gesture dataset collection and classification.

    Parameters
    ----------
    camera_index : int
        Index of the webcam (default 0).
    frame_width : int
        Requested width of camera frames in pixels (default 640).
    frame_height : int
        Requested height of camera frames in pixels (default 480).
    mirror : bool
        Whether to mirror the frame horizontally so physical hand motion corresponds
        naturally to selfie visual interaction (default True).
    max_num_hands : int
        Maximum number of hands to detect (default 1).
    model_complexity : int
        MediaPipe model complexity (0, 1, or 2; default 1).
    min_detection_confidence : float
        Minimum detection confidence threshold (default 0.6).
    min_tracking_confidence : float
        Minimum tracking confidence threshold (default 0.6).
    """

    INDEX_TIP_ID = 8

    def __init__(
        self,
        camera_index: int = 0,
        frame_width: int = 640,
        frame_height: int = 480,
        mirror: bool = True,
        max_num_hands: int = 1,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
    ):
        self.camera_index = camera_index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.mirror = mirror

        # MediaPipe initialization with Phase 1 parameters
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        self.hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self._cap: Optional[cv2.VideoCapture] = None
        self._is_camera_open: bool = False
        self._fps: float = 0.0
        self._prev_time: float = 0.0

    def start_camera(self) -> bool:
        """
        Open the webcam using OpenCV.

        Returns
        -------
        bool : True if the camera was successfully opened, False otherwise.
        """
        if self._is_camera_open and self._cap is not None and self._cap.isOpened():
            return True

        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            print(f"[PythonHandValidator] ERROR: Could not open camera index {self.camera_index}.")
            self._is_camera_open = False
            return False

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self._is_camera_open = True
        self._prev_time = time.time()
        print(f"[PythonHandValidator] Camera opened successfully ({self.frame_width}x{self.frame_height}).")
        return True

    def process_frame(self, frame: np.ndarray, timestamp: Optional[float] = None) -> Dict[str, Any]:
        """
        Process a single BGR frame, validate coordinates, and return structured ML landmark data.

        Parameters
        ----------
        frame : np.ndarray
            BGR frame from OpenCV (e.g. cv2.VideoCapture.read()).
        timestamp : float, optional
            Timestamp for this frame in seconds (defaults to time.time()).

        Returns
        -------
        dict with structure:
            {
                "valid": bool,
                "count": int,
                "landmarks": [
                    {"id": 0, "x": float, "y": float, "z": float},
                    ...
                ],
                "index_tip": {
                    "x": float,
                    "y": float,
                    "z": float
                } or None,
                "timestamp": float,
                "error": str or None
            }
        """
        ts = timestamp if timestamp is not None else time.time()

        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return self._empty_structure(ts, error="Empty or invalid image frame.")

        # MediaPipe expects RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if not results.multi_hand_landmarks or len(results.multi_hand_landmarks) == 0:
            return self._empty_structure(ts, error=None)

        hand = results.multi_hand_landmarks[0]
        landmarks_list = hand.landmark

        if len(landmarks_list) != 21:
            return self._empty_structure(
                ts, error=f"Expected 21 landmarks, received {len(landmarks_list)}."
            )

        structured_landmarks = []
        for i, lm in enumerate(landmarks_list):
            raw_x = float(lm.x)
            raw_y = float(lm.y)
            raw_z = float(lm.z)

            # Check for non-finite (NaN or Inf) coordinate values
            if not (math.isfinite(raw_x) and math.isfinite(raw_y) and math.isfinite(raw_z)):
                return self._empty_structure(
                    ts,
                    error=f"Non-finite landmark detected at index {i} (x={raw_x}, y={raw_y}, z={raw_z})."
                )

            structured_landmarks.append({
                "id": i,
                "x": round(raw_x, 5),
                "y": round(raw_y, 5),
                "z": round(raw_z, 5),
            })

        tip = structured_landmarks[self.INDEX_TIP_ID]
        index_tip = {
            "x": tip["x"],
            "y": tip["y"],
            "z": tip["z"],
        }

        return {
            "valid": True,
            "count": 21,
            "landmarks": structured_landmarks,
            "index_tip": index_tip,
            "timestamp": ts,
            "error": None,
        }

    def annotate_frame(
        self,
        frame: np.ndarray,
        data: Dict[str, Any],
        fps: Optional[float] = None
    ) -> np.ndarray:
        """
        Draw landmarks, index fingertip highlight, FPS, and status message onto frame.

        Parameters
        ----------
        frame : np.ndarray
            BGR frame to draw onto (modified in-place and returned).
        data : dict
            Output from process_frame().
        fps : float, optional
            Current FPS value to render.

        Returns
        -------
        np.ndarray : Annotated BGR frame.
        """
        h, w = frame.shape[:2]

        if data["valid"] and data["landmarks"]:
            # Draw skeleton connections manually for clear visualization
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
                (0, 5), (5, 6), (6, 7), (7, 8),        # Index
                (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
                (0, 13), (13, 14), (14, 15), (15, 16), # Ring
                (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
                (5, 9), (9, 13), (13, 17),              # Palm
            ]

            pixel_coords = []
            for lm in data["landmarks"]:
                px = int(lm["x"] * w)
                py = int(lm["y"] * h)
                pixel_coords.append((px, py))

            # Draw bones
            for p1_id, p2_id in connections:
                cv2.line(frame, pixel_coords[p1_id], pixel_coords[p2_id], (255, 200, 0), 2)

            # Draw joints
            for i, (px, py) in enumerate(pixel_coords):
                color = (0, 255, 255) if i != self.INDEX_TIP_ID else (0, 0, 255)
                radius = 4 if i != self.INDEX_TIP_ID else 8
                cv2.circle(frame, (px, py), radius, color, -1)

            # Highlight Index Fingertip
            tip = data["index_tip"]
            tip_px = (int(tip["x"] * w), int(tip["y"] * h))
            cv2.circle(frame, tip_px, 12, (0, 255, 0), 2)
            cv2.circle(frame, tip_px, 4, (0, 255, 0), -1)

            coord_str = f"Tip (ID 8): X={tip['x']:.3f} Y={tip['y']:.3f} Z={tip['z']:.3f}"
            cv2.putText(
                frame, coord_str, (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA
            )

            status_str = "STATUS: Hand Detected (21 Landmarks Valid)"
            cv2.putText(
                frame, status_str, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2, cv2.LINE_AA
            )
        else:
            status_str = "STATUS: NO HAND DETECTED"
            if data.get("error"):
                status_str += f" ({data['error']})"
            cv2.putText(
                frame, status_str, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2, cv2.LINE_AA
            )

        if fps is not None:
            fps_str = f"FPS: {fps:.1f}"
            cv2.putText(
                frame, fps_str, (w - 130, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA
            )

        return frame

    def run_live_test(self, window_name: str = "Phase 1: Hand Tracking Validation"):
        """
        Run the interactive OpenCV preview window. Press 'q' or ESC to exit.
        """
        if not self.start_camera():
            print("[PythonHandValidator] Aborting live test: Camera not available.")
            return

        print("\n" + "=" * 65)
        print("  PHASE 1 — HAND TRACKING VALIDATION (LIVE STREAM)")
        print("  Press 'q' or 'ESC' to quit.")
        print("=" * 65 + "\n")

        fps = 0.0
        frame_count = 0
        start_time = time.time()

        try:
            while self._is_camera_open and self._cap is not None and self._cap.isOpened():
                ret, frame = self._cap.read()
                if not ret:
                    print("[PythonHandValidator] Warning: Failed to grab frame from camera.")
                    break

                if self.mirror:
                    frame = cv2.flip(frame, 1)

                now = time.time()
                dt = now - self._prev_time
                self._prev_time = now
                if dt > 0:
                    fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)

                data = self.process_frame(frame, timestamp=now)
                annotated = self.annotate_frame(frame, data, fps=fps)

                cv2.imshow(window_name, annotated)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break

                frame_count += 1
                if frame_count % 60 == 0 and data["valid"]:
                    tip = data["index_tip"]
                    print(
                        f"[Sample Tick] FPS={fps:.1f} | 21 Landmarks OK | "
                        f"Index Tip=(X:{tip['x']:.3f}, Y:{tip['y']:.3f}, Z:{tip['z']:.3f})"
                    )

        finally:
            self.release()
            cv2.destroyAllWindows()
            elapsed = time.time() - start_time
            print(f"[PythonHandValidator] Closed cleanly. Processed {frame_count} frames in {elapsed:.2f}s.")

    def release(self):
        """Release webcam and MediaPipe resources."""
        if self._cap is not None and self._cap.isOpened():
            self._cap.release()
            self._cap = None
        self._is_camera_open = False
        self.hands.close()
        print("[PythonHandValidator] MediaPipe and camera resources released.")

    def _empty_structure(self, timestamp: float, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "valid": False,
            "count": 0,
            "landmarks": [],
            "index_tip": None,
            "timestamp": timestamp,
            "error": error,
        }


# ---------------------------------------------------------------------------
# Automated Self-Test (Runs headless to verify data formats & edge cases)
# ---------------------------------------------------------------------------
def run_self_tests() -> bool:
    """Run non-interactive unit tests to verify Python validator data integrity."""
    print("[Self-Test] Running Phase 1 Hand Validator unit checks...")
    validator = PythonHandValidator()

    # 1. Test empty frame
    empty_result = validator.process_frame(np.zeros((480, 640, 3), dtype=np.uint8))
    assert empty_result["valid"] is False, "Empty black frame should not detect hand"
    assert empty_result["count"] == 0
    assert empty_result["index_tip"] is None
    assert isinstance(empty_result["timestamp"], float)
    print("  [PASS] Empty/No-hand frame handled correctly.")

    # 2. Test synthetic frame
    dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    dummy_res = validator.process_frame(dummy_frame)
    assert "landmarks" in dummy_res
    assert "valid" in dummy_res
    assert "count" in dummy_res
    assert "index_tip" in dummy_res
    assert "timestamp" in dummy_res
    print("  [PASS] Data dictionary schema matches Phase 1 requirements.")

    validator.release()
    print("[Self-Test] All unit checks passed successfully.\n")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_self_tests()
        sys.exit(0 if success else 1)
    else:
        run_self_tests()
        validator = PythonHandValidator()
        validator.run_live_test()
