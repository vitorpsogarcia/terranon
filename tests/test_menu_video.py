import math
import os
import sys
import unittest
from pathlib import Path
import numpy as np
import pygame

# Set up paths
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "scripts"))

from core.manager.game_manager import GameManager
from core.manager.state_manager import StateManager
from core.settings.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from core.states.ui.menu_state import MenuBackgroundVideo, TitleMenuScene
from generate_menu_video import MenuBackgroundRenderer


class TestMenuBackgroundRenderer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.w = SCREEN_WIDTH
        self.h = SCREEN_HEIGHT
        self.duration = 8.0
        self.renderer = MenuBackgroundRenderer(
            width=self.w, height=self.h, duration=self.duration
        )

    def test_initialization(self):
        """Verifica se o renderer inicializa estrelas, nebulosas e nave corretamente."""
        self.assertEqual(self.renderer.w, self.w)
        self.assertEqual(self.renderer.h, self.h)
        self.assertEqual(self.renderer.duration, self.duration)
        self.assertGreater(len(self.renderer.stars), 100)
        self.assertGreater(len(self.renderer.nebulae), 0)
        self.assertEqual(len(self.renderer.shooting_stars), 2)
        self.assertIsNotNone(self.renderer.ship_base_sprite)

    def test_perfect_loop_identity(self):
        """O frame em t=0 e o frame em t=duration devem ser matematicamente idênticos (diferença <= 1)."""
        surf_t0 = pygame.Surface((self.w, self.h))
        self.renderer.render(surf_t0, 0.0)

        surf_tend = pygame.Surface((self.w, self.h))
        self.renderer.render(surf_tend, self.duration)

        arr0 = pygame.surfarray.array3d(surf_t0).astype(np.int32)
        arr_end = pygame.surfarray.array3d(surf_tend).astype(np.int32)

        max_diff = np.max(np.abs(arr0 - arr_end))
        self.assertLessEqual(max_diff, 1)

    def test_shooting_stars_timing(self):
        """Estrelas cadentes não devem estar ativas no início (t=0) nem no fim (t=duration)."""
        for star in self.renderer.shooting_stars:
            # Não pode estar ativa em t=0
            self.assertFalse(star.start_time <= 0.0 <= star.start_time + star.duration)
            # Não pode estar ativa em t=duration
            self.assertFalse(
                star.start_time <= self.duration <= star.start_time + star.duration
            )

    def test_render_at_multiple_timestamps(self):
        """Garante que a renderização ocorre sem exceções ao longo de todo o ciclo de tempo."""
        test_surface = pygame.Surface((self.w, self.h))
        for t in [0.0, 1.5, 3.0, 4.8, 6.0, 8.0]:
            self.renderer.render(test_surface, t)


class TestMenuBackgroundVideo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.surface = pygame.Surface(self.screen_size)
        self.gm = GameManager(self.surface)
        self.sm = StateManager(self.gm)
        self.menu = TitleMenuScene(self.sm, self.screen_size)

    def tearDown(self):
        self.menu.exit()

    def test_menu_background_video_initialization(self):
        """TitleMenuScene deve inicializar o MenuBackgroundVideo."""
        self.assertIsNotNone(self.menu.bg_video)
        self.assertTrue(isinstance(self.menu.bg_video, MenuBackgroundVideo))

    def test_menu_background_video_graceful_missing_file(self):
        """MenuBackgroundVideo deve lidar com arquivos inexistentes sem lançar exceções."""
        dummy_video = MenuBackgroundVideo(Path("assets/videos/non_existent.mp4"))
        dummy_video.start()
        dummy_video.update(0.1)
        test_surf = pygame.Surface(self.screen_size)
        dummy_video.draw(test_surf)
        dummy_video.close()

    def test_menu_update_and_draw_with_video(self):
        """Menu principal deve atualizar frames do vídeo e desenhar na tela normalmente."""
        self.menu.enter()
        self.menu.update(0.033)
        self.menu.draw(self.surface)


if __name__ == "__main__":
    unittest.main()

