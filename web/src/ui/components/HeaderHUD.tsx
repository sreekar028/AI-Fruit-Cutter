import React from 'react';
import type { GameStatus } from '../../game/GameEngine';
import type { GameMode } from '../../game/Difficulty';

interface HeaderHUDProps {
  status: GameStatus;
  mode: GameMode;
  onPause: () => void;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({ status, mode, onPause }) => {
  const { score, highScore, lives, timeStr, combo } = status;

  return (
    <div className="hud-container">
      {/* Top Header Bar */}
      <header className="hud-header">
        <div className="hud-card score-card">
          <span className="hud-label">SCORE</span>
          <span className="hud-value score-val">{score}</span>
          <span className="best-tag">BEST {highScore}</span>
        </div>

        <div className="hud-card mode-card">
          <span className="hud-label">MODE</span>
          <span className="hud-value mode-val">{mode.toUpperCase()}</span>
        </div>

        <div className="hud-card timer-card">
          <span className="hud-value timer-val">{timeStr}</span>
          <button
            className="hud-pause-btn"
            onClick={onPause}
            title="Pause Game (P)"
            aria-label="Pause Game"
          >
            ⏸
          </button>
        </div>

        <div className="hud-card lives-card">
          <span className="hud-label">LIVES</span>
          <div className="hearts-container">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className={`heart-icon ${i < lives ? 'filled' : 'lost'}`}
                title={`Life ${i + 1}`}
              >
                ♥
              </span>
            ))}
          </div>
        </div>
      </header>

      {/* Combo Banner (Active when combo >= 2) */}
      {combo >= 2 && (
        <div className="combo-banner-wrap">
          <div className={`combo-banner ${combo >= 4 ? 'super-combo' : ''}`}>
            <span>
              {combo >= 4
                ? `SUPER COMBO ${combo}x! +20`
                : combo === 3
                ? `COMBO 3x! +10`
                : `COMBO 2x! +5`}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
