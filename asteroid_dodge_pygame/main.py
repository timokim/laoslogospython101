#!/usr/bin/env python3
"""Minimal asteroid dodge — green arrow vs white dots on black."""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass

import pygame

WIDTH, HEIGHT = 640, 420
FPS = 60
PLAYER_SPEED = 4
PLAYER_HIT_RADIUS = 4
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SPEED_LABELS = ["Slow", "Medium", "Fast", "Very Fast"]
SPEED_VALUES = [1.8, 2.8, 4.2, 6.5]
ASTEROID_COUNTS = [4, 8, 14, 28]


@dataclass
class GameConfig:
    speed_label: str
    speed: float
    count: int
    radius: int


@dataclass
class Asteroid:
    x: float
    y: float
    vx: float
    vy: float
    r: int

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        if self.x < self.r:
            self.x = self.r
            self.vx *= -1
        elif self.x > WIDTH - self.r:
            self.x = WIDTH - self.r
            self.vx *= -1
        if self.y < self.r:
            self.y = self.r
            self.vy *= -1
        elif self.y > HEIGHT - self.r:
            self.y = HEIGHT - self.r
            self.vy *= -1

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.r)


def make_config(speed_idx: int, count_idx: int) -> GameConfig:
    count = ASTEROID_COUNTS[count_idx]
    return GameConfig(
        speed_label=SPEED_LABELS[speed_idx],
        speed=SPEED_VALUES[speed_idx],
        count=count,
        radius=3 if count >= 14 else 2,
    )


def make_asteroids(cfg: GameConfig) -> list[Asteroid]:
    return [
        Asteroid(
            x=random.uniform(20, WIDTH - 20),
            y=random.uniform(20, HEIGHT - 20),
            vx=random.uniform(-1, 1) * cfg.speed,
            vy=random.uniform(-1, 1) * cfg.speed,
            r=cfg.radius,
        )
        for _ in range(cfg.count)
    ]


def collides(px: float, py: float, asteroid: Asteroid) -> bool:
    dx = asteroid.x - px
    dy = asteroid.y - py
    dist = asteroid.r + PLAYER_HIT_RADIUS
    return dx * dx + dy * dy < dist * dist


def draw_arrow(surface: pygame.Surface, x: float, y: float) -> None:
    points = [(x, y - 7), (x - 5, y + 5), (x + 5, y + 5)]
    pygame.draw.polygon(surface, GREEN, points)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int] = GREEN,
    center: bool = False,
) -> None:
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def run_menu(screen: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font) -> GameConfig | None:
    speed_idx = 1
    count_idx = 1
    focus = 0  # 0 = speed, 1 = count

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    focus = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    focus = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if focus == 0:
                        speed_idx = (speed_idx - 1) % len(SPEED_LABELS)
                    else:
                        count_idx = (count_idx - 1) % len(ASTEROID_COUNTS)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if focus == 0:
                        speed_idx = (speed_idx + 1) % len(SPEED_LABELS)
                    else:
                        count_idx = (count_idx + 1) % len(ASTEROID_COUNTS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return make_config(speed_idx, count_idx)
                elif event.key == pygame.K_ESCAPE:
                    return None

        screen.fill(BLACK)
        draw_text(screen, font, "ASTEROID DODGE", WIDTH // 2, 50, GREEN, center=True)
        draw_text(screen, font, "Arrow keys to move in game", WIDTH // 2, 85, WHITE, center=True)
        draw_text(screen, font, "↑↓ pick row   ←→ change value   Enter = start", WIDTH // 2, 115, WHITE, center=True)

        speed_line = f"Speed:  < {SPEED_LABELS[speed_idx]} >"
        count_line = f"Asteroids:  < {ASTEROID_COUNTS[count_idx]} >"
        draw_text(
            screen,
            font,
            speed_line,
            WIDTH // 2,
            170,
            GREEN if focus == 0 else WHITE,
            center=True,
        )
        draw_text(
            screen,
            font,
            count_line,
            WIDTH // 2,
            210,
            GREEN if focus == 1 else WHITE,
            center=True,
        )

        draw_text(screen, font, "ESC = quit", WIDTH // 2, HEIGHT - 40, WHITE, center=True)
        pygame.display.flip()
        clock.tick(FPS)


def run_game(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    font: pygame.font.Font,
    cfg: GameConfig,
) -> str:
    """Returns 'menu' or 'quit'."""
    px, py = WIDTH / 2, HEIGHT / 2
    asteroids = make_asteroids(cfg)
    score = 0
    frame = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                        return "menu"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

        keys = pygame.key.get_pressed()
        if not game_over:
            dx = dy = 0.0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += 1
            if dx or dy:
                length = math.hypot(dx, dy) or 1
                px += (dx / length) * PLAYER_SPEED
                py += (dy / length) * PLAYER_SPEED
            px = max(8, min(WIDTH - 8, px))
            py = max(8, min(HEIGHT - 8, py))

            frame += 1
            if frame % FPS == 0:
                score += 1

            for asteroid in asteroids:
                asteroid.update()
                if collides(px, py, asteroid):
                    game_over = True
                    break

        screen.fill(BLACK)
        for asteroid in asteroids:
            asteroid.draw(screen)
        draw_arrow(screen, px, py)

        draw_text(
            screen,
            font,
            f"SCORE: {score}  |  SPD: {cfg.speed_label}  |  ASTEROIDS: {cfg.count}",
            12,
            8,
        )
        if game_over:
            draw_text(screen, font, "GAME OVER", WIDTH // 2, HEIGHT // 2 - 30, GREEN, center=True)
            draw_text(
                screen,
                font,
                f"Score: {score} sec",
                WIDTH // 2,
                HEIGHT // 2 + 5,
                WHITE,
                center=True,
            )
            draw_text(
                screen,
                font,
                "R = menu   ESC = quit",
                WIDTH // 2,
                HEIGHT // 2 + 40,
                WHITE,
                center=True,
            )

        pygame.display.flip()
        clock.tick(FPS)


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Asteroid Dodge")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 18)

    while True:
        cfg = run_menu(screen, clock, font)
        if cfg is None:
            break
        result = run_game(screen, clock, font, cfg)
        if result == "quit":
            break

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
