import pygame

SCREEN_SIZE = [1280, 720]
DEGREES_DIR = {
    "left": 90,
    "right": -90,
    "up": 0,
    "down": 180
}

pygame.init()

pygame.key.set_repeat(100, 10)

screen = pygame.display.set_mode(SCREEN_SIZE)
image_main = pygame.image.load("a.png").convert()
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

image_main = pygame.transform.scale(image_main, (50, 50))
image_main.set_colorkey((255, 255, 0))
image = pygame.transform.rotate(image_main, DEGREES_DIR["right"])

delta_time = 0.1
pos = [0.1, SCREEN_SIZE[1] // 2]
velocity = 80
running = True
while running:
    screen.fill((0, 0, 0))
    
    screen.blit(image, (pos[0], pos[1]))

    hitbox = pygame.Rect(pos[0], pos[1], image.get_width(), image.get_height())

    target = pygame.Rect(600, 300, 50, 50)

    target_hit = target.colliderect(hitbox)
    color = (0, 255, 0) if target_hit else (255, 0, 0)
    pygame.draw.rect(screen, color, target, 2)

    text = font.render(f"X: {pos[0]:.2f}, Y: {pos[1]:.2f}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    for event in pygame.event.get():
        all_keys = pygame.key.get_pressed()
        keys_pressed = {
            "left": all_keys[pygame.K_LEFT], 
            "right": all_keys[pygame.K_RIGHT], 
            "up": all_keys[pygame.K_UP], 
            "down": all_keys[pygame.K_DOWN]
        }
        if event.type == pygame.QUIT:
            running = False
        if sum(keys_pressed.values()) > 0:
            
            if keys_pressed["up"] and keys_pressed["right"]:
                pos[1] -= velocity / 2 * delta_time
                pos[0] += velocity / 2 * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["right"] + 45)
            elif keys_pressed["up"] and keys_pressed["left"]:
                pos[1] -= velocity / 2 * delta_time
                pos[0] -= velocity / 2 * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["left"] - 45)
            elif keys_pressed["down"] and keys_pressed["right"]:
                pos[1] += velocity / 2 * delta_time
                pos[0] += velocity / 2 * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["right"] - 45)
            elif keys_pressed["down"] and keys_pressed["left"]:
                pos[1] += velocity / 2 * delta_time
                pos[0] -= velocity / 2 * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["left"] + 45)
            elif keys_pressed["down"]:
                pos[1] += velocity * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["down"])
            elif keys_pressed["up"]:
                pos[1] -= velocity * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["up"])
            elif keys_pressed["right"]:
                pos[0] += velocity * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["right"])
            elif keys_pressed["left"]:
                pos[0] -= velocity * delta_time
                image = pygame.transform.rotate(image_main, DEGREES_DIR["left"])
                
                


    pygame.display.flip()

    delta_time = clock.tick(60) / 1000.0
    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()