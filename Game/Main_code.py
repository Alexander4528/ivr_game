#Импорт необходимых библиотек
import pygame
import sys
import random
import json
from pygame import Surface

pygame.init()

# Настройки игры
font_path = 'caviar-dreams.ttf'
font_large = pygame.font.Font(font_path, 48)
font_medium = pygame.font.Font(font_path, 36)
font_small = pygame.font.Font(font_path, 24)
player_points = 0
difficulty_level = 0

monsters = []
last_spawn_time = 0
spawn_delay = 3000
score = 0

#Переменные для активации разделов игры(уровни, меню, настройки и т.д.)
menu = False
level_1_part_1_in = False
level_2_part_1_in = False
levels_in = False

playing_menu = True
playing_level = False
from_menu = False
from_level = False

#Переменные для скроллинга
level_1_part_1_WIDTH = 5000
level_1_part_1_scroll_pos = 0
W, H = 1000, 800
screen = pygame.display.set_mode((W, H))
FPS = 60
clock = pygame.time.Clock()

#Экран при отсутствии изображения скина
surface_image = pygame.Surface((40, 50))

# Загрузка изображений
ground_image: Surface = pygame.image.load('Sprites and objects/Objects, background and other/ground.jpg')
ground_image = pygame.transform.scale(ground_image, (W, 60))
GROUND_H = ground_image.get_height()

me_image = pygame.image.load('Sprites and objects/Skins/Me/Me.png')
me_image = pygame.transform.scale(me_image, (70, 80))

portal_image = pygame.image.load('Sprites and objects/Objects, background and other/p2.gif')
portal_image = pygame.transform.scale(portal_image, (80, 90))

me_damaged_image = pygame.image.load('Sprites and objects/Skins/Me/Me_damaged.png')
me_damaged_image = pygame.transform.scale(me_damaged_image, (70, 80))

#Переменные для меню
menu_move_up = False
menu_move_down = False
menu_last_move_time = 0
MENU_MOVE_DELAY = 300

# Скины
skins = [
    {'name': 'Классика',
     'unlocked': True,
     'image': 'Sprites and objects/Skins/Me/Me.png',
     'walk_right': ['Sprites and objects/Skins/Me/Me-right1.png',
                    'Sprites and objects/Skins/Me/Me-right2.png',
                    'Sprites and objects/Skins/Me/Me-right3.png',
                    'Sprites and objects/Skins/Me/Me-right4.png'],
     'walk_left': ['Sprites and objects/Skins/Me/Me-left1.png',
                   'Sprites and objects/Skins/Me/Me-left2.png',
                   'Sprites and objects/Skins/Me/Me-left3.png',
                   'Sprites and objects/Skins/Me/Me-left4.png'],
     'damaged': 'Sprites and objects/Skins/Me/Me_damaged.png',
     'unlock': ' ',
     'img': surface_image},
    {'name': 'Потерянный',
     'unlocked': True,
     'image': 'Sprites and objects/Skins/Lost/Lost_Me.png',
     'walk_right': ['Sprites and objects/Skins/Lost/Lost-right1.png',
                    'Sprites and objects/Skins/Lost/Lost-right2.png',
                    'Sprites and objects/Skins/Lost/Lost-right3.png',
                    'Sprites and objects/Skins/Lost/Lost-right4.png'],
     'walk_left': ['Sprites and objects/Skins/Lost/Lost-left1.png',
                   'Sprites and objects/Skins/Lost/Lost-left2.png',
                   'Sprites and objects/Skins/Lost/Lost-left3.png',
                   'Sprites and objects/Skins/Lost/Lost-left4.png'],
     'damaged': 'Sprites and objects/Skins/Lost/Lost_Me-Damaged.png',
     'unlock': ' ',
     'img': surface_image},
    {'name': 'Соник',
     'unlocked': False,
     'image': 'Sprites and objects/Skins/Sonic/Sonic.png',
     'walk_right': ['Sprites and objects/Skins/Sonic/Sonic-right1.png',
                    'Sprites and objects/Skins/Sonic/Sonic-right2.png',
                    'Sprites and objects/Skins/Sonic/Sonic-right3.png',
                    'Sprites and objects/Skins/Sonic/Sonic-right4.png'],
     'walk_left': ['Sprites and objects/Skins/Sonic/Sonic-left1.png',
                   'Sprites and objects/Skins/Sonic/Sonic-left2.png',
                   'Sprites and objects/Skins/Sonic/Sonic-left3.png',
                   'Sprites and objects/Skins/Sonic/Sonic-left4.png'],
     'unlock': 'Открой способность "Бег"',
     'damaged': 'Sprites and objects/Skins/Sonic/Sonic-damaged.png',
     'img': surface_image},
    {'name': 'Марио',
     'unlocked': False,
     'image': 'Sprites and objects/Skins/Mario/Mario.png',
     'walk_right': ['Sprites and objects/Skins/Mario/Mario_right1.png',
                    'Sprites and objects/Skins/Mario/Mario_right2.png',
                    'Sprites and objects/Skins/Mario/Mario_right3.png',
                    'Sprites and objects/Skins/Mario/Mario_right4.png'],
     'walk_left': ['Sprites and objects/Skins/Mario/Mario_left1.png',
                   'Sprites and objects/Skins/Mario/Mario_left2.png',
                   'Sprites and objects/Skins/Mario/Mario_left3.png',
                   'Sprites and objects/Skins/Mario/Mario_left4.png'],
     'unlock': 'Открой способность "Двойной прыжок"',
     'damaged': 'Sprites and objects/Skins/Mario/Mario_damaged.png',
     'img': surface_image},
    {'name': 'Эксклюзивный',
     'unlocked': False,
     'image': 'exclusive.png',
     'unlock': 'Пройди игру на всех уровнях сложности',
     'img': surface_image}
]

# Анимации
running_sprites_right = []
for i in range(1, 5):
    try:
        img = pygame.image.load(f'Me-right{i}.png')
        running_sprites_right.append(pygame.transform.scale(img, (70, 80)))
    except:
        running_sprites_right.append(pygame.Surface((70, 80)))

running_sprites_left = []
for i in range(1, 5):
    try:
        img = pygame.image.load(f'Me-left{i}.png')
        running_sprites_left.append(pygame.transform.scale(img, (70, 80)))
    except:
        running_sprites_left.append(pygame.Surface((70, 80)))

