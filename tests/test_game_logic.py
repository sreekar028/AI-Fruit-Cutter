"""
tests/test_game_logic.py
========================
Automated Unit & Integration Test Suite for Game Logic Module (Member 2)
AI Fruit Cutter Game

Tests:
1. Fruit system: creation, physics update, splitting into halves, bounds checking
2. Spawner system: wave spawning, trajectories, intervals, difficulty scaling
3. Collision detection: segment-circle intersection, trajectory sweep, speed checks
4. ScoreManager: fruit points, combos, bonuses, bomb reset
5. LivesManager: missed fruits, bomb penalty, game over trigger
6. GameTimer: elapsed time, countdown mode, time up
7. GameStateManager: state transitions, key bindings
8. GameEngine: headless logic update, Member 1 motion_data integration
"""

import time
import unittest
from game.fruit import Fruit, FruitHalf, FRUIT_TYPES
from game.spawner import FruitSpawner
from game.collision import CollisionDetector
from game.score_manager import ScoreManager
from game.lives_manager import LivesManager
from game.timer import GameTimer
from game.game_state import GameState, GameStateManager
from game.game_engine import GameEngine


class TestFruitSystem(unittest.TestCase):
    """Test Fruit creation, physics, and slicing mechanics."""

    def test_fruit_initialization(self):
        fruit = Fruit(fruit_type="watermelon", x=300, y=400, vx=2.0, vy=-15.0)
        self.assertEqual(fruit.fruit_type, "watermelon")
        self.assertEqual(fruit.points, 10)
        self.assertFalse(fruit.is_bomb)
        self.assertTrue(fruit.is_active)
        self.assertEqual(len(fruit.halves), 0)

    def test_bomb_initialization(self):
        bomb = Fruit(fruit_type="bomb", x=200, y=300)
        self.assertTrue(bomb.is_bomb)
        self.assertEqual(bomb.points, 0)
        self.assertTrue(bomb.is_active)

    def test_fruit_physics_update(self):
        fruit = Fruit(fruit_type="apple", x=100.0, y=200.0, vx=3.0, vy=-10.0, gravity=0.5)
        fruit.update(640, 480)
        self.assertEqual(fruit.x, 103.0)
        self.assertEqual(fruit.y, 190.0)
        self.assertEqual(fruit.vy, -9.5)  # -10 + 0.5

    def test_fruit_slice_splits_into_halves(self):
        fruit = Fruit(fruit_type="orange", x=320, y=240, vx=0, vy=0)
        fruit.slice(cut_angle=45.0)
        self.assertTrue(fruit.is_sliced)
        self.assertFalse(fruit.is_active)
        self.assertEqual(len(fruit.halves), 2)
        self.assertIsInstance(fruit.halves[0], FruitHalf)
        self.assertIsInstance(fruit.halves[1], FruitHalf)

    def test_fruit_out_of_bounds(self):
        fruit = Fruit(fruit_type="banana", x=320, y=550, vy=5.0)
        fruit.update(640, 480)
        self.assertEqual(fruit.state, "missed")
        self.assertTrue(fruit.is_out_of_bounds(640, 480))


class TestSpawnerSystem(unittest.TestCase):
    """Test FruitSpawner wave generation and trajectory rules."""

    def test_spawner_generates_fruits(self):
        spawner = FruitSpawner(bounds_width=640, bounds_height=480, base_interval=0.1)
        fruits = spawner.update(current_time=1.0, current_score=0)
        self.assertGreater(len(fruits), 0)
        for f in fruits:
            self.assertGreaterEqual(f.y, 480)  # Launched from bottom
            self.assertLess(f.vy, 0)           # Upward velocity

    def test_spawner_difficulty_scaling(self):
        spawner = FruitSpawner(bounds_width=640, bounds_height=480, base_interval=2.0)
        spawner.update(current_time=1.0, current_score=0)
        interval_low = spawner._current_interval

        spawner.update(current_time=3.0, current_score=250)
        interval_high = spawner._current_interval
        self.assertLess(interval_high, interval_low)


