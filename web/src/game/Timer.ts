/**
 * web/src/game/Timer.ts
 * =====================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's GameTimer:
 * - Survival elapsed clock (counts up)
 * - Optional countdown timer (counts down)
 * - Pause & resume duration tracking
 * - Formatted MM:SS output
 */

export class GameTimer {
  public countdownDuration: number | null;

  private startTime = 0;
  private pauseTime = 0;
  private totalPausedDuration = 0;
  private isRunningState = false;
  private isPausedState = false;

  constructor(countdownDuration: number | null = null) {
    this.countdownDuration = countdownDuration;
  }

  public start() {
    this.startTime = performance.now() / 1000.0;
    this.pauseTime = 0;
    this.totalPausedDuration = 0;
    this.isRunningState = true;
    this.isPausedState = false;
  }

  public pause() {
    if (this.isRunningState && !this.isPausedState) {
      this.pauseTime = performance.now() / 1000.0;
      this.isPausedState = true;
    }
  }

  public resume() {
    if (this.isRunningState && this.isPausedState) {
      this.totalPausedDuration += performance.now() / 1000.0 - this.pauseTime;
      this.isPausedState = false;
    }
  }

  public reset() {
    this.startTime = 0;
    this.pauseTime = 0;
    this.totalPausedDuration = 0;
    this.isRunningState = false;
    this.isPausedState = false;
  }

  public get isRunning(): boolean {
    return this.isRunningState && !this.isPausedState;
  }

  public get elapsedSeconds(): number {
    if (!this.isRunningState) return 0;
    const current = this.isPausedState
      ? this.pauseTime
      : performance.now() / 1000.0;
    return Math.max(0, current - this.startTime - this.totalPausedDuration);
  }

  public get remainingSeconds(): number {
    if (this.countdownDuration === null) return 0;
    return Math.max(0, this.countdownDuration - this.elapsedSeconds);
  }

  public get isTimeUp(): boolean {
    if (this.countdownDuration === null) return false;
    return this.isRunningState && this.elapsedSeconds >= this.countdownDuration;
  }

  public getFormattedTime(): string {
    const totalSec =
      this.countdownDuration !== null
        ? Math.floor(this.remainingSeconds)
        : Math.floor(this.elapsedSeconds);

    const minutes = Math.floor(totalSec / 60);
    const seconds = totalSec % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
}
