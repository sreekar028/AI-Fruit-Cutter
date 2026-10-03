export const GAME_MODES = {
  EASY: 'easy',
  MEDIUM: 'medium',
  HARD: 'hard',
} as const;

export type GameMode = typeof GAME_MODES[keyof typeof GAME_MODES];

export interface DifficultyConfig {
  label: string;
  fruitSpeedMultiplier: number;
  spawnInterval: number;
  minInterval: number;
  bombChance: number;
  maxConcurrentFruits: number;
}

export const DIFFICULTY_SETTINGS: Record<GameMode, DifficultyConfig> = {
  easy: {
    label: 'EASY',
    fruitSpeedMultiplier: 0.8,
    spawnInterval: 2.8,
    minInterval: 1.8,
    bombChance: 0.08,
    maxConcurrentFruits: 2,
  },
  medium: {
    label: 'MEDIUM',
    fruitSpeedMultiplier: 1,
    spawnInterval: 2.0,
    minInterval: 1.0,
    bombChance: 0.18,
    maxConcurrentFruits: 3,
  },
  hard: {
    label: 'HARD',
    fruitSpeedMultiplier: 1.35,
    spawnInterval: 1.35,
    minInterval: 0.72,
    bombChance: 0.32,
    maxConcurrentFruits: 4,
  },
};

export const getDifficultyConfig = (mode: GameMode): DifficultyConfig => {
  return DIFFICULTY_SETTINGS[mode] ?? DIFFICULTY_SETTINGS.medium;
};
