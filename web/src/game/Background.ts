/**
 * web/src/game/Background.ts
 * ==========================
 * Interactive Ambient Background for AI Fruit Cutter Game
 * 
 * Provides:
 * - Clean, modern fruit-dojo aesthetic with subtle deep gradients.
 * - Soft ambient light glows and decorative wooden borders.
 * - Interactive floating ambient particles (sakura / light motes) that drift
 *   slowly and scatter gently when slashed near by the katana.
 * - Clean open center ensuring maximum contrast and visibility for fruits.
 * - Ultra-lightweight: zero heavy graphics, 60 FPS performance.
 */

interface AmbientParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  alpha: number;
  baseAlpha: number;
  phase: number;
  color: string;
}

export class BackgroundManager {
  private width: number;
  private height: number;
  private particles: AmbientParticle[] = [];
  private maxParticles = 24;
  private time = 0;

  constructor(width = 960, height = 720) {
    this.width = width;
    this.height = height;
    this.initParticles();
  }

  public setDimensions(width: number, height: number) {
    this.width = width;
    this.height = height;
  }

  private initParticles() {
    this.particles = [];
    const colors = [
      'rgba(255, 180, 200, ', // Sakura petal pink
      'rgba(255, 230, 150, ', // Soft golden light mote
      'rgba(180, 240, 255, ', // Cool cyan glow
      'rgba(255, 150, 100, ', // Warm fruit amber
    ];

    for (let i = 0; i < this.maxParticles; i++) {
      const baseAlpha = 0.15 + Math.random() * 0.25;
      this.particles.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: -0.25 - Math.random() * 0.45,
        size: 2.0 + Math.random() * 2.8,
        alpha: baseAlpha,
        baseAlpha,
        phase: Math.random() * Math.PI * 2,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }
  }

  public update(dt = 0.016, cutterX = -1, cutterY = -1, isCutting = false) {
    this.time += dt;

    for (const p of this.particles) {
      // Gentle floating drift with sine oscillation
      p.x += p.vx + Math.sin(this.time * 1.2 + p.phase) * 0.3;
      p.y += p.vy;

      // Pulse alpha subtly
      p.alpha = p.baseAlpha + Math.sin(this.time * 2.0 + p.phase) * 0.08;

      // Interactive wind reaction: scatter if katana slashes close
      if (cutterX >= 0 && cutterY >= 0) {
        const dx = p.x - cutterX;
        const dy = p.y - cutterY;
        const distSq = dx * dx + dy * dy;
        const radius = isCutting ? 120 : 60;

        if (distSq < radius * radius && distSq > 4) {
          const dist = Math.sqrt(distSq);
          const force = ((radius - dist) / radius) * (isCutting ? 3.5 : 1.2);
          p.x += (dx / dist) * force;
          p.y += (dy / dist) * force;
        }
      }

      // Screen wrap
      if (p.y < -10) {
        p.y = this.height + 10;
        p.x = Math.random() * this.width;
      }
      if (p.x < -10) p.x = this.width + 10;
      if (p.x > this.width + 10) p.x = -10;
    }
  }

  public draw(ctx: CanvasRenderingContext2D) {
    const w = this.width;
    const h = this.height;

    // 1. Deep modern fruit-dojo gradient background
    // Radial glow centered slightly above middle, fading to rich obsidian navy at edges
    const bgGradient = ctx.createRadialGradient(
      w * 0.5,
      h * 0.35,
      w * 0.1,
      w * 0.5,
      h * 0.5,
      w * 0.8
    );
    bgGradient.addColorStop(0.0, '#1c2438'); // Soft luminous slate navy
    bgGradient.addColorStop(0.5, '#121624'); // Deep midnight indigo
    bgGradient.addColorStop(1.0, '#090b12'); // Rich dark vignette

    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, w, h);

    // 2. Subtle ambient top lantern/sunbeam light beam
    ctx.save();
    const lightGlow = ctx.createRadialGradient(
      w * 0.5,
      0,
      10,
      w * 0.5,
      0,
      h * 0.55
    );
    const pulseIntensity = 0.06 + Math.sin(this.time * 0.8) * 0.02;
    lightGlow.addColorStop(0.0, `rgba(255, 230, 180, ${pulseIntensity * 1.5})`);
    lightGlow.addColorStop(0.6, `rgba(180, 220, 255, ${pulseIntensity * 0.5})`);
    lightGlow.addColorStop(1.0, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = lightGlow;
    ctx.fillRect(0, 0, w, h * 0.6);
    ctx.restore();

    // 3. Subtle Japanese wooden border accent at bottom
    ctx.save();
    const bottomH = Math.min(28, h * 0.04);
    const woodGrad = ctx.createLinearGradient(0, h - bottomH, 0, h);
    woodGrad.addColorStop(0, 'rgba(28, 20, 16, 0.4)');
    woodGrad.addColorStop(1, 'rgba(14, 10, 8, 0.85)');

    ctx.fillStyle = woodGrad;
    ctx.fillRect(0, h - bottomH, w, bottomH);

    // Fine gold/amber separator line
    ctx.strokeStyle = 'rgba(218, 165, 32, 0.3)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h - bottomH);
    ctx.lineTo(w, h - bottomH);
    ctx.stroke();
    ctx.restore();

    // 4. Draw interactive floating ambient particles
    ctx.save();
    for (const p of this.particles) {
      ctx.fillStyle = `${p.color}${Math.max(0, p.alpha)})`;
      ctx.beginPath();
      // Draw smooth soft circles
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();

      // Soft glow halo
      ctx.fillStyle = `${p.color}${Math.max(0, p.alpha * 0.35)})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * 2.2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}
