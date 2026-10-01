/**
 * web/src/game/Collision.ts
 * =========================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Continuous line-segment to circle distance testing.
 * Prevents tunneling on rapid player swipes by projecting distance to
 * trajectory segments.
 */

import { Fruit } from './Fruit';
import type { MotionData } from '../ai/MotionDetector';

export class CollisionDetector {
  public bladeThickness: number;

  constructor(bladeThickness = 14.0) {
    this.bladeThickness = bladeThickness;
  }

  public checkCollisions(motionData: MotionData, activeFruits: Fruit[]): Fruit[] {
    if (!motionData.handDetected) return [];

    const isCutting = motionData.isCutting;
    const speed = motionData.movementSpeed;

    // Must be cutting or moving with sufficient speed
    if (!isCutting && speed < 0.28) {
      return [];
    }

    const fx = motionData.fingerX;
    const fy = motionData.fingerY;
    const px = motionData.previousX;
    const py = motionData.previousY;
    const trajectory = motionData.trajectory;
    const direction = motionData.movementDirection;

    if (fx < 0 || fy < 0) return [];

    // Collect line segments
    const segments: Array<[[number, number], [number, number]]> = [];
    if (px >= 0 && py >= 0 && (px !== fx || py !== fy)) {
      segments.push([[px, py], [fx, fy]]);
    }

    if (trajectory.length >= 2) {
      const recent = trajectory.slice(-5);
      for (let i = 0; i < recent.length - 1; i++) {
        const p1 = recent[i];
        const p2 = recent[i + 1];
        if (p1[0] !== p2[0] || p1[1] !== p2[1]) {
          segments.push([p1, p2]);
        }
      }
    }

    if (segments.length === 0) {
      segments.push([[fx, fy], [fx, fy]]);
    }

    const sliced: Fruit[] = [];

    for (const fruit of activeFruits) {
      if (!fruit.isActive) continue;

      let hit = false;
      const effectiveRadius = fruit.radius + this.bladeThickness;

      for (const [p1, p2] of segments) {
        const dist = this.distPointToSegment(fruit.x, fruit.y, p1[0], p1[1], p2[0], p2[1]);
        if (dist <= effectiveRadius) {
          hit = true;
          break;
        }
      }

      if (hit) {
        fruit.slice(direction);
        sliced.push(fruit);
      }
    }

    return sliced;
  }

  private distPointToSegment(
    px: number,
    py: number,
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): number {
    const dx = x2 - x1;
    const dy = y2 - y1;

    if (dx === 0 && dy === 0) {
      return Math.hypot(px - x1, py - y1);
    }

    const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)));
    const closestX = x1 + t * dx;
    const closestY = y1 + t * dy;

    return Math.hypot(px - closestX, py - closestY);
  }
}