current_skin_index = 0
skin_message_timer = 0

# Загрузка изображений скинов
for skin_number in skins:
    try:
        img = pygame.image.load(skin_number['image'])
        skin_number['img'] = pygame.transform.scale(img, (40, 50))
    except:
        pass

#Загрузка скина
def apply_skin(skin_index):
    global me_image, running_sprites_right, running_sprites_left, me_damaged_image

    if skin_index < 0 or skin_index >= len(skins):
        skin_index = 0  # Защита от неверного индекса

    skin = skins[skin_index]
    try:
        # Загружаем основное изображение
        me_image = pygame.transform.scale(pygame.image.load(skin['image']), (70, 80))

        # Загружаем анимации
        if skin.get('walk_right', []):
            running_sprites_right = [
                pygame.transform.scale(pygame.image.load(fname), (70, 80))
                for fname in skin['walk_right']
            ]
        else:
            running_sprites_right = [me_image] * 4

        if skin.get('walk_left', []):
            running_sprites_left = [
                pygame.transform.scale(pygame.image.load(fname), (70, 80))
                for fname in skin['walk_left']
            ]
        else:
            running_sprites_left = [me_image] * 4
        if skin.get('damaged', []):
            me_damaged_image = pygame.transform.scale(pygame.image.load(skin['damaged']), (70, 80))
        else:
            me_damaged_image = me_image
    except Exception as e:
        print(f"Ошибка загрузки скина: {e}")
        # Загружаем скин по умолчанию при ошибке
        if skin_index != 0:
            apply_skin(0)

#сохранение скина
def save_skin(filename='Save_files/Skin_selected.json'):
    global current_skin_index
    current_skin = {
        'current_skin_index': current_skin_index,
    }
    with open(filename, 'w') as f:
        json_str = json.dumps(current_skin)
        f.write(json_str)

#Сохранение прогресса
def save_game(play, current_score=None, filename='Save_files/last.json'):
    global level_1_part_1_scroll_pos
    game_state = {
        'player_pos': level_1_part_1_scroll_pos,
        'difficulty level': difficulty_level
    }
    if current_score is not None:
        game_state['score'] = current_score
        game_state['HP'] = play.HP
    with open(filename, 'w') as f:
        json_str = json.dumps(game_state)
        f.write(json_str)

#Сохранение настроек
def save_settings(filename='Save_files/settings.json'):
    current_settings = {
        'music_on': music_on,
        'player_points' : player_points,
        'difficulty_level': difficulty_level
    }
    with open(filename, 'w') as f:
        json_str = json.dumps(current_settings)
        f.write(json_str)

#Сохранение характеристик
def save_upgrades(play, filename='Save_files/upgrades.json'):
    current_char_stats = {
        'player_points': player_points,
        'Attack': play.attack,
        'HP' : play.HP,
        'Running' : play.running_unlocked,
        'Double jump' : play.double_jump_unlocked,
        'Shield': play.shield
    }
    with open(filename, 'w') as f:
        json_str = json.dumps(current_char_stats)
        f.write(json_str)

