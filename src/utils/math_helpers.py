import math

import pygame


def calculate_intercept_position(
    shooter_pos: pygame.Vector2,
    bullet_speed: float,
    target_pos: pygame.Vector2,
    target_velocity: pygame.Vector2,
) -> pygame.Vector2:
    """
    Calcula o ponto futuro onde o projétil e o alvo irão colidir.
    Se não houver solução (alvo rápido demais), retorna a posição atual do alvo.
    """
    to_target = target_pos - shooter_pos

    a = target_velocity.length_squared() - bullet_speed**2
    b = 2 * to_target.dot(target_velocity)
    c = to_target.length_squared()

    # Se a ~= 0 (velocidades iguais), equação linear
    if abs(a) < 1e-6:
        if abs(b) < 1e-6:
            return target_pos
        t = -c / b
        return target_pos + target_velocity * t if t > 0 else target_pos

    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        # Bala não alcança o alvo antes dele fugir
        return target_pos

    sqrt_disc = math.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2 * a)
    t2 = (-b + sqrt_disc) / (2 * a)

    # Escolhe o menor tempo positivo
    t = None
    if t1 > 0 and t2 > 0:
        t = min(t1, t2)
    elif t1 > 0:
        t = t1
    elif t2 > 0:
        t = t2

    if t is None:
        return target_pos

    return target_pos + target_velocity * t
