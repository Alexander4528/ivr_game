import pygame
import sys

pygame.init()

W, H = 1000, 800
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# Загрузка изображений (замените на ваши, сейчас просто создадим цвета)
platform_image = pygame.Surface((50, 50))
platform_image.fill((0, 255, 0))
player_image = pygame.Surface((50, 50))
player_image.fill((255, 0, 0))

# Создаем карту уровня из 0 и 1
level_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
]

level_cells = []

def generate_level_from_map(level_map_example):
    global level_cells
    level_cells = []
    for row_idx, row in enumerate(level_map_example):
        for col_idx, cell_example in enumerate(row):
            if cell_example == 1:
                rect = pygame.Rect(col_idx * 50, row_idx * 50, 50, 50)
                level_cells.append({"rect": rect, "image": platform_image})

generate_level_from_map(level_map)

# Игрок
player_rect = player_image.get_rect()
player_rect.midbottom = (W // 2, H - 50)
player_y_speed = 0
player_speed = 5
player_gravity = 0.5
player_is_grounded = False

# Основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    # Передвижение
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keys[pygame.K_SPACE] and player_is_grounded:
        player_y_speed = -15

    # Гравитация
    # Гравитация
    player_y_speed += player_gravity
    player_rect.y += player_y_speed

    # Проверка коллизий по вертикали
    player_is_grounded = False
    for cell in level_cells:
        if player_rect.colliderect(cell["rect"]):
            if player_y_speed > 0:  # падаем вниз
                player_rect.bottom = cell["rect"].top
                player_y_speed = 0
                player_is_grounded = True
            elif player_y_speed < 0:  # движемся вверх (например, при прыжке)
                player_rect.top = cell["rect"].bottom
                player_y_speed = 0

    # Обработка границ экрана
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > W:
        player_rect.right = W
    if player_rect.bottom > H:
        player_rect.bottom = H
        player_y_speed = 0
        player_is_grounded = True


    # Отрисовка
    screen.fill((135, 206, 250))
    # Отрисовываем клетки уровня
    for cell in level_cells:
        screen.blit(cell["image"], (cell["rect"].x, cell["rect"].y))
    # Отрисовываем игрока
    screen.blit(player_image, player_rect)

    pygame.display.flip()
    clock.tick(60)