import os
import sys
import unittest
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.camera_group import CameraGroup
from core.components.animator_component import AnimatorComponent
from core.components.health_component import HealthComponent
from core.enums.game_event_enum import GameEventEnum
from core.game_object import GameObject
from core.manager.effect_manager import EffectManager, FloatingText, Particles
from core.manager.event_manager import EventManager


class DummyOwner(GameObject):
    def __init__(self):
        super().__init__(pygame.Vector2(100, 100))
        self.animator = AnimatorComponent(self)
        self.render_component = self.animator


class DummyPlayer(GameObject):
    def __init__(self):
        super().__init__(pygame.Vector2(200, 200))
        self.animator = AnimatorComponent(self)
        self.render_component = self.animator


class TestGameJuice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()
        cls.surface = pygame.Surface((800, 600))

    def setUp(self):
        EffectManager().clear()

    def test_floating_text_update_and_decay(self):
        font = pygame.font.SysFont("Arial", 12)
        initial_pos = pygame.Vector2(100, 100)
        ft = FloatingText(
            pos=initial_pos,
            text="15",
            color=(255, 230, 80),
            font=font,
            duration=0.5,
        )

        initial_y = ft.pos.y
        alive = ft.update(0.1)
        self.assertTrue(alive)
        self.assertLess(ft.pos.y, initial_y)  # Moves upwards

        # Should draw without errors
        ft.draw(self.surface, pygame.Vector2(0, 0))

        # Update until expired
        alive = ft.update(0.5)
        self.assertFalse(alive)

    def test_particles_update_and_decay(self):
        p = Particles(
            pos=pygame.Vector2(50, 50),
            velocity=pygame.Vector2(100, -50),
            color=(255, 200, 50),
            size=4.0,
            duration=0.4,
        )
        self.assertEqual(p.velocity.x, 100)
        self.assertEqual(p.velocity.y, -50)

        alive = p.update(0.1)
        self.assertTrue(alive)
        self.assertGreater(p.pos.x, 50)
        self.assertLess(p.pos.y, 50)

        p.draw(self.surface, pygame.Vector2(0, 0))

        alive = p.update(0.35)
        self.assertFalse(alive)

    def test_effect_manager_singleton_and_batch_handling(self):
        mgr = EffectManager()
        mgr.clear()

        mgr.add_floating_text(pygame.Vector2(10, 10), "99")
        mgr.add_particle(pygame.Vector2(10, 10), count=6)

        self.assertEqual(len(mgr.texts), 1)
        self.assertEqual(len(mgr.particles), 6)

        # Batch draw and update
        mgr.draw(self.surface, pygame.Vector2(0, 0))
        mgr.update(0.01)

        self.assertEqual(len(mgr.texts), 1)
        self.assertEqual(len(mgr.particles), 6)

        # Expire all
        mgr.update(1.0)
        self.assertEqual(len(mgr.texts), 0)
        self.assertEqual(len(mgr.particles), 0)

        mgr.add_floating_text(pygame.Vector2(10, 10), "10")
        mgr.clear()
        self.assertEqual(len(mgr.texts), 0)

    def test_camera_shake(self):
        cam = CameraGroup()
        self.assertEqual(cam.shake_offset, pygame.Vector2(0, 0))

        cam.shake(intensity=12.0, duration=0.3)
        self.assertEqual(cam.shake_timer, 0.3)
        self.assertEqual(cam.shake_intensity, 12.0)

        cam.update_shake(0.1)
        self.assertGreater(cam.shake_timer, 0)
        # Offset should have been jittered
        self.assertIsInstance(cam.shake_offset.x, float)
        self.assertIsInstance(cam.shake_offset.y, float)

        # Finish shake
        cam.update_shake(0.25)
        self.assertEqual(cam.shake_timer, 0.0)
        self.assertEqual(cam.shake_offset, pygame.Vector2(0, 0))

    def test_animator_hit_flash(self):
        owner = DummyOwner()
        animator = owner.animator

        frame = pygame.Surface((32, 32))
        frame.fill((100, 100, 100))
        animator.add_animation("idle", [frame], frame_duration=1.0)
        animator.play("idle")
        animator.update(0.0)

        self.assertEqual(animator.flash_timer, 0.0)
        animator.trigger_flash(0.08)
        self.assertEqual(animator.flash_timer, 0.08)

        # Drawing during flash
        animator.draw(self.surface, pygame.Vector2(0, 0))

        animator.update(0.04)
        self.assertAlmostEqual(animator.flash_timer, 0.04)

        animator.update(0.05)
        self.assertLessEqual(animator.flash_timer, 0.0)

    def test_health_component_triggers_flash_and_player_shake(self):
        player = DummyPlayer()
        health = HealthComponent(max_hp=100.0)
        health.owner = player

        shake_events = []

        def on_shake(data):
            shake_events.append(data)

        EventManager().subscribe(GameEventEnum.SCREEN_SHAKE, on_shake)

        health.take_damage(20.0)

        # Hit flash triggered on animator
        self.assertGreater(player.animator.flash_timer, 0.0)

        # Screen shake event received for player damage
        self.assertEqual(len(shake_events), 1)
        self.assertGreaterEqual(shake_events[0]["intensity"], 7.0)

        EventManager().unsubscribe(GameEventEnum.SCREEN_SHAKE, on_shake)

    def test_enemy_take_damage_flash_and_death_particles(self):
        from unittest.mock import MagicMock
        from core.enums.enemy_enum import EnemyEnum
        from core.factories.enemy_factory import EnemyFactory

        mock_polyline = MagicMock()
        enemy = EnemyFactory.create_enemy(
            EnemyEnum.GOBLIN, pygame.Vector2(100, 100), mock_polyline, points=10
        )
        # Verify owner is set
        self.assertIs(enemy.health.owner, enemy)

        # Taking damage
        enemy.take_damage(5.0, by_player=True)
        self.assertEqual(enemy.health.current_hp, 15.0)
        self.assertGreater(enemy.animator.flash_timer, 0.0)

        # Lethal damage triggers death particles
        enemy.take_damage(20.0, by_player=True)
        self.assertTrue(enemy.health.is_dead)
        self.assertGreater(len(EffectManager().particles), 0)

    def test_crosshair_cursor(self):
        from utils.cursor import (
            create_crosshair_surface,
            get_crosshair_cursor,
            set_game_cursor,
            set_ui_cursor,
        )

        surf = create_crosshair_surface(size=31)
        self.assertEqual(surf.get_size(), (31, 31))

        cursor = get_crosshair_cursor()
        self.assertIsInstance(cursor, pygame.cursors.Cursor)

        # Should execute safely without raising any exceptions
        set_game_cursor()
        set_ui_cursor()


if __name__ == "__main__":
    unittest.main()
