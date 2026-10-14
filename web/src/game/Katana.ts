/**
 * web/src/game/Katana.ts
 * ======================
 * Mini-Katana Cutter Indicator for AI Fruit Cutter Game
 * 
 * Replaces visible webcam feed, face, and hand landmarks with a sleek,
 * game-friendly Japanese mini-katana indicator:
 * - Smoothly tracks index fingertip with jitter-free exponential smoothing.
 * - Dynamically rotates in the direction of cutting / motion.
 * - Smoothly returns to an elegant resting pose (-45 deg) when stationary.
 * - Features metallic curved blade, golden tsuba (guard), and wrapped tsuka (hilt).
 * - Emits a sharp slicing gleam and impact sparks upon cutting fruits.
 * - Compact dimensions (~50px) that never obscure fruits or bombs.
 */

interface Spark {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  size: number;
  life: number;
  maxLife: number;
}

export class KatanaCutter {
  public x = -1;
  public y = -1;
  public angle = -Math.PI / 4; // -45 degrees resting angle

  private targetX = -1;
  private targetY = -1;
  private targetAngle = -Math.PI / 4;

  public isVisible = false;
  private alpha = 0.0;
  private sliceFlash = 0.0;
  private sparks: Spark[] = [];

  // Cutter dimensions
  public readonly bladeLength = 44;
  public readonly hiltLength = 16;
  public readonly totalLength = 60;

  constructor() {
    this.x = -1;
    this.y = -1;
  }

  public setPosition(targetX: number, targetY: number, isHandActive: boolean, movementAngleDeg?: number) {
    if (isHandActive && targetX >= 0 && targetY >= 0) {
      this.isVisible = true;
      this.targetX = targetX;
      this.targetY = targetY;

      // If initial position, snap directly
      if (this.x < 0 || this.y < 0) {
        this.x = targetX;
        this.y = targetY;
      }

      // Calculate dynamic angle
      if (movementAngleDeg !== undefined && !isNaN(movementAngleDeg)) {
        // Convert movement degrees to radians.
        // Movement direction is where the blade is slashing towards!
        const rad = (movementAngleDeg * Math.PI) / 180.0;
        this.targetAngle = rad;
      }
    } else {
      this.isVisible = false;
    }
  }

