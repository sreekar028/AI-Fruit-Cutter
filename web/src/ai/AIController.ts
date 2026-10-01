/**
 * web/src/ai/AIController.ts
 * ==========================
 * AI Module Façade — Web Version (Member 1 equivalent)
 * 
 * Replicates Member 1's AIController:
 * - Accesses browser webcam via navigator.mediaDevices.getUserMedia
 * - Handles camera permissions, errors, and disconnections gracefully
 * - Coordinates HandTracker (MediaPipe) and MotionDetector
 * - Provides frame-by-frame tick() method for GameEngine
 */

import { HandTracker, type TrackingData } from './HandTracker';
import { MotionDetector, type MotionData } from './MotionDetector';

export interface CameraInitResult {
  success: boolean;
  error?: string;
}

export class AIController {
  private video: HTMLVideoElement | null = null;
  private stream: MediaStream | null = null;
  private tracker: HandTracker;
  private detector: MotionDetector;

  private isRunning = false;
  private width = 640;
  private height = 480;

  public onDisconnect?: () => void;

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;
    this.tracker = new HandTracker(width, height);
    this.detector = new MotionDetector();
  }

  public async start(videoElement: HTMLVideoElement): Promise<CameraInitResult> {
    this.video = videoElement;

    // Check if getUserMedia is supported in browser
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return {
        success: false,
        error: 'Camera access (getUserMedia) is not supported in this browser.',
      };
    }

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

      // Handle mid-game camera disconnection
      const videoTrack = this.stream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.onended = () => {
          console.warn('[AIController] Webcam stream disconnected.');
          this.isRunning = false;
          if (this.onDisconnect) this.onDisconnect();
        };
      }

      await this.video.play();

      const modelReady = await this.tracker.initialize();
      if (!modelReady) {
        return {
          success: false,
          error: 'Failed to initialize MediaPipe Hand Landmarker model.',
        };
      }

      this.isRunning = true;
      return { success: true };
    } catch (err: any) {
      console.error('[AIController] Camera initialization error:', err);
      let errorMsg = 'Could not access camera.';

      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMsg = 'Camera permission was denied. Please allow camera access in your browser settings to play.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMsg = 'No camera device found on this computer. Touch/mouse slicing is available.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMsg = 'Camera is currently in use by another application. Please close other camera apps.';
      } else if (err.message) {
        errorMsg = err.message;
      }

      this.isRunning = false;
      return { success: false, error: errorMsg };
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
