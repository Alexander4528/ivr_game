import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 500, 50, 50)
        self.velocity_y = 0
        self.gravity = 1
        self.jump_strength = 15
        self.is_grounded = False
        self.can_double_jump = False
        self.can_jump = True

    def jump(self):
        self.velocity_y = -self.jump_strength

    def update(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        ground_level = 550
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.velocity_y = 0
            self.is_grounded = True
            self.can_double_jump = True
        else:
            self.is_grounded = False

    def handle_jump(self):
        if self.is_grounded:
            self.jump()
            self.can_double_jump = True
        elif self.can_double_jump:
            self.jump()
            self.can_double_jump = False

player = Player()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                player.handle_jump()

    player.update()

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), player.rect)
    pygame.draw.line(screen, (255, 255, 255), (0, 550), (800, 550), 2)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()