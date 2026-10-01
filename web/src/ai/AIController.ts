/**
 * web/src/ai/AIController.ts
 * ==========================
 * AI Module Façade — Web Version (Member 1 equivalent)
 * 
 * Replicates Member 1's AIController:
 * - Accesses browser webcam via navigator.mediaDevices.getUserMedia
 * - Coordinates HandTracker (MediaPipe) and MotionDetector
 * - Provides frame-by-frame tick() method for GameEngine
 */

import { HandTracker, type TrackingData } from './HandTracker';
import { MotionDetector, type MotionData } from './MotionDetector';

export class AIController {
  private video: HTMLVideoElement | null = null;
  private stream: MediaStream | null = null;
  private tracker: HandTracker;
  private detector: MotionDetector;

  private isRunning = false;
  private width = 640;
  private height = 480;

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;
    this.tracker = new HandTracker(width, height);
    this.detector = new MotionDetector();
  }

  public async start(videoElement: HTMLVideoElement): Promise<boolean> {
    this.video = videoElement;
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: this.width },
          height: { ideal: this.height },
          facingMode: 'user',
        },
        audio: false,
      });

      this.video.srcObject = this.stream;
      this.video.setAttribute('playsinline', 'true');
      this.video.muted = true;
      await this.video.play();

      await this.tracker.initialize();
      this.isRunning = true;
      return true;
    } catch (err) {
      console.error('[AIController] Error accessing webcam:', err);
      this.isRunning = false;
      return false;
    }
  }

  public setDimensions(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.tracker.setDimensions(width, height);
  }

  public tick(timestampMs: number): { motionData: MotionData; trackingData: TrackingData } {
    if (!this.isRunning || !this.video || this.video.readyState < 2) {
      const emptyTracking: TrackingData = {
        handDetected: false,
        fingerX: -1,
        fingerY: -1,
        landmarks: [],
        rawLandmarks: null,
      };
      const motionData = this.detector.update(emptyTracking);
      return { motionData, trackingData: emptyTracking };
    }

    const trackingData = this.tracker.getTrackingData(this.video, timestampMs);
    const motionData = this.detector.update(trackingData);

    return { motionData, trackingData };
  }

  public drawLandmarks(ctx: CanvasRenderingContext2D, trackingData: TrackingData) {
    this.tracker.drawLandmarks(ctx, trackingData);
  }

  public resetTrajectory() {
    this.detector.reset();
  }

  public stop() {
    this.isRunning = false;
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    if (this.video) {
      this.video.srcObject = null;
    }
    this.tracker.release();
  }

  public get running(): boolean {
    return this.isRunning;
  }
}