  public triggerSlice(x: number, y: number) {
    this.sliceFlash = 1.0;

    // Burst of cutting sparks
    const colors = ['#00FFFF', '#FFFFFF', '#FFD700', '#70E0FF'];
    for (let i = 0; i < 8; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 2.5 + Math.random() * 5.0;
      this.sparks.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 1.5 + Math.random() * 2.5,
        life: 0,
        maxLife: 0.25 + Math.random() * 0.2,
      });
    }
  }

  public update(dt = 0.016, speed = 0) {
    // 1. Smooth position interpolation (responsive, no lag, zero jitter)
    if (this.targetX >= 0 && this.targetY >= 0) {
      const lerpFactor = 0.52;
      this.x += (this.targetX - this.x) * lerpFactor;
      this.y += (this.targetY - this.y) * lerpFactor;
    }

    // 2. Smooth angle interpolation
    // If stationary, ease toward -45 deg resting angle
    if (speed < 0.12) {
      this.targetAngle = -Math.PI / 4;
    }

    // Shortest angular difference
    let diff = this.targetAngle - this.angle;
    while (diff < -Math.PI) diff += Math.PI * 2;
    while (diff > Math.PI) diff -= Math.PI * 2;
    this.angle += diff * (speed > 0.3 ? 0.35 : 0.15);

    // 3. Alpha transition (smooth appearance / disappearance)
    const targetAlpha = this.isVisible ? 1.0 : 0.0;
    this.alpha += (targetAlpha - this.alpha) * 0.25;

    // 4. Slice flash decay
    if (this.sliceFlash > 0) {
      this.sliceFlash = Math.max(0, this.sliceFlash - dt * 3.5);
    }

    // 5. Update sparks
    for (const s of this.sparks) {
      s.x += s.vx;
      s.y += s.vy;
      s.life += dt;
    }
    this.sparks = this.sparks.filter((s) => s.life < s.maxLife);
  }

  public draw(ctx: CanvasRenderingContext2D, isCutting: boolean) {
    if (this.alpha <= 0.01 || this.x < 0 || this.y < 0) return;

    ctx.save();
    ctx.globalAlpha = this.alpha;

    // Draw spark particles first
    for (const s of this.sparks) {
      const progress = s.life / s.maxLife;
      ctx.fillStyle = s.color;
      ctx.globalAlpha = this.alpha * (1.0 - progress);
      ctx.beginPath();
      ctx.arc(s.x, s.y, Math.max(0.5, s.size * (1.0 - progress * 0.7)), 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalAlpha = this.alpha;

    // Translate to the tip of the blade!
    // Positioning at the index fingertip: the tip of the katana sits at (this.x, this.y).
    // The katana extends backward from the tip along the angle direction.
    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle);

    // 1. Blade Energy Glow (active when slashing fast or cutting)
    if (isCutting || this.sliceFlash > 0) {
      const glowAlpha = Math.min(1.0, (isCutting ? 0.45 : 0.2) + this.sliceFlash * 0.5);
      ctx.save();
      ctx.shadowColor = '#00F0FF';
      ctx.shadowBlur = 12 + this.sliceFlash * 8;
      ctx.strokeStyle = `rgba(180, 245, 255, ${glowAlpha})`;
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(0, 0); // Tip
      ctx.quadraticCurveTo(-this.bladeLength * 0.5, -2, -this.bladeLength, 0);
      ctx.stroke();
      ctx.restore();
    }

    // 2. Katana Blade
    // Curved back and sharp front edge
    const bl = this.bladeLength;
    ctx.save();

    // Blade back (mune) & body
    ctx.beginPath();
    ctx.moveTo(0, 0); // Kissaki (Tip)
    // Curved cutting edge (ha)
    ctx.quadraticCurveTo(-bl * 0.5, 3.5, -bl, 2.5);
    // Base of blade (at habaki)
    ctx.lineTo(-bl, -2.5);
    // Curved back spine (mune)
    ctx.quadraticCurveTo(-bl * 0.5, -3.5, 0, 0);
    ctx.closePath();

    // Metallic silver/chrome gradient
    const bladeGrad = ctx.createLinearGradient(0, -3, 0, 3);
    bladeGrad.addColorStop(0.0, '#CFDCE8'); // Steel spine
    bladeGrad.addColorStop(0.4, '#F5FAFF'); // Bright chrome gleam
    bladeGrad.addColorStop(0.7, '#D4E2ED'); // Hamon temper line
    bladeGrad.addColorStop(1.0, '#FFFFFF'); // Razor sharp cutting edge
    ctx.fillStyle = bladeGrad;
    ctx.fill();

    // Fine dark steel outline
    ctx.strokeStyle = '#5A6878';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Hamon (wavy temper line detail)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-2, 0);
    for (let x = -6; x > -bl + 4; x -= 5) {
      ctx.quadraticCurveTo(x + 2, Math.sin(x * 0.8) * 1.2 + 0.8, x, 0.8);
    }
    ctx.stroke();

    // 3. Habaki (Blade Collar - Brass Gold)
    ctx.fillStyle = '#D4AF37';
    ctx.fillRect(-bl - 3, -3, 3, 6);
    ctx.strokeStyle = '#8C701E';
    ctx.lineWidth = 0.8;
    ctx.strokeRect(-bl - 3, -3, 3, 6);

    // 4. Tsuba (Handguard - Ornate Oval Gold & Iron)
    ctx.fillStyle = '#222228';
    ctx.beginPath();
    ctx.ellipse(-bl - 3.5, 0, 2.5, 7.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Gold rim on tsuba
    ctx.strokeStyle = '#E5B834';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    // 5. Tsuka (Handle / Hilt - Dark Charcoal wrapped with Red Diamonds)
    const hl = this.hiltLength;
    const hiltX = -bl - 3.5;

    // Base handle
    ctx.fillStyle = '#16161D';
    ctx.beginPath();
    ctx.roundRect(hiltX - hl, -2.5, hl, 5, 2);
    ctx.fill();

    // Ito wrap pattern (crimson diamond cross-laces)
    ctx.fillStyle = '#B22222';
    for (let i = 2; i < hl - 2; i += 3.5) {
      ctx.beginPath();
      ctx.moveTo(hiltX - i, -2);
      ctx.lineTo(hiltX - i - 1.5, 0);
      ctx.lineTo(hiltX - i, 2);
      ctx.lineTo(hiltX - i + 1.5, 0);
      ctx.closePath();
      ctx.fill();
    }

    // 6. Kashira (Pommel Cap - Polished Brass)
    ctx.fillStyle = '#D4AF37';
    ctx.beginPath();
    ctx.arc(hiltX - hl, 0, 3, Math.PI / 2, (3 * Math.PI) / 2);
    ctx.fill();
    ctx.strokeStyle = '#8C701E';
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // 7. Slicing Flash Glint at Kissaki (Tip)
    if (this.sliceFlash > 0.05 || isCutting) {
      const glintSize = 4 + this.sliceFlash * 6;
      ctx.fillStyle = '#FFFFFF';
      ctx.beginPath();
      ctx.arc(0, 0, glintSize * 0.5, 0, Math.PI * 2);
      ctx.fill();

      // Star glint cross
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(-glintSize, 0);
      ctx.lineTo(glintSize, 0);
      ctx.moveTo(0, -glintSize);
      ctx.lineTo(0, glintSize);
      ctx.stroke();
    }

    ctx.restore();
    ctx.restore();
  }
}
