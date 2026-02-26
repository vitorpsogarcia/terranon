import pygame

SCREEN_SIZE = [1280, 720]
DEGREES_DIR = {
    "left": 90,
    "right": -90,
    "up": 0,
    "down": 180
}

pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
image = pygame.image.load("a.png").convert()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

image = pygame.transform.scale(image, (50, 50))
image = pygame.transform.rotate(image, DEGREES_DIR["right"])
image.set_colorkey((255, 255, 0))

delta_time = 0.1
x= 0.1
velocity = 80
running = True
while running:
    screen.fill((0, 0, 0))
    
    screen.blit(image, (x, SCREEN_SIZE[1] // 2))

    x += velocity * delta_time

    text = font.render(f"X: {x:.2f}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

    delta_time = clock.tick(60) / 1000.0
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()