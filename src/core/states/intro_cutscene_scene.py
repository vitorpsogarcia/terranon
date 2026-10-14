import math
import random
from pathlib import Path

import pygame

from core.enums.game_event_enum import GameEventEnum
from core.enums.game_state_enum import GameStateEnum
from core.manager.event_manager import EventManager
from core.settings.settings import ASSETS_FOLDER, SCREEN_HEIGHT, SCREEN_WIDTH
from core.states.base_state import GameScene
from utils.cursor import set_ui_cursor


class _CutsceneParticle:
    def __init__(
        self,
        pos: pygame.Vector2,
        velocity: pygame.Vector2,
        color: tuple[int, int, int],
        size: float,
        lifetime: float,
        shrink: bool = True,
    ):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.timer = lifetime
        self.shrink = shrink

    def update(self, dt: float) -> bool:
        self.timer -= dt
        self.pos += self.velocity * dt
        self.velocity *= 0.96
        if self.shrink and self.lifetime > 0:
            scale = max(0.0, self.timer / self.lifetime)
            self.size = max(1.0, self.initial_size * scale)
        return self.timer > 0

    def draw(self, surface: pygame.Surface):
        if self.lifetime <= 0:
            return
        alpha = int(255 * max(0.0, min(1.0, self.timer / self.lifetime)))
        p_surf = pygame.Surface(
            (int(self.size * 2 + 2), int(self.size * 2 + 2)), pygame.SRCALPHA
        )
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(
            p_surf, c, (int(self.size + 1), int(self.size + 1)), int(self.size)
        )
        surface.blit(p_surf, (self.pos.x - self.size, self.pos.y - self.size))


