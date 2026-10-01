import React from 'react';

interface StartOverlayProps {
  onStart: () => void;
  isLoadingCamera: boolean;
  cameraReady: boolean;
}

export const StartOverlay: React.FC<StartOverlayProps> = ({
  onStart,
  isLoadingCamera,
  cameraReady,
}) => {
  return (
    <div className="overlay-backdrop">
      <div className="start-modal glass-panel">
        <div className="hero-header">
          <h1 className="game-title">AI-BASED FRUIT CUTTER</h1>
          <p className="game-subtitle">Real-Time Hand Motion Detection</p>
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

        <div className="cta-section">
          {isLoadingCamera ? (
            <div className="loading-spinner-box">
              <div className="spinner"></div>
              <span>Connecting webcam & MediaPipe model...</span>
            </div>
          ) : (
            <button
              className="start-button pulse-glow"
              onClick={onStart}
              disabled={!cameraReady && isLoadingCamera}
            >
              <span className="key-badge">SPACE</span>
              <span className="btn-label">START GAME</span>
            </button>
          )}

          <p className="shortcut-hint">
            Press <strong>SPACE</strong> to Start &bull; Press <strong>Q</strong> to Quit
          </p>
        </div>
      </div>
    </div>
  );
};
