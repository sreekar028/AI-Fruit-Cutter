/**
 * web/src/game/GameState.ts
 * =========================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Finite State Machine managing:
 * - START (Home screen)
 * - PLAYING (Active gameplay)
 * - PAUSED (Temporary pause)
 * - GAME_OVER (Results screen)
 * 
 * Strictly preserves keyboard controls:
 * - SPACE: Start / Play Again
 * - R: Restart
 * - P: Pause / Resume
 * - Q / ESC: Quit
 */

export const GameState = {
  START: 'START',
  PLAYING: 'PLAYING',
  PAUSED: 'PAUSED',
  GAME_OVER: 'GAME_OVER',
} as const;

export type GameState = typeof GameState[keyof typeof GameState];

export class GameStateManager {
  public state: GameState;

  constructor(initialState: GameState = GameState.START) {
    this.state = initialState;
  }

  public get isStart(): boolean {
    return this.state === GameState.START;
  }

  public get isPlaying(): boolean {
    return this.state === GameState.PLAYING;
  }

  public get isPaused(): boolean {
    return this.state === GameState.PAUSED;
  }

  public get isGameOver(): boolean {
    return this.state === GameState.GAME_OVER;
  }

  public startGame() {
    this.state = GameState.PLAYING;
  }

  public triggerGameOver() {
    this.state = GameState.GAME_OVER;
  }

  public restartGame() {
    this.state = GameState.PLAYING;
  }

  public togglePause() {
    if (this.state === GameState.PLAYING) {
      this.state = GameState.PAUSED;
    } else if (this.state === GameState.PAUSED) {
      this.state = GameState.PLAYING;
    }
  }

  public handleKey(key: string): 'quit' | 'start' | 'restart' | 'pause' | '' {
    const k = key.toLowerCase();

    if (k === 'q' || key === 'Escape') {
      return 'quit';
    }

    if (key === ' ' || key === 'Space') {
      if (this.isStart) {
        this.startGame();
        return 'start';
      }
      if (this.isGameOver) {
        this.restartGame();
        return 'restart';
      }
    }

    if (k === 'r') {
      this.restartGame();
      return 'restart';
    }

    if (k === 'p') {
      this.togglePause();
      return 'pause';
    }

    return '';
  }
}
