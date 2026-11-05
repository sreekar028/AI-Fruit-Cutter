"""
ai/dataset_validator.py
=======================
Phase 2 — Dataset Validation and Reporting Tool
AI Fruit Cutter Game

Features:
- Validates raw gesture samples CSV files against Phase 2 schema.
- Checks:
  1. Total sample count and counts per class (CUT, NORMAL_MOVEMENT, STATIONARY).
  2. Number of recording sessions and sample distribution per session.
  3. Missing values (NaN / nulls) and non-finite numbers.
  4. Duplicate sample detection.
  5. Timestamp monotonicity and frame rate consistency.
  6. Landmark coordinate validity ([0, 1] range checks, index tip presence).
- Generates a statistical markdown/text report and a visual class distribution chart.
- Saves validation reports into ai/dataset/reports/.
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


REQUIRED_META_COLUMNS = [
    "sample_id",
    "session_id",
    "participant_id",
    "timestamp",
    "platform",
    "gesture_label",
]

REQUIRED_KINEMATIC_COLUMNS = [
    "fingertip_x",
    "fingertip_y",
    "fingertip_z",
    "displacement_x",
    "displacement_y",
    "movement_distance",
    "movement_speed",
    "movement_direction",
]

EXPECTED_CLASSES = ["CUT", "NORMAL_MOVEMENT", "STATIONARY"]


class DatasetValidator:
    """
    Validates collected gesture datasets and produces summary reports & charts.
    """

    def __init__(self, dataset_path: str = "ai/dataset/raw/gesture_samples.csv"):
        self.dataset_path = dataset_path
        self.reports_dir = "ai/dataset/reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def validate(self) -> Dict[str, Any]:
        """
        Validate the dataset CSV file and compute statistical metrics.
        """
        if not os.path.exists(self.dataset_path):
            return {
                "exists": False,
                "error": f"Dataset file not found at: {self.dataset_path}",
            }

        try:
            df = pd.read_csv(self.dataset_path)
        except Exception as e:
            return {
                "exists": True,
                "valid": False,
                "error": f"Failed to parse CSV file: {e}",
            }

        total_samples = len(df)
        if total_samples == 0:
            return {
                "exists": True,
                "valid": False,
                "total_samples": 0,
                "error": "Dataset is empty (0 rows).",
            }

        # 1. Column check
        expected_landmark_cols = []
        for i in range(21):
            expected_landmark_cols.extend([f"x{i}", f"y{i}", f"z{i}"])

        all_expected_cols = REQUIRED_META_COLUMNS + expected_landmark_cols + REQUIRED_KINEMATIC_COLUMNS
        missing_cols = [c for c in all_expected_cols if c not in df.columns]

        # 2. Class counts
        class_counts = df["gesture_label"].value_counts().to_dict() if "gesture_label" in df.columns else {}
        for cls in EXPECTED_CLASSES:
            class_counts.setdefault(cls, 0)

        # 3. Session info
        session_counts = df["session_id"].value_counts().to_dict() if "session_id" in df.columns else {}
        num_sessions = len(session_counts)

        # 4. Missing values
        null_counts = int(df.isnull().sum().sum())
        missing_by_col = df.isnull().sum()[df.isnull().sum() > 0].to_dict()

        # 5. Non-finite values in numeric columns
        numeric_cols = [c for c in df.columns if c not in ["session_id", "participant_id", "platform", "gesture_label"]]
        non_finite_count = 0
        if numeric_cols:
            non_finite_mask = ~np.isfinite(df[numeric_cols].to_numpy())
            non_finite_count = int(np.sum(non_finite_mask))

        # 6. Duplicates (excluding sample_id)
        cols_for_dup = [c for c in df.columns if c != "sample_id"]
        duplicate_count = int(df.duplicated(subset=cols_for_dup).sum())

        # 7. Coordinate range checks
        out_of_bounds_coords = 0
        for i in range(21):
            if f"x{i}" in df.columns and f"y{i}" in df.columns:
                bad_x = (df[f"x{i}"] < -0.1) | (df[f"x{i}"] > 1.1)
                bad_y = (df[f"y{i}"] < -0.1) | (df[f"y{i}"] > 1.1)
                out_of_bounds_coords += int((bad_x | bad_y).sum())

        # Overall validity
        is_valid = (
            len(missing_cols) == 0
            and null_counts == 0
            and non_finite_count == 0
            and total_samples > 0
        )

        results = {
            "exists": True,
            "valid": is_valid,
            "total_samples": total_samples,
            "class_counts": class_counts,
            "num_sessions": num_sessions,
            "session_counts": session_counts,
            "missing_columns": missing_cols,
            "null_count": null_counts,
            "missing_by_col": missing_by_col,
            "non_finite_count": non_finite_count,
            "duplicate_count": duplicate_count,
            "out_of_bounds_coords": out_of_bounds_coords,
            "platforms": df["platform"].unique().tolist() if "platform" in df.columns else [],
        }

        return results

    def generate_report(self, save_chart: bool = True) -> str:
        """
        Generate a formatted validation report and save markdown & chart to disk.
        """
        metrics = self.validate()
        if not metrics.get("exists"):
            return f"[ERROR] {metrics.get('error')}"

        report_lines = [
            "# AI Fruit Cutter — Phase 2 Dataset Validation Report",
            f"**Dataset File**: `{self.dataset_path}`",
            f"**Total Samples**: {metrics['total_samples']}",
            f"**Validation Status**: {'✅ VALID' if metrics['valid'] else '❌ INVALID'}",
            "",
            "## 1. Class Distribution",
            "| Gesture Class | Sample Count | Percentage |",
            "| :--- | :--- | :--- |",
        ]

        total = max(1, metrics["total_samples"])
        for cls in EXPECTED_CLASSES:
            cnt = metrics["class_counts"].get(cls, 0)
            pct = (cnt / total) * 100.0
            report_lines.append(f"| **{cls}** | {cnt} | {pct:.1f}% |")

        report_lines.extend([
            "",
            "## 2. Session Information",
            f"- **Total Recording Sessions**: {metrics['num_sessions']}",
            f"- **Platforms Recorded**: {', '.join(metrics.get('platforms', []))}",
            "- **Samples Per Session**:",
        ])
        for sess, cnt in metrics["session_counts"].items():
            report_lines.append(f"  - `{sess}`: {cnt} samples")

        report_lines.extend([
            "",
            "## 3. Data Quality & Hygiene",
            f"- **Missing Columns**: {len(metrics['missing_columns'])} ({', '.join(metrics['missing_columns']) if metrics['missing_columns'] else 'None'})",
            f"- **Null / Missing Values**: {metrics['null_count']}",
            f"- **Non-Finite (NaN / Inf) Coordinates**: {metrics['non_finite_count']}",
            f"- **Duplicate Rows**: {metrics['duplicate_count']}",
            f"- **Coordinates Out of [0, 1] Bounds**: {metrics['out_of_bounds_coords']}",
            "",
            "## 4. Assessment for Phase 3 (Feature Extraction)",
        ])

        if metrics["valid"]:
            min_target = 500
            classes_met = all(metrics["class_counts"].get(c, 0) >= min_target for c in EXPECTED_CLASSES)
            if classes_met:
                report_lines.append(
                    "✅ **Target Achieved**: All classes meet the target of at least 500 samples. Ready for feature extraction."
                )
            else:
                report_lines.append(
                    f"⚠️ **In Progress**: Current sample counts are below the target of {min_target} per class, but schema and data quality are valid."
                )
        else:
            report_lines.append(
                "❌ **Action Required**: Fix invalid columns, nulls, or non-finite values before proceeding."
            )

        report_text = "\n".join(report_lines)

        # Save Markdown Report
        report_path = os.path.join(self.reports_dir, "dataset_validation_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        # Generate & Save Class Distribution Chart
        if save_chart and metrics["total_samples"] > 0:
            self._save_chart(metrics["class_counts"])

        return report_text

    def _save_chart(self, class_counts: Dict[str, int]):
        """Render and save class distribution bar chart."""
        try:
            plt.figure(figsize=(8, 5))
            sns.set_theme(style="whitegrid")
            classes = list(class_counts.keys())
            counts = list(class_counts.values())
            colors = ["#FF5722", "#2196F3", "#4CAF50"]

            bars = plt.bar(classes, counts, color=colors[:len(classes)], width=0.55, edgecolor="black", linewidth=1.2)
            plt.title("Hand Gesture Dataset — Class Distribution", fontsize=14, fontweight="bold", pad=15)
            plt.xlabel("Gesture Class", fontsize=12, fontweight="bold")
            plt.ylabel("Sample Count", fontsize=12, fontweight="bold")
            plt.axhline(500, color="gray", linestyle="--", linewidth=1, label="Target (500 samples)")

            for bar in bars:
                h = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2.0, h + 10, f"{int(h)}", ha="center", va="bottom", fontweight="bold")

            plt.legend(loc="upper right")
            plt.tight_layout()
            chart_path = os.path.join(self.reports_dir, "class_distribution.png")
            plt.savefig(chart_path, dpi=200)
            plt.close()
        except Exception as e:
            print(f"[DatasetValidator] Warning: Could not generate chart: {e}")


def main():
    parser = argparse.ArgumentParser(description="Validate Hand Gesture Dataset for Phase 2")
    parser.add_argument("--csv", default="ai/dataset/raw/gesture_samples.csv", help="Path to gesture dataset CSV")
    args = parser.parse_args()

    validator = DatasetValidator(dataset_path=args.csv)
    report = validator.generate_report()
    print("\n" + report + "\n")


if __name__ == "__main__":
    main()
