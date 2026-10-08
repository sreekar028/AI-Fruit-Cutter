/**
 * web/src/game/Fruit.ts
 * =====================
 * Game Logic Module — Web Version (Member 2 equivalent)
 * 
 * Replicates Member 2's Fruit system:
 * - 12 distinct fruit types plus the bomb hazard
 * - Physics: Position, velocity, gravity, rotation
 * - Slicing: Splits into two separate rotating halves separating along cut normal
 * - HTML5 Canvas rendering matching the desktop visual style
 */

export type FruitType =
  | 'apple'
  | 'banana'
  | 'orange'
  | 'watermelon'
  | 'pineapple'
  | 'strawberry'
  | 'mango'
  | 'grapes'
  | 'kiwi'
  | 'peach'
  | 'lemon'
  | 'coconut'
  | 'bomb';

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

export const FRUIT_TYPES: Record<FruitType, FruitTypeConfig> = {
  watermelon: {
    name: 'Watermelon',
    radius: 38,
    points: 10,
    colorRind: '#287947',
    colorFlesh: '#D72638',
    colorSeed: '#141414',
    colorSplash: '#E63946',
    isBomb: false,
  },
  apple: {
    name: 'Apple',
    radius: 29,
    points: 15,
    colorRind: '#C92E37',
    colorFlesh: '#FDF0D5',
    colorSeed: '#141414',
    colorSplash: '#E63946',
    isBomb: false,
  },
  banana: {
    name: 'Banana',
    radius: 31,
    points: 20,
    colorRind: '#F4CA45',
    colorFlesh: '#FFF3B0',
    colorSeed: '#C9A227',
    colorSplash: '#FFE66D',
    isBomb: false,
  },
  orange: {
    name: 'Orange',
    radius: 30,
    points: 10,
    colorRind: '#ED791B',
    colorFlesh: '#FFA200',
    colorSeed: '#FFFFFF',
    colorSplash: '#FF9E00',
    isBomb: false,
  },
  strawberry: {
    name: 'Strawberry',
    radius: 25,
    points: 25,
    colorRind: '#D93445',
    colorFlesh: '#F48498',
    colorSeed: '#2A9D8F',
    colorSplash: '#FF4D6D',
    isBomb: false,
  },
  pineapple: {
    name: 'Pineapple',
    radius: 34,
    points: 20,
    colorRind: '#C89132',
    colorFlesh: '#F6D96B',
    colorSeed: '#557D38',
    colorSplash: '#F6D96B',
    isBomb: false,
  },
  mango: {
    name: 'Mango',
    radius: 31,
    points: 15,
    colorRind: '#E5A535',
    colorFlesh: '#FFC95D',
    colorSeed: '#8A522A',
    colorSplash: '#FFB52E',
    isBomb: false,
  },
  grapes: {
    name: 'Grapes',
    radius: 24,
    points: 25,
    colorRind: '#70449B',
    colorFlesh: '#B994D8',
    colorSeed: '#36254C',
    colorSplash: '#9867BD',
    isBomb: false,
  },
  kiwi: {
    name: 'Kiwi',
    radius: 27,
    points: 20,
    colorRind: '#81523A',
    colorFlesh: '#91B949',
    colorSeed: '#24251D',
    colorSplash: '#9CCB4A',
    isBomb: false,
  },
  peach: {
    name: 'Peach',
    radius: 29,
    points: 15,
    colorRind: '#EF9D78',
    colorFlesh: '#FFD1A1',
    colorSeed: '#8A4B36',
    colorSplash: '#F9A27C',
    isBomb: false,
  },
  lemon: {
    name: 'Lemon',
    radius: 27,
    points: 15,
    colorRind: '#E5C637',
    colorFlesh: '#FFF18A',
    colorSeed: '#B49C3B',
    colorSplash: '#FFE75A',
    isBomb: false,
  },
  coconut: {
    name: 'Coconut',
    radius: 33,
    points: 20,
    colorRind: '#76513A',
    colorFlesh: '#F8F1DD',
    colorSeed: '#493226',
    colorSplash: '#EDE3CC',
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

const grapePositions: Array<[number, number, number]> = [
  [-0.34, -0.42, 0.25], [0.02, -0.48, 0.27], [0.36, -0.30, 0.24],
  [-0.48, -0.05, 0.24], [-0.12, -0.10, 0.27], [0.25, 0.02, 0.26],
  [-0.30, 0.30, 0.25], [0.06, 0.34, 0.26], [0.35, 0.35, 0.21],
];

function traceFruitShape(ctx: CanvasRenderingContext2D, type: FruitType, r: number) {
  ctx.beginPath();

  switch (type) {
    case 'apple':
      ctx.moveTo(0, -r * 0.73);
      ctx.bezierCurveTo(-r * 0.16, -r * 1.12, -r * 0.88, -r * 0.82, -r * 0.94, -r * 0.22);
      ctx.bezierCurveTo(-r * 1.04, r * 0.46, -r * 0.51, r * 0.94, -r * 0.10, r * 0.91);
      ctx.quadraticCurveTo(0, r * 0.84, r * 0.10, r * 0.91);
      ctx.bezierCurveTo(r * 0.56, r * 0.96, r * 1.02, r * 0.43, r * 0.94, -r * 0.22);
      ctx.bezierCurveTo(r * 0.86, -r * 0.83, r * 0.17, -r * 1.08, 0, -r * 0.73);
      break;
    case 'banana':
      ctx.moveTo(-r * 0.92, -r * 0.50);
      ctx.bezierCurveTo(-r * 0.48, -r * 0.03, r * 0.05, r * 0.13, r * 0.91, -r * 0.60);
      ctx.quadraticCurveTo(r * 0.68, r * 0.73, r * 0.05, r * 0.62);
      ctx.bezierCurveTo(-r * 0.51, r * 0.54, -r * 0.88, r * 0.15, -r * 0.92, -r * 0.50);
      break;
    case 'watermelon':
      ctx.ellipse(0, 0, r * 0.96, r * 0.83, 0, 0, Math.PI * 2);
      break;
    case 'pineapple':
      ctx.moveTo(-r * 0.68, -r * 0.65);
      ctx.quadraticCurveTo(-r * 0.92, 0, -r * 0.57, r * 0.72);
      ctx.quadraticCurveTo(0, r * 1.03, r * 0.57, r * 0.72);
      ctx.quadraticCurveTo(r * 0.92, 0, r * 0.68, -r * 0.65);
      ctx.quadraticCurveTo(0, -r * 0.95, -r * 0.68, -r * 0.65);
      break;
    case 'strawberry':
      ctx.moveTo(-r * 0.79, -r * 0.44);
      ctx.bezierCurveTo(-r * 0.50, -r * 0.90, r * 0.52, -r * 0.84, r * 0.80, -r * 0.40);
      ctx.bezierCurveTo(r * 0.91, 0.02, r * 0.30, r * 0.74, 0, r * 0.99);
      ctx.bezierCurveTo(-r * 0.30, r * 0.74, -r * 0.91, 0.02, -r * 0.79, -r * 0.44);
      break;
    case 'mango':
      ctx.moveTo(-r * 0.59, -r * 0.75);
      ctx.bezierCurveTo(-r * 1.03, -r * 0.28, -r * 0.59, r * 0.62, 0, r * 0.85);
      ctx.bezierCurveTo(r * 0.55, r * 1.04, r * 0.97, r * 0.25, r * 0.79, -r * 0.36);
      ctx.bezierCurveTo(r * 0.59, -r * 0.90, -r * 0.02, -r * 1.04, -r * 0.59, -r * 0.75);
      break;
    case 'grapes':
      for (const [x, y, size] of grapePositions) {
        ctx.moveTo(x * r + size * r, y * r);
        ctx.arc(x * r, y * r, size * r, 0, Math.PI * 2);
      }
      break;
    case 'kiwi':
    case 'orange':
    case 'coconut':
      ctx.ellipse(0, 0, r * (type === 'kiwi' ? 0.79 : 0.9), r * 0.84, 0, 0, Math.PI * 2);
      break;
    case 'peach':
      ctx.moveTo(0, -r * 0.76);
      ctx.bezierCurveTo(-r * 0.38, -r * 1.02, -r * 0.91, -r * 0.65, -r * 0.94, -r * 0.07);
      ctx.bezierCurveTo(-r * 0.98, r * 0.55, -r * 0.46, r * 0.96, 0, r * 0.88);
      ctx.bezierCurveTo(r * 0.48, r * 0.96, r * 0.99, r * 0.50, r * 0.93, -r * 0.08);
      ctx.bezierCurveTo(r * 0.87, -r * 0.62, r * 0.40, -r * 1.02, 0, -r * 0.76);
      break;
    case 'lemon':
      ctx.moveTo(-r, 0);
      ctx.quadraticCurveTo(-r * 0.45, -r * 0.91, 0, -r * 0.72);
      ctx.quadraticCurveTo(r * 0.45, -r * 0.91, r, 0);
      ctx.quadraticCurveTo(r * 0.45, r * 0.91, 0, r * 0.72);
      ctx.quadraticCurveTo(-r * 0.45, r * 0.91, -r, 0);
      break;
    default:
      ctx.ellipse(0, 0, r, r, 0, 0, Math.PI * 2);
  }

  ctx.closePath();
}

function drawFruitArtwork(
  ctx: CanvasRenderingContext2D,
  type: FruitType,
  r: number,
  rind: string
) {
  if (type === 'grapes') {
    for (const [x, y, size] of grapePositions) {
      const grapeR = size * r;
      const gradient = ctx.createRadialGradient(
        x * r - grapeR * 0.35, y * r - grapeR * 0.42, grapeR * 0.08,
        x * r, y * r, grapeR
      );
      gradient.addColorStop(0, '#C9A6E5');
      gradient.addColorStop(0.46, rind);
      gradient.addColorStop(1, '#44265F');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x * r, y * r, grapeR, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255,255,255,0.48)';
      ctx.beginPath();
      ctx.ellipse(x * r - grapeR * 0.3, y * r - grapeR * 0.36, grapeR * 0.17, grapeR * 0.10, -0.5, 0, Math.PI * 2);
      ctx.fill();
    }
  } else {
    traceFruitShape(ctx, type, r);
    const skin = ctx.createRadialGradient(-r * 0.35, -r * 0.4, r * 0.08, 0, 0, r * 1.2);
    skin.addColorStop(0, type === 'watermelon' ? '#63A95D' : '#FFF0B1');
    skin.addColorStop(0.23, rind);
    skin.addColorStop(1, type === 'apple' ? '#782832' : '#59402A');
    ctx.fillStyle = skin;
    ctx.shadowColor = 'rgba(0,0,0,0.34)';
    ctx.shadowBlur = Math.max(3, r * 0.15);
    ctx.shadowOffsetY = Math.max(1, r * 0.07);
    ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    ctx.strokeStyle = 'rgba(42,24,17,0.55)';
    ctx.lineWidth = Math.max(1, r * 0.055);
    ctx.stroke();
  }

  ctx.save();
  traceFruitShape(ctx, type, r);
  ctx.clip();

  if (type === 'watermelon') {
    ctx.lineWidth = Math.max(2, r * 0.12);
    for (const x of [-0.61, -0.28, 0.08, 0.43, 0.70]) {
      ctx.strokeStyle = x % 2 ? 'rgba(13,80,49,0.70)' : 'rgba(180,220,117,0.62)';
      ctx.beginPath();
      ctx.moveTo(x * r, -r);
      ctx.bezierCurveTo((x - 0.16) * r, -r * 0.36, (x + 0.17) * r, r * 0.30, x * r, r);
      ctx.stroke();
    }
  } else if (type === 'pineapple') {
    ctx.strokeStyle = 'rgba(105,67,27,0.66)';
    ctx.lineWidth = Math.max(1, r * 0.035);
    for (let row = -3; row <= 3; row++) {
      for (let col = -3; col <= 3; col++) {
        const x = col * r * 0.25 + (row % 2) * r * 0.12;
        const y = row * r * 0.21;
        ctx.beginPath();
        ctx.moveTo(x, y - r * 0.07);
        ctx.lineTo(x + r * 0.06, y);
        ctx.lineTo(x, y + r * 0.07);
        ctx.stroke();
      }
    }
  } else if (type === 'orange' || type === 'lemon') {
    ctx.fillStyle = 'rgba(255,245,190,0.25)';
    for (let i = 0; i < 26; i++) {
      const x = (((i * 37) % 97) / 100 - 0.48) * r * 1.6;
      const y = (((i * 61) % 89) / 100 - 0.44) * r * 1.5;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(0.55, r * 0.018), 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (type === 'strawberry') {
    ctx.fillStyle = '#FBE3A0';
    for (const [x, y] of [[-0.42, -0.30], [0, -0.42], [0.40, -0.28], [-0.52, 0.04], [-0.16, -0.03], [0.26, -0.02], [0.53, 0.12], [-0.34, 0.35], [0.04, 0.28], [0.34, 0.38], [0, 0.58]]) {
      ctx.save();
      ctx.translate(x * r, y * r);
      ctx.rotate(-0.35);
      ctx.ellipse(0, 0, r * 0.035, r * 0.07, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  } else if (type === 'kiwi' || type === 'coconut') {
    ctx.strokeStyle = type === 'kiwi' ? 'rgba(236,207,148,0.52)' : 'rgba(205,178,145,0.43)';
    ctx.lineWidth = Math.max(0.7, r * 0.025);
    for (let i = 0; i < 22; i++) {
      const x = (((i * 29) % 83) / 100 - 0.4) * r * 1.35;
      const y = (((i * 43) % 79) / 100 - 0.38) * r * 1.25;
      ctx.beginPath();
      ctx.moveTo(x - r * 0.035, y + r * 0.04);
      ctx.lineTo(x + r * 0.035, y - r * 0.04);
      ctx.stroke();
    }
  } else if (type === 'peach') {
    ctx.strokeStyle = 'rgba(255,240,212,0.55)';
    ctx.lineWidth = Math.max(1, r * 0.035);
    ctx.beginPath();
    ctx.moveTo(0, -r * 0.72);
    ctx.bezierCurveTo(-r * 0.11, -r * 0.16, r * 0.12, r * 0.32, 0, r * 0.84);
    ctx.stroke();
  }
  ctx.restore();

  if (type === 'apple') {
    ctx.strokeStyle = '#67412A';
    ctx.lineWidth = r * 0.12;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(0, -r * 0.72);
    ctx.quadraticCurveTo(r * 0.02, -r * 1.02, r * 0.14, -r * 1.10);
    ctx.stroke();
    drawLeaf(ctx, r * 0.12, -r * 0.88, r * 0.38, '#4E8A3E');
  } else if (type === 'banana') {
    ctx.strokeStyle = 'rgba(255,244,169,0.78)';
    ctx.lineWidth = r * 0.065;
    ctx.beginPath();
    ctx.moveTo(-r * 0.66, -r * 0.35);
    ctx.quadraticCurveTo(0, r * 0.18, r * 0.70, -r * 0.42);
    ctx.stroke();
    ctx.fillStyle = '#765139';
    for (const x of [-0.89, 0.86]) {
      ctx.beginPath();
      ctx.ellipse(x * r, -r * 0.50, r * 0.09, r * 0.07, x, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (type === 'pineapple') {
    ctx.fillStyle = '#476F38';
    for (let i = -2; i <= 2; i++) {
      const x = i * r * 0.13;
      ctx.beginPath();
      ctx.moveTo(x - r * 0.10, -r * 0.61);
      ctx.quadraticCurveTo(x - r * 0.25, -r * 1.03, x - r * 0.20, -r * 1.10);
      ctx.quadraticCurveTo(x + r * 0.06, -r * 0.96, x + r * 0.12, -r * 0.62);
      ctx.closePath();
      ctx.fill();
    }
  } else if (type === 'strawberry') {
    ctx.fillStyle = '#4A8A45';
    for (let i = 0; i < 5; i++) {
      const angle = Math.PI + (i / 4) * Math.PI;
      ctx.beginPath();
      ctx.ellipse(Math.cos(angle) * r * 0.39, -r * 0.63 + Math.sin(angle) * r * 0.13, r * 0.21, r * 0.09, angle, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (type === 'mango') {
    const blush = ctx.createRadialGradient(-r * 0.40, r * 0.18, r * 0.03, -r * 0.25, r * 0.12, r * 0.9);
    blush.addColorStop(0, 'rgba(224,61,39,0.65)');
    blush.addColorStop(1, 'rgba(224,61,39,0)');
    ctx.fillStyle = blush;
    ctx.beginPath();
    ctx.ellipse(-r * 0.20, r * 0.08, r * 0.8, r * 0.75, -0.45, 0, Math.PI * 2);
    ctx.fill();
    drawLeaf(ctx, r * 0.43, -r * 0.67, r * 0.35, '#4F873A');
  } else if (type === 'grapes') {
    ctx.strokeStyle = '#536B3B';
    ctx.lineWidth = r * 0.08;
    ctx.beginPath();
    ctx.moveTo(0, -r * 0.42);
    ctx.lineTo(r * 0.05, -r * 0.67);
    ctx.stroke();
    drawLeaf(ctx, r * 0.06, -r * 0.58, r * 0.43, '#608C43');
  } else if (type === 'kiwi') {
    ctx.fillStyle = 'rgba(255,255,235,0.67)';
    ctx.beginPath();
    ctx.ellipse(-r * 0.28, -r * 0.32, r * 0.20, r * 0.09, -0.5, 0, Math.PI * 2);
    ctx.fill();
  } else if (type === 'peach') {
    drawLeaf(ctx, r * 0.34, -r * 0.68, r * 0.32, '#5A873F');
  } else if (type === 'lemon') {
    ctx.strokeStyle = 'rgba(255,248,184,0.74)';
    ctx.lineWidth = r * 0.07;
    ctx.beginPath();
    ctx.moveTo(-r * 0.61, -r * 0.05);
    ctx.quadraticCurveTo(0, -r * 0.28, r * 0.62, -r * 0.06);
    ctx.stroke();
  } else if (type === 'coconut') {
    ctx.fillStyle = '#443027';
    for (const [x, y] of [[-0.26, -0.12], [0, -0.20], [0.24, -0.10]]) {
      ctx.beginPath();
      ctx.arc(x * r, y * r, r * 0.07, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (type === 'orange') {
    ctx.fillStyle = '#4F7B3E';
    ctx.beginPath();
    ctx.ellipse(r * 0.12, -r * 0.83, r * 0.16, r * 0.08, -0.5, 0, Math.PI * 2);
    ctx.fill();
  }

  if (type !== 'grapes') {
    const shine = ctx.createRadialGradient(-r * 0.34, -r * 0.38, 0, -r * 0.34, -r * 0.38, r * 0.42);
    shine.addColorStop(0, 'rgba(255,255,255,0.38)');
    shine.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = shine;
    ctx.beginPath();
    ctx.ellipse(-r * 0.24, -r * 0.25, r * 0.48, r * 0.31, -0.65, 0, Math.PI * 2);
    ctx.fill();
  }

}

function drawLeaf(ctx: CanvasRenderingContext2D, x: number, y: number, size: number, color: string) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(-0.48);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(-size * 0.55, 0);
  ctx.quadraticCurveTo(0, -size * 0.48, size * 0.62, -size * 0.08);
  ctx.quadraticCurveTo(size * 0.03, size * 0.42, -size * 0.55, 0);
  ctx.fill();
  ctx.strokeStyle = 'rgba(220,239,171,0.7)';
  ctx.lineWidth = Math.max(0.7, size * 0.035);
  ctx.beginPath();
  ctx.moveTo(-size * 0.46, 0);
  ctx.lineTo(size * 0.48, -size * 0.08);
  ctx.stroke();
  ctx.restore();
}

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
  public age = 0;
  public fruitType: FruitType;
  public colorSeed: string;

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
    isLeft: boolean,
    fruitType: FruitType,
    colorSeed: string
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
    this.fruitType = fruitType;
    this.colorSeed = colorSeed;
  }

  public update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += this.gravity;
    this.angle += this.rotSpeed;
    this.age += 1;
  }

  public draw(ctx: CanvasRenderingContext2D) {
    ctx.save();
    ctx.globalAlpha = Math.max(0, 1 - this.age / 72);
    ctx.translate(this.x, this.y);
    ctx.rotate((this.angle * Math.PI) / 180.0);

    ctx.beginPath();
    if (this.isLeft) {
      ctx.rect(-this.radius * 1.5, -this.radius * 1.5, this.radius * 1.5, this.radius * 3);
    } else {
      ctx.rect(0, -this.radius * 1.5, this.radius * 1.5, this.radius * 3);
    }
    ctx.clip();
    drawFruitArtwork(ctx, this.fruitType, this.radius, this.colorRind);

    const face = ctx.createLinearGradient(-this.radius * 0.08, 0, this.radius * 0.08, 0);
    face.addColorStop(0, this.colorFlesh);
    face.addColorStop(0.5, '#FFF8E8');
    face.addColorStop(1, this.colorFlesh);
    ctx.fillStyle = face;
    ctx.fillRect(-this.radius * 0.06, -this.radius * 0.62, this.radius * 0.12, this.radius * 1.24);
    ctx.strokeStyle = 'rgba(255,255,255,0.78)';
    ctx.lineWidth = Math.max(1, this.radius * 0.035);
    ctx.beginPath();
    ctx.moveTo(0, -this.radius * 0.62);
    ctx.lineTo(0, this.radius * 0.62);
    ctx.stroke();

    if (this.fruitType === 'watermelon' || this.fruitType === 'kiwi' || this.fruitType === 'apple') {
      ctx.fillStyle = this.colorSeed;
      for (const [x, y] of [[-0.20, -0.32], [0.20, -0.18], [-0.18, 0.05], [0.20, 0.25]]) {
        ctx.beginPath();
        ctx.ellipse(x * this.radius, y * this.radius, this.radius * 0.035, this.radius * 0.065, -0.35, 0, Math.PI * 2);
        ctx.fill();
      }
    }
    ctx.restore();
  }
}

export class Fruit {
  public fruitType: FruitType;
  public name: string;
  public radius: number;
  public points: number;
  public isBomb: boolean;
  public colorRind: string;
  public colorFlesh: string;
  public colorSeed: string;
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
    fruitType: FruitType = 'watermelon',
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
    this.colorSeed = config.colorSeed ?? '#33271F';
    this.colorSplash = config.colorSplash;

    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.gravity = gravity;

    this.angle = Math.random() * 360;
    this.rotSpeed = (Math.random() < 0.5 ? -1 : 1) * (0.45 + Math.random() * 1.75);
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
        true,
        this.fruitType,
        this.colorSeed
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
        false,
        this.fruitType,
        this.colorSeed
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
      if (
        this.halves.length === 0 ||
        this.halves.every((h) => h.y > boundsHeight + 80 || h.age >= 72)
      ) {
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
    drawFruitArtwork(ctx, this.fruitType, this.radius, this.colorRind);
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
