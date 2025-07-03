import pygame
import random
import json
import sys
import tkinter as tk
from tkinter import messagebox
from enum import Enum

# Инициализация tkinter
root = tk.Tk()
root.withdraw()

# Инициализация pygame
pygame.init()
pygame.mixer.init()

# Константы
W, H = 800, 600
FPS = 60
GROUND_H = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (92, 148, 252)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# Статусы игры
class GameState(Enum):
    MAIN_MENU = 0
    LEVEL_SELECT = 1
    SETTINGS = 2
    UPGRADES = 3
    PLAYING = 4
    PAUSED = 5
    BOSS_LEVEL = 6
    SKINS = 7
    SECRETS = 8


# Окно
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Adventure Game")
clock = pygame.time.Clock()

# Загрузка шрифтов
try:
    font_large = pygame.font.Font('caviar-dreams.ttf', 48)
    font_medium = pygame.font.Font('caviar-dreams.ttf', 36)
    font_small = pygame.font.Font('caviar-dreams.ttf', 24)
except:
    font_large = pygame.font.SysFont('arial', 48)
    font_medium = pygame.font.SysFont('arial', 36)
    font_small = pygame.font.SysFont('arial', 24)

# Загрузка изображений
try:
    ground_image = pygame.image.load('ground.jpg')
    ground_image = pygame.transform.scale(ground_image, (804, 60))
except:
    ground_image = pygame.Surface((804, 60))
    ground_image.fill((100, 100, 50))
GROUND_H = ground_image.get_height()

try:
    me_image = pygame.image.load('Me.png')
except:
    me_image = pygame.Surface((70, 80))
    me_image.fill((0, 0, 255))
me_image = pygame.transform.scale(me_image, (70, 80))

try:
    portal_image = pygame.image.load('p2.gif')
except:
    portal_image = pygame.Surface((80, 90))
    portal_image.fill((255, 255, 0))
portal_image = pygame.transform.scale(portal_image, (80, 90))

try:
    monster_image = pygame.image.load('Enemy.png')
except:
    monster_image = pygame.Surface((90, 90))
    monster_image.fill((255, 0, 0))
monster_image = pygame.transform.scale(monster_image, (90, 90))

try:
    monster2_image = pygame.image.load('Enemyleft.png')
except:
    monster2_image = pygame.Surface((90, 90))
    monster2_image.fill((255, 100, 100))
monster2_image = pygame.transform.scale(monster2_image, (90, 90))

try:
    died_image = pygame.image.load('EnemyDead.png')
except:
    died_image = pygame.Surface((90, 90))
    died_image.fill((50, 50, 50))
died_image = pygame.transform.scale(died_image, (90, 90))


