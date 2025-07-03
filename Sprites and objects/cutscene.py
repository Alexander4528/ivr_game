import pygame
import sys
import time

# Инициализация Pygame
pygame.init()

# Настройки экрана
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Катсцена")

# Цвета
WHITE = (255, 255, 255)

# Загрузка изображений
bg_home = pygame.image.load('home.png')  # Фон дома
bg_bedroom = pygame.image.load('bedroom.png')  # Фон спальни
bg_dreamworld = pygame.image.load('dreamworld.png')  # Фон мира снов
hero_images = [pygame.image.load(f'hero_{i}.png') for i in range(1, 4)]  # Персонаж (разные позы)
parent_images = [pygame.image.load(f'parent_{i}.png') for i in range(1, 3)]  # Родители (разные позы)


# Анимация ссоры
def argue_scene():
    screen.fill(WHITE)
    screen.blit(bg_home, (0, 0))

    # Показываем анимацию ссоры
    for i in range(len(hero_images)):
        screen.blit(hero_images[i], (100, 300))  # Позиция героя
        screen.blit(parent_images[0], (500, 300))  # Позиция родителя 1
        screen.blit(parent_images[1], (600, 300))  # Позиция родителя 2
        pygame.display.flip()
        pygame.time.delay(500)  # Задержка между кадрами


# Анимация в кровати
def in_bed_scene():
    screen.fill(WHITE)
    screen.blit(bg_bedroom, (0, 0))

    # Показываем героя в кровати
    for i in range(len(hero_images)):
        screen.blit(hero_images[0], (300, 400))  # Позиция героя в кровати
        pygame.display.flip()
        pygame.time.delay(500)  # Задержка


# Переход в мир снов
def dream_scene():
    screen.fill(WHITE)
    screen.blit(bg_dreamworld, (0, 0))

    # Показываем переход в мир снов
    for i in range(len(hero_images)):
        screen.blit(hero_images[0], (350, 250))  # Позиция героя в мире снов
        pygame.display.flip()
        pygame.time.delay(500)  # Задержка


# Основной цикл игры
def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Запускаем катсцену
        argue_scene()
        in_bed_scene()
        dream_scene()

        # Выход из игры после катсцены
        break

    print("Катсцена завершена!")
    pygame.quit()


# Запуск игры
if __name__ == "__main__":
    main()