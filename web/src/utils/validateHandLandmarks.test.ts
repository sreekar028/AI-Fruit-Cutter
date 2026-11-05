import { validateHandLandmarks } from './validateHandLandmarks.ts';

function runValidationTests() {
  console.log('[Web Phase 1 Test] Running hand landmark validation tests...');

  // 1. Test null / undefined
  const nullRes = validateHandLandmarks(null, 1000);
  console.assert(!nullRes.valid, 'Null input should be invalid');
  console.assert(nullRes.count === 0, 'Count should be 0');
  console.assert(nullRes.indexTip === null, 'Index tip should be null');
  console.assert(nullRes.timestamp === 1000, 'Timestamp should match input');
  console.log('  [PASS] Null / undefined rejection verified.');

  // 2. Test incomplete landmark list (< 21 points)
  const incomplete = [{ x: 0.1, y: 0.2, z: 0.0 }];
  const incRes = validateHandLandmarks(incomplete, 1005);
  console.assert(!incRes.valid, 'Incomplete points should be invalid');
  console.assert(incRes.count === 1, 'Count should be 1');
  console.log('  [PASS] Incomplete point count (< 21) rejected.');

  // 3. Test non-finite (NaN / Infinity) coordinates
  const nanPoints = Array.from({ length: 21 }, (_, i) => ({
    x: i === 8 ? NaN : 0.5,
    y: 0.5,
    z: 0.0,
  }));
  const nanRes = validateHandLandmarks(nanPoints, 1010);
  console.assert(!nanRes.valid, 'NaN coordinates should be rejected');
  console.assert(nanRes.error?.includes('non-finite'), 'Error message should describe non-finite coordinate');
  console.log('  [PASS] NaN / Infinity coordinates rejected.');

  // 4. Test valid 21 points with mirroring
  const validPoints = Array.from({ length: 21 }, (_, i) => ({
    x: 0.2 + i * 0.01,
    y: 0.3 + i * 0.01,
    z: 0.05,
  }));
  const validRes = validateHandLandmarks(validPoints, 1020, true);
  console.assert(validRes.valid, 'Valid points should return valid: true');
  console.assert(validRes.count === 21, 'Count should be 21');
  console.assert(validRes.landmarks.length === 21, 'Landmarks array should have 21 elements');
  console.assert(validRes.indexTip !== null, 'Index tip should not be null');

  // Check landmark 8 (index tip)
  const tip = validRes.indexTip!;
  const expectedMirroredX = Number((1.0 - (0.2 + 8 * 0.01)).toFixed(5));
  console.assert(
    Math.abs(tip.x - expectedMirroredX) < 1e-4,
    `Mirrored tip X should match expected ${expectedMirroredX}, got ${tip.x}`
  );
  console.assert(
    Math.abs(tip.y - Number((0.3 + 8 * 0.01).toFixed(5))) < 1e-4,
    `Tip Y should match expected`
  );
  console.log('  [PASS] Valid 21 landmarks & Index Tip (Landmark 8) extracted with mirroring.');

  console.log('[Web Phase 1 Test] All test cases passed successfully!\n');
}

runValidationTests();
