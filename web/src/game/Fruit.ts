/**
 * web/src/game/Fruit.ts
 * =====================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's Fruit system:
 * - 6 Fruit types: Watermelon, Apple, Banana, Orange, Strawberry, Bomb
 * - Physics: Position, velocity, gravity, rotation
 * - Slicing: Splits into two separate rotating halves separating along cut normal
 * - HTML5 Canvas rendering matching the desktop visual style
 */

export interface FruitTypeConfig {
  name: string;
  radius: number;
  points: number;
  colorRind: string;
  colorFlesh: string;
  colorSeed?: string;
  colorSplash: string;
  isBomb: boolean;
}

export const FRUIT_TYPES: Record<string, FruitTypeConfig> = {
  watermelon: {
    name: 'Watermelon',
    radius: 36,
    points: 10,
    colorRind: '#228B22',     // Forest Green
    colorFlesh: '#D72638',    // Crimson Flesh
    colorSeed: '#141414',
    colorSplash: '#E63946',
    isBomb: false,
  },
  apple: {
    name: 'Apple',
    radius: 28,
    points: 15,
    colorRind: '#D62246',     // Crimson Red
    colorFlesh: '#FDF0D5',    // Pale Cream
    colorSeed: '#141414',
    colorSplash: '#E63946',
    isBomb: false,
  },
  banana: {
    name: 'Banana',
    radius: 26,
    points: 20,
    colorRind: '#FFD700',     // Bright Yellow
    colorFlesh: '#FFF3B0',    // Cream Yellow
    colorSeed: '#C9A227',
    colorSplash: '#FFE66D',
    isBomb: false,
  },
  orange: {
    name: 'Orange',
    radius: 30,
    points: 10,
    colorRind: '#FF8500',     // Neon Orange
    colorFlesh: '#FFA200',
    colorSeed: '#FFFFFF',
    colorSplash: '#FF9E00',
    isBomb: false,
  },
  strawberry: {
    name: 'Strawberry',
    radius: 24,
    points: 25,
    colorRind: '#E63946',     // Ruby Red
    colorFlesh: '#F48498',
    colorSeed: '#2A9D8F',     // Green leaves/seeds
    colorSplash: '#FF4D6D',
    isBomb: false,
  },
  bomb: {
    name: 'Bomb',
    radius: 30,
    points: 0,
    colorRind: '#252525',     // Charcoal Dark
    colorFlesh: '#141414',
    colorSeed: '#FF5400',     // Orange fuse
    colorSplash: '#FF3300',
    isBomb: true,
  },
};

export class FruitHalf {
  public x: number;
  public y: number;
  public vx: number;
  public vy: number;
  public radius: number;
  public colorRind: string;
  public colorFlesh: string;
  public angle: number;
  public rotSpeed: number;
  public isLeft: boolean;
  public gravity = 0.45;

  constructor(
    x: number,
    y: number,
    vx: number,
    vy: number,
    radius: number,
    colorRind: string,
    colorFlesh: string,
    angle: number,
    rotSpeed: number,
    isLeft: boolean
  ) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.radius = radius;
    this.colorRind = colorRind;
    this.colorFlesh = colorFlesh;
    this.angle = angle;
    this.rotSpeed = rotSpeed;
    this.isLeft = isLeft;
  }

  public update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.angle += this.rotSpeed;
  }

  public draw(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate((this.angle * Math.PI) / 180.0);

    const startAngle = this.isLeft ? Math.PI / 2 : (3 * Math.PI) / 2;
    const endAngle = startAngle + Math.PI;

    // Outer rind
    ctx.fillStyle = this.colorRind;
    ctx.beginPath();
    ctx.arc(0, 0, this.radius, startAngle, endAngle);
    ctx.closePath();
    ctx.fill();

    // Inner flesh
    ctx.fillStyle = this.colorFlesh;
    ctx.beginPath();
    ctx.arc(0, 0, this.radius * 0.75, startAngle, endAngle);
    ctx.closePath();
    ctx.fill();

    // Cut edge highlight
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, -this.radius);
    ctx.lineTo(0, this.radius);
    ctx.stroke();

    ctx.restore();
  }
}

export class Fruit {
  public fruitType: string;
  public name: string;
  public radius: number;
  public points: number;
  public isBomb: boolean;
  public colorRind: string;
  public colorFlesh: string;
  public colorSplash: string;

  public x: number;
  public y: number;
  public vx: number;
  public vy: number;
  public gravity: number;

  public angle: number;
  public rotSpeed: number;

  public state: 'active' | 'sliced' | 'missed' | 'removed' = 'active';
  public halves: FruitHalf[] = [];
  private sparkPhase = 0;

  constructor(
    fruitType = 'watermelon',
    x = 320,
    y = 500,
    vx = 0,
    vy = -16.0,
    gravity = 0.38
  ) {
    const config = FRUIT_TYPES[fruitType] || FRUIT_TYPES.watermelon;
    this.fruitType = fruitType;
    this.name = config.name;
    this.radius = config.radius;
    this.points = config.points;
    this.isBomb = config.isBomb;
    this.colorRind = config.colorRind;
    this.colorFlesh = config.colorFlesh;
    this.colorSplash = config.colorSplash;

    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.gravity = gravity;

    this.angle = Math.random() * 360;
    this.rotSpeed = (Math.random() - 0.5) * 8.0;
  }

