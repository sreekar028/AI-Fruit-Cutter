/**
 * web/src/game/GameEngine.ts
 * ==========================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Master coordinator uniting:
 * - AIController (Member 1 MediaPipe webcam tracking)
 * - FruitSpawner (wave-based parabolic arc fruit launches)
 * - CollisionDetector (continuous segment-to-circle testing)
 * - ScoreManager (fruit scores & combos)
 * - LivesManager (3 strikes)
 * - GameTimer (stopwatch & countdown)
 * - GameStateManager (FSM state machine)
 * - EffectsManager (particles, floating text, blade glow)
 * - HTML5 Canvas rendering pipeline
 */

import { AIController } from '../ai/AIController';
import { FruitSpawner } from './Spawner';
import { CollisionDetector } from './Collision';
import { ScoreManager } from './ScoreManager';
import { LivesManager } from './LivesManager';
import { GameTimer } from './Timer';
import { GameState, GameStateManager } from './GameState';
import { EffectsManager } from './Effects';

export interface GameStatus {
  state: GameState;
  score: number;
  highScore: number;
  lives: number;
  timeStr: string;
  combo: number;
  fps: number;
  handDetected: boolean;
  fingerX: number;
  fingerY: number;
}

export class GameEngine {
  public width: number;
  public height: number;

  public ai: AIController;
  public spawner: FruitSpawner;
  public collision: CollisionDetector;
  public scoreMgr: ScoreManager;
  public livesMgr: LivesManager;
  public timer: GameTimer;
  public stateMgr: GameStateManager;
  public effects: EffectsManager;

  private fps = 60;
  private lastTime = 0;
  private _isRunning = false;

  public get isRunning(): boolean {
    return this._isRunning;
  }

  constructor(width = 640, height = 480) {
    this.width = width;
    this.height = height;

    this.ai = new AIController(width, height);
    this.spawner = new FruitSpawner(width, height);
    this.collision = new CollisionDetector(14.0);
    this.scoreMgr = new ScoreManager(0.50);
    this.livesMgr = new LivesManager(3, 1);
    this.timer = new GameTimer();
    this.stateMgr = new GameStateManager(GameState.START);
    this.effects = new EffectsManager();
  }

  public setDimensions(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.ai.setDimensions(width, height);
    this.spawner.setDimensions(width, height);
  }

  public async startWebcam(videoElement: HTMLVideoElement): Promise<{ success: boolean; error?: string }> {
    const res = await this.ai.start(videoElement);
    this._isRunning = res.success;
    return res;
  }

  public stop() {
    this._isRunning = false;
    this.ai.stop();
  }

  public restartGame() {
    this.spawner.reset();
    this.scoreMgr.reset();
    this.livesMgr.reset();
    this.timer.start();
    this.effects.reset();
    this.ai.resetTrajectory();
    this.stateMgr.restartGame();
  }

  public update(
    timestampMs: number,
    aiFrame = this.ai.tick(timestampMs)
  ): GameStatus {
    const nowSec = timestampMs / 1000.0;
    const dt = this.lastTime > 0 ? (timestampMs - this.lastTime) / 1000.0 : 0.016;
    this.lastTime = timestampMs;
    this.fps = dt > 0 ? Math.round(1.0 / dt) : 60;

    // 1. AI Tracking
    const { motionData } = aiFrame;

    // 2. Game Logic (only when in PLAYING state)
    if (this.stateMgr.isPlaying) {
      if (this.timer.isTimeUp) {
        this.stateMgr.triggerGameOver();
      }

      this.scoreMgr.update(nowSec);
      this.spawner.update(nowSec, this.scoreMgr.score);

      // Check missed fruits (dropped below screen)
      for (const fruit of this.spawner.getAllFruits()) {
        if (fruit.state === 'missed') {
          fruit.state = 'removed';
          if (!fruit.isBomb) {
            this.effects.spawnFloatingText('MISS!', fruit.x, this.height - 40, '#FF3333', 18);
            const dead = this.livesMgr.onFruitMissed();
            if (dead) {
              this.stateMgr.triggerGameOver();
            }
          }
        }
      }

      // Check slicing collisions
      const active = this.spawner.getActiveFruits();
      const sliced = this.collision.checkCollisions(motionData, active);

      for (const fruit of sliced) {
        if (fruit.isBomb) {
          // Detonate bomb
          this.effects.spawnBombExplosion(fruit.x, fruit.y);
          this.effects.spawnFloatingText('BOMB! -1 LIFE', fruit.x, fruit.y - 20, '#FF2222', 24);
          this.scoreMgr.registerSlice(fruit, nowSec);
          const dead = this.livesMgr.onBombCut();
          if (dead) {
            this.stateMgr.triggerGameOver();
          }
        } else {
          // Fruit sliced
          const result = this.scoreMgr.registerSlice(fruit, nowSec);
          this.effects.spawnFruitSplash(fruit.x, fruit.y, fruit.colorSplash);

          if (result.comboCount >= 2) {
            this.effects.spawnFloatingText(
              `COMBO ${result.comboCount}x! +${result.totalAwarded}`,
              fruit.x,
              fruit.y - 20,
              '#FFD700',
              24
            );
          } else {
            this.effects.spawnFloatingText(`+${result.totalAwarded}`, fruit.x, fruit.y - 20, '#00FF66', 20);
          }
        }
      }

      this.effects.update(dt);
    }

    return {
      state: this.stateMgr.state,
      score: this.scoreMgr.score,
      highScore: this.scoreMgr.highScore,
      lives: this.livesMgr.lives,
      timeStr: this.timer.getFormattedTime(),
      combo: this.scoreMgr.currentCombo,
      fps: this.fps,
      handDetected: motionData.handDetected,
      fingerX: motionData.fingerX,
      fingerY: motionData.fingerY,
    };
  }

  public render(
    ctx: CanvasRenderingContext2D,
    motionData: any,
    trackingData: any
  ) {
    ctx.clearRect(0, 0, this.width, this.height);

    // 1. Draw fruits (both active and split halves)
    for (const fruit of this.spawner.getAllFruits()) {
      fruit.draw(ctx);
    }

    // 2. Draw VFX particles
    this.effects.draw(ctx);

    // 3. Draw neon blade trail along Member 1's trajectory
    if (motionData && motionData.trajectory) {
      this.effects.drawBladeTrail(ctx, motionData.trajectory, motionData.isCutting);
    }

    // 4. Draw hand skeleton landmarks
    if (trackingData) {
      this.ai.drawLandmarks(ctx, trackingData);
    }
  }

  public handleKey(key: string): 'quit' | 'start' | 'restart' | 'pause' | '' {
    const action = this.stateMgr.handleKey(key);
    if (action === 'start' || action === 'restart') {
      this.restartGame();
    }
    return action;
  }
}
