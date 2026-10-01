/**
 * web/src/game/Effects.ts
 * =======================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Visual feedback & particle system:
 * - Juice splatter particles
 * - Bomb explosion fire & smoke
 * - Floating score labels (+10, COMBO 3x!, MISS!)
 * - Glowing neon blade trail rendering
 */

export class Particle {
  public x: number;
  public y: number;
  public vx: number;
  public vy: number;
  public color: string;
  public radius: number;
  public lifetime: number;
  public age = 0;
  public gravity = 0.35;

  constructor(
    x: number,
    y: number,
    vx: number,
    vy: number,
    color: string,
    radius = 4.0,
    lifetime = 0.6
  ) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.color = color;
    this.radius = radius;
    this.lifetime = lifetime;
  }

  public update(dt = 0.033) {
    this.age += dt;
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
  }

  public get isAlive(): boolean {
    return this.age < this.lifetime;
  }

  public draw(ctx: CanvasRenderingContext2D) {
    if (!this.isAlive) return;
    const progress = this.age / this.lifetime;
    const currentR = Math.max(1, this.radius * (1.0 - progress));

    ctx.save();
    ctx.globalAlpha = Math.max(0, 1.0 - progress);
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, currentR, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

export class FloatingText {
  public text: string;
  public x: number;
  public y: number;
  public color: string;
  public size: number;
  public lifetime: number;
  public age = 0;

  constructor(text: string, x: number, y: number, color = '#FFD700', size = 20, lifetime = 0.8) {
    this.text = text;
    this.x = x;
    this.y = y;
    this.color = color;
    this.size = size;
    this.lifetime = lifetime;
  }

  public update(dt = 0.033) {
    this.age += dt;
    this.y -= 1.8; // float upwards
  }

  public get isAlive(): boolean {
    return this.age < this.lifetime;
  }

  public draw(ctx: CanvasRenderingContext2D) {
    if (!this.isAlive) return;
    const progress = this.age / this.lifetime;

    ctx.save();
    ctx.globalAlpha = Math.max(0, 1.0 - progress);
    ctx.font = `bold ${this.size}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Black stroke shadow
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 3;
    ctx.strokeText(this.text, this.x, this.y);

    ctx.fillStyle = this.color;
    ctx.fillText(this.text, this.x, this.y);
    ctx.restore();
  }
}

export class EffectsManager {
  public particles: Particle[] = [];
  public texts: FloatingText[] = [];

  public spawnFruitSplash(x: number, y: number, colorSplash: string, count = 16) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 3.0 + Math.random() * 5.5;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed - 1.5;
      const radius = 3.0 + Math.random() * 3.0;
      const lifetime = 0.4 + Math.random() * 0.35;
      this.particles.push(new Particle(x, y, vx, vy, colorSplash, radius, lifetime));
    }
  }

  public spawnBombExplosion(x: number, y: number, count = 30) {
    const colors = ['#FF4500', '#FFD700', '#FF0000', '#888888'];
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 4.0 + Math.random() * 8.0;
      const vx = Math.cos(angle) * speed;
      const vy = Math.sin(angle) * speed - 2.0;
      const color = colors[Math.floor(Math.random() * colors.length)];
      const radius = 4.0 + Math.random() * 5.0;
      const lifetime = 0.5 + Math.random() * 0.4;
      this.particles.push(new Particle(x, y, vx, vy, color, radius, lifetime));
    }
  }

  public spawnFloatingText(text: string, x: number, y: number, color = '#FFD700', size = 20) {
    this.texts.push(new FloatingText(text, x, y, color, size));
  }

  public update(dt = 0.033) {
    for (const p of this.particles) p.update(dt);
    this.particles = this.particles.filter((p) => p.isAlive);

    for (const t of this.texts) t.update(dt);
    this.texts = this.texts.filter((t) => t.isAlive);
  }

  public draw(ctx: CanvasRenderingContext2D) {
    for (const p of this.particles) p.draw(ctx);
    for (const t of this.texts) t.draw(ctx);
  }

  public drawBladeTrail(
    ctx: CanvasRenderingContext2D,
    trajectory: Array<[number, number]>,
    isCutting: boolean
  ) {
    const n = trajectory.length;
    if (n < 2) return;

    ctx.save();
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    const glowColor = isCutting ? '#00FFFF' : '#00E676';

    for (let i = 1; i < n; i++) {
      const progress = i / n;
      const width = Math.max(1, progress * (isCutting ? 8 : 4));

      const [x1, y1] = trajectory[i - 1];
      const [x2, y2] = trajectory[i];

      // Outer glow
      ctx.strokeStyle = glowColor;
      ctx.lineWidth = width + 4;
      ctx.globalAlpha = progress * 0.7;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      // Sharp white core
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = Math.max(1, width - 1);
      ctx.globalAlpha = progress * 0.95;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    ctx.restore();
  }

  public reset() {
    this.particles = [];
    this.texts = [];
  }
}
