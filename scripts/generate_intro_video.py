import os
import sys
from pathlib import Path
import cv2
import numpy as np
import pygame

# Add src to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.settings.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from core.states.intro_cutscene_scene import IntroCutsceneScene


def generate_intro_video(
    output_path: str = "assets/videos/intro.mp4",
    fps: int = 30,
    width: int = SCREEN_WIDTH,
    height: int = SCREEN_HEIGHT,
):
    print(f"Iniciando renderização do vídeo de introdução ({width}x{height} @ {fps}fps)...")
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    surface = pygame.display.set_mode((width, height))

    cutscene = IntroCutsceneScene(state_manager=None, screen_size=(width, height))
    cutscene.enter()

    out_file = project_root / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(str(out_file), fourcc, float(fps), (width, height))

    total_duration = cutscene.total_duration
    total_frames = int(total_duration * fps)
    dt = 1.0 / fps

    for frame_idx in range(total_frames):
        cutscene.update(dt)
        cutscene.draw(surface)

        raw_bytes = pygame.image.tobytes(surface, "RGB")
        frame_rgb = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((height, width, 3))
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        video_writer.write(frame_bgr)

        if frame_idx % 60 == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames * 100
            print(f"Progresso: {progress:.1f}% ({frame_idx + 1}/{total_frames} frames)")

    video_writer.release()
    pygame.quit()

    file_size_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"\nVídeo de introdução gerado com sucesso!")
    print(f"Arquivo: {out_file}")
    print(f"Tamanho: {file_size_mb:.2f} MB")
    print(f"Duração: {total_duration:.1f} segundos ({total_frames} frames)")
    return str(out_file)


if __name__ == "__main__":
    generate_intro_video()
