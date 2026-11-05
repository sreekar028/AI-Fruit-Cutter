/**
 * web/src/utils/validateHandLandmarks.ts
 * =====================================
 * Phase 1 — Hand Landmark Validation Utility for Machine Learning Preparation
 * 
 * Validates raw MediaPipe hand landmarks and extracts normalized coordinates
 * formatted consistently with the Python ML pipeline.
 */

export interface NormalizedLandmark {
  id: number;
  x: number;
  y: number;
  z: number;
}

export interface IndexTipCoord {
  x: number;
  y: number;
  z: number;
}

export interface ValidatedHandData {
  valid: boolean;
  count: number;
  landmarks: NormalizedLandmark[];
  indexTip: IndexTipCoord | null;
  timestamp: number;
  error?: string;
}

/**
 * Validates a MediaPipe hand landmark array.
 * 
 * @param rawLandmarks Array of landmarks from MediaPipe (e.g. results.landmarks[0] or HandTracker rawLandmarks)
 * @param timestamp Optional timestamp in milliseconds (defaults to performance.now())
 * @param mirrorX Whether to mirror the normalized X coordinate (default true to match user-facing interaction)
 * @returns ValidatedHandData with 21 normalized landmarks, indexTip (landmark 8), count, validity and timestamp
 */
export function validateHandLandmarks(
  rawLandmarks: any[] | null | undefined,
  timestamp: number = performance.now(),
  mirrorX: boolean = true
): ValidatedHandData {
  const ts = Number.isFinite(timestamp) ? timestamp : performance.now();

  if (!rawLandmarks || !Array.isArray(rawLandmarks)) {
    return {
      valid: false,
      count: 0,
      landmarks: [],
      indexTip: null,
      timestamp: ts,
      error: 'No landmark data provided or landmark object is not an array.',
    };
  }

  const count = rawLandmarks.length;
  if (count !== 21) {
    return {
      valid: false,
      count,
      landmarks: [],
      indexTip: null,
      timestamp: ts,
      error: `Expected exactly 21 landmarks, received ${count}.`,
    };
  }

  const validatedLandmarks: NormalizedLandmark[] = [];

  for (let i = 0; i < count; i++) {
    const lm = rawLandmarks[i];
    if (!lm || typeof lm !== 'object') {
      return {
        valid: false,
        count,
        landmarks: [],
        indexTip: null,
        timestamp: ts,
        error: `Landmark at index ${i} is missing or not an object.`,
      };
    }

    const rawX = typeof lm.x === 'number' ? lm.x : Number(lm.x);
    const rawY = typeof lm.y === 'number' ? lm.y : Number(lm.y);
    const rawZ = typeof lm.z === 'number' ? lm.z : (lm.z !== undefined ? Number(lm.z) : 0.0);

    if (!Number.isFinite(rawX) || !Number.isFinite(rawY) || !Number.isFinite(rawZ)) {
      return {
        valid: false,
        count,
        landmarks: [],
        indexTip: null,
        timestamp: ts,
        error: `Landmark at index ${i} contains non-finite coordinates (x=${rawX}, y=${rawY}, z=${rawZ}).`,
      };
    }

    // Mirror normalized X for user-facing camera perspective if requested
    const finalX = mirrorX ? 1.0 - rawX : rawX;

    validatedLandmarks.push({
      id: i,
      x: Number(finalX.toFixed(5)),
      y: Number(rawY.toFixed(5)),
      z: Number(rawZ.toFixed(5)),
    });
  }

  const tip = validatedLandmarks[8]; // Landmark 8 is INDEX_FINGER_TIP
  const indexTip: IndexTipCoord = {
    x: tip.x,
    y: tip.y,
    z: tip.z,
  };

  return {
    valid: true,
    count: 21,
    landmarks: validatedLandmarks,
    indexTip,
    timestamp: ts,
  };
}
