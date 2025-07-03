import pygame
import sys
import random
import json
from pygame import Surface
from enum import Enum, auto

# Инициализация Pygame
pygame.init()
pygame.mixer.init()


# Константы и перечисления
class GameState(Enum):
    MAIN_MENU = auto()
    LEVEL_SELECT = auto()
    SETTINGS = auto()
    UPGRADES = auto()
    LEVEL_1 = auto()
    LEVEL_2 = auto()
    BOSS_LEVEL = auto()
    SKINS = auto()
    SECRETS = auto()
    CONTROLS = auto()
    PAUSE = auto()


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


# Настройки игры
W, H = 800, 600
FPS = 60
GROUND_H = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (92, 148, 252)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# Класс для настроек игры
class GameSettings:
    def __init__(self):
        self.difficulty = Difficulty.EASY
        self.music_enabled = True
        self.sound_enabled = True
        self.controls = {
            "left": [pygame.K_a, pygame.K_LEFT],
            "right": [pygame.K_d, pygame.K_RIGHT],
            "jump": [pygame.K_w, pygame.K_UP],
            "save": pygame.K_s,
            "pause": pygame.K_ESCAPE
        }

    def save(self):
        with open('settings.json', 'w') as f:
            json.dump({
                'difficulty': self.difficulty.value,
                'music': self.music_enabled,
                'sound': self.sound_enabled
            }, f)

    def load(self):
        try:
            with open('settings.json', 'r') as f:
                data = json.load(f)
                self.difficulty = Difficulty(data['difficulty'])
                self.music_enabled = data['music']
                self.sound_enabled = data['sound']
        except:
            pass


# Класс для управления игрой
class Game:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.current_level = 1
        self.unlocked_levels = 1
        self.points = 0
        self.secrets_found = 0
        self.total_secrets = 10
        self.settings = GameSettings()
        self.settings.load()
        self.load_progress()

    def load_progress(self):
        try:
            with open('progress.json', 'r') as f:
                data = json.load(f)
                self.current_level = data.get('current_level', 1)
                self.unlocked_levels = data.get('unlocked_levels', 1)
                self.points = data.get('points', 0)
                self.secrets_found = data.get('secrets_found', 0)
        except:
            pass

    def save_progress(self):
        with open('progress.json', 'w') as f:
            json.dump({
                'current_level': self.current_level,
                'unlocked_levels': self.unlocked_levels,
                'points': self.points,
                'secrets_found': self.secrets_found
            }, f)

    def reset_progress(self):
        self.current_level = 1
        self.unlocked_levels = 1
        self.points = 0
        self.secrets_found = 0
        self.save_progress()


# Класс для игрока
class Player:
    def __init__(self):
        self.upgrades = {
            "health": 0,
            "attack": 1,
            "double_jump": False,
            "sprint": False,
            "shields": 0
        }
        self.skin = "default"
        self.load_skin()
        self.reset()  # Move reset() after upgrades initialization

    def reset(self):
        self.rect = pygame.Rect(0, 0, 70, 80)
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.speed = 5
        self.gravity = 0.4
        self.y_speed = 0
        self.is_grounded = False
        self.health = 3 + self.upgrades["health"]
        self.max_health = 3 + self.upgrades["health"]
        self.is_dead = False
        self.facing_right = True
        self.animation_frame = 0
        self.last_animation_time = 0
        self.jump_count = 0

    def load_skin(self):
        try:
            self.image = self.load_image(f'skins/{self.skin}/idle.png', (70, 80))
            self.walk_right = [self.load_image(f'skins/{self.skin}/walk_{i}.png', (70, 80)) for i in range(1, 5)]
            self.walk_left = [pygame.transform.flip(img, True, False) for img in self.walk_right]
        except:
            self.image = pygame.Surface((70, 80))
            self.walk_right = [pygame.Surface((70, 80)) for _ in range(4)]
            self.walk_left = [pygame.Surface((70, 80)) for _ in range(4)]

    def load_image(self, path, size):
        try:
            return pygame.transform.scale(pygame.image.load(path), size)
        except:
            return pygame.Surface(size)

    def update(self, keys):
        # Движение
        left_pressed = any(keys[key] for key in game.settings.controls["left"])
        right_pressed = any(keys[key] for key in game.settings.controls["right"])

        if left_pressed:
            self.rect.x -= self.speed
            self.facing_right = False
        if right_pressed:
            self.rect.x += self.speed
            self.facing_right = True

        # Анимация
        now = pygame.time.get_ticks()
        if left_pressed or right_pressed:
            if now - self.last_animation_time > 100:
                self.animation_frame = (self.animation_frame + 1) % 4
                self.last_animation_time = now
            self.image = self.walk_left[self.animation_frame] if not self.facing_right else self.walk_right[
                self.animation_frame]
        else:
            self.image = self.walk_left[0] if not self.facing_right else self.walk_right[0]

        # Прыжок
        jump_pressed = any(keys[key] for key in game.settings.controls["jump"])
        if jump_pressed and (self.is_grounded or (self.upgrades["double_jump"] and self.jump_count < 1)):
            self.y_speed = -12
            self.is_grounded = False
            self.jump_count += 1

        # Гравитация
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        # Ограничение экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > W:
            self.rect.right = W

        # Проверка земли
        if self.rect.bottom > H - GROUND_H:
            self.rect.bottom = H - GROUND_H
            self.y_speed = 0
            self.is_grounded = True
            self.jump_count = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Класс для врагов
