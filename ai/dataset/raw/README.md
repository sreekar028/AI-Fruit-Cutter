"""
ai/dataset/raw/README.md
========================
Phase 2 — Raw Gesture Dataset Storage

This directory contains the collected CSV gesture samples and session metadata recorded
using either:
- Python interactive tool: `python ai/collect_data.py`
- Browser recording session export via `BrowserGestureRecorder`

Structure:
- `gesture_samples.csv`: Consolidated sample-level recordings containing 21 normalized landmarks (x0..z20)
  and fingertip kinematic parameters.
- `session_metadata.csv`: High-level session logs (session_id, participant_id, timestamps, sample counts per class).
"""
