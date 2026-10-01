/**
 * web/src/ai/HandTracker.ts
 * =========================
 * AI / Hand Tracking Module — Web Version (Member 1 equivalent)
 * 
 * Uses Google MediaPipe Tasks Vision (HandLandmarker) to track 21 hand landmarks
 * from a browser HTMLVideoElement in real time using WebGL/WASM acceleration.
 * Extracts index fingertip (Landmark 8) in pixel coordinates.
 */

import { FilesetResolver, HandLandmarker } from '@mediapipe/tasks-vision';

export interface HandLandmark {
  x: number;
  y: number;
  z?: number;
}

export interface TrackingData {
  handDetected: boolean;
  fingerX: number;
  fingerY: number;
  landmarks: HandLandmark[];
  rawLandmarks: any;
}

export class HandTracker {
  private handLandmarker: HandLandmarker | null = null;
  private isLoaded = false;
  private isLoading = false;
  private width = 640;
  private height = 480;

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;
  }

  public setDimensions(width: number, height: number) {
    this.width = width;
    this.height = height;
  }

  public async initialize(): Promise<boolean> {
    if (this.isLoaded) return true;
    if (this.isLoading) return false;

    this.isLoading = true;
    try {
      // Load MediaPipe WASM binaries from Google CDN
      const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      );

      this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
          delegate: 'GPU',
        },
        runningMode: 'VIDEO',
        numHands: 1,
        minHandDetectionConfidence: 0.65,
        minHandPresenceConfidence: 0.6,
        minTrackingConfidence: 0.6,
      });

      this.isLoaded = true;
      this.isLoading = false;
      return true;
    } catch (err) {
      console.warn('[HandTracker] Failed to load GPU delegate, trying CPU fallback...', err);
      try {
        const vision = await FilesetResolver.forVisionTasks(
          'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
        );
        this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
            delegate: 'CPU',
          },
          runningMode: 'VIDEO',
          numHands: 1,
          minHandDetectionConfidence: 0.6,
          minTrackingConfidence: 0.6,
        });
        this.isLoaded = true;
        this.isLoading = false;
        return true;
      } catch (fallbackErr) {
        console.error('[HandTracker] Failed to initialize HandLandmarker:', fallbackErr);
        this.isLoading = false;
        return false;
      }
    }
  }

  public getTrackingData(video: HTMLVideoElement, timestampMs: number): TrackingData {
    if (!this.isLoaded || !this.handLandmarker || video.readyState < 2) {
      return this.emptyData();
    }

    try {
      const results = this.handLandmarker.detectForVideo(video, timestampMs);

      if (!results.landmarks || results.landmarks.length === 0) {
        return this.emptyData();
      }

      // First hand detected
      const hand = results.landmarks[0];

      // Convert normalized [0, 1] to mirrored pixel coordinates
      // Index 8 = INDEX_FINGER_TIP
      // Since video is mirrored for natural interaction, x is (1.0 - lm.x)
      const landmarksPx: HandLandmark[] = hand.map((lm) => ({
        x: Math.round((1.0 - lm.x) * this.width),
        y: Math.round(lm.y * this.height),
        z: lm.z,
      }));

      const indexTip = landmarksPx[8];

      return {
        handDetected: true,
        fingerX: indexTip ? indexTip.x : -1,
        fingerY: indexTip ? indexTip.y : -1,
        landmarks: landmarksPx,
        rawLandmarks: hand,
      };
    } catch {
      return this.emptyData();
    }
  }

  public drawLandmarks(ctx: CanvasRenderingContext2D, data: TrackingData) {
    if (!data.handDetected || data.landmarks.length < 21) return;

    // Draw hand connections
    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4],       // Thumb
      [0, 5], [5, 6], [6, 7], [7, 8],       // Index
      [0, 9], [9, 10], [10, 11], [11, 12],  // Middle
      [0, 13], [13, 14], [14, 15], [15, 16],// Ring
      [0, 17], [17, 18], [18, 19], [19, 20],// Pinky
      [5, 9], [9, 13], [13, 17],             // Palm
    ];

    ctx.save();
    ctx.strokeStyle = 'rgba(0, 230, 255, 0.4)';
    ctx.lineWidth = 2;

    for (const [i, j] of connections) {
      const p1 = data.landmarks[i];
      const p2 = data.landmarks[j];
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
    }

    // Draw small landmark dots
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    for (const lm of data.landmarks) {
      ctx.beginPath();
      ctx.arc(lm.x, lm.y, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    // Highlight Index Fingertip (Landmark 8) with green halo
    ctx.fillStyle = '#00FF66';
    ctx.beginPath();
    ctx.arc(data.fingerX, data.fingerY, 8, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(data.fingerX, data.fingerY, 12, 0, Math.PI * 2);
    ctx.stroke();

    ctx.restore();
  }

  private emptyData(): TrackingData {
    return {
      handDetected: false,
      fingerX: -1,
      fingerY: -1,
      landmarks: [],
      rawLandmarks: null,
    };
  }

  public release() {
    if (this.handLandmarker) {
      this.handLandmarker.close();
      this.handLandmarker = null;
      this.isLoaded = false;
    }
  }
}