class TestCollisionSystem(unittest.TestCase):
    """Test collision detection against Member 1 motion data."""

    def setUp(self):
        self.detector = CollisionDetector(blade_thickness=10.0)

    def test_direct_hit_when_cutting(self):
        fruit = Fruit(fruit_type="watermelon", x=300.0, y=250.0)
        motion_data = {
            "hand_detected": True,
            "finger_x": 310,
            "finger_y": 255,
            "previous_x": 280,
            "previous_y": 240,
            "trajectory": [(280, 240), (310, 255)],
            "is_cutting": True,
            "movement_speed": 0.8,
            "movement_direction": 45.0,
        }
        hit = self.detector.check_collisions(motion_data, [fruit])
        self.assertEqual(len(hit), 1)
        self.assertTrue(fruit.is_sliced)

    def test_no_cut_if_slow_movement(self):
        fruit = Fruit(fruit_type="apple", x=300.0, y=250.0)
        motion_data = {
            "hand_detected": True,
            "finger_x": 305,
            "finger_y": 252,
            "previous_x": 304,
            "previous_y": 251,
            "trajectory": [(304, 251), (305, 252)],
            "is_cutting": False,
            "movement_speed": 0.05,  # Very slow, not a cut
            "movement_direction": 0.0,
        }
        hit = self.detector.check_collisions(motion_data, [fruit])
        self.assertEqual(len(hit), 0)
        self.assertFalse(fruit.is_sliced)

    def test_no_cut_if_no_hand_detected(self):
        fruit = Fruit(fruit_type="banana", x=300.0, y=250.0)
        motion_data = {
            "hand_detected": False,
            "finger_x": 300,
            "finger_y": 250,
            "is_cutting": True,
            "movement_speed": 1.0,
        }
        hit = self.detector.check_collisions(motion_data, [fruit])
        self.assertEqual(len(hit), 0)


class TestScoreAndCombo(unittest.TestCase):
    """Test scoring by fruit type, high score, and combo multipliers."""

    def setUp(self):
        self.score_mgr = ScoreManager(combo_window_sec=0.5)

    def test_single_fruit_score(self):
        fruit = Fruit(fruit_type="strawberry")
        pts, combo, bonus = self.score_mgr.register_slice(fruit, current_time=1.0)
        self.assertEqual(pts, 25)
        self.assertEqual(combo, 1)
        self.assertEqual(bonus, 0)
        self.assertEqual(self.score_mgr.score, 25)
        self.assertEqual(self.score_mgr.high_score, 25)

    def test_combo_multiplier(self):
        f1 = Fruit(fruit_type="apple")       # 15 pts
        f2 = Fruit(fruit_type="watermelon")  # 10 pts + 5 bonus = 15 pts
        f3 = Fruit(fruit_type="banana")      # 20 pts + 10 bonus = 30 pts

        self.score_mgr.register_slice(f1, current_time=1.0)
        _, combo2, bonus2 = self.score_mgr.register_slice(f2, current_time=1.2)
        _, combo3, bonus3 = self.score_mgr.register_slice(f3, current_time=1.4)

        self.assertEqual(combo2, 2)
        self.assertEqual(bonus2, 5)
        self.assertEqual(combo3, 3)
        self.assertEqual(bonus3, 10)
        self.assertEqual(self.score_mgr.score, 15 + 15 + 30)

    def test_bomb_resets_combo(self):
        f1 = Fruit(fruit_type="apple")
        bomb = Fruit(fruit_type="bomb")

        self.score_mgr.register_slice(f1, current_time=1.0)
        self.assertEqual(self.score_mgr.current_combo, 1)

        self.score_mgr.register_slice(bomb, current_time=1.1)
        self.assertEqual(self.score_mgr.current_combo, 0)


