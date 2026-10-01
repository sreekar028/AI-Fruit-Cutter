import React from 'react';
import type { GameStatus } from '../../game/GameEngine';

interface GameOverModalProps {
  status: GameStatus;
  onRestart: () => void;
  onHome: () => void;
}

export const GameOverModal: React.FC<GameOverModalProps> = ({ status, onRestart, onHome }) => {
  const { score, highScore } = status;
  const isNewBest = score >= highScore && score > 0;

  return (
    <div className="overlay-backdrop">
      <div className="game-over-modal glass-panel">
        <h1 className="game-over-title">GAME OVER</h1>

        <div className="score-summary-card">
          <span className="summary-label">FINAL SCORE</span>
          <span className="summary-score">{score}</span>

          {isNewBest ? (
            <div className="new-record-pill">★ NEW BEST RECORD! ★</div>
          ) : (
            <div className="best-score-sub">Personal Best: {highScore}</div>
          )}
        </div>

        <div className="game-over-actions">
          <button className="replay-button pulse-glow" onClick={onRestart}>
            <span className="key-badge">SPACE</span>
            <span className="btn-label">PLAY AGAIN</span>
          </button>

          <button className="home-button" onClick={onHome}>
            <span className="key-badge">Q</span>
            <span className="btn-label">HOME MENU</span>
          </button>

          <p className="shortcut-hint">
            Press <strong>SPACE</strong> or <strong>R</strong> to Restart &bull; Press <strong>Q</strong> for Home
          </p>
        </div>
      </div>
    </div>
  );
};