class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.type = enemy_type
        self.load_images()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.x_speed = 2 if random.random() > 0.5 else -2
        self.y_speed = 0
        self.health = 2
        self.is_dead = False

    def load_images(self):
        try:
            if self.type == "normal":
                self.image = pygame.transform.scale(pygame.image.load('Enemy.png'), (90, 90))
            elif self.type == "boss":
                self.image = pygame.transform.scale(pygame.image.load('boss.png'), (120, 120))
        except:
            self.image = pygame.Surface((90, 90) if self.type == "normal" else (120, 120))
            self.image.fill(RED)

    def update(self):
        if not self.is_dead:
            self.rect.x += self.x_speed
            self.y_speed += 0.4
            self.rect.y += self.y_speed

            if self.rect.bottom > H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0

            if self.rect.left < 0 or self.rect.right > W:
                self.x_speed *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Инициализация игры
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Platformer Game")
clock = pygame.time.Clock()

font_path = None  # Используем стандартный шрифт
font_large = pygame.font.Font(font_path, 48)
font_medium = pygame.font.Font(font_path, 36)
font_small = pygame.font.Font(font_path, 24)

game = Game()
player = Player()
enemies = []
boss = None
enemies_defeated = 0
selected_menu_item = 0
selected_level_item = 0
selected_setting_item = 0
selected_upgrade_item = 0
selected_skin_item = 0

# Загрузка изображений
ground_image = pygame.Surface((W, GROUND_H))
ground_image.fill((100, 100, 100))
portal_image = pygame.Surface((80, 90))
portal_image.fill((0, 255, 255))


# Основные функции
def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    if center:
        screen.blit(text_surface, (x - text_surface.get_width() // 2, y))
    else:
        screen.blit(text_surface, (x, y))


def show_message(text, duration=1500):
    msg = font_medium.render(text, True, WHITE)
    screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2))
    pygame.display.flip()
    pygame.time.delay(duration)


def save_game():
    data = {
        'level': game.state.value,
        'player_pos': (player.rect.x, player.rect.y),
        'health': player.health,
        'points': game.points
    }

    if game.state == GameState.LEVEL_2 or game.state == GameState.BOSS_LEVEL:
        data['enemies_defeated'] = enemies_defeated

    with open('save.json', 'w') as f:
        json.dump(data, f)

    show_message("Игра сохранена")


def load_game():
    try:
        with open('save.json', 'r') as f:
            data = json.load(f)
            game.state = GameState(data['level'])
            player.rect.x, player.rect.y = data['player_pos']
            player.health = data['health']
            game.points = data['points']

            if game.state == GameState.LEVEL_2 or game.state == GameState.BOSS_LEVEL:
                global enemies_defeated
                enemies_defeated = data.get('enemies_defeated', 0)
    except:
        show_message("Не удалось загрузить сохранение")


