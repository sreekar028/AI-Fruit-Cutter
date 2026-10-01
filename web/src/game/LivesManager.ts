/**
 * web/src/game/LivesManager.ts
 * ============================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's LivesManager:
 * - 3 strikes / lives system
 * - Fruit dropped off-screen deducts 1 life
 * - Bomb cut penalty deducts 1 life
 * - Triggers Game Over when lives reach 0
 */

export class LivesManager {
  public maxLives: number;
  public bombPenaltyLives: number;
  public lives: number;
  public missedFruitsTotal = 0;
  public bombsCutTotal = 0;

  constructor(maxLives = 3, bombPenaltyLives = 1) {
    this.maxLives = maxLives;
    this.bombPenaltyLives = bombPenaltyLives;
    this.lives = maxLives;
  }

  public get isDead(): boolean {
    return this.lives <= 0;
  }

  public onFruitMissed(): boolean {
    if (this.lives > 0) {
      this.lives -= 1;
      this.missedFruitsTotal += 1;
    }
    return this.isDead;
  }

  public onBombCut(): boolean {
    this.lives = Math.max(0, this.lives - this.bombPenaltyLives);
    this.bombsCutTotal += 1;
    return this.isDead;
  }

  public reset() {
    this.lives = this.maxLives;
    this.missedFruitsTotal = 0;
    this.bombsCutTotal = 0;
  }
}
