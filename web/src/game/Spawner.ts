/**
 * web/src/game/Spawner.ts
 * =======================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's FruitSpawner:
 * - Spawns periodic waves of fruits and bombs
 * - Upward launch physics in parabolic arcs
 * - Difficulty scaling: spawn interval tightens as score rises
 * - Bomb hazard probabilities (active after score >= 20)
 */

import { Fruit, FRUIT_TYPES } from './Fruit';
import { type DifficultyConfig, getDifficultyConfig } from './Difficulty';

export class FruitSpawner {
  public boundsWidth: number;
  public boundsHeight: number;
  public baseInterval: number;
  public minInterval: number;
  public bombChance: number;
  public difficulty: DifficultyConfig;

  private lastSpawnTime = 0;
  private currentInterval: number;
  private activeFruits: Fruit[] = [];
  private edibleTypes: string[];

  constructor(
    boundsWidth = 640,
    boundsHeight = 480,
    difficulty: DifficultyConfig = getDifficultyConfig('medium')
  ) {
    this.boundsWidth = boundsWidth;
    this.boundsHeight = boundsHeight;
    this.difficulty = difficulty;
    this.baseInterval = difficulty.spawnInterval;
    this.minInterval = difficulty.minInterval;
    this.bombChance = difficulty.bombChance;
    this.currentInterval = difficulty.spawnInterval;

    this.edibleTypes = Object.keys(FRUIT_TYPES).filter((t) => t !== 'bomb');
  }

  public setDimensions(width: number, height: number) {
    this.boundsWidth = width;
    this.boundsHeight = height;
  }

  public setDifficulty(difficulty: DifficultyConfig) {
    this.difficulty = difficulty;
    this.baseInterval = difficulty.spawnInterval;
    this.minInterval = difficulty.minInterval;
    this.bombChance = difficulty.bombChance;
    this.currentInterval = difficulty.spawnInterval;
  }

  public update(currentTimeSec: number, currentScore: number): Fruit[] {
    // Difficulty scaling
    const scoreFactor = Math.min(currentScore / 200.0, 1.0);
    this.currentInterval = Math.max(
      this.minInterval,
      this.baseInterval - scoreFactor * 0.8
    );

    let newlySpawned: Fruit[] = [];

    if (currentTimeSec - this.lastSpawnTime >= this.currentInterval) {
      this.lastSpawnTime = currentTimeSec;
      newlySpawned = this.spawnWave(currentScore);
      this.activeFruits.push(...newlySpawned);
    }

    // Update active fruits
    for (const fruit of this.activeFruits) {
      fruit.update(this.boundsWidth, this.boundsHeight);
    }

    // Clean up off-screen removed fruits
    this.activeFruits = this.activeFruits.filter(
      (f) =>
        !(
          f.state === 'removed' ||
          (f.state === 'missed' && f.y > this.boundsHeight + 60)
        )
    );

    return newlySpawned;
  }

  public getActiveFruits(): Fruit[] {
    return this.activeFruits.filter((f) => f.isActive);
  }

  public getAllFruits(): Fruit[] {
    return this.activeFruits;
  }

  public reset() {
    this.lastSpawnTime = performance.now() / 1000.0;
    this.currentInterval = this.baseInterval;
    this.activeFruits = [];
  }

  private spawnWave(currentScore: number): Fruit[] {
    let count = 1;
    if (currentScore < 30) {
      count = Math.random() < 0.65 ? 1 : 2;
    } else if (currentScore < 80) {
      count = Math.floor(Math.random() * 3) + 1;
    } else {
      count = Math.random() < 0.4 ? 2 : 3;
    }

    count = Math.min(count, this.difficulty.maxConcurrentFruits);

    const wave: Fruit[] = [];
    let bombSpawned = false;

    const marginX = 90;
    const availableWidth = Math.max(100, this.boundsWidth - 2 * marginX);
    const slotWidth = availableWidth / Math.max(1, count);
    const speedMultiplier = this.difficulty.fruitSpeedMultiplier;

    for (let i = 0; i < count; i++) {
      const slotMin = marginX + Math.round(i * slotWidth);
      const slotMax = marginX + Math.round((i + 1) * slotWidth);
      const spawnX = slotMin + Math.random() * Math.max(1, slotMax - slotMin);
      const spawnY = this.boundsHeight + 35 + Math.random() * 30;

      const shouldSpawnBomb =
        !bombSpawned &&
        currentScore >= 20 &&
        Math.random() < this.bombChance;

      let fType: string;
      if (shouldSpawnBomb) {
        fType = 'bomb';
        bombSpawned = true;
      } else {
        const idx = Math.floor(Math.random() * this.edibleTypes.length);
        fType = this.edibleTypes[idx];
      }

      const vy = -(15.2 * speedMultiplier + Math.random() * 2.8 * speedMultiplier);
      const centerX = this.boundsWidth / 2.0;
      const distFromCenter = (centerX - spawnX) / (this.boundsWidth / 2.0);
      const vx =
        distFromCenter * (1.8 * speedMultiplier + Math.random() * 2.0 * speedMultiplier) +
        (Math.random() - 0.5);

      const fruit = new Fruit(fType, spawnX, spawnY, vx, vy, 0.38 * (1 + (speedMultiplier - 1) * 0.2));
      wave.push(fruit);
    }

    return wave;
  }
}
