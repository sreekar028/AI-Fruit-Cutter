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
  private startPromise: Promise<CameraInitResult> | null = null;
  private startGeneration = 0;

  public onDisconnect?: () => void;
  public onError?: (message: string) => void;

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;
    this.tracker = new HandTracker(width, height);
    this.detector = new MotionDetector();
  }

  public start(videoElement: HTMLVideoElement): Promise<CameraInitResult> {
    if (this.isRunning) return Promise.resolve({ success: true });
    if (this.startPromise) return this.startPromise;

    const generation = ++this.startGeneration;
    const attempt = this.initializeCamera(videoElement, generation);
    this.startPromise = attempt;
    return attempt.finally(() => {
      if (this.startPromise === attempt) this.startPromise = null;
    });
  }

  private async initializeCamera(
    videoElement: HTMLVideoElement,
    generation: number
  ): Promise<CameraInitResult> {
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

      if (generation !== this.startGeneration) {
        this.stream.getTracks().forEach((track) => track.stop());
        this.stream = null;
        return { success: false, error: 'Camera setup was cancelled.' };
      }

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
      await this.waitForVideoReady(this.video);

      if (generation !== this.startGeneration) {
        this.stop();
        return { success: false, error: 'Camera setup was cancelled.' };
      }

      const modelReady = await this.tracker.initialize();
      if (!modelReady) {
        const detail = this.tracker.initializationFailure;
        this.stop();
        return {
          success: false,
          error: detail
            ? `MediaPipe initialization failed: ${detail}`
            : 'MediaPipe could not initialize. Check access to its model and WASM resources.',
        };
      }

      if (generation !== this.startGeneration) {
        this.stop();
        return { success: false, error: 'Camera setup was cancelled.' };
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

      if (generation === this.startGeneration) this.stop();
      return { success: false, error: errorMsg };
    }
  }

  private waitForVideoReady(video: HTMLVideoElement): Promise<void> {
    const hasFrame = () =>
      video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA &&
      video.videoWidth > 0 &&
      video.videoHeight > 0;

    if (hasFrame()) return Promise.resolve();

    return new Promise((resolve, reject) => {
      const cleanup = () => {
        window.clearTimeout(timeoutId);
        video.removeEventListener('loadeddata', checkReady);
        video.removeEventListener('loadedmetadata', checkReady);
        video.removeEventListener('error', handleError);
      };
      const checkReady = () => {
        if (!hasFrame()) return;
        cleanup();
        resolve();
      };
      const handleError = () => {
        cleanup();
        reject(new Error('The webcam opened but did not provide video frames.'));
      };
      const timeoutId = window.setTimeout(() => {
        cleanup();
        reject(new Error('Timed out waiting for webcam video to become ready.'));
      }, 10000);

      video.addEventListener('loadeddata', checkReady);
      video.addEventListener('loadedmetadata', checkReady);
      video.addEventListener('error', handleError, { once: true });
      checkReady();
    });
  }

  public setDimensions(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.tracker.setDimensions(width, height);
  }

  public tick(timestampMs: number): { motionData: MotionData; trackingData: TrackingData } {
    if (
      !this.isRunning ||
      !this.video ||
      this.video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA ||
      this.video.videoWidth === 0 ||
      this.video.videoHeight === 0
    ) {
      const emptyTracking = this.emptyTrackingData();
      const motionData = this.detector.update(emptyTracking);
      return { motionData, trackingData: emptyTracking };
    }

    try {
      const trackingData = this.tracker.getTrackingData(this.video, timestampMs);
      const motionData = this.detector.update(trackingData);

      return { motionData, trackingData };
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      console.error('[AIController] Hand detection stopped:', error);
      this.stop();
      const emptyTracking = this.emptyTrackingData();
      const motionData = this.detector.update(emptyTracking);
      this.onError?.(`Hand detection stopped: ${detail}`);
      return { motionData, trackingData: emptyTracking };
    }
  }

  private emptyTrackingData(): TrackingData {
    return {
      handDetected: false,
      fingerX: -1,
      fingerY: -1,
      landmarks: [],
      rawLandmarks: null,
    };
  }

  public drawLandmarks(ctx: CanvasRenderingContext2D, trackingData: TrackingData) {
    this.tracker.drawLandmarks(ctx, trackingData);
  }

  public resetTrajectory() {
    this.detector.reset();
  }

  public stop() {
    this.startGeneration += 1;
    this.isRunning = false;
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    if (this.video) {
      this.video.pause();
      this.video.srcObject = null;
    }
    this.tracker.release();
    this.detector.reset();
  }

  public get running(): boolean {
    return this.isRunning;
  }
}
