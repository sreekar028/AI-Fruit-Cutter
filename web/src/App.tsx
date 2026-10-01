import React, { useEffect, useRef, useState, useCallback } from 'react';
import { GameEngine, type GameStatus } from './game/GameEngine';
import { GameState } from './game/GameState';
import { HeaderHUD } from './ui/components/HeaderHUD';
import { StartOverlay } from './ui/components/StartOverlay';
import { GameOverModal } from './ui/components/GameOverModal';
import { PauseModal } from './ui/components/PauseModal';
import { StatusFooter } from './ui/components/StatusFooter';
import './App.css';

export const App: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const engineRef = useRef<GameEngine | null>(null);

  const [isLoadingCamera, setIsLoadingCamera] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const [gameStatus, setGameStatus] = useState<GameStatus>({
    state: GameState.START,
    score: 0,
    highScore: 0,
    lives: 3,
    timeStr: '00:00',
    combo: 0,
    fps: 60,
    handDetected: false,
    fingerX: -1,
    fingerY: -1,
  });

  // Track last dispatched state for performance throttling
  const lastDispatchedRef = useRef<{
    state: GameState;
    score: number;
    lives: number;
    combo: number;
    lastThrottleTime: number;
  }>({
    state: GameState.START,
    score: 0,
    lives: 3,
    combo: 0,
    lastThrottleTime: 0,
  });

  // Mouse / Touch swipe fallback tracking
  const isMouseDownRef = useRef(false);
  const lastMousePosRef = useRef<{ x: number; y: number } | null>(null);

  // Initialize GameEngine
  useEffect(() => {
    const engine = new GameEngine(640, 480);
    engineRef.current = engine;

    // Handle mid-game camera disconnection gracefully
    engine.ai.onDisconnect = () => {
      setCameraReady(false);
      setCameraError('Webcam disconnected. Touch/mouse slicing is still active.');
    };

    return () => {
      engine.stop();
    };
  }, []);

  // Connect Camera & MediaPipe
  const connectWebcam = useCallback(async (): Promise<boolean> => {
    if (!videoRef.current || !engineRef.current) return false;
    setIsLoadingCamera(true);
    setCameraError(null);

    const result = await engineRef.current.startWebcam(videoRef.current);
    setIsLoadingCamera(false);
    setCameraReady(result.success);

    if (!result.success) {
      setCameraError(result.error || 'Camera connection failed.');
      return false;
    }
    return true;
  }, []);

  // Start game action (from Start Screen)
  const handleStartGame = useCallback(async () => {
    if (!cameraReady && !isLoadingCamera) {
      await connectWebcam();
    }
    if (engineRef.current) {
      engineRef.current.restartGame();
    }
  }, [cameraReady, isLoadingCamera, connectWebcam]);

  // Start game with mouse/touch directly without camera
  const handlePlayWithMouse = useCallback(() => {
    if (engineRef.current) {
      engineRef.current.restartGame();
    }
  }, []);

  const handleRestart = useCallback(() => {
    if (engineRef.current) {
      engineRef.current.restartGame();
    }
  }, []);

  const handlePause = useCallback(() => {
    if (engineRef.current) {
      engineRef.current.stateMgr.togglePause();
    }
  }, []);

  const handleHome = useCallback(() => {
    if (engineRef.current) {
      engineRef.current.stateMgr.state = GameState.START;
      engineRef.current.timer.reset();
      engineRef.current.scoreMgr.reset();
      engineRef.current.livesMgr.reset();
      engineRef.current.spawner.reset();
    }
  }, []);

  // Keyboard controls listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!engineRef.current) return;

      const key = e.key;
      const k = key.toLowerCase();

      // Q or ESC in Game Over / Pause / Start acts as Home / Quit
      if ((k === 'q' || key === 'Escape') && engineRef.current.stateMgr.state !== GameState.PLAYING) {
        handleHome();
        return;
      }

      const action = engineRef.current.handleKey(key);
      if (action === 'start' && !cameraReady) {
        handleStartGame();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [cameraReady, handleStartGame, handleHome]);

  // Main 60 FPS Canvas Game Loop
  useEffect(() => {
    let animId: number;

    const gameLoop = (timestamp: number) => {
      const engine = engineRef.current;
      const canvas = canvasRef.current;

      if (engine && canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          // 1. Update Game Engine Physics & Logic
          const status = engine.update(timestamp);

          // 2. Render Canvas Game Elements
          const { motionData, trackingData } = engine.ai.tick(timestamp);
          engine.render(ctx, motionData, trackingData);

          // 3. Throttled React state updates to avoid re-rendering React every frame
          const last = lastDispatchedRef.current;
          const nowMs = performance.now();
          const stateChanged = last.state !== status.state;
          const scoreChanged = last.score !== status.score;
          const livesChanged = last.lives !== status.lives;
          const comboChanged = last.combo !== status.combo;
          const timeElapsed = nowMs - last.lastThrottleTime > 120; // 8-10 Hz for clock/FPS

          if (stateChanged || scoreChanged || livesChanged || comboChanged || timeElapsed) {
            setGameStatus(status);
            last.state = status.state;
            last.score = status.score;
            last.lives = status.lives;
            last.combo = status.combo;
            last.lastThrottleTime = nowMs;
          }
        }
      }

      animId = requestAnimationFrame(gameLoop);
    };

    animId = requestAnimationFrame(gameLoop);
    return () => cancelAnimationFrame(animId);
  }, []);

  // Mouse / Touch Slicing event handlers
  const handlePointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    isMouseDownRef.current = true;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 640;
    const y = ((e.clientY - rect.top) / rect.height) * 480;
    lastMousePosRef.current = { x, y };
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!isMouseDownRef.current || !engineRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 640;
    const y = ((e.clientY - rect.top) / rect.height) * 480;

    const prev = lastMousePosRef.current || { x, y };
    const dx = x - prev.x;
    const dy = y - prev.y;
    const dist = Math.hypot(dx, dy);

    // Inject simulated motion data for mouse/touch slice
    if (dist > 15) {
      const simulatedMotion = {
        handDetected: true,
        fingerX: Math.round(x),
        fingerY: Math.round(y),
        previousX: Math.round(prev.x),
        previousY: Math.round(prev.y),
        movementDistance: dist,
        movementSpeed: 0.8,
        movementDirection: (Math.atan2(dy, dx) * 180) / Math.PI,
        trajectory: [[prev.x, prev.y], [x, y]] as Array<[number, number]>,
        isCutting: true,
      };

      if (engineRef.current.stateMgr.isPlaying) {
        const active = engineRef.current.spawner.getActiveFruits();
        const sliced = engineRef.current.collision.checkCollisions(simulatedMotion, active);
        for (const fruit of sliced) {
          if (fruit.isBomb) {
            engineRef.current.effects.spawnBombExplosion(fruit.x, fruit.y);
            engineRef.current.livesMgr.onBombCut();
            if (engineRef.current.livesMgr.isDead) engineRef.current.stateMgr.triggerGameOver();
          } else {
            const res = engineRef.current.scoreMgr.registerSlice(fruit, performance.now() / 1000.0);
            engineRef.current.effects.spawnFruitSplash(fruit.x, fruit.y, fruit.colorSplash);
            engineRef.current.effects.spawnFloatingText(`+${res.totalAwarded}`, fruit.x, fruit.y - 20, '#00FF66');
          }
        }
      }
    }

    lastMousePosRef.current = { x, y };
  };

  const handlePointerUp = () => {
    isMouseDownRef.current = false;
    lastMousePosRef.current = null;
  };

  return (
    <div className="game-app-root">
      {/* Game Stage Arena */}
      <main className="game-stage">
        {/* Mirrored webcam video stream */}
        <video
          ref={videoRef}
          className="webcam-video"
          playsInline
          muted
        />

        {/* Game Canvas */}
        <canvas
          ref={canvasRef}
          className="game-canvas"
          width={640}
          height={480}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
        />

        {/* Glassmorphism In-Game HUD */}
        {gameStatus.state === GameState.PLAYING && (
          <HeaderHUD status={gameStatus} onPause={handlePause} />
        )}

        {/* Start / Home Screen Overlay */}
        {gameStatus.state === GameState.START && (
          <StartOverlay
            onStart={handleStartGame}
            onPlayWithMouse={handlePlayWithMouse}
            isLoadingCamera={isLoadingCamera}
            cameraReady={cameraReady}
            cameraError={cameraError}
          />
        )}

        {/* Game Over Modal */}
        {gameStatus.state === GameState.GAME_OVER && (
          <GameOverModal
            status={gameStatus}
            onRestart={handleRestart}
            onHome={handleHome}
          />
        )}

        {/* Pause Modal */}
        {gameStatus.state === GameState.PAUSED && (
          <PauseModal
            onResume={handlePause}
            onRestart={handleRestart}
            onHome={handleHome}
          />
        )}

        {/* Status Bar Footer */}
        <StatusFooter
          handDetected={gameStatus.handDetected}
          fps={gameStatus.fps}
        />
      </main>
    </div>
  );
};

export default App;
