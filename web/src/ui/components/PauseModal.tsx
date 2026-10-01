import React from 'react';

interface PauseModalProps {
  onResume: () => void;
  onRestart: () => void;
  onHome: () => void;
}

export const PauseModal: React.FC<PauseModalProps> = ({ onResume, onRestart, onHome }) => {
  return (
    <div className="overlay-backdrop">
      <div className="pause-modal glass-panel">
        <h2 className="pause-title">GAME PAUSED</h2>

        <div className="pause-actions">
          <button className="pause-btn primary" onClick={onResume}>
            <span className="key-badge">P</span>
            <span className="btn-label">RESUME GAME</span>
          </button>

          <button className="pause-btn secondary" onClick={onRestart}>
            <span className="key-badge">R</span>
            <span className="btn-label">RESTART ROUND</span>
          </button>

          <button className="pause-btn tertiary" onClick={onHome}>
            <span className="key-badge">Q</span>
            <span className="btn-label">HOME MENU</span>
          </button>
        </div>

        <p className="shortcut-hint">
          Press <strong>P</strong> to Resume &bull; Press <strong>Q</strong> for Home
        </p>
      </div>
    </div>
  );
};
