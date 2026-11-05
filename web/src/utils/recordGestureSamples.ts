/**
 * web/src/utils/recordGestureSamples.ts
 * ====================================
 * Phase 2 — Browser-side Gesture Dataset Collection and CSV Exporter
 * 
 * Reuses existing MediaPipe HandTracker pipeline (zero extra webcams or loops).
 * Collects normalized hand landmarks (x0..x20, y0..y20, z0..z20) and fingertip
 * kinematic metrics identically matching the Python collector schema.
 */

import type { ValidatedHandData } from './validateHandLandmarks.ts';

export type GestureClass = 'CUT' | 'NORMAL_MOVEMENT' | 'STATIONARY';

export interface GestureSampleRecord {
  sample_id: string;
  session_id: string;
  participant_id: string;
  timestamp: number;
  platform: 'web';
  gesture_label: GestureClass;
  // 63 landmark coordinates (x0..z20)
  [key: `x${number}` | `y${number}` | `z${number}`]: number;
  // Kinematics
  fingertip_x: number;
  fingertip_y: number;
  fingertip_z: number;
  displacement_x: number;
  displacement_y: number;
  movement_distance: number;
  movement_speed: number;
  movement_direction: number;
}

export class BrowserGestureRecorder {
  private sessionId: string;
  private participantId: string;
  private currentClass: GestureClass = 'STATIONARY';
  private isRecording = false;
  private samples: GestureSampleRecord[] = [];

  private prevTipX = -1;
  private prevTipY = -1;
  private prevTime = 0;

  constructor(participantId = 'web_user') {
    this.participantId = participantId;
    this.sessionId = `web_sess_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
  }

  public setClass(label: GestureClass) {
    this.currentClass = label;
  }

  public getClass(): GestureClass {
    return this.currentClass;
  }

  public toggleRecording(): boolean {
    this.isRecording = !this.isRecording;
    return this.isRecording;
  }

  public getIsRecording(): boolean {
    return this.isRecording;
  }

  public getSampleCount(): number {
    return this.samples.length;
  }

  public getClassCounts(): Record<GestureClass, number> {
    const counts: Record<GestureClass, number> = {
      CUT: 0,
      NORMAL_MOVEMENT: 0,
      STATIONARY: 0,
    };
    for (const s of this.samples) {
      if (counts[s.gesture_label] !== undefined) {
        counts[s.gesture_label]++;
      }
    }
    return counts;
  }

  /**
   * Process a validated frame from the existing HandTracker pipeline.
   */
  public recordFrame(validatedML: ValidatedHandData | undefined): GestureSampleRecord | null {
    if (!this.isRecording || !validatedML || !validatedML.valid || !validatedML.indexTip) {
      this.prevTipX = -1;
      this.prevTipY = -1;
      this.prevTime = 0;
      return null;
    }

    const now = validatedML.timestamp / 1000.0; // seconds
    const tip = validatedML.indexTip;

    let dx = 0.0;
    let dy = 0.0;
    let dist = 0.0;
    let speed = 0.0;
    let direction = 0.0;

    if (this.prevTipX >= 0 && this.prevTipY >= 0 && this.prevTime > 0) {
      const dt = Math.max(1e-4, now - this.prevTime);
      dx = tip.x - this.prevTipX;
      dy = tip.y - this.prevTipY;
      dist = Math.hypot(dx, dy);
      speed = dist / dt;
      direction = (Math.atan2(dy, dx) * 180.0) / Math.PI;
    }

    this.prevTipX = tip.x;
    this.prevTipY = tip.y;
    this.prevTime = now;

    const record: any = {
      sample_id: `${this.sessionId}_${this.samples.length + 1}`,
      session_id: this.sessionId,
      participant_id: this.participantId,
      timestamp: Number(now.toFixed(5)),
      platform: 'web',
      gesture_label: this.currentClass,
    };

    for (const lm of validatedML.landmarks) {
      record[`x${lm.id}`] = lm.x;
      record[`y${lm.id}`] = lm.y;
      record[`z${lm.id}`] = lm.z;
    }

    record.fingertip_x = tip.x;
    record.fingertip_y = tip.y;
    record.fingertip_z = tip.z;
    record.displacement_x = Number(dx.toFixed(5));
    record.displacement_y = Number(dy.toFixed(5));
    record.movement_distance = Number(dist.toFixed(5));
    record.movement_speed = Number(speed.toFixed(5));
    record.movement_direction = Number(direction.toFixed(2));

    this.samples.push(record as GestureSampleRecord);
    return record as GestureSampleRecord;
  }

  /**
   * Export collected samples as a CSV formatted string.
   */
  public toCSV(): string {
    if (this.samples.length === 0) return '';

    const headers: string[] = [
      'sample_id',
      'session_id',
      'participant_id',
      'timestamp',
      'platform',
      'gesture_label',
    ];

    for (let i = 0; i < 21; i++) {
      headers.push(`x${i}`, `y${i}`, `z${i}`);
    }

    headers.push(
      'fingertip_x',
      'fingertip_y',
      'fingertip_z',
      'displacement_x',
      'displacement_y',
      'movement_distance',
      'movement_speed',
      'movement_direction'
    );

    const rows: string[] = [headers.join(',')];

    for (const s of this.samples) {
      const row = headers.map((h) => (s as any)[h] ?? '');
      rows.push(row.join(','));
    }

    return rows.join('\n');
  }

  public clearBuffer() {
    this.samples = [];
  }
}