# Класс данных игры
class GameData:
    def __init__(self):
        self.difficulty = "Medium"  # Easy, Medium, Hard
        self.music_enabled = True
        self.sound_enabled = True
        self.completed_levels = 0
        self.upgrade_points = 0
        self.player_attack = 1
        self.player_hp = 3
        self.double_jump = False
        self.sprint = False
        self.shields = 0
        self.unlocked_skins = ["default"]
        self.current_skin = "default"
        self.found_secrets = []

    def save(self):
        with open('save_data.json', 'w') as f:
            json.dump(self.__dict__, f)

    def load(self):
        try:
            with open('save_data.json', 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    setattr(self, key, value)
        except (FileNotFoundError, json.JSONDecodeError):
            self.__init__()

    def reset_progress(self):
        self.__init__()
        self.save()


game_data = GameData()
game_data.load()

# Звуки
try:
    jump_sound = pygame.mixer.Sound('jump.wav')
    hit_sound = pygame.mixer.Sound('hit.wav')
    victory_sound = pygame.mixer.Sound('victory.wav')
    menu_select_sound = pygame.mixer.Sound('menu_select.wav')
except:
    jump_sound = pygame.mixer.Sound(buffer=bytearray(44))
    hit_sound = pygame.mixer.Sound(buffer=bytearray(44))
    victory_sound = pygame.mixer.Sound(buffer=bytearray(44))
    menu_select_sound = pygame.mixer.Sound(buffer=bytearray(44))


# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY, hover_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        text_surf = font_small.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# Класс игрока
class Player:
    def __init__(self):
        self.running_sprites_right = [pygame.transform.scale(me_image, (70, 80))] * 3
        self.running_sprites_left = [pygame.transform.scale(me_image, (70, 80))] * 3
        self.idle_sprite = me_image
        self.image = self.idle_sprite
        self.rect = self.image.get_rect()
        self.rect.midbottom = (W // 4, H - GROUND_H)
        self.speed = 5
        self.gravity = 0.4
        self.y_speed = 0
        self.is_grounded = False
        self.run_animation_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.facing_right = True
        self.max_hp = 3 + game_data.player_hp
        self.current_hp = self.max_hp
        self.attack = game_data.player_attack
        self.has_double_jump = game_data.double_jump
        self.has_sprint = game_data.sprint
        self.shields = game_data.shields
        self.jump_count = 0
        self.max_jumps = 2 if self.has_double_jump else 1

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move_speed = self.speed * 1.5 if (keys[pygame.K_LSHIFT] and self.has_sprint) else self.speed
        if keys[pygame.K_a]:
            self.rect.x -= move_speed
            self.facing_right = False
            self.update_animation()
        elif keys[pygame.K_d]:
            self.rect.x += move_speed
            self.facing_right = True
            self.update_animation()
        else:
            self.image = self.idle_sprite
            self.run_animation_index = 0

        if keys[pygame.K_SPACE] and (self.is_grounded or self.jump_count < self.max_jumps):
            self.jump()

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > 70:
            if not self.facing_right:
                self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_left)
                self.image = self.running_sprites_left[self.run_animation_index]
            else:
                self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_right)
                self.image = self.running_sprites_right[self.run_animation_index]
            self.last_update_time = now

    def jump(self):
        self.y_speed = -10
        self.is_grounded = False
        self.jump_count += 1
        if game_data.sound_enabled:
            jump_sound.play()

    def take_damage(self, amount):
        if self.shields > 0:
            self.shields -= 1
        else:
            self.current_hp -= amount
        if game_data.sound_enabled:
            hit_sound.play()

    def update(self):
        # Обработка границ экрана
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > W:
            self.rect.right = W

        # Гравитация
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        # Коллизия с землей
        if self.rect.bottom > H - GROUND_H:
            self.rect.bottom = H - GROUND_H
            self.y_speed = 0
            self.is_grounded = True
            self.jump_count = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Отображение HP
        bar_width = 70
        bar_height = 10
        health_percent = self.current_hp / self.max_hp
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 15, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 15, bar_width * health_percent, bar_height))
        # Щиты
        if self.shields > 0:
            shield_text = font_small.render(f"S: {self.shields}", True, WHITE)
            surface.blit(shield_text, (self.rect.x, self.rect.y - 30))


