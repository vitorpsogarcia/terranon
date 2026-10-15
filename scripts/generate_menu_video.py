import math
import os
import random
import sys
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np
import pygame

# Add src to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.settings.settings import ASSETS_FOLDER, SCREEN_HEIGHT, SCREEN_WIDTH


class Star:
    def __init__(self, x: float, y: float, size: float, base_alpha: int, amp_alpha: int, k_freq: int, phase: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.size = size
        self.base_alpha = base_alpha
        self.amp_alpha = amp_alpha
        self.k_freq = k_freq
        self.phase = phase
        self.color = color


class ShootingStarDef(NamedTuple):
    start_time: float
    duration: float
    p_start: tuple[float, float]
    p_end: tuple[float, float]
    tail_length: float
    core_color: tuple[int, int, int]
    glow_color: tuple[int, int, int]


class MenuBackgroundRenderer:
    """Renderizador determinístico e contínuo para o fundo animado do menu."""

    def __init__(
        self,
        width: int = SCREEN_WIDTH,
        height: int = SCREEN_HEIGHT,
        duration: float = 8.0,
    ):
        self.w = width
        self.h = height
        self.duration = duration
        self.omega = (2.0 * math.pi) / duration

        # Pre-render deep space base gradient
        self.bg_gradient = self._create_gradient_surface()

        # Pre-render cosmic nebulae
        self.nebulae = self._create_nebulae()

        # Seeded deterministic starfield
        self.stars = self._create_stars()

        # Shooting stars schedule
        self.shooting_stars = [
            ShootingStarDef(
                start_time=1.2,
                duration=0.9,
                p_start=(80.0, 40.0),
                p_end=(460.0, 250.0),
                tail_length=150.0,
                core_color=(255, 255, 255),
                glow_color=(80, 220, 255),
            ),
            ShootingStarDef(
                start_time=4.8,
                duration=1.0,
                p_start=(540.0, 25.0),
                p_end=(920.0, 230.0),
                tail_length=160.0,
                core_color=(255, 255, 255),
                glow_color=(100, 235, 255),
            ),
        ]

        # Load ship sprite
        self.ship_scale = 0.54
        self._load_ship()

        # Base ship position (centered in the right region of the menu, between x=668 and 1056)
        self.ship_base_x = 840.0
        self.ship_base_y = 360.0

        # Pre-render vignette
        self.vignette_surf = self._create_vignette()

    def _load_ship(self):
        ship_path = ASSETS_FOLDER / "images" / "nave_inteira.png"
        try:
            img = pygame.image.load(str(ship_path))
            sw = int(img.get_width() * self.ship_scale)
            sh = int(img.get_height() * self.ship_scale)
            self.ship_base_sprite = pygame.transform.smoothscale(img, (sw, sh))
        except Exception:
            # Fallback procedural ship if image not found
            sw = int(500 * self.ship_scale)
            sh = int(500 * self.ship_scale)
            self.ship_base_sprite = pygame.Surface((sw, sh), pygame.SRCALPHA)
            pygame.draw.polygon(
                self.ship_base_sprite,
                (200, 210, 225),
                [(sw // 2, 20), (sw - 20, sh - 40), (sw // 2, sh - 80), (20, sh - 40)],
            )

    def _create_gradient_surface(self) -> pygame.Surface:
        surf = pygame.Surface((self.w, self.h))
        # Deep space gradient from top-left (8, 12, 22) to bottom-right (15, 20, 34)
        c_top = np.array([8.0, 12.0, 22.0])
        c_bot = np.array([15.0, 20.0, 34.0])
        for y in range(self.h):
            t = y / max(1, self.h - 1)
            c = (c_top * (1.0 - t) + c_bot * t).astype(int)
            pygame.draw.line(surf, (int(c[0]), int(c[1]), int(c[2])), (0, y), (self.w, y))
        return surf

    def _create_nebulae(self) -> list[dict]:
        # Nebulae definitions with soft concentric alpha circles
        nebulae_data = [
            {"center": (240, 160), "radius": 280, "color": (55, 20, 68), "base_a": 28},
            {"center": (880, 450), "radius": 260, "color": (16, 48, 68), "base_a": 24},
            {"center": (520, 620), "radius": 220, "color": (25, 30, 58), "base_a": 20},
        ]
        nebulae_surfs = []
        for n in nebulae_data:
            s = pygame.Surface((n["radius"] * 2, n["radius"] * 2), pygame.SRCALPHA)
            r = n["radius"]
            color = n["color"]
            # Draw soft gradient radial circles
            steps = 30
            for i in range(steps, 0, -1):
                cur_r = int(r * (i / steps))
                # Gaussian falloff approximation
                frac = 1.0 - (i / steps)
                alpha = int(n["base_a"] * (frac ** 1.6))
                pygame.draw.circle(s, (*color, alpha), (r, r), cur_r)
            nebulae_surfs.append({
                "surf": s,
                "pos": (n["center"][0] - r, n["center"][1] - r),
                "base_a": n["base_a"],
            })
        return nebulae_surfs

    def _create_stars(self) -> list[Star]:
        rng = random.Random(42)
        stars = []
        # Layer 1: distant tiny stars (110)
        for _ in range(110):
            x = rng.uniform(0, self.w)
            y = rng.uniform(0, self.h)
            base_a = rng.randint(130, 200)
            amp_a = rng.randint(30, 55)
            k_freq = rng.choice([1, 2, 3])
            phase = rng.uniform(0, 2 * math.pi)
            color = rng.choice([(200, 220, 255), (240, 245, 255), (255, 245, 230)])
            stars.append(Star(x, y, 1.0, base_a, amp_a, k_freq, phase, color))

        # Layer 2: medium stars (40)
        for _ in range(40):
            x = rng.uniform(0, self.w)
            y = rng.uniform(0, self.h)
            base_a = rng.randint(180, 230)
            amp_a = rng.randint(40, 60)
            k_freq = rng.choice([2, 3, 4])
            phase = rng.uniform(0, 2 * math.pi)
            color = rng.choice([(220, 240, 255), (255, 255, 255), (190, 235, 255)])
            stars.append(Star(x, y, 1.8, base_a, amp_a, k_freq, phase, color))

        # Layer 3: bright prominent stars (15) with subtle glow
        for _ in range(15):
            x = rng.uniform(0, self.w)
            y = rng.uniform(0, self.h)
            base_a = rng.randint(210, 245)
            amp_a = rng.randint(25, 45)
            k_freq = rng.choice([1, 2])
            phase = rng.uniform(0, 2 * math.pi)
            color = (255, 255, 255)
            stars.append(Star(x, y, 2.5, base_a, amp_a, k_freq, phase, color))
        return stars

    def _create_vignette(self) -> pygame.Surface:
        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        # Gentle dark corner gradient
        cx, cy = self.w / 2, self.h / 2
        max_dist = math.hypot(cx, cy)
        # Sample low-res grid and scale up for fast smooth vignette
        vw, vh = 66, 45
        v_small = pygame.Surface((vw, vh), pygame.SRCALPHA)
        for vy in range(vh):
            for vx in range(vw):
                dx = (vx / (vw - 1) - 0.5) * self.w
                dy = (vy / (vh - 1) - 0.5) * self.h
                d = math.hypot(dx, dy) / max_dist
                # Only darken outer 40%
                if d > 0.55:
                    alpha = int(140 * ((d - 0.55) / 0.45) ** 1.8)
                    v_small.set_at((vx, vy), (4, 6, 12, min(160, alpha)))
        return pygame.transform.smoothscale(v_small, (self.w, self.h))

    def render(self, surface: pygame.Surface, t: float) -> None:
        """Renderiza a cena no tempo t garantindo periodicidade exata com período self.duration."""
        # 1. Base Gradient
        surface.blit(self.bg_gradient, (0, 0))

        # 2. Cosmic Nebulae with subtle harmonic breathing
        nebula_pulse = math.sin(self.omega * t)
        for n in self.nebulae:
            alpha_mod = 1.0 + 0.18 * nebula_pulse
            surf_copy = n["surf"].copy()
            surf_copy.set_alpha(int(255 * alpha_mod))
            surface.blit(surf_copy, n["pos"])

        # 3. Starfield with integer-harmonic twinkle
        self._draw_starfield(surface, t)

        # 4. Shooting Stars (Estrelas Cadentes)
        self._draw_shooting_stars(surface, t)

        # 5. Floating Spaceship on the right side
        self._draw_ship(surface, t)

        # 6. Vignette overlay
        surface.blit(self.vignette_surf, (0, 0))

    def _draw_starfield(self, surface: pygame.Surface, t: float):
        # We can draw onto a transparent overlay for stars with halos
        for star in self.stars:
            # Twinkle formula with exact integer harmonic frequency:
            # sin(k * omega * t + phase) has exactly the same value at t=0 and t=T!
            twinkle = math.sin(star.k_freq * self.omega * t + star.phase)
            alpha = int(star.base_alpha + star.amp_alpha * twinkle)
            alpha = max(30, min(255, alpha))

            color = (
                int(star.color[0] * (alpha / 255.0)),
                int(star.color[1] * (alpha / 255.0)),
                int(star.color[2] * (alpha / 255.0)),
            )

            # Draw core
            if star.size <= 1.2:
                surface.set_at((int(star.x), int(star.y)), color)
            elif star.size < 2.2:
                pygame.draw.circle(surface, color, (int(star.x), int(star.y)), 1)
            else:
                # Prominent star with cross diffraction spike
                px, py = int(star.x), int(star.y)
                pygame.draw.circle(surface, color, (px, py), 2)
                # Subtle cross diffraction spikes
                spike_len = int(4 + 3 * (alpha / 255.0))
                spike_col = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.line(surface, spike_col, (px - spike_len, py), (px + spike_len, py), 1)
                pygame.draw.line(surface, spike_col, (px, py - spike_len), (px, py + spike_len), 1)

    def _draw_shooting_stars(self, surface: pygame.Surface, t: float):
        for s in self.shooting_stars:
            if s.start_time <= t <= s.start_time + s.duration:
                prog = (t - s.start_time) / s.duration  # 0.0 -> 1.0

                # Alpha envelope: smooth fade-in, steady brilliance, smooth fade-out
                if prog < 0.15:
                    env_alpha = prog / 0.15
                elif prog > 0.70:
                    env_alpha = (1.0 - prog) / 0.30
                else:
                    env_alpha = 1.0

                # Interpolate head position
                hx = s.p_start[0] + prog * (s.p_end[0] - s.p_start[0])
                hy = s.p_start[1] + prog * (s.p_end[1] - s.p_start[1])

                # Direction vector
                dx = s.p_end[0] - s.p_start[0]
                dy = s.p_end[1] - s.p_start[1]
                dist = math.hypot(dx, dy)
                if dist == 0:
                    continue
                ux = dx / dist
                uy = dy / dist

                # Tail length (grows on spawn, shrinks on burn-out)
                cur_tail_len = s.tail_length * min(1.0, prog / 0.25) * env_alpha
                tx = hx - ux * cur_tail_len
                ty = hy - uy * cur_tail_len

                # Draw glowing trail layers
                trail_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

                # Outer glow line
                outer_a = int(120 * env_alpha)
                pygame.draw.line(
                    trail_surf,
                    (*s.glow_color, outer_a),
                    (int(tx), int(ty)),
                    (int(hx), int(hy)),
                    4,
                )

                # Inner core line
                inner_a = int(240 * env_alpha)
                pygame.draw.line(
                    trail_surf,
                    (*s.core_color, inner_a),
                    (int(tx + ux * (cur_tail_len * 0.3)), int(ty + uy * (cur_tail_len * 0.3))),
                    (int(hx), int(hy)),
                    2,
                )

                # Head corona
                head_r = int(4 * env_alpha) + 1
                pygame.draw.circle(trail_surf, (*s.glow_color, int(180 * env_alpha)), (int(hx), int(hy)), head_r + 2)
                pygame.draw.circle(trail_surf, (*s.core_color, int(255 * env_alpha)), (int(hx), int(hy)), head_r)

                # Trailing spark particles along the trail
                for i in range(1, 4):
                    spark_dist = cur_tail_len * (i / 4.0)
                    sx = hx - ux * spark_dist + math.sin(prog * 20.0 + i) * 2.0
                    sy = hy - uy * spark_dist + math.cos(prog * 20.0 + i) * 2.0
                    spark_a = int(180 * env_alpha * (1.0 - i / 4.0))
                    if spark_a > 10:
                        pygame.draw.circle(trail_surf, (*s.glow_color, spark_a), (int(sx), int(sy)), 1)

                surface.blit(trail_surf, (0, 0))

    def _draw_ship(self, surface: pygame.Surface, t: float):
        # 1. Harmonic zero-G floating motion
        # Period is self.duration, so sin(omega * t) is perfectly periodic!
        y_offset = 16.0 * math.sin(self.omega * t)
        x_offset = 7.0 * math.sin(2.0 * self.omega * t)  # Figure-8 drift
        angle = -13.0 + 3.2 * math.sin(self.omega * t - math.pi / 3.0)

        ship_x = self.ship_base_x + x_offset
        ship_y = self.ship_base_y + y_offset

        # 2. Rotate ship
        rot_ship = pygame.transform.rotate(self.ship_base_sprite, angle)
        ship_rect = rot_ship.get_rect(center=(int(ship_x), int(ship_y)))

        # 3. Calculate Engine Nozzles and Flame Vectors
        rad = math.radians(angle)
        # In unrotated 500x500 image, nozzles are at (250, 410) -> dy = +160
        # Scaled nozzle offset:
        unrot_dy = 160.0 * self.ship_scale
        rot_dx = unrot_dy * math.sin(rad)
        rot_dy = unrot_dy * math.cos(rad)

        nozzle_cx = ship_x + rot_dx
        nozzle_cy = ship_y + rot_dy

        # Exhaust direction pointing away from ship nose
        ux = math.sin(rad)
        uy = math.cos(rad)
        # Perpendicular vector across engine nozzle width
        vx = math.cos(rad)
        vy = -math.sin(rad)

        # 4. Render Engine Thruster Plasma Flumes (behind ship)
        flame_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        # Engine harmonic pulse (frequency 3 * omega guarantees perfect loop)
        pulse = math.sin(3.0 * self.omega * t)
        flame_len = 32.0 + 7.0 * pulse
        core_len = 18.0 + 4.0 * pulse
        flame_width = 14.0

        # Diffuse cyan glow aura behind the nozzles
        pygame.draw.circle(flame_surf, (20, 130, 255, 60), (int(nozzle_cx), int(nozzle_cy)), 28)
        pygame.draw.circle(flame_surf, (40, 180, 255, 90), (int(nozzle_cx), int(nozzle_cy)), 16)

        # Twin engine exhausts (left and right nozzle)
        for offset_sign in [-1.0, 1.0]:
            nx = nozzle_cx + vx * (offset_sign * 12.0)
            ny = nozzle_cy + vy * (offset_sign * 12.0)

            # Outer cyan/blue plasma flame cone
            tip_x = nx + ux * flame_len
            tip_y = ny + uy * flame_len
            p_left = (nx - vx * flame_width, ny - vy * flame_width)
            p_right = (nx + vx * flame_width, ny + vy * flame_width)
            p_tip = (tip_x, tip_y)

            pygame.draw.polygon(
                flame_surf,
                (35, 170, 255, 130),
                [p_left, p_right, p_tip],
            )

            # Inner bright electric blue core
            core_tip_x = nx + ux * core_len
            core_tip_y = ny + uy * core_len
            cp_left = (nx - vx * (flame_width * 0.55), ny - vy * (flame_width * 0.55))
            cp_right = (nx + vx * (flame_width * 0.55), ny + vy * (flame_width * 0.55))
            cp_tip = (core_tip_x, core_tip_y)

            pygame.draw.polygon(
                flame_surf,
                (220, 248, 255, 230),
                [cp_left, cp_right, cp_tip],
            )

            # Small glowing corona at nozzle outlet
            pygame.draw.circle(flame_surf, (80, 210, 255, 160), (int(nx), int(ny)), 6)
            pygame.draw.circle(flame_surf, (240, 250, 255, 230), (int(nx), int(ny)), 3)

        # Blit flames onto surface before the ship
        surface.blit(flame_surf, (0, 0))

        # 5. Draw the ship itself
        surface.blit(rot_ship, ship_rect)

        # 6. Navigation Strobe Lights & Cockpit Glow (on top of ship)
        lights_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)

        # Strobe pulse: sharp periodic blink (2 blinks per loop cycle)
        # sin(2 * omega * t)^8 is non-zero only during sharp peaks and matches at t=0 and t=T!
        strobe = max(0.0, math.sin(2.0 * self.omega * t)) ** 8.0

        # Left wingtip: unrotated (-180, +60)
        lw_scaled_x = -180.0 * self.ship_scale
        lw_scaled_y = 60.0 * self.ship_scale
        lw_rot_x = lw_scaled_x * math.cos(rad) + lw_scaled_y * math.sin(rad)
        lw_rot_y = -lw_scaled_x * math.sin(rad) + lw_scaled_y * math.cos(rad)
        lw_x = int(ship_x + lw_rot_x)
        lw_y = int(ship_y + lw_rot_y)

        # Right wingtip: unrotated (+180, +60)
        rw_scaled_x = 180.0 * self.ship_scale
        rw_scaled_y = 60.0 * self.ship_scale
        rw_rot_x = rw_scaled_x * math.cos(rad) + rw_scaled_y * math.sin(rad)
        rw_rot_y = -rw_scaled_x * math.sin(rad) + rw_scaled_y * math.cos(rad)
        rw_x = int(ship_x + rw_rot_x)
        rw_y = int(ship_y + rw_rot_y)

        # Red port navigation light (left)
        red_alpha = int(40 + 215 * strobe)
        pygame.draw.circle(lights_surf, (255, 60, 60, red_alpha), (lw_x, lw_y), 3)
        if strobe > 0.3:
            glow_r = int(5 + 8 * strobe)
            pygame.draw.circle(lights_surf, (255, 80, 80, int(120 * strobe)), (lw_x, lw_y), glow_r)

        # Green starboard navigation light (right)
        green_alpha = int(40 + 215 * strobe)
        pygame.draw.circle(lights_surf, (60, 255, 120, green_alpha), (rw_x, rw_y), 3)
        if strobe > 0.3:
            glow_r = int(5 + 8 * strobe)
            pygame.draw.circle(lights_surf, (80, 255, 140, int(120 * strobe)), (rw_x, rw_y), glow_r)

        # Cockpit soft cyan breathing glow: unrotated (0, -40)
        cp_scaled_y = -40.0 * self.ship_scale
        cp_rot_x = cp_scaled_y * math.sin(rad)
        cp_rot_y = cp_scaled_y * math.cos(rad)
        cp_x = int(ship_x + cp_rot_x)
        cp_y = int(ship_y + cp_rot_y)
        cockpit_alpha = int(50 + 30 * math.sin(self.omega * t))
        pygame.draw.circle(lights_surf, (120, 230, 255, cockpit_alpha), (cp_x, cp_y), 5)

        surface.blit(lights_surf, (0, 0))


def generate_menu_video(
    output_path: str = "assets/videos/menu_background.mp4",
    fps: int = 30,
    duration: float = 8.0,
    width: int = SCREEN_WIDTH,
    height: int = SCREEN_HEIGHT,
) -> str:
    print(f"Iniciando renderização do vídeo de fundo do menu ({width}x{height} @ {fps}fps, {duration}s)...")
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    surface = pygame.display.set_mode((width, height))

    renderer = MenuBackgroundRenderer(width=width, height=height, duration=duration)

    out_file = project_root / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(str(out_file), fourcc, float(fps), (width, height))

    total_frames = int(duration * fps)

    # Verifica conformidade matemática do loop: frame 0 e frame final
    t0_surf = pygame.Surface((width, height))
    renderer.render(t0_surf, 0.0)

    t_end_surf = pygame.Surface((width, height))
    renderer.render(t_end_surf, duration)

    diff = np.max(np.abs(
        pygame.surfarray.array3d(t0_surf).astype(np.int32) - 
        pygame.surfarray.array3d(t_end_surf).astype(np.int32)
    ))
    print(f"Verificação de loop perfeito: diferença máxima de pixels entre t=0s e t={duration}s = {diff}")

    for frame_idx in range(total_frames):
        # Cada frame i corresponde a t = i * duration / total_frames
        # Ao atingir o fim e voltar para o frame 0, a transição é contínua e sem salto!
        t = frame_idx * (duration / total_frames)
        renderer.render(surface, t)

        raw_bytes = pygame.image.tobytes(surface, "RGB")
        frame_rgb = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((height, width, 3))
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        video_writer.write(frame_bgr)

        if frame_idx % 30 == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames * 100
            print(f"Progresso: {progress:.1f}% ({frame_idx + 1}/{total_frames} frames)")

    video_writer.release()
    pygame.quit()

    file_size_mb = out_file.stat().st_size / (1024 * 1024)
    print("\nVídeo de fundo do menu gerado com sucesso!")
    print(f"Arquivo: {out_file}")
    print(f"Tamanho: {file_size_mb:.2f} MB")
    print(f"Duração: {duration:.1f} segundos ({total_frames} frames)")
    return str(out_file)


if __name__ == "__main__":
    generate_menu_video()
