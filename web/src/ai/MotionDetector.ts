/**
 * web/src/ai/MotionDetector.ts
 * ============================
 * AI / Motion Detection Module — Web Version (Member 1 equivalent)
 * 
 * Replicates Member 1's Python MotionDetector:
 * - Maintains a rolling trajectory buffer of recent fingertip coordinates
 * - Computes Euclidean distance, velocity (px/ms), and direction angle (degrees)
 * - Detects cutting gestures when movement speed & distance meet thresholds
 * - Handles auto-reset when hand temporarily disappears
 */

import type { TrackingData } from './HandTracker';

export interface MotionData {
  handDetected: boolean;
  fingerX: number;
  fingerY: number;
  previousX: number;
  previousY: number;
  movementDistance: number;
  movementSpeed: number;
  movementDirection: number;
  trajectory: Array<[number, number]>;
  isCutting: boolean;
}

export class MotionDetector {
  private trajectory: Array<[number, number]> = [];
  private trajectoryMaxLen: number;
  private cutSpeedThreshold: number;
  private cutDistanceMin: number;
  private handLostResetSec: number;

  private prevX = -1;
  private prevY = -1;
  private prevTime = 0;
  private lastSeen = 0;

  constructor(
    trajectoryMaxLen = 20,
    cutSpeedThreshold = 0.40,
    cutDistanceMin = 25.0,
    handLostResetSec = 0.50
  ) {
    this.trajectoryMaxLen = trajectoryMaxLen;
    this.cutSpeedThreshold = cutSpeedThreshold;
    this.cutDistanceMin = cutDistanceMin;
    this.handLostResetSec = handLostResetSec;
  }

  public update(trackingData: TrackingData): MotionData {
    const now = performance.now() / 1000.0; // seconds

    if (!trackingData.handDetected) {
      if (this.lastSeen > 0 && now - this.lastSeen > this.handLostResetSec) {
        this.reset();
      }
      return this.buildOutput(false, -1, -1, 0, 0, 0, false);
    }

    const fx = trackingData.fingerX;
    const fy = trackingData.fingerY;
    this.lastSeen = now;

    let distance = 0;
    let speed = 0;
    let direction = 0;

    if (this.prevX === -1) {
      // First frame with hand
      distance = 0;
      speed = 0;
      direction = 0;
    } else {
      const dx = fx - this.prevX;
      const dy = fy - this.prevY;
      distance = Math.hypot(dx, dy);

      const dtMs = (now - this.prevTime) * 1000.0;
      speed = dtMs > 0 ? distance / dtMs : 0;

      // Angle in degrees: 0 = right, 90 = down
      direction = (Math.atan2(dy, dx) * 180.0) / Math.PI;
    }

    // Update trajectory buffer
    this.trajectory.push([fx, fy]);
    if (this.trajectory.length > this.trajectoryMaxLen) {
      this.trajectory.shift();
    }

    // Cutting condition
    const isCutting =
      distance >= this.cutDistanceMin && speed >= this.cutSpeedThreshold;

    const output = this.buildOutput(
      true,
      fx,
      fy,
      distance,
      speed,
      direction,
      isCutting
    );

    this.prevX = fx;
    this.prevY = fy;
    this.prevTime = now;

    return output;
  }

  public getTrajectory(): Array<[number, number]> {
    return [...this.trajectory];
  }

  public reset() {
    this.trajectory = [];
    this.prevX = -1;
    this.prevY = -1;
    this.prevTime = 0;
    this.lastSeen = 0;
  }

  private buildOutput(
    handDetected: boolean,
    fx: number,
    fy: number,
    distance: number,
    speed: number,
    direction: number,
    isCutting: boolean
  ): MotionData {
    return {
      handDetected,
      fingerX: fx,
      fingerY: fy,
      previousX: handDetected ? this.prevX : -1,
      previousY: handDetected ? this.prevY : -1,
      movementDistance: Math.round(distance * 100) / 100,
      movementSpeed: Math.round(speed * 1000) / 1000,
      movementDirection: Math.round(direction * 10) / 10,
      trajectory: [...this.trajectory],
      isCutting,
    };
  }
}
