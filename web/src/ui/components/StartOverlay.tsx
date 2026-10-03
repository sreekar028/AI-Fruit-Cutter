import React from 'react';
import { GAME_MODES, type GameMode, getDifficultyConfig } from '../../game/Difficulty';

interface StartOverlayProps {
  onStart: () => void;
  onPlayWithMouse: () => void;
  isLoadingCamera: boolean;
  cameraReady: boolean;
  cameraError: string | null;
  selectedMode: GameMode;
  onModeSelect: (mode: GameMode) => void;
}

export const StartOverlay: React.FC<StartOverlayProps> = ({
  onStart,
  onPlayWithMouse,
  isLoadingCamera,
  cameraReady,
  cameraError,
  selectedMode,
  onModeSelect,
}) => {
  return (
    <div className="overlay-backdrop">
      <div className="start-modal glass-panel">
        <div className="hero-header">
          <h1 className="game-title">AI-BASED FRUIT CUTTER</h1>
          <p className="game-subtitle">Real-Time Hand Motion Detection</p>
        </div>

        <div className="mode-picker">
          <span className="section-title">GAME MODE</span>
          <div className="mode-buttons">
            {Object.values(GAME_MODES).map((mode) => {
              const config = getDifficultyConfig(mode);
              const active = selectedMode === mode;

              return (
                <button
                  key={mode}
                  type="button"
                  className={`mode-button ${active ? 'active' : ''}`}
                  onClick={() => onModeSelect(mode)}
                >
                  <span className="mode-button-label">{config.label}</span>
                  <span className="mode-button-meta">{config.fruitSpeedMultiplier >= 1.3 ? 'FAST' : config.fruitSpeedMultiplier > 0.9 ? 'MEDIUM' : 'SLOW'}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="instructions-card">
          <h3 className="section-title">HOW TO PLAY</h3>
          <ul className="instruction-list">
            <li>
              <span className="inst-badge">1. SLICE</span>
              <span>Wave your <strong>index fingertip</strong> quickly across fruits to slice them.</span>
            </li>
            <li>
              <span className="inst-badge">2. COMBOS</span>
              <span>Slice multiple fruits in one swift swipe for massive bonus points!</span>
            </li>
            <li>
              <span className="inst-badge warning">3. BOMBS</span>
              <span>Avoid slicing bombs — cutting a bomb detonates and costs <strong>1 Life</strong>!</span>
            </li>
            <li>
              <span className="inst-badge danger">4. LIVES</span>
              <span>Do not let fruits fall below the screen (3 missed fruits = Game Over).</span>
            </li>
          </ul>
        </div>

        {cameraError && (
          <div className="camera-error-banner">
            <span className="error-icon">⚠️</span>
            <div className="error-text-wrap">
              <strong>Camera Notice:</strong> {cameraError}
            </div>
          </div>
        )}

        <div className="cta-section">
          {isLoadingCamera ? (
            <div className="loading-spinner-box">
              <div className="spinner"></div>
              <span>Connecting webcam & MediaPipe model...</span>
            </div>
          ) : (
            <div className="button-group-cta">
              <button
                className="start-button pulse-glow"
                onClick={onStart}
              >
                <span className="key-badge">SPACE</span>
                <span className="btn-label">{cameraReady ? 'START GAME' : 'ENABLE CAMERA & PLAY'}</span>
              </button>

              <button
                className="mouse-fallback-btn"
                onClick={onPlayWithMouse}
                title="Play using mouse or touchscreen swipe without webcam"
              >
                <span>Play with Mouse / Touch</span>
              </button>
            </div>
          )}

          <p className="shortcut-hint">
            Press <strong>SPACE</strong> to Start &bull; Press <strong>Q</strong> to Quit
          </p>
        </div>
      </div>
    </div>
  );
};
