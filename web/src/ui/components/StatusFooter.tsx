import React from 'react';

interface StatusFooterProps {
  handDetected: boolean;
  fps: number;
}

export const StatusFooter: React.FC<StatusFooterProps> = ({ handDetected, fps }) => {
  return (
    <footer className="status-footer">
      <div className="status-left">
        <div className={`status-pill ${handDetected ? 'active' : 'searching'}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {handDetected ? 'HAND ACTIVE' : 'SEARCHING HAND...'}
          </span>
          {fps > 0 && <span className="fps-counter">{fps} FPS</span>}
        </div>
      </div>

      <div className="status-right">
        <span className="key-hint">[ P ] Pause</span>
        <span className="key-hint-sep">&bull;</span>
        <span className="key-hint">[ R ] Restart</span>
        <span className="key-hint-sep">&bull;</span>
        <span className="key-hint">[ Q ] Quit</span>
      </div>
    </footer>
  );
};