# Монстр
class Monster:
    def __init__(self):
        direction = random.randint(0, 1)
        if direction == 0:
            self.x_speed = 3
            self.image = monster2_image
            self.rect = self.image.get_rect(bottomleft=(0, H - GROUND_H))
        else:
            self.x_speed = -3
            self.image = monster_image
            self.rect = self.image.get_rect(bottomright=(W, H - GROUND_H))
        self.y_speed = 0
        self.gravity = 0.4
        self.is_dead = False
        self.is_out = False
        self.hp = 2 if game_data.difficulty == "Hard" else 1

    def update(self):
        if not self.is_dead:
            self.rect.x += self.x_speed
            self.y_speed += self.gravity
            self.rect.y += self.y_speed

            if self.rect.bottom > H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0

            # Вышел за границы
            if (self.x_speed > 0 and self.rect.left > W) or (self.x_speed < 0 and self.rect.right < 0):
                self.is_out = True

    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.is_dead = True
            self.image = died_image
            self.x_speed = -self.x_speed
            self.y_speed = -5
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# Босс
class Boss:
    def __init__(self):
        self.image = pygame.transform.scale(monster_image, (150, 150))
        self.rect = self.image.get_rect(midbottom=(W // 2, H - GROUND_H))
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.speed = 2
        self.attack_damage = 2
        self.phase = 1
        self.x_speed = self.speed
        self.y_speed = 0
        self.gravity = 0.4
        self.is_dead = False
        self.phase_change_timer = 0
        self.jump_timer = 0
        self.is_grounded = True

    def update_phase(self):
        if self.current_hp <= self.max_hp * 0.5 and self.phase == 1:
            self.phase = 2
            self.speed *= 1.5
            self.attack_damage = 3
            self.phase_change_timer = pygame.time.get_ticks()
        elif self.current_hp <= self.max_hp * 0.25 and self.phase == 2:
            self.phase = 3
            self.speed *= 1.5
            self.attack_damage = 4
            self.phase_change_timer = pygame.time.get_ticks()

    def update(self):
        if self.phase_change_timer > 0 and pygame.time.get_ticks() - self.phase_change_timer < 5000:
            # Ожидание после смены фаз
            return

        self.update_phase()

        # Движение
        self.rect.x += self.x_speed

        # Меняет направление при границах
        if self.rect.left < 0 or self.rect.right > W:
            self.x_speed = -self.x_speed

        # Прыжки в 3 фазе
        if self.phase == 3 and self.is_grounded:
            now = pygame.time.get_ticks()
            if now - self.jump_timer > 3000:
                self.y_speed = -15
                self.is_grounded = False
                self.jump_timer = now

        # Гравитация
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        # Коллизия с землей
        if self.rect.bottom > H - GROUND_H:
            self.rect.bottom = H - GROUND_H
            self.y_speed = 0
            self.is_grounded = True

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.is_dead = True
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Здоровье
        bar_width = 200
        bar_height = 20
        health_percent = self.current_hp / self.max_hp
        pygame.draw.rect(surface, RED, (W // 2 - bar_width // 2, 50, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (W // 2 - bar_width // 2, 50, bar_width * health_percent, bar_height))
        # Фаза
        phase_text = font_small.render(f"Phase: {self.phase}", True, WHITE)
        surface.blit(phase_text, (W // 2 - phase_text.get_width() // 2, 30))


# Вспомогательные функции
def draw_text(text, font, color, x, y, centered=True):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if centered:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(text_surface, rect)
    return rect


# Создание кнопок
def create_main_menu_buttons():
    buttons = []
    button_width, button_height = 200, 50
    start_x = W // 2 - button_width // 2
    y_positions = [200, 270, 340, 410, 480, 550]
    labels = ["Start Game", "Level Select", "Settings", "Upgrades", "Skins", "Exit"]
    for y, label in zip(y_positions, labels):
        buttons.append(Button(start_x, y, button_width, button_height, label))
    return buttons


def create_level_select_buttons():
    buttons = []
    button_width, button_height = 150, 50
    start_x = W // 2 - (button_width * 1.5 + 20)
    for i in range(3):
        level_num = i + 1
        enabled = level_num <= game_data.completed_levels + 1
        text = f"Level {level_num}" if enabled else "Locked"
        color = LIGHT_GRAY if enabled else (50, 50, 50)
        buttons.append(Button(start_x + i * (button_width + 20), 200, button_width, button_height, text, color))
    # Назад
    buttons.append(Button(W // 2 - 100, 500, 200, 50, "Back to Menu"))
    return buttons


def create_settings_buttons():
    buttons = []
    button_width, button_height = 150, 50
    start_x = W // 2 - button_width // 2
    # Тут добавьте, что нужно
    buttons.append(Button(start_x, 150, button_width, button_height, f"Difficulty: {game_data.difficulty}"))
    sound_text = "Music: ON" if game_data.music_enabled else "Music: OFF"
    buttons.append(Button(start_x, 220, button_width, button_height, sound_text))
    sound_text = "Sound: ON" if game_data.sound_enabled else "Sound: OFF"
    buttons.append(Button(start_x, 290, button_width, button_height, sound_text))
    # Дополнительно
    buttons.append(Button(start_x, 360, button_width, button_height, "Controls"))
    buttons.append(Button(start_x, 430, button_width, button_height, "Reset Progress", RED))
    buttons.append(Button(start_x, 500, button_width, button_height, "Save Settings", GREEN))
    buttons.append(Button(start_x, 570, button_width, button_height, "Back to Menu"))
    return buttons


def create_upgrade_buttons():
    buttons = []
    button_width, button_height = 200, 40
    start_x = W // 2 - button_width // 2
    # Можно добавить отображение очков и кнопки +/-
    # Для простоты пропустим детали
    # ...
    # В конце возврат
    return buttons


def create_pause_buttons():
    buttons = []
    button_width, button_height = 200, 50
    start_x = W // 2 - button_width // 2
    buttons.append(Button(start_x, 200, button_width, button_height, "Resume"))
    buttons.append(Button(start_x, 270, button_width, button_height, "Restart Level"))
    buttons.append(Button(start_x, 340, button_width, button_height, "Main Menu"))
    return buttons


def create_skin_buttons():
    buttons = []
    button_width, button_height = 150, 50
    start_x = W // 2 - button_width // 2
    skins = ["default", "warrior", "mage", "rogue", "sonic", "legendary"]
    for i, skin in enumerate(skins):
        row = i // 3
        col = i % 3
        x = start_x + (col - 1) * (button_width + 20)
        y = 150 + row * 70
        if skin in game_data.unlocked_skins:
            color = GREEN if game_data.current_skin == skin else LIGHT_GRAY
            buttons.append(Button(x, y, button_width, button_height, skin.capitalize(), color))
        else:
            buttons.append(Button(x, y, button_width, button_height, "Locked", (50, 50, 50)))
    # Назад
    buttons.append(Button(start_x, 500, button_width, button_height, "Back to Menu"))
    return buttons


def show_controls():
    controls = [
        "Controls:",
        "A - Move Left",
        "D - Move Right",
        "SPACE - Jump",
        "SHIFT - Sprint (if unlocked)",
        "ESC - Pause Game",
        "S - Quick Save"
    ]
    screen.fill(BLUE)
    for i, line in enumerate(controls):
        draw_text(line, font_small, WHITE, W // 2, 150 + i * 40)
    back_button = Button(W // 2 - 100, 500, 200, 50, "Back")
    back_button.draw(screen)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.rect.collidepoint(pygame.mouse.get_pos()):
                    waiting = False


# Очистка состояния
def reset_game_state():
    global game_state, current_level, player, monsters, boss, score, spawn_delay, last_spawn_time
    game_state = GameState.MAIN_MENU
    current_level = 1
    player = Player()
    monsters = []
    boss = None
    score = 0
    spawn_delay = 2000
    last_spawn_time = pygame.time.get_ticks()


# Основная функция
def main():
    global player, monsters, spawn_delay, last_spawn_time
    boss = None
    reset_game_state()
    def handle_boss_battle():
        player = Player()
        nonlocal boss, game_state, current_level, score
        # Обновляем босса
        if boss is None:
            boss = Boss()

        # Обновление игрока и босса
        player.handle_input()
        player.update()
        boss.update()

        # Проверка столкновений
        if not player.is_dead and not boss.is_dead and player.rect.colliderect(boss.rect):
            # Игрок прыгает на босса
            if player.rect.bottom - player.y_speed < boss.rect.top:
                if boss.take_damage(player.attack):
                    score += 10
                player.jump()
            else:
                player.take_damage(boss.attack_damage)
                if player.current_hp <= 0:
                    player.is_dead = True

        # Победа
        if boss and boss.is_dead:
            if game_data.sound_enabled:
                victory_sound.play()
            score += 20
            if current_level > game_data.completed_levels:
                game_data.completed_levels = current_level
            game_data.upgrade_points += 6
            game_data.save()

            # Отрисовать сообщение
            screen.fill(BLUE)
            draw_text("Boss Defeated!", font_large, WHITE, W // 2, H // 2 - 50)
            draw_text(f"Earned 6 upgrade points", font_medium, WHITE, W // 2, H // 2 + 20)
            draw_text("Press any key to continue", font_small, WHITE, W // 2, H // 2 + 80)
            pygame.display.flip()

            # Ждем нажатия
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                        waiting = False
            # Возврат в меню
            game_state = GameState.MAIN_MENU
            boss = None
            return True  # чтобы выйти из основного цикла

        # Проверка проигрыша
        if player.is_dead:
            # Отображение "Game Over"
            screen.fill(BLACK)
            draw_text("Game Over", font_large, RED, W // 2, H // 2 - 50)
            draw_text("Press R to Restart or Q to Quit", font_medium, WHITE, W // 2, H // 2 + 20)
            pygame.display.flip()

            # Ждем ответа
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Перезапуск уровня
                            player = Player()
                            monsters.clear()
                            boss = None
                            score = 0
                            spawn_delay = 2000
                            last_spawn_time = pygame.time.get_ticks()
                            game_state = GameState.PLAYING
                            waiting = False
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            return True  # чтобы выйти из основного цикла
        return False

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_data.save()
                pygame.quit()
                sys.exit()

            if game_state in [GameState.PLAYING, GameState.BOSS_LEVEL]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.PAUSED
                    elif event.key == pygame.K_s:
                        game_data.save()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Обработка нажатий по кнопкам в разных состояниях
                if game_state == GameState.MAIN_MENU:
                    buttons = create_main_menu_buttons()
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if game_data.sound_enabled:
                                menu_select_sound.play()
                            if i == 0:
                                # Старт игры
                                game_state = GameState.PLAYING
                                current_level = min(game_data.completed_levels + 1, 3)
                                player = Player()
                            elif i == 1:
                                # Выбор уровня
                                game_state = GameState.LEVEL_SELECT
                            elif i == 2:
                                # Настройки
                                game_state = GameState.SETTINGS
                            elif i == 3:
                                # Апгрейды
                                game_state = GameState.UPGRADES
                            elif i == 4:
                                # Скины
                                game_state = GameState.SKINS
                            elif i == 5:
                                # Выход
                                pygame.quit()
                                sys.exit()

                elif game_state == GameState.LEVEL_SELECT:
                    buttons = create_level_select_buttons()
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if game_data.sound_enabled:
                                menu_select_sound.play()
                            if i < 3:
                                level_num = i + 1
                                if level_num <= game_data.completed_levels + 1:
                                    if level_num < 3:
                                        game_state = GameState.PLAYING
                                    else:
                                        game_state = GameState.BOSS_LEVEL
                                    current_level = level_num
                                    player = Player()
                            elif i == 3:
                                game_state = GameState.MAIN_MENU

                elif game_state == GameState.SETTINGS:
                    buttons = create_settings_buttons()
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if game_data.sound_enabled:
                                menu_select_sound.play()
                            if i == 0:
                                # Переключение сложности
                                if game_data.difficulty == "Easy":
                                    game_data.difficulty = "Medium"
                                elif game_data.difficulty == "Medium":
                                    game_data.difficulty = "Hard"
                                else:
                                    game_data.difficulty = "Easy"
                                buttons[i].text = f"Difficulty: {game_data.difficulty}"
                            elif i == 1:
                                game_data.music_enabled = not game_data.music_enabled
                                buttons[i].text = "Music: ON" if game_data.music_enabled else "Music: OFF"
                            elif i == 2:
                                game_data.sound_enabled = not game_data.sound_enabled
                                buttons[i].text = "Sound: ON" if game_data.sound_enabled else "Sound: OFF"
                            elif i == 3:
                                show_controls()
                            elif i == 4:
                                if messagebox.askyesno("Reset Progress",
                                                       "Are you sure you want to reset all progress?"):
                                    game_data.reset_progress()
                            elif i == 5:
                                game_data.save()
                            elif i == 6:
                                game_state = GameState.MAIN_MENU

                elif game_state == GameState.UPGRADES:
                    # Обработка апгрейдов
                    # Тут можно дополнительно реализовать логику
                    pass

                elif game_state == GameState.PAUSED:
                    # Обработка паузы
                    pass

                elif game_state == GameState.SKINS:
                    # Обработка скинов
                    pass

        # Обновление состояния игры
        if game_state == GameState.PLAYING:
            # Обновление игрока
            player.handle_input()
            player.update()

            # Спавн монстров
            now = pygame.time.get_ticks()
            if now - last_spawn_time > spawn_delay:
                last_spawn_time = now
                monsters.append(Monster())
                spawn_delay = max(500, 2000 / (1.01 ** score))

            # Обновляем монстров
            for m in list(monsters):
                m.update()
                if m.is_out:
                    monsters.remove(m)

                # Столкновение игрока и монстра
                if not player.is_dead and not m.is_dead and player.rect.colliderect(m.rect):
                    # если игрок прыгает на монстра
                    if player.rect.bottom - player.y_speed < m.rect.top:
                        if m.take_damage():
                            score += 1
                        player.jump()
                    else:
                        player.take_damage(1)
                        if player.current_hp <= 0:
                            player.is_dead = True

            # Проверка завершения уровня
            if score >= (10 if current_level == 1 else 20):
                if current_level > game_data.completed_levels:
                    game_data.completed_levels = current_level
                # награда за уровень
                if current_level < 3:
                    points = {"Easy": 3, "Medium": 4, "Hard": 5}[game_data.difficulty]
                else:
                    points = {"Easy": 4, "Medium": 5, "Hard": 6}[game_data.difficulty]
                game_data.upgrade_points += points
                game_data.save()

                # сообщение о победе
                screen.fill(BLUE)
                draw_text("Level Complete!", font_large, WHITE, W // 2, H // 2 - 50)
                draw_text(f"Earned {points} upgrade points", font_medium, WHITE, W // 2, H // 2 + 20)
                draw_text("Press any key to continue", font_small, WHITE, W // 2, H // 2 + 80)
                pygame.display.flip()

                # Ждем нажатия
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                            waiting = False

                game_state = GameState.MAIN_MENU

        elif game_state == GameState.BOSS_LEVEL:
            # Обработка боя с боссом
            exit_boss_battle = handle_boss_battle()
            if exit_boss_battle:
                continue  # Перейти в главный цикл

        # Рендеринг сцены
        if game_state in [GameState.PLAYING, GameState.BOSS_LEVEL]:
            screen.fill(BLUE)
            screen.blit(ground_image, (0, H - GROUND_H))
            player.draw(screen)
            for m in monsters:
                m.draw(screen)
            if boss:
                boss.draw(screen)

            # Отображение очков
            draw_text(f"Score: {score}", font_small, WHITE, 10, 10, False)
            draw_text(f"Up Points: {game_data.upgrade_points}", font_small, WHITE, 10, 30, False)
            if player.shields > 0:
                draw_text(f"Shields: {player.shields}", font_small, WHITE, 10, 50, False)
            pygame.display.flip()

        # Обработка паузы
        if game_state == GameState.PAUSED:
            screen.fill(BLACK)
            for b in create_pause_buttons():
                b.draw(screen)
            draw_text("Paused", font_large, WHITE, W // 2, 100)
            pygame.display.flip()

        clock.tick(FPS)
        game_data.save()


# Запуск
if __name__ == "__main__":
    main()