  public get isActive(): boolean {
    return this.state === 'active';
  }

  public get isSliced(): boolean {
    return this.state === 'sliced';
  }

  public slice(cutAngle = 0) {
    if (this.state !== 'active') return;

    this.state = 'sliced';

    if (this.isBomb) return; // Bombs detonate rather than splitting cleanly

    const rad = ((cutAngle + 90) * Math.PI) / 180.0;
    const sepSpeed = 3.5;

    const leftVx = this.vx - Math.cos(rad) * sepSpeed;
    const leftVy = this.vy - Math.sin(rad) * sepSpeed - 1.5;
    const rightVx = this.vx + Math.cos(rad) * sepSpeed;
    const rightVy = this.vy + Math.sin(rad) * sepSpeed - 1.5;

    this.halves = [
      new FruitHalf(
        this.x,
        this.y,
        leftVx,
        leftVy,
        this.radius,
        this.colorRind,
        this.colorFlesh,
        this.angle,
        -6.0,
        true
      ),
      new FruitHalf(
        this.x,
        this.y,
        rightVx,
        rightVy,
        this.radius,
        this.colorRind,
        this.colorFlesh,
        this.angle,
        6.0,
        false
      ),
    ];
  }

  public update(_boundsWidth = 640, boundsHeight = 480) {
    if (this.state === 'active') {
      this.x += this.vx;
      this.y += this.vy;
      this.vy += this.gravity;
      this.angle = (this.angle + this.rotSpeed) % 360;

      // Check if dropped below screen
      if (this.y > boundsHeight + 50 && this.vy > 0) {
        this.state = 'missed';
      }
    } else if (this.state === 'sliced') {
      for (const half of this.halves) {
        half.update();
      }
      if (this.halves.every((h) => h.y > boundsHeight + 80) || this.halves.length === 0) {
        this.state = 'removed';
      }
    }
  }

  public draw(ctx: CanvasRenderingContext2D) {
    if (this.state === 'sliced') {
      for (const half of this.halves) {
        half.draw(ctx);
      }
      return;
    }

    if (this.state !== 'active') return;

    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate((this.angle * Math.PI) / 180.0);

    if (this.isBomb) {
      this.drawBomb(ctx);
    } else {
      this.drawFruit(ctx);
    }

    ctx.restore();
  }

  private drawFruit(ctx: CanvasRenderingContext2D) {
    const r = this.radius;

    // Outer skin / rind
    ctx.fillStyle = this.colorRind;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.fill();

    // Inner pulp / flesh
    ctx.fillStyle = this.colorFlesh;
    ctx.beginPath();
    ctx.arc(0, 0, r * 0.78, 0, Math.PI * 2);
    ctx.fill();

    // Seeds / fruit detailing
    if (this.fruitType === 'watermelon') {
      ctx.fillStyle = '#141414';
      const seedOffsets = [[-7, -5], [7, -5], [-5, 6], [5, 6]];
      for (const [sx, sy] of seedOffsets) {
        ctx.beginPath();
        ctx.arc(sx, sy, 2, 0, Math.PI * 2);
        ctx.fill();
      }
    } else if (this.fruitType === 'orange') {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
      ctx.lineWidth = 1.5;
      for (let i = 0; i < 6; i++) {
        const segAngle = (i * 60 * Math.PI) / 180.0;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(r * 0.7 * Math.cos(segAngle), r * 0.7 * Math.sin(segAngle));
        ctx.stroke();
      }
    }

    // Specular shine highlight
    ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
    ctx.beginPath();
    ctx.arc(-r * 0.32, -r * 0.32, r * 0.22, 0, Math.PI * 2);
    ctx.fill();

    // Outer border
    ctx.strokeStyle = '#101010';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  private drawBomb(ctx: CanvasRenderingContext2D) {
    const r = this.radius;

    // Bomb body
    ctx.fillStyle = '#242424';
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#0F0F0F';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Shine
    ctx.fillStyle = 'rgba(120, 120, 120, 0.5)';
    ctx.beginPath();
    ctx.arc(-r * 0.3, -r * 0.3, r * 0.2, 0, Math.PI * 2);
    ctx.fill();

    // Fuse
    ctx.strokeStyle = '#A0522D';
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo(0, -r);
    ctx.quadraticCurveTo(8, -r - 10, 12, -r - 14);
    ctx.stroke();

    // Animated glowing spark
    this.sparkPhase = (this.sparkPhase + 0.3) % (Math.PI * 2);
    const sparkR = 5 + 2 * Math.sin(this.sparkPhase);

    ctx.fillStyle = '#FF4500';
    ctx.beginPath();
    ctx.arc(12, -r - 14, sparkR + 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#FFD700';
    ctx.beginPath();
    ctx.arc(12, -r - 14, sparkR, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.arc(12, -r - 14, 2, 0, Math.PI * 2);
    ctx.fill();

    // Danger 'X' symbol
    ctx.fillStyle = '#FF3333';
    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('✕', 0, 1);
  }
}
