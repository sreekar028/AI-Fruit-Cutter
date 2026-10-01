/**
 * web/src/game/ScoreManager.ts
 * ============================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's ScoreManager:
 * - Base points per fruit type
 * - Multi-fruit combos with 0.50s decay timer
 * - High score tracking (persisted via localStorage in web)
 * - Bomb hit combo reset
 */

import { Fruit } from './Fruit';

export interface SliceResult {
  totalAwarded: number;
  comboCount: number;
  bonus: number;
  comboText: string;
}

export class ScoreManager {
  public score = 0;
  public highScore = 0;
  public fruitsSlicedTotal = 0;
  public combosAchievedTotal = 0;
  public currentCombo = 0;
  public lastComboText = '';

  private comboWindowSec: number;
  private lastSliceTime = 0;

  constructor(comboWindowSec = 0.50) {
    this.comboWindowSec = comboWindowSec;
    // Load high score from browser storage
    try {
      const saved = localStorage.getItem('ai_fruit_cutter_highscore');
      if (saved) this.highScore = parseInt(saved, 10) || 0;
    } catch {
      this.highScore = 0;
    }
  }

  public update(currentTimeSec: number) {
    if (this.currentCombo > 0) {
      if (currentTimeSec - this.lastSliceTime > this.comboWindowSec) {
        this.currentCombo = 0;
      }
    }
  }

  public registerSlice(fruit: Fruit, currentTimeSec: number): SliceResult {
    if (fruit.isBomb) {
      this.currentCombo = 0;
      this.lastComboText = '';
      return { totalAwarded: 0, comboCount: 0, bonus: 0, comboText: '' };
    }

    if (currentTimeSec - this.lastSliceTime <= this.comboWindowSec) {
      this.currentCombo += 1;
    } else {
      this.currentCombo = 1;
    }

    this.lastSliceTime = currentTimeSec;
    this.fruitsSlicedTotal += 1;

    const basePoints = fruit.points;
    let bonus = 0;

    if (this.currentCombo === 2) {
      bonus = 5;
      this.lastComboText = 'COMBO 2x! +5';
      this.combosAchievedTotal += 1;
    } else if (this.currentCombo === 3) {
      bonus = 10;
      this.lastComboText = 'COMBO 3x! +10';
      this.combosAchievedTotal += 1;
    } else if (this.currentCombo >= 4) {
      bonus = 20;
      this.lastComboText = `SUPER COMBO ${this.currentCombo}x! +20`;
      this.combosAchievedTotal += 1;
    } else {
      this.lastComboText = '';
    }

    const totalAwarded = basePoints + bonus;
    this.score += totalAwarded;

    if (this.score > this.highScore) {
      this.highScore = this.score;
      try {
        localStorage.setItem('ai_fruit_cutter_highscore', this.highScore.toString());
      } catch {
        // Ignore localStorage restrictions
      }
    }

    return {
      totalAwarded,
      comboCount: this.currentCombo,
      bonus,
      comboText: this.lastComboText,
    };
  }

  public reset() {
    this.score = 0;
    this.currentCombo = 0;
    this.fruitsSlicedTotal = 0;
    this.combosAchievedTotal = 0;
    this.lastSliceTime = 0;
    this.lastComboText = '';
  }
}