class IntroCutsceneScene(GameScene):
    def __init__(
        self,
        state_manager=None,
        screen_size: tuple[int, int] = (SCREEN_WIDTH, SCREEN_HEIGHT),
    ):
        super().__init__(
            state_manager=state_manager,
            screen_size=screen_size,
            is_transparent=False,
            blocks_update=True,
        )
        self.w, self.h = screen_size
        self.time: float = 0.0
        self.total_duration: float = 13.0
        self._started: bool = False

        # Visual FX
        self.flash_timer: float = 0.0
        self.shake_intensity: float = 0.0
        self.shake_offset = pygame.Vector2(0, 0)
        self.particles: list[_CutsceneParticle] = []

        # Assets
        self._load_assets()

        # Starfield
        self.stars = [
            {
                "x": random.uniform(0, self.w),
                "y": random.uniform(0, self.h),
                "speed": random.uniform(60, 260),
                "size": random.choice([1, 1, 2, 2, 3]),
                "alpha": random.randint(140, 255),
            }
            for _ in range(120)
        ]

        # Story logs: (start_time, end_time, title, text)
        self.story_logs = [
            (
                0.0,
                3.5,
                "DIÁRIO DE BORDO - ANO 2342",
                "ALERTA VERMELHO! Falha catastrófica no motor de dobra... Queda iminente em planeta desconhecido!",
            ),
            (
                3.5,
                6.5,
                "REENTRADA ATMOSFÉRICA",
                "Atrito orbital crítico! Casco superaquecendo... Segurem-se para o impacto!",
            ),
            (
                6.5,
                9.5,
                "SETOR TERRANON - IMPACTO CONFIRMADO",
                "Nave derrubada em território inóspito. Sistemas de suporte à vida em modo de contingência.",
            ),
            (
                9.5,
                13.0,
                "RADAR DE COMBATE: AMEAÇA IMINENTE",
                "Múltiplas hordas detectadas se aproximando da carcaça da nave. SOBREVIVA E DEFENDA A BASE!",
            ),
        ]

    def _load_assets(self):
        # Fonts
        if not pygame.font.get_init():
            pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_text = pygame.font.SysFont("Consolas", 14)
        self.font_hint = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_alert = pygame.font.SysFont("Arial", 22, bold=True)

        # Ship sprites: intact (pre-crash) and damaged (post-crash)
        intact_path = ASSETS_FOLDER / "images" / "nave_inteira.png"
        damaged_path = ASSETS_FOLDER / "images" / "Nave-D.png"

        try:
            img = pygame.image.load(str(intact_path))
            if pygame.display.get_surface():
                try:
                    img = img.convert_alpha()
                except Exception:
                    pass
            self.ship_intact = img
        except Exception:
            self.ship_intact = pygame.Surface((128, 128), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.ship_intact,
                (180, 190, 200),
                [(64, 10), (118, 118), (64, 90), (10, 118)],
            )

        try:
            img = pygame.image.load(str(damaged_path))
            if pygame.display.get_surface():
                try:
                    img = img.convert_alpha()
                except Exception:
                    pass
            self.ship_damaged = img
        except Exception:
            self.ship_damaged = self.ship_intact

        # Player sprite
        player_path = ASSETS_FOLDER / "images" / "player" / "idle" / "S.png"
        try:
            p_img = pygame.image.load(str(player_path))
            if pygame.display.get_surface():
                try:
                    p_img = p_img.convert_alpha()
                except Exception:
                    pass
            self.player_img = pygame.transform.scale(
                p_img, (int(p_img.get_width() * 2.5), int(p_img.get_height() * 2.5))
            )
        except Exception:
            self.player_img = pygame.Surface((28, 48), pygame.SRCALPHA)
            pygame.draw.rect(self.player_img, (50, 180, 240), (0, 0, 28, 48))

        # Goblin silhouette
        goblin_path = (
            ASSETS_FOLDER / "images" / "goblin-pack" / "frames" / "S" / "0.png"
        )
        try:
            g_img = pygame.image.load(str(goblin_path))
            if pygame.display.get_surface():
                try:
                    g_img = g_img.convert_alpha()
                except Exception:
                    pass
            self.goblin_img = pygame.transform.scale(
                g_img, (int(g_img.get_width() * 2.5), int(g_img.get_height() * 2.5))
            )
        except Exception:
            self.goblin_img = None

    def enter(self) -> None:
        self.time = 0.0
        self._started = False
        self.flash_timer = 0.0
        self.shake_intensity = 0.0
        self.particles.clear()
        set_ui_cursor()

        # Play atmospheric background audio
        try:
            EventManager().emit(
                GameEventEnum.PLAY_MUSIC,
                filename="Electricity.wav",
                loops=-1,
                fade_ms=500,
            )
        except Exception:
            pass

    def exit(self) -> None:
        pass

    def _start_game(self):
        if self._started:
            return
        self._started = True
        if self.state_manager is not None:
            self.state_manager.change_to(GameStateEnum.PLAY)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    self._start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                self._start_game()

    def update(self, dt: float) -> None:
        prev_time = self.time
        self.time += dt

        # Screen Shake decay
        if self.shake_intensity > 0:
            self.shake_intensity = max(0.0, self.shake_intensity - dt * 15.0)
            self.shake_offset.x = random.uniform(
                -self.shake_intensity, self.shake_intensity
            )
            self.shake_offset.y = random.uniform(
                -self.shake_intensity, self.shake_intensity
            )
        else:
            self.shake_offset = pygame.Vector2(0, 0)

        # Hit Flash decay
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

        # Trigger crash explosion at t=6.5s
        if prev_time < 6.5 <= self.time:
            self.flash_timer = 0.35
            self.shake_intensity = 22.0
            try:
                EventManager().emit(
                    GameEventEnum.PLAY_SFX, filename="effects/death.mp3"
                )
                EventManager().emit(
                    GameEventEnum.PLAY_SFX, filename="effects/damage.mp3"
                )
            except Exception:
                pass
            # Massive impact debris and explosion burst
            impact_pos = pygame.Vector2(self.w / 2, self.h / 2 - 20)
            for _ in range(70):
                ang = random.uniform(0, 360)
                spd = random.uniform(80, 360)
                vel = pygame.Vector2(spd, 0).rotate(ang)
                col = random.choice(
                    [
                        (255, 120, 20),
                        (255, 200, 40),
                        (220, 40, 20),
                        (80, 60, 50),
                        (50, 40, 35),
                    ]
                )
                self.particles.append(
                    _CutsceneParticle(
                        impact_pos,
                        vel,
                        col,
                        size=random.uniform(3, 7),
                        lifetime=random.uniform(0.6, 1.4),
                    )
                )

        # Continuous particles
        self._spawn_continuous_particles(dt)

        # Update all particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Move stars
        for star in self.stars:
            star_speed = star["speed"]
            if self.time < 3.5:
                star["y"] += star_speed * dt
            elif self.time < 6.5:
                star["y"] += star_speed * dt * 2.5
            if star["y"] > self.h:
                star["y"] = 0
                star["x"] = random.uniform(0, self.w)

        # Automatically transition when finished
        if self.time >= self.total_duration:
            self._start_game()

    def _spawn_continuous_particles(self, dt: float):
        # Ship positions over time
        if self.time < 3.5:
            # Space descent: smoking thruster
            prog = self.time / 3.5
            ship_x = -60 + prog * (self.w * 0.55 + 60)
            ship_y = -40 + prog * (self.h * 0.45 + 40)
            engine_pos = pygame.Vector2(ship_x - 30, ship_y - 25)

            # Fire & smoke
            for _ in range(2):
                vel = pygame.Vector2(-random.uniform(60, 140), -random.uniform(40, 100))
                self.particles.append(
                    _CutsceneParticle(
                        engine_pos,
                        vel,
                        (255, random.randint(80, 180), 20),
                        size=random.uniform(3, 5),
                        lifetime=random.uniform(0.3, 0.6),
                    )
                )
                smoke_vel = pygame.Vector2(
                    -random.uniform(30, 80), -random.uniform(20, 60)
                )
                self.particles.append(
                    _CutsceneParticle(
                        engine_pos,
                        smoke_vel,
                        (70, 70, 75),
                        size=random.uniform(4, 9),
                        lifetime=random.uniform(0.6, 1.1),
                    )
                )

        elif self.time < 6.5:
            # Atmospheric reentry: intense fire trail
            prog = (self.time - 3.5) / 3.0
            ship_x = self.w * 0.55 + prog * (self.w * 0.5 - self.w * 0.55)
            ship_y = self.h * 0.45 + prog * (self.h * 0.5 - self.h * 0.45)
            engine_pos = pygame.Vector2(ship_x - 40, ship_y - 35)

            for _ in range(4):
                vel = pygame.Vector2(-random.uniform(100, 220), -random.uniform(80, 160))
                self.particles.append(
                    _CutsceneParticle(
                        engine_pos,
                        vel,
                        (255, random.randint(120, 230), 40),
                        size=random.uniform(4, 7),
                        lifetime=random.uniform(0.25, 0.5),
                    )
                )
            # Reentry shake
            self.shake_intensity = max(self.shake_intensity, 4.0)

        elif self.time >= 6.5:
            # Ground smoke billowing gently from the crashed ship
            if random.random() < 0.6:
                smoke_pos = pygame.Vector2(
                    self.w / 2 + random.uniform(-40, 40),
                    self.h / 2 - 30 + random.uniform(-10, 10),
                )
                vel = pygame.Vector2(random.uniform(-15, 15), -random.uniform(25, 55))
                self.particles.append(
                    _CutsceneParticle(
                        smoke_pos,
                        vel,
                        (60, 60, 65),
                        size=random.uniform(5, 11),
                        lifetime=random.uniform(0.8, 1.6),
                    )
                )

    def draw(self, surface: pygame.Surface) -> None:
        # Create cutscene surface to apply screen shake
        shake_x = int(self.shake_offset.x)
        shake_y = int(self.shake_offset.y)

        # Background rendering
        if self.time < 3.5:
            # Deep space
            surface.fill((10, 12, 22))
            self._draw_starfield(surface)
        elif self.time < 6.5:
            # Atmospheric entry heating up
            reentry_prog = (self.time - 3.5) / 3.0
            r = int(15 + reentry_prog * 110)
            g = int(15 + reentry_prog * 35)
            b = int(25 - reentry_prog * 15)
            surface.fill((r, g, b))
            self._draw_starfield(surface)
            self._draw_atmospheric_heat(surface, reentry_prog)
        else:
            # Alien Planet Surface (Crashed)
            surface.fill((28, 25, 30))
            self._draw_planet_terrain(surface)

        # Draw particles behind ship
        for p in self.particles:
            p.draw(surface)

        # Draw Ship
        self._draw_ship(surface, shake_x, shake_y)

        # Draw Player emerging (t >= 8.5s)
        if self.time >= 8.5:
            self._draw_player_emerging(surface, shake_x, shake_y)

        # Draw Alien Shadows in fog (t >= 9.5s)
        if self.time >= 9.5:
            self._draw_alien_shadows(surface)

        # Fullscreen Impact Flash
        if self.flash_timer > 0:
            flash_alpha = int(255 * (self.flash_timer / 0.35))
            flash_surf = pygame.Surface((self.w, self.h))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(flash_alpha)
            surface.blit(flash_surf, (0, 0))

        # Letterbox & Narrative HUD
        self._draw_cinematic_hud(surface)

        # Fade to black at the end (t > 12.0s)
        if self.time > 12.0:
            fade_alpha = int(255 * min(1.0, (self.time - 12.0) / 1.0))
            fade_surf = pygame.Surface((self.w, self.h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(fade_alpha)
            surface.blit(fade_surf, (0, 0))

    def _draw_starfield(self, surface: pygame.Surface):
        for s in self.stars:
            color = (s["alpha"], s["alpha"], s["alpha"])
            pygame.draw.circle(
                surface, color, (int(s["x"]), int(s["y"])), s["size"]
            )

    def _draw_atmospheric_heat(self, surface: pygame.Surface, prog: float):
        heat_overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for i in range(5):
            y_pos = int(self.h * (0.6 + i * 0.08))
            alpha = int((80 + i * 25) * prog)
            pygame.draw.line(
                heat_overlay, (255, 140, 30, alpha), (0, y_pos), (self.w, y_pos), 4
            )
        surface.blit(heat_overlay, (0, 0))

    def _draw_planet_terrain(self, surface: pygame.Surface):
        # Crash Trench
        center_x = self.w // 2
        center_y = self.h // 2 - 20
        # Skid mark plowed into terrain
        skid_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        start_pt = (center_x - 220, center_y - 120)
        end_pt = (center_x, center_y)
        pygame.draw.line(skid_surf, (15, 12, 16, 220), start_pt, end_pt, 48)
        pygame.draw.line(skid_surf, (45, 35, 30, 200), start_pt, end_pt, 28)
        # Impact crater
        pygame.draw.circle(skid_surf, (15, 12, 16, 220), (center_x, center_y + 10), 90)
        pygame.draw.circle(skid_surf, (40, 32, 28, 180), (center_x, center_y + 10), 75)
        surface.blit(skid_surf, (0, 0))

    def _draw_ship(self, surface: pygame.Surface, sx: int, sy: int):
        center_x = self.w // 2
        center_y = self.h // 2 - 20

        if self.time < 3.5:
            # Flying through space (nave inteira)
            ship_sprite = self.ship_intact
            prog = self.time / 3.5
            x = -60 + prog * (self.w * 0.55 + 60) + sx
            y = -40 + prog * (self.h * 0.45 + 40) + sy
            scale = 0.22 + prog * 0.12
            angle = -35 + math.sin(self.time * 6) * 4
        elif self.time < 6.5:
            # Reentry descent (nave inteira com atrito e calor)
            ship_sprite = self.ship_intact
            prog = (self.time - 3.5) / 3.0
            x = self.w * 0.55 + prog * (center_x - self.w * 0.55) + sx
            y = self.h * 0.45 + prog * (center_y - self.h * 0.45) + sy
            scale = 0.34 + prog * 0.08
            angle = -25 + math.sin(self.time * 18) * 8
        else:
            # Impacto & pós-queda: nave destruída (Nave-D) na cratera
            ship_sprite = self.ship_damaged
            x = center_x + sx
            y = center_y + sy
            scale = 0.36
            angle = -8

        w = int(ship_sprite.get_width() * scale)
        h = int(ship_sprite.get_height() * scale)
        scaled = pygame.transform.smoothscale(ship_sprite, (w, h))
        rotated = pygame.transform.rotate(scaled, angle)
        rect = rotated.get_rect(center=(int(x), int(y)))
        surface.blit(rotated, rect)

    def _draw_player_emerging(self, surface: pygame.Surface, sx: int, sy: int):
        prog = min(1.0, (self.time - 8.5) / 1.5)
        # Walk out from ship door towards south
        start_x = self.w // 2
        start_y = self.h // 2 + 5
        cur_y = start_y + prog * 65

        rect = self.player_img.get_rect(center=(int(start_x + sx), int(cur_y + sy)))
        surface.blit(self.player_img, rect)

    def _draw_alien_shadows(self, surface: pygame.Surface):
        if not self.goblin_img:
            return

        prog = min(1.0, (self.time - 9.5) / 1.5)
        alpha = int(190 * prog)

        # Goblin silhouettes with glowing red eyes lurking in the shadows
        positions = [
            (self.w * 0.18, self.h * 0.42),
            (self.w * 0.82, self.h * 0.46),
            (self.w * 0.25, self.h * 0.68),
            (self.w * 0.75, self.h * 0.66),
        ]

        silhouette = self.goblin_img.copy()
        silhouette.fill((10, 5, 12, alpha), special_flags=pygame.BLEND_RGBA_MULT)

        for gx, gy in positions:
            surface.blit(silhouette, (gx, gy))
            # Glowing red eyes
            eye_alpha = int(220 * (0.6 + 0.4 * math.sin(self.time * 8)))
            pygame.draw.circle(surface, (255, 30, 30), (int(gx + 12), int(gy + 10)), 2)
            pygame.draw.circle(surface, (255, 30, 30), (int(gx + 20), int(gy + 10)), 2)

    def _draw_cinematic_hud(self, surface: pygame.Surface):
        bar_height = 54

        # 1. Top and bottom letterbox bars
        pygame.draw.rect(surface, (5, 5, 8), (0, 0, self.w, bar_height))
        pygame.draw.rect(
            surface, (5, 5, 8), (0, self.h - bar_height - 70, self.w, bar_height + 70)
        )

        # Decorative neon borders
        pygame.draw.line(
            surface, (0, 200, 220), (0, bar_height), (self.w, bar_height), 2
        )
        pygame.draw.line(
            surface,
            (0, 200, 220),
            (0, self.h - bar_height - 70),
            (self.w, self.h - bar_height - 70),
            2,
        )

        # Header info
        header_text = self.font_title.render(
            "// REGISTRO DE VOO // SETOR: TERRANON-IX // STATUS: CRÍTICO",
            True,
            (0, 240, 220),
        )
        surface.blit(header_text, (24, 18))

        # Skip Prompt (pulsing)
        skip_alpha = int(180 + 75 * math.sin(self.time * 4))
        skip_surf = self.font_hint.render(
            "PRESSIONE [ESPAÇO] PARA PULAR", True, (255, 255, 255)
        )
        skip_surf.set_alpha(skip_alpha)
        surface.blit(skip_surf, (self.w - skip_surf.get_width() - 24, 18))

        # 2. Subtitle / Narrative Box
        current_log = None
        for start, end, title, body in self.story_logs:
            if start <= self.time < end:
                current_log = (start, title, body)
                break

        if current_log:
            start_t, title, body = current_log
            elapsed = self.time - start_t
            # Typewriter character reveal
            chars_to_show = int(elapsed * 45)
            revealed_body = body[:chars_to_show]

            title_surf = self.font_title.render(title, True, (255, 215, 60))
            body_surf = self.font_text.render(revealed_body, True, (230, 235, 245))

            box_y = self.h - bar_height - 56
            surface.blit(title_surf, (36, box_y))
            surface.blit(body_surf, (36, box_y + 24))