class TestLivesManager(unittest.TestCase):
    """Test 3 lives strike system and bomb damage."""

    def setUp(self):
        self.lives_mgr = LivesManager(max_lives=3, bomb_penalty_lives=1)

    def test_initial_lives(self):
        self.assertEqual(self.lives_mgr.lives, 3)
        self.assertFalse(self.lives_mgr.is_dead)

    def test_fruit_misses_decrease_life(self):
        self.assertFalse(self.lives_mgr.on_fruit_missed())
        self.assertEqual(self.lives_mgr.lives, 2)

        self.assertFalse(self.lives_mgr.on_fruit_missed())
        self.assertEqual(self.lives_mgr.lives, 1)

        is_game_over = self.lives_mgr.on_fruit_missed()
        self.assertEqual(self.lives_mgr.lives, 0)
        self.assertTrue(is_game_over)
        self.assertTrue(self.lives_mgr.is_dead)

    def test_bomb_penalty(self):
        self.lives_mgr.on_bomb_cut()
        self.assertEqual(self.lives_mgr.lives, 2)


class TestGameTimer(unittest.TestCase):
    """Test game clock stopwatch and countdown."""

    def test_survival_stopwatch(self):
        timer = GameTimer()
        timer.start()
        time.sleep(0.05)
        self.assertGreater(timer.elapsed_seconds, 0.04)
        formatted = timer.get_formatted_time()
        self.assertEqual(formatted, "00:00")

    def test_countdown_timer(self):
        timer = GameTimer(countdown_duration=0.1)
        timer.start()
        self.assertFalse(timer.is_time_up)
        time.sleep(0.12)
        self.assertTrue(timer.is_time_up)


class TestGameStateManager(unittest.TestCase):
    """Test game state machine and key handler."""

    def test_state_flow(self):
        sm = GameStateManager(initial_state=GameState.START)
        self.assertTrue(sm.is_start)

        # SPACE to start
        action = sm.handle_key(ord(' '))
        self.assertEqual(action, "start")
        self.assertTrue(sm.is_playing)

        # 'p' to pause
        action = sm.handle_key(ord('p'))
        self.assertEqual(action, "pause")
        self.assertTrue(sm.is_paused)

        # 'p' to resume
        sm.handle_key(ord('p'))
        self.assertTrue(sm.is_playing)

        # Trigger game over
        sm.trigger_game_over()
        self.assertTrue(sm.is_game_over)

        # 'r' to restart
        action = sm.handle_key(ord('r'))
        self.assertEqual(action, "restart")
        self.assertTrue(sm.is_playing)

        # 'q' or ESC to quit
        self.assertEqual(sm.handle_key(ord('q')), "quit")
        self.assertEqual(sm.handle_key(27), "quit")


class TestGameEngineIntegration(unittest.TestCase):
    """Test GameEngine logic step without camera."""

    def test_engine_headless_logic(self):
        engine = GameEngine()
        engine.state_mgr.start_game()
        engine.timer.start()

        # Mock fruit
        fruit = Fruit(fruit_type="apple", x=300, y=250)
        engine.spawner._active_fruits.append(fruit)

        # Mock Member 1 cutting motion
        motion_data = {
            "hand_detected": True,
            "finger_x": 305,
            "finger_y": 255,
            "previous_x": 290,
            "previous_y": 245,
            "trajectory": [(290, 245), (305, 255)],
            "is_cutting": True,
            "movement_speed": 1.2,
            "movement_direction": 45.0,
        }

        events = engine.update_logic(motion_data, current_time=time.time())
        self.assertEqual(len(events["sliced_fruits"]), 1)
        self.assertEqual(engine.score_mgr.score, 15)
        self.assertEqual(engine.lives_mgr.lives, 3)
        self.assertFalse(events["game_over"])


if __name__ == "__main__":
    unittest.main()
