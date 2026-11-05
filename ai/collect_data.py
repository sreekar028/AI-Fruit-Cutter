"""
ai/collect_data.py
==================
Phase 2 — Custom Hand Gesture Dataset Collection Tool
AI Fruit Cutter Game

Features:
- Primary interactive Python tool for recording labeled gesture datasets from real webcam video.
- Supports three target classes:
    [1] CUT             — intentional fast swipe movements (horizontal, vertical, diagonal)
    [2] NORMAL_MOVEMENT — slow repositioning, wandering, natural hand movements
    [3] STATIONARY      — hand held still in place
- Uses Phase 1 PythonHandValidator (MediaPipe 21 landmarks, normalized coords, finite validation).
- Computes per-frame kinematics for landmark 8 (index fingertip):
    displacement_x, displacement_y, movement_distance, movement_speed, movement_direction.
- Keyboard controls:
    [1] Select CUT
    [2] Select NORMAL_MOVEMENT
    [3] Select STATIONARY
    [SPACE] Toggle recording ON / PAUSED
    [S] Save current session to CSV
    [C] Clear unsaved buffer
    [Q] / [ESC] Quit and auto-save
- Safe persistent storage:
    Appends samples to ai/dataset/raw/gesture_samples.csv without overwriting previous sessions.
    Maintains session metadata in ai/dataset/raw/session_metadata.csv.
- Displays rich on-screen HUD (class, sample counters, recording state, FPS).
- Automated self-test mode (--test) for CI/headless verification.
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import math
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

import cv2
import numpy as np
import pandas as pd

from ai.phase1_hand_test import PythonHandValidator


# Gesture Classes
CLASSES = {
    "1": "CUT",
    "2": "NORMAL_MOVEMENT",
    "3": "STATIONARY",
}

CLASS_COLORS = {
    "CUT": (0, 0, 255),             # Red
    "NORMAL_MOVEMENT": (255, 140, 0),# Orange/Cyan in BGR
    "STATIONARY": (0, 255, 0),       # Green
    "NONE": (180, 180, 180),
}


class GestureDataCollector:
    """
    Interactive tool for recording genuine hand gesture datasets for custom ML models.
    """

    def __init__(
        self,
        camera_index: int = 0,
        output_dir: str = "ai/dataset/raw",
        participant_id: str = "P1",
    ):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.samples_csv = os.path.join(self.output_dir, "gesture_samples.csv")
        self.metadata_csv = os.path.join(self.output_dir, "session_metadata.csv")

        self.participant_id = participant_id
        self.session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self.validator = PythonHandValidator(camera_index=camera_index, mirror=True)

        self.current_label = "STATIONARY"
        self.is_recording = False
        self.session_samples: List[Dict[str, Any]] = []

        # Previous fingertip position for motion calculation
        self._prev_tip_x: float = -1.0
        self._prev_tip_y: float = -1.0
        self._prev_time: float = 0.0

        # Cumulative counters across all sessions
        self.total_saved_counts = self._load_existing_counts()

    def _load_existing_counts(self) -> Dict[str, int]:
        counts = {"CUT": 0, "NORMAL_MOVEMENT": 0, "STATIONARY": 0}
        if os.path.exists(self.samples_csv):
            try:
                df = pd.read_csv(self.samples_csv, usecols=["gesture_label"])
                vc = df["gesture_label"].value_counts().to_dict()
                for k in counts:
                    counts[k] = int(vc.get(k, 0))
            except Exception as e:
                print(f"[Collector] Note: Could not read existing sample counts: {e}")
        return counts

    def process_frame_data(
        self,
        data: Dict[str, Any],
        now: float
    ) -> Optional[Dict[str, Any]]:
        """
        Compute kinematic features and format sample dictionary if valid hand is present.
        """
        if not data["valid"] or not data["landmarks"] or data["index_tip"] is None:
            self._prev_tip_x = -1.0
            self._prev_tip_y = -1.0
            self._prev_time = 0.0
            return None

        tip = data["index_tip"]
        tip_x, tip_y, tip_z = tip["x"], tip["y"], tip["z"]

        dx = 0.0
        dy = 0.0
        dist = 0.0
        speed = 0.0
        direction = 0.0

        if self._prev_tip_x >= 0 and self._prev_tip_y >= 0 and self._prev_time > 0:
            dt = max(1e-4, now - self._prev_time)
            dx = tip_x - self._prev_tip_x
            dy = tip_y - self._prev_tip_y
            dist = math.hypot(dx, dy)
            # Speed in normalized units per second (or px/ms equivalent scaled by 1000)
            speed = dist / dt
            direction = (math.atan2(dy, dx) * 180.0) / math.pi

        self._prev_tip_x = tip_x
        self._prev_tip_y = tip_y
        self._prev_time = now

        # Build row dictionary
        sample: Dict[str, Any] = {
            "sample_id": f"{self.session_id}_{len(self.session_samples) + 1}",
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "timestamp": round(now, 5),
            "platform": "python",
            "gesture_label": self.current_label,
        }

        # 21 landmarks (x, y, z)
        for lm in data["landmarks"]:
            idx = lm["id"]
            sample[f"x{idx}"] = lm["x"]
            sample[f"y{idx}"] = lm["y"]
            sample[f"z{idx}"] = lm["z"]

        # Kinematic movement fields
        sample["fingertip_x"] = round(tip_x, 5)
        sample["fingertip_y"] = round(tip_y, 5)
        sample["fingertip_z"] = round(tip_z, 5)
        sample["displacement_x"] = round(dx, 5)
        sample["displacement_y"] = round(dy, 5)
        sample["movement_distance"] = round(dist, 5)
        sample["movement_speed"] = round(speed, 5)
        sample["movement_direction"] = round(direction, 2)

        return sample

    def save_session(self) -> int:
        """
        Append collected session samples to CSV and record session metadata.
        """
        if not self.session_samples:
            print("[Collector] No new samples to save.")
            return 0

        new_df = pd.DataFrame(self.session_samples)
        file_exists = os.path.exists(self.samples_csv)
        new_df.to_csv(self.samples_csv, mode="a", index=False, header=not file_exists)

        # Update metadata
        counts = new_df["gesture_label"].value_counts().to_dict()
        meta_row = {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "recorded_at": datetime.now().isoformat(),
            "total_samples": len(new_df),
            "cut_samples": int(counts.get("CUT", 0)),
            "normal_samples": int(counts.get("NORMAL_MOVEMENT", 0)),
            "stationary_samples": int(counts.get("STATIONARY", 0)),
            "platform": "python",
        }
        meta_df = pd.DataFrame([meta_row])
        meta_exists = os.path.exists(self.metadata_csv)
        meta_df.to_csv(self.metadata_csv, mode="a", index=False, header=not meta_exists)

        saved_count = len(self.session_samples)
        for k, v in counts.items():
            self.total_saved_counts[k] = self.total_saved_counts.get(k, 0) + int(v)

        print(f"[Collector] Successfully saved {saved_count} samples to '{self.samples_csv}'.")
        self.session_samples.clear()
        # Refresh session ID for subsequent recordings
        self.session_id = f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        return saved_count

    def render_hud(
        self,
        frame: np.ndarray,
        data: Dict[str, Any],
        fps: float
    ) -> np.ndarray:
        """
        Render interactive instructions, current class, recording indicators, and sample counts.
        """
        h, w = frame.shape[:2]
        canvas = frame.copy()

        # Top banner for session info & recording status
        status_color = (0, 0, 255) if self.is_recording else (120, 120, 120)
        cv2.rectangle(canvas, (0, 0), (w, 95), (20, 20, 30), -1)
        cv2.line(canvas, (0, 95), (w, 95), (80, 80, 100), 1)

        # Recording badge
        rec_text = "[REC ACTIVE]" if self.is_recording else "[REC PAUSED]"
        cv2.putText(canvas, rec_text, (15, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color, 2, cv2.LINE_AA)

        # Selected Class badge
        cls_color = CLASS_COLORS.get(self.current_label, (255, 255, 255))
        cv2.putText(
            canvas, f"CLASS: {self.current_label}", (200, 30),
            cv2.FONT_HERSHEY_DUPLEX, 0.75, cls_color, 2, cv2.LINE_AA
        )

        # Session & FPS
        cv2.putText(canvas, f"FPS: {fps:.1f}", (w - 130, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(canvas, f"Session: {self.session_id[:18]}...", (15, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)

        # Counter summary
        in_buffer = len(self.session_samples)
        cut_cnt = self.total_saved_counts["CUT"] + sum(1 for s in self.session_samples if s["gesture_label"] == "CUT")
        norm_cnt = self.total_saved_counts["NORMAL_MOVEMENT"] + sum(1 for s in self.session_samples if s["gesture_label"] == "NORMAL_MOVEMENT")
        stat_cnt = self.total_saved_counts["STATIONARY"] + sum(1 for s in self.session_samples if s["gesture_label"] == "STATIONARY")

        counter_str = f"TOTAL: CUT={cut_cnt} | NORMAL={norm_cnt} | STATIONARY={stat_cnt} | (Unsaved Buffer={in_buffer})"
        cv2.putText(canvas, counter_str, (15, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 215, 0), 1, cv2.LINE_AA)

        # Bottom keymap guide
        cv2.rectangle(canvas, (0, h - 35), (w, h), (15, 15, 20), -1)
        guide = "[1] CUT  [2] NORMAL  [3] STATIONARY  |  [SPACE] Rec/Pause  |  [S] Save  |  [Q] Quit"
        cv2.putText(canvas, guide, (15, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (220, 220, 220), 1, cv2.LINE_AA)

        # Draw hand landmarks if detected
        if data["valid"] and data["landmarks"]:
            self.validator.annotate_frame(canvas, data, fps=None)
        else:
            cv2.putText(
                canvas, "NO HAND IN VIEW - HOLD HAND UP TO RECORD",
                (w // 2 - 230, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2
            )

        return canvas

    def run_interactive_collector(self):
        """
        Run interactive recording window.
        """
        if not self.validator.start_camera():
            print("[Collector] ERROR: Camera could not be opened.")
            return

        print("\n" + "=" * 70)
        print("  AI FRUIT CUTTER — PHASE 2 GESTURE DATASET RECORDER")
        print("  Controls:")
        print("    [1] Set Class to CUT")
        print("    [2] Set Class to NORMAL_MOVEMENT")
        print("    [3] Set Class to STATIONARY")
        print("    [SPACE] Toggle Recording ON / PAUSED")
        print("    [S] Save collected samples to CSV")
        print("    [C] Clear unsaved buffer")
        print("    [Q] / [ESC] Quit (auto-saves buffer)")
        print("=" * 70 + "\n")

        fps = 0.0
        prev_tick = time.time()
        window_name = "Phase 2: Hand Gesture Dataset Collector"

        try:
            while True:
                ret, frame = self.validator._cap.read()
                if not ret:
                    break

                if self.validator.mirror:
                    frame = cv2.flip(frame, 1)

                now = time.time()
                dt = now - prev_tick
                prev_tick = now
                if dt > 0:
                    fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)

                tracking_data = self.validator.process_frame(frame, timestamp=now)

                # If recording and hand is valid, store sample
                if self.is_recording and tracking_data["valid"]:
                    sample = self.process_frame_data(tracking_data, now)
                    if sample is not None:
                        self.session_samples.append(sample)

                display_frame = self.render_hud(frame, tracking_data, fps)
                cv2.imshow(window_name, display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('1'):
                    self.current_label = "CUT"
                    print(f"[Collector] Active class changed to: CUT")
                elif key == ord('2'):
                    self.current_label = "NORMAL_MOVEMENT"
                    print(f"[Collector] Active class changed to: NORMAL_MOVEMENT")
                elif key == ord('3'):
                    self.current_label = "STATIONARY"
                    print(f"[Collector] Active class changed to: STATIONARY")
                elif key == ord(' '):
                    self.is_recording = not self.is_recording
                    state_msg = "RECORDING STARTED" if self.is_recording else "RECORDING PAUSED"
                    print(f"[Collector] {state_msg} (Class={self.current_label})")
                elif key == ord('s') or key == ord('S'):
                    self.save_session()
                elif key == ord('c') or key == ord('C'):
                    discarded = len(self.session_samples)
                    self.session_samples.clear()
                    print(f"[Collector] Discarded {discarded} unsaved samples from buffer.")
                elif key == ord('q') or key == 27:  # 'q' or ESC
                    break

        finally:
            if self.session_samples:
                print("[Collector] Auto-saving remaining buffer before exit...")
                self.save_session()
            self.validator.release()
            cv2.destroyAllWindows()
            print("[Collector] Exited cleanly.")


def run_unit_tests():
    """Verify collector data integrity without opening webcam."""
    print("[Collector Test] Running unit checks for data collector...")
    collector = GestureDataCollector()

    # Verify dummy landmark processing
    synthetic_landmarks = [
        {"id": i, "x": 0.5 + i * 0.01, "y": 0.4 + i * 0.01, "z": 0.0}
        for i in range(21)
    ]
    data = {
        "valid": True,
        "count": 21,
        "landmarks": synthetic_landmarks,
        "index_tip": {"x": 0.58, "y": 0.48, "z": 0.0},
        "timestamp": 100.0,
        "error": None,
    }

    sample = collector.process_frame_data(data, 100.0)
    assert sample is not None, "Sample should be created for valid hand"
    assert sample["gesture_label"] == "STATIONARY"
    assert sample["platform"] == "python"
    assert "x0" in sample and "y20" in sample and "z20" in sample
    assert "movement_speed" in sample
    print("  [PASS] Frame processing and column layout verified.")
    print("[Collector Test] All unit checks passed!\n")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    else:
        collector = GestureDataCollector()
        collector.run_interactive_collector()
