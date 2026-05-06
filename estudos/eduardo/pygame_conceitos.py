import pygame 

pygame.init()

running = True
moving_right = False
moving_left = False
moving_up = False
moving_down = False
boost_velocit = False

clock = pygame.time.Clock()
screen = pygame.display.set_mode((980,720))
image = pygame.image.load("estudos/eduardo/img.jpg").convert()
image = pygame.transform.scale(image, (image.get_width() * 0.25, image.get_height() * 0.25))
font = pygame.font.Font(None, size=30)

x = 0 
y = 0
delta_time = 0.1

while running:
    screen.fill((255, 255, 255))
    screen.blit(image, (x, y))
    hitbox = pygame.Rect(x, y, image.get_width(), image.get_height())
    mpos = pygame.mouse.get_pos()
    target = pygame.Rect(300, 0, 160, 280)
    collision = hitbox.colliderect(target)
    m_collision = target.collidepoint(mpos)
    pygame.draw.rect(screen, (255 * collision, 255 * m_collision, 0), target)
    
    text = font.render("Hello, World!", True, (0, 0, 0))
    screen.blit(text, (80, 80))
    
    if moving_right:
        x += 50 * delta_time
        if boost_velocit:
            x += 300 * delta_time 
        else:
            x += 50 * delta_time
    
    if moving_left:
        x -= 50 * delta_time
        if boost_velocit:
            x -= 300 * delta_time 
        else:
            x -= 50 * delta_time
    
    if moving_up:
        y -= 50 * delta_time
        if boost_velocit:
            y -= 300 * delta_time 
        else:
            y -= 50 * delta_time
    
    if moving_down:
        y += 50 * delta_time
        if boost_velocit:
            y += 300 * delta_time
        else:
            y += 50 * delta_time
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                moving_right = True
                # image = pygame.transform.flip(image, True, False)
            if event.key == pygame.K_a:
                moving_left = True
                # image = pygame.transform.flip(image, True, False)
            if event.key == pygame.K_w:
                moving_up = True
                # image = pygame.transform.flip(image, False, True)
            if event.key == pygame.K_s:
                moving_down = True
                # image = pygame.transform.flip(image, False, True)
            if event.key == pygame.K_b:
                boost_velocit = True
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False
            if event.key == pygame.K_b:
                boost_velocit = False
                
        
                
        
            
    pygame.display.flip() 
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.01, delta_time)) 
        
pygame.quit()

# X --> positivo a direita;
# Y positivo para baixo;

# pygame.display.flip(), pega o que colocamos na superficie da tela e exibe na janela;