# Функции отрисовки экранов
def draw_main_menu():
    screen.fill(BLUE)
    draw_text("Главное меню", font_large, WHITE, W // 2, 100)

    buttons = [
        ("Начать игру", GameState.LEVEL_SELECT),
        ("Улучшения", GameState.UPGRADES),
        ("Скины", GameState.SKINS),
        ("Настройки", GameState.SETTINGS),
        ("Секреты", GameState.SECRETS),
        ("Выход", None)
    ]

    for i, (text, state) in enumerate(buttons):
        color = WHITE if i == selected_menu_item else (200, 200, 200)
        draw_text(text, font_medium, color, W // 2, 200 + i * 60)


def draw_level_select():
    screen.fill(BLUE)
    draw_text("Выбор уровня", font_large, WHITE, W // 2, 100)

    for i in range(1, game.unlocked_levels + 1):
        color = WHITE if i - 1 == selected_level_item else (200, 200, 200)
        draw_text(f"Уровень {i}", font_medium, color, W // 2, 200 + i * 60)

    draw_text("Назад", font_medium, WHITE, W // 2, H - 100)


def draw_settings():
    screen.fill(BLUE)
    draw_text("Настройки", font_large, WHITE, W // 2, 100)

    settings_items = [
        f"Сложность: {game.settings.difficulty.name}",
        f"Музыка: {'Вкл' if game.settings.music_enabled else 'Выкл'}",
        f"Звуки: {'Вкл' if game.settings.sound_enabled else 'Выкл'}",
        "Управление",
        "Сброс прогресса",
        "Сохранить настройки",
        "Отменить",
        "Назад"
    ]

    for i, item in enumerate(settings_items):
        color = WHITE if i == selected_setting_item else (200, 200, 200)
        draw_text(item, font_medium, color, W // 2, 150 + i * 50)


def draw_upgrades():
    screen.fill(BLUE)
    draw_text("Улучшения", font_large, WHITE, W // 2, 100)
    draw_text(f"Очков: {game.points}", font_medium, WHITE, W // 2, 150)

    upgrades = [
        f"Здоровье: {player.upgrades['health']} (+1 HP)",
        f"Атака: {player.upgrades['attack']}",
        f"Двойной прыжок: {'Да' if player.upgrades['double_jump'] else 'Нет'} (4 очка)",
        f"Бег: {'Да' if player.upgrades['sprint'] else 'Нет'} (3 очка)",
        f"Щиты: {player.upgrades['shields']} (3 очка за щит)",
        "Назад"
    ]

    for i, item in enumerate(upgrades):
        color = WHITE if i == selected_upgrade_item else (200, 200, 200)
        draw_text(item, font_medium, color, W // 2, 200 + i * 50)


def draw_skins_menu():
    screen.fill(BLUE)
    draw_text("Скины", font_large, WHITE, W // 2, 100)

    skins = [
        "Классика (по умолчанию)",
        "Потерянный (открыт)",
        "Соник (навык 'Бег')",
        "Эксклюзивный (все секреты)",
        "Назад"
    ]

    for i, skin in enumerate(skins):
        color = WHITE if i == selected_skin_item else (200, 200, 200)
        draw_text(skin, font_medium, color, W // 2, 150 + i * 60)


def draw_secrets():
    screen.fill(BLUE)
    draw_text("Секреты", font_large, WHITE, W // 2, 100)
    draw_text(f"Найдено: {game.secrets_found}/{game.total_secrets}", font_medium, WHITE, W // 2, 150)

    if game.secrets_found > 0:
        draw_text("Найденные секреты:", font_medium, WHITE, W // 2, 200)
        # Здесь можно добавить список найденных секретов

    draw_text("Назад", font_medium, WHITE, W // 2, H - 100)


def draw_controls():
    screen.fill(BLUE)
    draw_text("Управление", font_large, WHITE, W // 2, 100)

    controls = [
        "Движение влево: A или ←",
        "Движение вправо: D или →",
        "Прыжок: W или ↑",
        "Сохранение: S",
        "Пауза: ESC",
        "Назад"
    ]

    for i, control in enumerate(controls):
        draw_text(control, font_medium, WHITE, W // 2, 150 + i * 50)


def draw_pause_menu():
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    draw_text("Пауза", font_large, WHITE, W // 2, 150)

    options = [
        "Продолжить",
        "Перезапустить уровень",
        "Сохранить игру",
        "Выход в меню"
    ]

    for i, option in enumerate(options):
        color = WHITE if i == selected_menu_item else (200, 200, 200)
        draw_text(option, font_medium, color, W // 2, 250 + i * 60)


def draw_game():
    screen.fill(BLUE)

    # Отрисовка фона и земли
    screen.blit(ground_image, (0, H - GROUND_H))

    # Отрисовка портала (если это уровень 1)
    if game.state == GameState.LEVEL_1:
        screen.blit(portal_image, (W - 150, H - GROUND_H - 90))

    # Отрисовка игрока
    player.draw(screen)

    # Отрисовка врагов
    for enemy in enemies:
        enemy.draw(screen)

    # Отрисовка босса
    if boss:
        boss.draw(screen)

    # Отрисовка HUD
    draw_text(f"HP: {player.health}/{player.max_health}", font_small, WHITE, 20, 20, False)
    draw_text(f"Очки: {game.points}", font_small, WHITE, 20, 50, False)

    if game.state == GameState.LEVEL_2 or game.state == GameState.BOSS_LEVEL:
        draw_text(f"Врагов: {enemies_defeated}", font_small, WHITE, 20, 80, False)

    # Сообщение о победе
    if game.state == GameState.BOSS_LEVEL and boss and boss.is_dead:
        draw_text("Победа!", font_large, WHITE, W // 2, H // 2)


# Основной игровой цикл
def main():
    global selected_menu_item, selected_level_item, selected_setting_item
    global selected_upgrade_item, selected_skin_item, enemies_defeated
    global enemies, boss

    running = True
    while running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Обработка навигации в меню
                if game.state == GameState.MAIN_MENU:
                    if event.key == pygame.K_DOWN:
                        selected_menu_item = min(selected_menu_item + 1, 5)
                    elif event.key == pygame.K_UP:
                        selected_menu_item = max(selected_menu_item - 1, 0)
                    elif event.key == pygame.K_RETURN:
                        if selected_menu_item == 5:  # Выход
                            running = False
                        else:
                            game.state = [GameState.LEVEL_SELECT, GameState.UPGRADES,
                                          GameState.SKINS, GameState.SETTINGS, GameState.SECRETS][selected_menu_item]
                            selected_menu_item = 0

                # Обработка паузы
                elif event.key == game.settings.controls["pause"]:
                    if game.state in [GameState.LEVEL_1, GameState.LEVEL_2, GameState.BOSS_LEVEL]:
                        game.prev_state = game.state
                        game.state = GameState.PAUSE
                        selected_menu_item = 0

                # Обработка сохранения
                elif event.key == game.settings.controls["save"]:
                    if game.state in [GameState.LEVEL_1, GameState.LEVEL_2, GameState.BOSS_LEVEL]:
                        save_game()

        # Очистка экрана
        screen.fill(BLACK)

        # Отрисовка текущего состояния
        if game.state == GameState.MAIN_MENU:
            draw_main_menu()
        elif game.state == GameState.LEVEL_SELECT:
            draw_level_select()
        elif game.state == GameState.SETTINGS:
            draw_settings()
        elif game.state == GameState.UPGRADES:
            draw_upgrades()
        elif game.state == GameState.SKINS:
            draw_skins_menu()
        elif game.state == GameState.SECRETS:
            draw_secrets()
        elif game.state == GameState.CONTROLS:
            draw_controls()
        elif game.state == GameState.PAUSE:
            draw_pause_menu()
        elif game.state in [GameState.LEVEL_1, GameState.LEVEL_2, GameState.BOSS_LEVEL]:
            # Обновление игровой логики
            if game.state == GameState.LEVEL_1:
                player.update(keys)

                # Проверка столкновения с порталом
                if player.rect.colliderect(pygame.Rect(W - 150, H - GROUND_H - 90, 80, 90)):
                    game.state = GameState.LEVEL_2
                    enemies_defeated = 0
                    enemies = [Enemy(random.randint(0, W), 0) for _ in range(3)]

            elif game.state == GameState.LEVEL_2:
                player.update(keys)

                # Обновление врагов
                for enemy in enemies[:]:
                    enemy.update()

                    # Проверка столкновения с игроком
                    if player.rect.colliderect(enemy.rect):
                        if player.rect.bottom < enemy.rect.centery and player.y_speed > 0:
                            enemy.is_dead = True
                            enemies_defeated += 1
                            player.y_speed = -10
                        else:
                            player.health -= 1

                # Удаление побежденных врагов
                enemies = [e for e in enemies if not e.is_dead]

                # Добавление новых врагов
                if len(enemies) < 3 and random.random() < 0.02:
                    enemies.append(Enemy(random.randint(0, W), 0))

                # Проверка завершения уровня
                if enemies_defeated >= 10:
                    game.state = GameState.BOSS_LEVEL
                    boss = Enemy(W // 2, 100, "boss")
                    boss.health = 10
                    enemies_defeated = 0

            elif game.state == GameState.BOSS_LEVEL:
                player.update(keys)

                # Логика босса
                if boss and not boss.is_dead:
                    boss.update()

                    # Проверка столкновения с боссом
                    if player.rect.colliderect(boss.rect):
                        if player.rect.bottom < boss.rect.centery and player.y_speed > 0:
                            boss.health -= 1
                            player.y_speed = -10
                            if boss.health <= 0:
                                boss.is_dead = True
                                game.points += 6 if game.settings.difficulty == Difficulty.HARD else 5
                        else:
                            player.health -= 1

                # Проверка смерти игрока
                if player.health <= 0:
                    player.is_dead = True
                    show_message("Вы погибли!")
                    game.state = GameState.MAIN_MENU

            draw_game()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()