#Загрузка последнего сохранения
def load_game(play, filename='Save_files/last.json'):
    global current_skin_index, level_1_part_1_scroll_pos

    try:
        with open(filename, 'r') as f:
            game_state = json.load(f)
            level_1_part_1_scroll_pos = game_state['player_pos']

            if 'HP' in game_state:
                play.HP = game_state['HP']
            return game_state.get('score', 0), game_state.get('player_pos', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        level_1_part_1_scroll_pos = 0
        return 0, level_1_part_1_scroll_pos

#Загрузка настроек
def load_settings():
    global music_on, player_points, difficulty_level
    try:
        with open('Save_files/settings.json', 'r') as f:
            current_settings = json.load(f)
            music_on = current_settings.get('music_on', True)
            player_points = current_settings.get('player_points', 0)
            difficulty_level = current_settings.get('difficulty_level', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def load_skin():
    global current_skin_index
    try:
        with open('Save_files/Skin_selected.json', 'r') as f:
            current_skin = json.load(f)
            current_skin_index = current_skin.get('current_skin_index', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

#Загрузка улучшении
def load_upgrades(play):
    global player_points
    try:
        with open('Save_files/upgrades.json', 'r') as f:
            current_upgrades = json.load(f)
            player_points = current_upgrades.get('player_points', 0)
            play.attack = current_upgrades.get('Attack', 1)
            play.HP = current_upgrades.get('HP', 3)
            play.running_unlocked = current_upgrades.get('Running', False)
            play.double_jump_unlocked = current_upgrades.get('Double jump', False)
            play.shield = current_upgrades.get('Shield', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

#Текст
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, rect)
#Переключение музыки
music_on = True
menu_music = 'Music/Carmen_Twillie_The_Lion_King_-_Circle_Of_Life_48727462.mp3'
level_1_part_1_music = 'Music/Смешарики - Погоня.mp3'
level_2_part_1_music = 'Music/Geometry_Dash_-_Geometrical_Dominator_67148396.mp3'
def play_menu_music():
    global music_playing, music_on, playing_menu
    if not music_playing and music_on and playing_menu:
        try:
            pygame.mixer.music.load(menu_music)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            music_playing = True
            music_on = True
        except Exception as e:
            print(f"Ошибка воспроизведения меню: {e}")

def play_level_music():
    global music_playing, music_on, playing_level, level_1_part_1_in, level_2_part_1_in
    if not music_playing and music_on and playing_level:
        try:
            if level_1_part_1_in:
                pygame.mixer.music.load(level_1_part_1_music)
            if level_2_part_1_in:
                pygame.mixer.music.load(level_2_part_1_music)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            music_playing = True
            music_on = True
        except Exception as e:
            print(f"Ошибка воспроизведения уровня: {e}")

def stop_music():
    global music_playing
    pygame.mixer.music.stop()
    music_playing = False

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()
    save_settings()

#Пауза
def pause():
    global music_on, playing_menu, from_level, from_menu, score, level_1_part_1_in, level_2_part_1_in
    load_settings()
    options_pause_rects = [
        pygame.Rect(W // 2 - 100, H // 2 , 200, 40),
        pygame.Rect(W // 2 - 100, H // 2 + 50, 200, 40),
        pygame.Rect(W // 2 - 100, H // 2 + 100, 200, 40)
    ]
    paused = True
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((92, 148, 252, 20))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    if music_on:  # Используем глобальную переменную
                        pygame.mixer.music.unpause()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for idx, rect in enumerate(options_pause_rects):
                    if rect.collidepoint(mouse_pos):
                        if idx == 0:
                            if not music_on:
                                toggle_music()
                                play_level_music()
                            elif music_on:
                                toggle_music()
                        elif idx == 1:
                            management_menu()
                        elif idx == 2:
                            playing_menu = True
                            from_level = True
                            from_menu = False
                            if level_1_part_1_in:
                                level_1_part_1_in = False
                            elif level_2_part_1_in:
                                level_2_part_1_in = False
                            level_menu()


        mouse_pos = pygame.mouse.get_pos()

        # Отрисовка полупрозрачного фона
        screen.blit(overlay, (0, 0))
        draw_text("ПАУЗА", font_large, (255, 255, 255), screen, W // 2, H // 4)

        # Получаем текущие цвета пунктов меню
        for j, opt in enumerate(['Музыка', 'Управление', 'Назад']):
            rect = options_pause_rects[j]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)  # выделение при наведении
            else:
                color = (0, 0, 0)  # обычный цвет
            # Центрируем текст по координате
            if j == 0:
                status = "Вкл" if music_on else "Выкл"
                text = f"{opt}: {status}"
            else:
                text = opt
            draw_text(text, font_small, color, screen, W // 2, H // 2 + j * 50)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.event.clear(pygame.KEYDOWN)

#Характеристики и функции игрока
class Player:
    def __init__(self):
        self.speed = 5
        self.gravity = 0.4
        self.y_speed = 0
        self.is_grounded = False
        self.run_animation_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.attack = 1
        self.HP = 3
        self.running_unlocked = False
        self.double_jump_unlocked = False
        self.shield = 0
        self.is_dead = False
        self.is_out = False
        self.falling_through = False
        self.can_jump = True
        self.can_double_jump = False
        self.jump_flag = False
        self.running_sprites_right = running_sprites_right
        self.running_sprites_left = running_sprites_left
        self.idle_sprite = me_image
        self.damaged_sprite = me_damaged_image
        self.rect = self.idle_sprite.get_rect()
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.image = self.idle_sprite

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            if self.running_unlocked and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                self.rect.x -= 2 * self.speed
            else:
                self.rect.x -= self.speed
            self.update_animation()
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.running_unlocked and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
                self.rect.x += 2 * self.speed
            else:
                self.rect.x += self.speed
            self.update_animation()
        else:
            self.image = self.idle_sprite
            self.run_animation_index = 0

    def handle_event(self, event):
        # Обработка события KEYDOWN/KEYUP
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.jump_flag = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.jump_flag = False

    def handle_jump(self):
        if self.is_grounded:
            self.jump()
            self.can_double_jump = True
        elif self.can_double_jump and self.double_jump_unlocked:
            self.jump()
            self.can_double_jump = False

    def update_animation(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        is_running_1 = keys[pygame.K_LSHIFT] and self.running_unlocked
        is_running_2 = keys[pygame.K_RSHIFT] and self.running_unlocked
        animation_delay = 50 if (is_running_1 or is_running_2) else 70
        if now - self.last_update_time > animation_delay:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_left)
                self.image = self.running_sprites_left[self.run_animation_index]
                self.last_update_time = now
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_right)
                self.image = self.running_sprites_right[self.run_animation_index]
                self.last_update_time = now

    def jump(self):
        self.y_speed = -10

    def update(self):
        global level_1_part_1_scroll_pos

        # Оригинальные границы для других уровней
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > W:
            self.rect.right = W

        # Остальная физика без изменений
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        if self.is_dead:
            # Персонаж мертв - особые правила
            if not self.falling_through:
                # Первая фаза - подпрыгивание и падение
                if self.rect.bottom > H - GROUND_H:
                    self.rect.bottom = H - GROUND_H
                    self.falling_through = True  # Начинаем проваливаться
            else:
                # Вторая фаза - проваливание
                if self.rect.top > H:  # Полностью ушел за экран
                    self.is_out = True
        else:
            # Обычная физика для живого персонажа
            if self.rect.bottom >= H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_grounded = True
                self.can_double_jump = True  # сбрасываем при приземлении
            else:
                self.is_grounded = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def respawn(self):
        self.is_out = False
        self.is_dead = False
        self.rect.midbottom = (W // 2, H - GROUND_H)

    def damaged(self):
        self.y_speed = -10
        self.is_grounded = False
        self.image = me_damaged_image
        self.can_jump = False

    def kill(self, dead_image):
        self.image = dead_image
        self.is_dead = True
        self.y_speed = -15  # Сильный прыжок вверх
        self.falling_through = False

#Характеристика и функции врагов
class Monster:
    def __init__(self):
        try:
            self.image = pygame.transform.scale(pygame.image.load('Sprites and objects/Enemies/Enemy.png'), (90, 90))
        except:
            self.image = pygame.Surface((90, 90))
        self.rect = self.image.get_rect()
        self.x_speed = 0
        self.y_speed = 0
        self.speed = 5
        self.jump_num = 0
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -10
        self.gravity = 0.4
        self.is_grounded = False
        self.damage_given = False
        self.spawn()

    def spawn(self):
        direction = random.randint(0, 1)
        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, 0)
            try:
                self.image = pygame.transform.scale(pygame.image.load('Sprites and objects/Enemies/Enemy-left.png'), (90, 90))
            except:
                self.image = pygame.Surface((90, 90))
        else:
            self.x_speed = -self.speed
            self.rect.bottomright = (W, 0)
            try:
                self.image = pygame.transform.scale(pygame.image.load('Sprites and objects/Enemies/Enemy.png'), (90, 90))
            except:
                self.image = pygame.Surface((90, 90))

    def kill(self):
        try:
            self.image = pygame.transform.scale(pygame.image.load('Sprites and objects/Enemies/EnemyDead.png'), (90, 90))
        except:
            self.image = pygame.Surface((90, 90))
        self.is_dead = True
        self.x_speed = -self.x_speed
        self.y_speed = self.jump_speed

    def update(self):
        self.rect.x += self.x_speed
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        if self.is_dead:
            if self.rect.top > H - GROUND_H:
                self.is_out = True
        else:
            if self.rect.bottom > H - GROUND_H:
                self.is_grounded = True
                self.jump_num = 0
                self.y_speed = 0
                self.rect.bottom = H - GROUND_H

    def draw(self, surface):
        surface.blit(self.image, self.rect)

player = Player()

#Главное меню
def main_menu():
    global player, menu, levels_in, from_menu, from_level, current_skin_index
    load_settings()
    menu = True
    options_rects = [
        pygame.Rect(W // 2 - 100, H // 2 - 100, 200, 40), # "Начать игру"
        pygame.Rect(W // 2 - 100, H // 2 - 50, 200, 40),  # "Скины"
        pygame.Rect(W // 2 - 100, H // 2, 200, 40),       # "Улучшение"
        pygame.Rect(W // 2 - 100, H // 2 + 50, 200, 40),  # "Настройки"
        pygame.Rect(W // 2 - 100, H // 2 + 100, 200, 40), # "Секреты"
        pygame.Rect(W // 2 - 100, H // 2 + 150, 200, 40)  # "Выход"
    ]
    temp_player = Player()
    load_game(temp_player)
    load_skin()
    apply_skin(current_skin_index)
    player = Player()
    from_level = False
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # левый клик
                mouse_pos = event.pos
                for idx, rect in enumerate(options_rects):
                    if rect.collidepoint(mouse_pos):
                        selected = idx
                        if selected == 0:
                            menu = False
                            from_menu = True
                            level_menu()
                        elif selected == 1:
                            skin_menu()
                        elif selected == 2:
                            upgrade()
                        elif selected == 3:
                            settings()
                        elif selected == 4:
                            secrets()
                        elif selected == 5:
                            pygame.quit()
                            sys.exit()

        mouse_pos = pygame.mouse.get_pos()

        screen.fill((92, 148, 252))
        draw_text('Главное меню', font_large, (255, 255, 255), screen, W // 2, H // 4)
        options = ['Начать игру', 'Скины', 'Улучшение', 'Настройки', 'Секреты', 'Выход из игры']
        for j, opt in enumerate(options):
            rect = options_rects[j]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            draw_text(opt, font_small, color, screen, W // 2, H // 2 - 90 + j * 50)
        pygame.display.flip()
        clock.tick(60)

#Меню со скинами
def skin_menu():
    global current_skin_index, me_image, running_sprites_right, running_sprites_left, skin_message_timer

    in_skin_menu = True
    for skin in skins:
        if skin['name'] == 'Соник':
            if player.running_unlocked:
                skin['unlocked'] = True
        if skin['name'] == 'Марио':
            if player.double_jump_unlocked:
                skin['unlocked'] = True
    # Создаем список прямоугольников для кликабельных областей
    skin_rects = []
    for idx in range(len(skins)):
        skin_rects.append(pygame.Rect(W // 2 - 150, H // 4 + idx * 60 - 20, 300, 40))
    load_upgrades(player)
    load_skin()
    # Прямоугольник для кнопки "Назад"
    back_rect = pygame.Rect(W // 2 - 50, H - 70, 100, 40)
    while in_skin_menu:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        screen.fill((92, 148, 252))
        draw_text('Выбор скина', font_large, (255, 255, 255), screen, W // 2, H // 6 - 40)

        for skin in skins:
            if skin['name'] == 'Соник':
                if player.running_unlocked:
                    skin['unlocked'] = True
            if skin['name'] == 'Марио':
                if player.double_jump_unlocked:
                    skin['unlocked'] = True

        # Отрисовка скинов и обработка кликов
        for idx, skin in enumerate(skins):
            y_pos = H // 4 + idx * 60
            is_hovered = skin_rects[idx].collidepoint(mouse_pos)
            is_selected = (idx == current_skin_index)
            color = (255, 255, 255) if (is_hovered or is_selected) else (0, 0, 0)

            draw_text(skin['name'], font_small, color, screen, W // 2, y_pos)

            if 'img' in skin:
                img_surface = skin['img']
                if isinstance(img_surface, pygame.Surface):
                    img_rect = img_surface.get_rect(center=(W // 2 - 120, y_pos))
                    screen.blit(img_surface, img_rect)
            status = 'Открыт' if skin['unlocked'] else 'Закрыт'
            draw_text(status, font_small, color, screen, W // 2 + 150, y_pos)

            if is_hovered and mouse_clicked and skin['unlocked']:
                current_skin_index = idx
                apply_skin(current_skin_index)
                player.running_sprites_right = running_sprites_right
                player.running_sprites_left = running_sprites_left
                player.idle_sprite = me_image
                player.image = player.idle_sprite
                player.damaged_sprite = me_damaged_image
                save_game(player)
                save_skin()

            if is_hovered and not skin['unlocked']:
                draw_text(skin['unlock'], font_small, (255, 255, 255), screen, W // 2, H // 2 + 130)

        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text('Главное меню', font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            in_skin_menu = False

        pygame.display.flip()
        clock.tick(60)

def settings():
    global music_on, player_points, difficulty_level
    load_upgrades(player)
    options_settings = [
        'Уровень сложности',
        'Музыка',
        'Сброс прогресса',
        'Сохранить настройки',
        'Отменить',
        'Управление',
        'Главное меню'
    ]
    options_settings_rects = [
        pygame.Rect(W // 2 - 100, H // 3, 200, 40),       # "Уровень сложности"
        pygame.Rect(W // 2 - 100, H // 3 + 50, 200, 40),  # "Музыка"
        pygame.Rect(W // 2 - 100, H // 3 + 100, 200, 40), # "Сброс прогресса"
        pygame.Rect(W // 2 - 100, H // 3 + 150, 200, 40), # "Сохранить настройки"
        pygame.Rect(W // 2 - 100, H // 3 + 200, 200, 40), # "Отменить"
        pygame.Rect(W // 2 - 100, H // 3 + 250, 200, 40),  # "Управление"
        pygame.Rect(W // 2 - 100, H // 3 + 300, 200, 40)  # "Главное меню"
    ]
    # Объявляем переменные один раз перед циклом
    temp_points = player_points
    temp_difficulty = difficulty_level

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # левый клик
                mouse_pos = event.pos
                for idx, rect in enumerate(options_settings_rects):
                    if rect.collidepoint(mouse_pos):
                        selected_idx = idx
                        if selected_idx == 0:
                            temp_difficulty = (temp_difficulty + 1) % 3
                        elif selected_idx == 1:
                            toggle_music()
                            if music_on:
                                play_menu_music()
                        elif selected_idx == 2:
                            with open('Save_files/last.json', 'w'):
                                pass
                            with open('Save_files/upgrades.json', 'w'):
                                pass
                            with open('Save_files/settings.json', 'w'):
                                pass
                            player_points = 0
                        elif selected_idx == 3:
                            player_points = temp_points
                            difficulty_level = temp_difficulty
                            save_settings()
                            save_game(player, score)
                            save_skin()
                            if music_on:
                                pygame.mixer.music.unpause()
                            else:
                                pygame.mixer.music.pause()
                        elif selected_idx == 4:
                            temp_difficulty = 0
                            save_settings()
                            save_game(player, score)
                            save_skin()
                        elif selected_idx == 5:
                            management_menu()
                        elif selected_idx == 6:
                            main_menu()
        mouse_pos = pygame.mouse.get_pos()
        # Отрисовка
        screen.fill((92, 148, 252))
        draw_text('Настройки', font_large, (255,255,255), screen, W // 2, H // 6)
        for idx, opt in enumerate(options_settings):
            rect = options_settings_rects[idx]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            if options_settings[idx] == 'Музыка':
                status = 'Вкл' if music_on else 'Выкл'
                draw_text(f'Музыка: {status}', font_small, color, screen, W // 2, H // 3 + idx * 50)
            elif options_settings[idx] == 'Уровень сложности':
                levels = ['Легко', 'Средне', 'Сложно']
                level_text = f'Уровень сложности: {levels[temp_difficulty]}'
                draw_text(level_text, font_small, color, screen, W // 2, H // 3 + idx * 50)
            else:
                draw_text(opt, font_small, color, screen, W//2, H//3 + idx * 50)


        # Кол-во очков
        draw_text(f'Очки: {player_points}', font_small, (255,255,255), screen, W - 100, 50)

        pygame.display.flip()
        clock.tick(60)

# Внутренний менеджер управления
def management_menu():
    rect_exit = pygame.Rect(W // 2 - 100, H - 70, 200, 40)
    # Можно реализовать список клавиш
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # левый клик
                mouse_pos = e.pos
                if rect_exit.collidepoint(mouse_pos):
                    return

        mouse_pos = pygame.mouse.get_pos()
        screen.fill((92, 148, 252))
        draw_text("Управление", font_large, (255, 255, 255), screen, W // 2, H // 3 - 80)
        controls = [
            'Передвижение: A / ←, D / →',
            'Прыжок: W / ↑',
            'Бег: (A / ←) / (D / →) + Shift',
            'Пауза: ESC',
            'Сохранение: S'
        ]
        for h, control in enumerate(controls):
            draw_text(control, font_small, (0, 0, 0), screen, W // 2, H // 3 + h * 40)

        if rect_exit.collidepoint(mouse_pos):
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)
        draw_text('Выход', font_small, color, screen, W//2, H - 50)
        pygame.display.flip()
        clock.tick(60)

def secrets():
    pass

# Выбор уровней
def level_menu():
    global levels_in, music_playing, from_menu, from_level
    load_skin()
    # Создаем прямоугольники для кликабельных областей уровней
    level_rects = []
    options = ['Уровень 1', 'Уровень 2', 'Уровень 3',
               'Уровень 4', 'Уровень 5', 'Уровень 6',
               'Уровень 7', 'Уровень 8', 'Уровень 9']

    for j in range(3):  # Первые 3 уровня слева
        level_rects.append(pygame.Rect(W // 3 - 200, H // 3 + j * 70 - 10, 150, 40))
    for j in range(3, 6):  # Следующие 3 уровня посередине
        level_rects.append(pygame.Rect(W // 2 - 50, H // 3 + (j - 3) * 70 - 10, 150, 40))
    for j in range(6, 9):  # Последние 3 уровня справа
        level_rects.append(pygame.Rect(W // 3 * 2, H // 3 + (j - 6) * 70 - 10, 150, 40))
    # Прямоугольник для кнопки "Назад"
    back_rect = pygame.Rect(W // 2 - 50, H - 70, 100, 40)
    levels_in = True
    if from_level and not from_menu:
        stop_music()
        play_menu_music()
    elif from_menu:
        pass
    while levels_in:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        screen.fill((92, 148, 252))
        draw_text('Выбор уровня', font_large, (255, 255, 255), screen, W // 2, H // 6)

        # Отрисовка уровней и обработка кликов
        for j, opt in enumerate(options):
            is_hovered = level_rects[j].collidepoint(mouse_pos)
            color = (255, 255, 255) if is_hovered else (0, 0, 0)
            x_pos = W // 3 - 100 if j < 3 else (W // 2 if (3 <= j < 6) else W // 3 * 2 + 100)
            draw_text(opt, font_small, color, screen, x_pos, H // 3 + 20 + (j % 3) * 70)

            if is_hovered and mouse_clicked:
                if j == 0:
                    level_1_part_1()
                elif j == 1:
                    level_2_part_1()
                elif j == 2:
                    pygame.quit()
                    sys.exit()

        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text('Главное меню', font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            main_menu()
            levels_in = False

        pygame.display.flip()
        clock.tick(60)

def upgrade():
    global music_playing, from_menu, from_level, player_points, player
    load_upgrades(player)
    # Создаем прямоугольники для кликабельных областей уровней
    pluses = []
    minuses = []
    options = ['Атака', 'HP', 'Бег', 'Двойной прыжок', 'Щит']
    upgrade_chars = [player.attack, player.HP, player.running_unlocked, player.double_jump_unlocked, player.shield]
    upgrading = True
    for j in range(5):
        if j != 2 and j != 3:
            pluses.append(pygame.Rect(W // 3 + 30, H // 3 + j * 70 - 10, 50, 40))
        else:
            pluses.append(pygame.Rect(W // 3 + 70, H // 3 + j * 70 - 10, 50, 40))
    for j in range(5):
        if j != 2 and j != 3:
            minuses.append(pygame.Rect(W // 3 + 110, H // 3 + j * 70 - 10, 50, 40))
        else:
            minuses.append(pygame.Rect(0, 0, 0, 0))
    # Прямоугольник для кнопки "Назад"
    back_rect = pygame.Rect(W // 2 - 50, H - 70, 100, 40)
    while upgrading:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        screen.fill((92, 148, 252))
        draw_text('Улучшение', font_large, (255, 255, 255), screen, W // 2, H // 6)

        # Отрисовка уровней и обработка кликов
        for j, opt in enumerate(options):
            is_hovered_pluses = pluses[j].collidepoint(mouse_pos)
            color_pluses = (255, 255, 255) if is_hovered_pluses else (0, 0, 0)
            is_hovered_minuses = minuses[j].collidepoint(mouse_pos)
            color_minuses = (255, 255, 255) if is_hovered_minuses else (0, 0, 0)
            x_pos = W // 3 - 100
            draw_text(opt, font_small, (0, 0, 0), screen, x_pos, H // 3 + 20 + j * 70)
            if j != 2 and j != 3:
                draw_text('+', font_medium, color_pluses, screen, W // 3 + 60, H // 3 + 20 + j * 70)
                draw_text('/', font_medium, (0, 0, 0), screen, W // 3 + 100, H // 3 + 20 + j * 70)
                draw_text('-', font_medium, color_minuses, screen, W // 3 + 140, H // 3 + 20 + j * 70)
            else:
                draw_text('+', font_medium, color_pluses, screen, W // 3 + 100, H // 3 + 20 + j * 70)
            if opt == 'Бег' or opt == 'Двойной прыжок':
                if upgrade_chars[j]:
                    draw_text('Открыт', font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)
                else:
                    draw_text('Закрыт', font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)
            else:
                draw_text(str(upgrade_chars[j]), font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)

            if is_hovered_pluses and mouse_clicked:
                if j == 0 and player_points >= 1:
                    upgrade_chars[j] += 1
                    player.attack += 1
                    player_points -= 1
                elif j == 1 and player_points >= 1:
                    upgrade_chars[j] += 1
                    player.HP += 1
                    player_points -= 1
                elif j == 2 and player_points >= 3 and not player.running_unlocked:
                    upgrade_chars[j] = True
                    player.running_unlocked = True
                    player_points -= 3
                elif j == 3 and player_points >= 4 and not player.double_jump_unlocked:
                    upgrade_chars[j] = True
                    player.double_jump_unlocked = True
                    player_points -= 4
                elif j == 4 and player_points >= 3:
                    upgrade_chars[j] += 1
                    player.shield += 1
                    player_points -= 3
                save_upgrades(player)
            if is_hovered_minuses and mouse_clicked and j != 2 and j != 3:
                if j == 0 and upgrade_chars[j] > 1:
                    upgrade_chars[j] -= 1
                    player.attack -= 1
                    player_points += 1
                elif j == 1 and upgrade_chars[j] > 3:
                    upgrade_chars[j] -= 1
                    player_points += 1
                    player.HP -= 1
                elif j == 4 and upgrade_chars[j] >= 1:
                    upgrade_chars[j] -= 1
                    player_points += 3
                save_upgrades(player)
                load_upgrades(player)

        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text('Главное меню', font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            save_upgrades(player)
            main_menu()
            upgrading = False
        draw_text(f'Очки: {player_points}', font_small, (255, 255, 255), screen, W - 100, 50)
        pygame.display.flip()
        clock.tick(60)

level_part_1 = True
HP = player.HP
Shield = player.shield

#Первая часть уровня
def level_1_part_1():
    global level_part_1, level_1_part_1_scroll_pos, level_1_part_1_in, menu, playing_level, playing_menu, score
    portal_rect = portal_image.get_rect(center=(level_1_part_1_WIDTH - 200, H - GROUND_H - 45))
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    menu = False
    level_1_part_1_in = True
    playing_menu = False
    playing_level = True
    stop_music()
    play_level_music()
    load_upgrades(player)
    # Создаем большую поверхность для уровня
    level_surface = pygame.Surface((level_1_part_1_WIDTH, H))
    level_surface.fill((92, 148, 252))  # Основной фон
    score, level_1_part_1_scroll_pos = load_game(player)
    # Рисуем землю
    for x in range(0, level_1_part_1_WIDTH, ground_image.get_width()):
        level_surface.blit(ground_image, (x, H - GROUND_H))

    while level_1_part_1_in:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                level_1_part_1_in = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(player, score)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                if event.key == pygame.K_w or event.key == pygame.K_UP and player.double_jump_unlocked:
                    player.handle_jump()

        # Очищаем экран
        screen.fill((0, 0, 0))

        # Отрисовываем видимую часть уровня
        screen.blit(level_surface, (0, 0), (level_1_part_1_scroll_pos, 0, W, H))

        # Отрисовываем портал (с учетом скролла)
        screen.blit(portal_image, (portal_rect.x - level_1_part_1_scroll_pos, portal_rect.y))

        # Отрисовываем игрока (всегда в центре экрана)
        player.draw(screen)

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        if not paused:
            # Обработка ввода и движение
            player.handle_input()
            player.update()
            keys = pygame.key.get_pressed()
            # Обновляем скролл на основе движения игрока
            if player.rect.centerx > W // 2 and level_1_part_1_scroll_pos < level_1_part_1_WIDTH - W:
                # Игрок движется вправо - скроллим фон
                scroll_amount = player.rect.centerx - W // 2
                scroll_speed = 5  # Скорость скролла
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    scroll_speed *= 2
                level_1_part_1_scroll_pos += min(scroll_amount, scroll_speed)
                # Фиксируем игрока в центре
                player.rect.centerx = W // 2
            elif player.rect.centerx < W // 2 and level_1_part_1_scroll_pos > 0:
                # Игрок движется влево - скроллим фон
                scroll_amount = W // 2 - player.rect.centerx
                scroll_speed = 5  # Скорость скролла
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    scroll_speed *= 2
                level_1_part_1_scroll_pos -= min(scroll_amount, scroll_speed)
                # Фиксируем игрока в центре
                player.rect.centerx = W // 2

            if player.rect.bottom > H - GROUND_H:
                player.rect.bottom = H - GROUND_H
                player.y_speed = 0
                player.is_grounded = True

            # Проверка коллизии с порталом
            if player.rect.colliderect(pygame.Rect(
                    portal_rect.x - level_1_part_1_scroll_pos,
                    portal_rect.y,
                    portal_rect.width,
                    portal_rect.height
            )):
                level_1_part_1_scroll_pos = 3200
                save_game(player, score)
                level_part_1 = False
                level_1_part_2()
                return

        # Индикатор прогресса
        progress = level_1_part_1_scroll_pos / (level_1_part_1_WIDTH - W)
        pygame.draw.rect(screen, (255, 255, 255), (50, 30, 200, 10))
        pygame.draw.rect(screen, (0, 255, 0), (50, 30, 200 * progress, 10))
        if player.jump_flag:
            player.handle_jump()
            player.jump_flag = False
        pygame.display.flip()
        clock.tick(FPS)

#Вторая часть уровня
def level_1_part_2():
    global monsters, last_spawn_time, spawn_delay, score, level_1_part_1_scroll_pos, player_points, HP, from_level, from_menu, \
        playing_menu, Shield
    load_upgrades(player)
    HP = player.HP
    Shield = player.shield
    # Обнуляем список врагов и таймеры при входе
    monsters = []
    last_spawn_time = pygame.time.get_ticks()

    # Остальной код уровня
    player.rect.midbottom = (W // 2, H - GROUND_H)

    save_message_displayed = False
    save_message_timer = 0
    paused = False
    running = True
    invincible = False
    invincible_end_time = 0

    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                if now >= invincible_end_time:
                    player.image = me_image
                    invincible = False
                    player.speed = 5
                    player.can_jump = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(player, score)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif player.is_out:
                    score, level_1_part_1_scroll_pos = load_game(player)
                    load_upgrades(player)
                    HP = player.HP
                    player.respawn()
                    monsters.clear()
                    spawn_delay = 2000
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.handle_jump()
        # В основном цикле, после обработки событий:
        if invincible:
            if now % 500 < 250:  # Мигание каждые 500 мс (250 мс видно, 250 мс нет)
                player.image = me_damaged_image
            else:
                player.image = me_image
        screen.fill((92, 148, 252))
        screen.blit(ground_image, (0, H - GROUND_H))

        for monster in monsters:
            monster.draw(screen)

        player.draw(screen)

        draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
        draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
        draw_text(f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20)

        if score >= 10:
            # Убиваем всех монстров
            for monster in list(monsters):
                monster.kill()

            end_time = pygame.time.get_ticks() + 2000  # 2 секунды на завершение

            while pygame.time.get_ticks() < end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Обновляем игрока (чтобы он мог упасть на землю)
                player.handle_input()
                player.update()

                # Обновляем монстров (чтобы они упали за экран)
                for monster in list(monsters):
                    monster.update()
                    if monster.is_out:
                        monsters.remove(monster)

                # Отрисовка
                screen.fill((92, 148, 252))
                screen.blit(ground_image, (0, H - GROUND_H))

                for monster in monsters:
                    monster.draw(screen)

                player.draw(screen)
                draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
                draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
                draw_text("Уровень пройден!", font_small, (255, 255, 255), screen, W // 2, H // 2)
                draw_text(f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20)
                pygame.mixer.music.pause()
                pygame.display.flip()
                clock.tick(FPS)

            # Очищаем сохранение и выходим
            with open('Save_files/last.json', 'w'):
                pass
            pygame.time.wait(2000)
            player_points += 3
            save_upgrades(player)
            save_settings()
            playing_menu = True
            from_level = True
            from_menu = False
            level_menu()

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        if player.is_out:
            draw_text("PRESS ANY KEY", font_small, (255, 255, 255), screen, W // 2, H // 2)
        else:
            if not paused:
                player.handle_input()
                player.update()

                if now - last_spawn_time > spawn_delay:
                    monsters.append(Monster())
                    last_spawn_time = now

                for monster in list(monsters):
                    if monster.is_out:
                        monsters.remove(monster)
                    else:
                        monster.update()

                        if player.rect.colliderect(monster.rect) and not monster.is_dead:
                            if (player.rect.bottom < monster.rect.centery and
                                    player.y_speed > 0 and
                                    abs(player.rect.centerx - monster.rect.centerx) < monster.rect.width / 2):
                                monster.kill()
                                player.y_speed -= 15
                                player.is_grounded = False
                                player.can_jump = False
                                score += 1
                            elif not monster.damage_given and not invincible:
                                if Shield >= 1:
                                    Shield -= 1
                                    player.shield -= 1
                                    save_upgrades(player)
                                    load_upgrades(player)
                                    invincible = True
                                    invincible_end_time = now + 1000
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                                else:
                                    HP -= 1
                                    player.damaged()
                                    monster.damage_given = True
                                    invincible = True
                                    invincible_end_time = now + 1000  # Устанавливаем время окончания
                                    player.speed = 0
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)

                                if HP <= 0:
                                    player.kill(me_image)
                        else:
                            monster.damage_given = False

        pygame.display.flip()
        clock.tick(FPS)

def level_2_part_1():
    global level_part_1, level_1_part_1_scroll_pos, level_2_part_1_in, menu, playing_level, playing_menu, score
    portal_rect = portal_image.get_rect(center=(level_1_part_1_WIDTH - 200, H - GROUND_H - 45))
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    menu = False
    level_2_part_1_in = True
    playing_menu = False
    playing_level = True
    stop_music()
    play_level_music()
    load_upgrades(player)
    # Создаем большую поверхность для уровня
    level_surface = pygame.Surface((level_1_part_1_WIDTH, H))
    level_surface.fill((92, 148, 252))  # Основной фон
    score, level_1_part_1_scroll_pos = load_game(player)
    # Рисуем землю
    for x in range(0, level_1_part_1_WIDTH, ground_image.get_width()):
        level_surface.blit(ground_image, (x, H - GROUND_H))

    while level_2_part_1_in:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                level_2_part_1_in = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(player, score)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                if event.key == pygame.K_w or event.key == pygame.K_UP and player.double_jump_unlocked:
                    player.handle_jump()

        # Очищаем экран
        screen.fill((0, 0, 0))

        # Отрисовываем видимую часть уровня
        screen.blit(level_surface, (0, 0), (level_1_part_1_scroll_pos, 0, W, H))

        # Отрисовываем портал (с учетом скролла)
        screen.blit(portal_image, (portal_rect.x - level_1_part_1_scroll_pos, portal_rect.y))

        # Отрисовываем игрока (всегда в центре экрана)
        player.draw(screen)

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        if not paused:
            # Обработка ввода и движение
            player.handle_input()
            player.update()
            keys = pygame.key.get_pressed()
            # Обновляем скролл на основе движения игрока
            if player.rect.centerx > W // 2 and level_1_part_1_scroll_pos < level_1_part_1_WIDTH - W:
                # Игрок движется вправо - скроллим фон
                scroll_amount = player.rect.centerx - W // 2
                scroll_speed = 5  # Скорость скролла
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    scroll_speed *= 2
                level_1_part_1_scroll_pos += min(scroll_amount, scroll_speed)
                # Фиксируем игрока в центре
                player.rect.centerx = W // 2
            elif player.rect.centerx < W // 2 and level_1_part_1_scroll_pos > 0:
                # Игрок движется влево - скроллим фон
                scroll_amount = W // 2 - player.rect.centerx
                scroll_speed = 5  # Скорость скролла
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    scroll_speed *= 2
                level_1_part_1_scroll_pos -= min(scroll_amount, scroll_speed)
                # Фиксируем игрока в центре
                player.rect.centerx = W // 2

            if player.rect.bottom > H - GROUND_H:
                player.rect.bottom = H - GROUND_H
                player.y_speed = 0
                player.is_grounded = True

            # Проверка коллизии с порталом
            if player.rect.colliderect(pygame.Rect(
                    portal_rect.x - level_1_part_1_scroll_pos,
                    portal_rect.y,
                    portal_rect.width,
                    portal_rect.height
            )):
                level_1_part_1_scroll_pos = 3200
                save_game(player, score)
                level_part_1 = False
                level_2_part_2()
                return

        # Индикатор прогресса
        progress = level_1_part_1_scroll_pos / (level_1_part_1_WIDTH - W)
        pygame.draw.rect(screen, (255, 255, 255), (50, 30, 200, 10))
        pygame.draw.rect(screen, (0, 255, 0), (50, 30, 200 * progress, 10))
        if player.jump_flag:
            player.handle_jump()
            player.jump_flag = False
        pygame.display.flip()
        clock.tick(FPS)

#Вторая часть уровня
def level_2_part_2():
    global monsters, last_spawn_time, spawn_delay, score, level_1_part_1_scroll_pos, player_points, HP, from_level, from_menu, \
        playing_menu, Shield
    load_upgrades(player)
    HP = player.HP
    Shield = player.shield
    # Обнуляем список врагов и таймеры при входе
    monsters = []
    last_spawn_time = pygame.time.get_ticks()

    # Остальной код уровня
    player.rect.midbottom = (W // 2, H - GROUND_H)

    save_message_displayed = False
    save_message_timer = 0
    paused = False
    running = True
    invincible = False
    invincible_end_time = 0

    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                if now >= invincible_end_time:
                    player.image = me_image
                    invincible = False
                    player.speed = 5
                    player.can_jump = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game(player, score)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif player.is_out:
                    score, level_1_part_1_scroll_pos = load_game(player)
                    load_upgrades(player)
                    HP = player.HP
                    player.respawn()
                    monsters.clear()
                    spawn_delay = 2000
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.handle_jump()
        # В основном цикле, после обработки событий:
        if invincible:
            if now % 500 < 250:  # Мигание каждые 500 мс (250 мс видно, 250 мс нет)
                player.image = me_damaged_image
            else:
                player.image = me_image
        screen.fill((92, 148, 252))
        screen.blit(ground_image, (0, H - GROUND_H))

        for monster in monsters:
            monster.draw(screen)

        player.draw(screen)

        draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
        draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
        draw_text(f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20)

        if score >= 10:
            # Убиваем всех монстров
            for monster in list(monsters):
                monster.kill()

            end_time = pygame.time.get_ticks() + 2000  # 2 секунды на завершение

            while pygame.time.get_ticks() < end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Обновляем игрока (чтобы он мог упасть на землю)
                player.handle_input()
                player.update()

                # Обновляем монстров (чтобы они упали за экран)
                for monster in list(monsters):
                    monster.update()
                    if monster.is_out:
                        monsters.remove(monster)

                # Отрисовка
                screen.fill((92, 148, 252))
                screen.blit(ground_image, (0, H - GROUND_H))

                for monster in monsters:
                    monster.draw(screen)

                player.draw(screen)
                draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
                draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
                draw_text("Уровень пройден!", font_small, (255, 255, 255), screen, W // 2, H // 2)
                draw_text(f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20)
                pygame.mixer.music.pause()
                pygame.display.flip()
                clock.tick(FPS)

            # Очищаем сохранение и выходим
            with open('Save_files/last.json', 'w'):
                pass
            pygame.time.wait(2000)
            player_points += 3
            save_upgrades(player)
            save_settings()
            playing_menu = True
            from_level = True
            from_menu = False
            level_menu()

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        if player.is_out:
            draw_text("PRESS ANY KEY", font_small, (255, 255, 255), screen, W // 2, H // 2)
        else:
            if not paused:
                player.handle_input()
                player.update()

                if now - last_spawn_time > spawn_delay:
                    monsters.append(Monster())
                    last_spawn_time = now

                for monster in list(monsters):
                    if monster.is_out:
                        monsters.remove(monster)
                    else:
                        monster.update()

                        if player.rect.colliderect(monster.rect) and not monster.is_dead:
                            if (player.rect.bottom < monster.rect.centery and
                                    player.y_speed > 0 and
                                    abs(player.rect.centerx - monster.rect.centerx) < monster.rect.width / 2):
                                monster.kill()
                                player.y_speed -= 15
                                player.is_grounded = False
                                player.can_jump = False
                                score += 1
                            elif not monster.damage_given and not invincible:
                                if Shield >= 1:
                                    Shield -= 1
                                    player.shield -= 1
                                    save_upgrades(player)
                                    load_upgrades(player)
                                    invincible = True
                                    invincible_end_time = now + 1000
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                                else:
                                    HP -= 1
                                    player.damaged()
                                    monster.damage_given = True
                                    invincible = True
                                    invincible_end_time = now + 1000  # Устанавливаем время окончания
                                    player.speed = 0
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)

                                if HP <= 0:
                                    player.kill(me_image)
                        else:
                            monster.damage_given = False

        pygame.display.flip()
        clock.tick(FPS)

#Запуск игры
load_settings()
music_playing = False
play_menu_music()
main_menu()
pygame.quit()