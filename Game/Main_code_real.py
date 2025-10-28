# Импорт необходимых библиотек
import random
import sqlite3
import sys
import pygame
from pygame import Surface

pygame.init()

# Настройки игры
font_path = "caviar-dreams.ttf"
font_large = pygame.font.Font(font_path, 48)
font_medium = pygame.font.Font(font_path, 36)
font_small = pygame.font.Font(font_path, 24)

# Игровые переменные
player_points_easy = 0
player_points_medium = 0
player_points_hard = 0
current_player_points = 0
difficulty_level = 0
current_difficulty = 0
dark_mode = False
pending_mode = dark_mode
background_image = (42, 98, 202) if dark_mode else (92, 148, 252)
save_message_displayed = False
save_message_timer = 0

# Игровые объекты
monsters = []
boss = []
score = 0

# Состояния игры
menu = False
playing_menu = True
playing_level = False
from_menu = False
from_level = False

# Настройки экрана
W, H = 1000, 800
screen = pygame.display.set_mode((W, H))
FPS = 60
clock = pygame.time.Clock()
GROUND_H = 60

# Загрузка изображений
ground_image: Surface = pygame.image.load("Sprites and objects/Objects, background and other/2d-Pixel-Grass.png")
ground_image = pygame.transform.scale(ground_image, (500, GROUND_H))
me_image = pygame.image.load("Sprites and objects/Skins/Me/Me.png")
me_image = pygame.transform.scale(me_image, (70, 80))

boss_image = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_right_1.png")
boss_image = pygame.transform.scale(boss_image, (140, 140))
portal_image = pygame.image.load("Sprites and objects/Objects, background and other/p2.gif")
portal_image = pygame.transform.scale(portal_image, (80, 90))
me_damaged_image = pygame.image.load("Sprites and objects/Skins/Me/Me_damaged.png")
me_damaged_image = pygame.transform.scale(me_damaged_image, (70, 80))

# Настройки звука
music_on = True
sound_on = True
music_playing = False
menu_music = "Music/day_of_chaos.mp3"
level_1_part_1_music = "Music/kevin-macleod-machine.mp3"
level_2_part_1_music = "Music/Geometry_Dash_-_Geometrical_Dominator_67148396.mp3"
level_3_part_1_music = "Music/riding-into-the-sunset-20240527-202603.mp3"
level_4_part_1_music = "Music/Ghost-Story(chosic.com).mp3"

Unlock_skin_sound = pygame.mixer.Sound("Sounds/mixkit-unlock-new-item-game-notification-254.wav")

# Сообщения
unlock_message = None
unlock_message_time = 0
UNLOCK_MESSAGE_DURATION = 3000

message = None
message_time = 0
MESSAGE_DURATION = 3000

# Состояния уровней
level1_cleared = False
level2_cleared = False
level3_cleared = False
level4_cleared = False
level5_cleared = False
level6_cleared = False
Level = 1


# Класс для управления уровнями
class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.levels = {
            1: {
                "name": "Уровень 1",
                "width": 5000,
                "music": level_1_part_1_music,
                "bg_color": (92, 148, 252),
                "platforms": [
                    pygame.Rect(200, 650, 150, 20),
                    pygame.Rect(400, 570, 150, 20),
                    pygame.Rect(600, 500, 200, 20),
                    pygame.Rect(850, 450, 150, 20),
                    pygame.Rect(1100, 550, 180, 20),
                    pygame.Rect(1300, 450, 120, 20),
                    pygame.Rect(1500, 350, 400, 20),
                    pygame.Rect(2000, 500, 190, 20),
                    pygame.Rect(2400, 450, 160, 20),
                    pygame.Rect(2700, 500, 140, 20),
                    pygame.Rect(3000, 400, 190, 20),
                    pygame.Rect(3300, 500, 170, 20),
                    pygame.Rect(3600, 450, 130, 20),
                    pygame.Rect(3900, 450, 150, 20),
                    pygame.Rect(4200, 550, 160, 20),
                    pygame.Rect(4500, 450, 140, 20)
                ],
                "has_boss": False,
                "enemy_count": 10
            },
            2: {
                "name": "Уровень 2",
                "width": 5000,
                "music": level_2_part_1_music,
                "bg_color": (148, 100, 92),
                "platforms": [
                    pygame.Rect(150, 600, 120, 20),
                    pygame.Rect(350, 500, 140, 20),
                    pygame.Rect(600, 570, 150, 20),
                    pygame.Rect(800, 450, 130, 20),
                    pygame.Rect(1000, 520, 160, 20),
                    pygame.Rect(1250, 400, 110, 20),
                    pygame.Rect(1450, 480, 170, 20),
                    pygame.Rect(1700, 350, 150, 20),
                    pygame.Rect(1950, 550, 140, 20),
                    pygame.Rect(2200, 420, 130, 20),
                    pygame.Rect(2450, 500, 160, 20),
                    pygame.Rect(2700, 380, 120, 20),
                    pygame.Rect(2950, 470, 150, 20),
                    pygame.Rect(3200, 580, 140, 20),
                    pygame.Rect(3450, 420, 130, 20),
                    pygame.Rect(3700, 520, 160, 20),
                    pygame.Rect(3950, 350, 110, 20),
                    pygame.Rect(4200, 450, 150, 20),
                    pygame.Rect(4450, 550, 140, 20),
                    pygame.Rect(4700, 400, 130, 20)
                ],
                "has_boss": False,
                "enemy_count": 15
            },
            3: {
                "name": "Уровень 3",
                "width": 5000,
                "music": level_3_part_1_music,
                "bg_color": (148, 150, 92),
                "platforms": [
                    pygame.Rect(100, 500, 100, 20),
                    pygame.Rect(300, 400, 120, 20),
                    pygame.Rect(500, 300, 140, 20),
                    pygame.Rect(750, 450, 130, 20),
                    pygame.Rect(950, 350, 110, 20),
                    pygame.Rect(1200, 250, 150, 20),
                    pygame.Rect(1450, 400, 140, 20),
                    pygame.Rect(1700, 300, 120, 20),
                    pygame.Rect(1950, 200, 130, 20),
                    pygame.Rect(2200, 350, 160, 20),
                    pygame.Rect(2450, 450, 140, 20),
                    pygame.Rect(2700, 320, 130, 20),
                    pygame.Rect(2950, 220, 120, 20),
                    pygame.Rect(3200, 380, 150, 20),
                    pygame.Rect(3450, 280, 140, 20),
                    pygame.Rect(3700, 180, 130, 20),
                    pygame.Rect(3950, 330, 160, 20),
                    pygame.Rect(4200, 430, 140, 20),
                    pygame.Rect(4450, 320, 130, 20),
                    pygame.Rect(4700, 220, 120, 20)
                ],
                "has_boss": True,
                "enemy_count": 1
            },
            4: {
                "name": "Уровень 4",
                "width": 5000,
                "music": level_4_part_1_music,
                "bg_color": (100, 100, 150),
                "platforms": [
                    pygame.Rect(120, 520, 100, 20),
                    pygame.Rect(320, 420, 110, 20),
                    pygame.Rect(520, 320, 120, 20),
                    pygame.Rect(750, 470, 130, 20),
                    pygame.Rect(950, 370, 140, 20),
                    pygame.Rect(1200, 270, 150, 20),
                    pygame.Rect(1450, 420, 160, 20),
                    pygame.Rect(1700, 320, 130, 20),
                    pygame.Rect(1950, 220, 120, 20),
                    pygame.Rect(2200, 370, 140, 20),
                    pygame.Rect(2450, 470, 150, 20),
                    pygame.Rect(2700, 340, 130, 20),
                    pygame.Rect(2950, 240, 120, 20),
                    pygame.Rect(3200, 390, 140, 20),
                    pygame.Rect(3450, 290, 130, 20),
                    pygame.Rect(3700, 190, 120, 20),
                    pygame.Rect(3950, 340, 150, 20),
                    pygame.Rect(4200, 440, 140, 20),
                    pygame.Rect(4450, 330, 130, 20),
                    pygame.Rect(4700, 230, 120, 20)
                ],
                "has_boss": False,
                "enemy_count": 10
            },
            5: {
                "name": "Уровень 5",
                "width": 5000,
                "music": level_4_part_1_music,
                "bg_color": (100, 100, 150),
                "platforms": [
                    pygame.Rect(150, 550, 120, 20),
                    pygame.Rect(350, 450, 130, 20),
                    pygame.Rect(550, 350, 140, 20),
                    pygame.Rect(800, 500, 150, 20),
                    pygame.Rect(1000, 400, 130, 20),
                    pygame.Rect(1250, 300, 120, 20),
                    pygame.Rect(1500, 450, 140, 20),
                    pygame.Rect(1750, 350, 130, 20),
                    pygame.Rect(2000, 250, 120, 20),
                    pygame.Rect(2250, 400, 150, 20),
                    pygame.Rect(2500, 500, 140, 20),
                    pygame.Rect(2750, 370, 130, 20),
                    pygame.Rect(3000, 270, 120, 20),
                    pygame.Rect(3250, 420, 140, 20),
                    pygame.Rect(3500, 320, 130, 20),
                    pygame.Rect(3750, 220, 120, 20),
                    pygame.Rect(4000, 370, 150, 20),
                    pygame.Rect(4250, 470, 140, 20),
                    pygame.Rect(4500, 360, 130, 20),
                    pygame.Rect(4750, 260, 120, 20)
                ],
                "has_boss": False,
                "enemy_count": 10
            },
            6: {
                "name": "Уровень 6",
                "width": 5000,
                "music": level_3_part_1_music,
                "bg_color": (100, 100, 150),
                "platforms": [
                    pygame.Rect(100, 500, 110, 20),
                    pygame.Rect(300, 380, 120, 20),
                    pygame.Rect(500, 260, 130, 20),
                    pygame.Rect(750, 420, 140, 20),
                    pygame.Rect(950, 300, 130, 20),
                    pygame.Rect(1200, 180, 120, 20),
                    pygame.Rect(1450, 340, 150, 20),
                    pygame.Rect(1700, 440, 140, 20),
                    pygame.Rect(1950, 320, 130, 20),
                    pygame.Rect(2200, 200, 120, 20),
                    pygame.Rect(2450, 360, 140, 20),
                    pygame.Rect(2700, 460, 150, 20),
                    pygame.Rect(2950, 340, 130, 20),
                    pygame.Rect(3200, 220, 120, 20),
                    pygame.Rect(3450, 380, 140, 20),
                    pygame.Rect(3700, 280, 130, 20),
                    pygame.Rect(3950, 160, 120, 20),
                    pygame.Rect(4200, 320, 150, 20),
                    pygame.Rect(4450, 420, 140, 20),
                    pygame.Rect(4700, 300, 130, 20)
                ],
                "has_boss": True,
                "enemy_count": 1
            }
        }
        self.scroll_pos = 0
        self.level_surface = None
        self.portal_rect = None

    def load_level(self, level_num):
        if level_num in self.levels:
            self.current_level = level_num
            self.scroll_pos = 0
            level_data = self.levels[level_num]

            # Создаем поверхность для уровня
            self.level_surface = pygame.Surface((level_data["width"], H))
            self.level_surface.fill(level_data["bg_color"])

            # Рисуем землю
            if level_num == 1:
                for x in range(0, 1800, ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
                for x in range(2200, level_data["width"], ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
            else:
                for x in range(0, level_data["width"], ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))

            # Создаем портал
            self.portal_rect = portal_image.get_rect(center=(level_data["width"] - 200, H - GROUND_H - 45))

            # Загружаем музыку
            if music_on:
                try:
                    pygame.mixer.music.load(level_data["music"])
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Ошибка загрузки музыки: {e}")

            return True
        return False

    def update_scroll(self, player_rect):
        # Простой скроллинг - игрок всегда в центре, фон движется
        target_scroll = player_rect.centerx - W // 2
        if target_scroll < 0:
            target_scroll = 0

        max_scroll = self.levels[self.current_level]["width"] - W

        if 0 < target_scroll < max_scroll:
            target_scroll += 1
        if target_scroll > max_scroll:
            target_scroll = max_scroll

        self.scroll_pos = target_scroll

    def draw(self, screen_0):
        # Отрисовываем видимую часть уровня
        if self.level_surface:
            screen_0.blit(self.level_surface, (0, 0), (self.scroll_pos, 0, W, H))

        # Отрисовываем платформы (с учетом скроллинга)
        if self.current_level in self.levels:
            for platform in self.levels[self.current_level]["platforms"]:
                platform_on_screen = platform.move(-self.scroll_pos, 0)
                pygame.draw.rect(screen_0, (139, 69, 19), platform_on_screen)

        # Отрисовываем портал (с учетом скроллинга)
        if self.portal_rect:
            screen_0.blit(portal_image, (self.portal_rect.x - self.scroll_pos, self.portal_rect.y))

        # Индикатор прогресса
        if self.levels[self.current_level]["width"] > W:
            progress = self.scroll_pos / (self.levels[self.current_level]["width"] - W)
            pygame.draw.rect(screen_0, (255, 255, 255), (50, 35, 200, 10))
            pygame.draw.rect(screen_0, (0, 255, 0), (50, 35, 200 * progress, 10))

    def check_portal_collision(self, player_rect):
        if not self.portal_rect:
            return False

        portal_on_screen = pygame.Rect(
            self.portal_rect.x - self.scroll_pos,
            self.portal_rect.y,
            self.portal_rect.width,
            self.portal_rect.height
        )
        return player_rect.colliderect(portal_on_screen)

    def check_platform_collisions(self, player_0, level_num):
        if self.current_level not in self.levels:
            return

        # Временно сбрасываем статус перед проверкой
        player_0.is_grounded = False  # Исправлено: убрали лишнюю букву

        for platform in self.levels[self.current_level]["platforms"]:
            platform_on_screen = platform.move(-self.scroll_pos, 0)

            # Проверяем, находится ли игрок над платформой по горизонтали
            if (player_0.rect.right > platform_on_screen.left + 20 and
                    player_0.rect.left < platform_on_screen.right - 20):
                # Проверяем коллизию сверху (падение на платформу)
                if (platform_on_screen.top < player_0.rect.bottom <= platform_on_screen.top + 20 and
                        player_0.y_speed >= 0):
                    player_0.rect.bottom = platform_on_screen.top
                    player_0.y_speed = 0
                    player_0.is_grounded = True  # Исправлено: убрали лишнюю букву
                    player_0.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении на платформу
                    break  # Важно: выходим после первой успешной коллизии

        # Если не на платформе, проверяем основную землю
        if not player_0.is_grounded and player_0.rect.bottom >= H - GROUND_H:  # Исправлено: убрали лишнюю букву
            if level_num == 1:
                if not (1505 < level_manager.scroll_pos < 1690):
                    player_0.rect.bottom = H - GROUND_H
                    player_0.y_speed = 0
                    player_0.is_grounded = True  # Исправлено: убрали лишнюю букву
                    player_0.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении на землю
                elif 1505 < level_manager.scroll_pos < 1690 and player_0.rect.bottom > H:
                    player_0.kill(me_image)
                else:
                    player_0.is_grounded = False  # Исправлено: убрали лишнюю букву
            else:
                player_0.rect.bottom = H - GROUND_H
                player_0.y_speed = 0
                player_0.is_grounded = True  # Исправлено: убрали лишнюю букву
                player_0.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении на землю



# Создаем менеджер уровней
level_manager = LevelManager()


# База данных
def init_db():
    conn = sqlite3.connect('Save_files/savegame_2.db')
    cursor = conn.cursor()

    # Таблица для настроек
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            music_on INTEGER,
            sound_on INTEGER,
            player_points INTEGER,
            difficulty_level INTEGER,
            dark_mode INTEGER
        )
    ''')

    # Таблицы для прогресса
    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS game_progress_{difficulty} (
                id INTEGER PRIMARY KEY,
                player_pos INTEGER,
                score INTEGER,
                HP INTEGER,
                shield INTEGER,
                level INTEGER
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS upgrades_{difficulty} (
                id INTEGER PRIMARY KEY,
                player_points INTEGER,
                attack INTEGER,
                HP INTEGER,
                running_unlocked INTEGER,
                double_jump_unlocked INTEGER,
                shield INTEGER
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS levels_{difficulty} (
                id INTEGER PRIMARY KEY,
                level_number INTEGER,
                cleared INTEGER,
                UNIQUE(level_number)
            )
        ''')

        # Инициализация улучшений
        cursor.execute(f'''
            INSERT OR IGNORE INTO upgrades_{difficulty} 
            (id, player_points, attack, HP, running_unlocked, double_jump_unlocked, shield) 
            VALUES (1, 0, 1, 3, 0, 0, 0)
        ''')

        # Инициализация уровней
        for level_num in range(1, 10):
            cursor.execute(f'''
                INSERT OR IGNORE INTO levels_{difficulty} (level_number, cleared) 
                VALUES (?, ?)
            ''', (level_num, 0))

    # Таблица для скинов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY,
            current_skin_index INTEGER
        )
    ''')

    conn.commit()
    return conn


saving = init_db()

# Скины
skins = [
    {
        "name": "Классика",
        "unlocked": True,
        "image": "Sprites and objects/Skins/Me/Me.png",
        "walk_right": [
            "Sprites and objects/Skins/Me/Me-right1.png",
            "Sprites and objects/Skins/Me/Me-right2.png",
            "Sprites and objects/Skins/Me/Me-right3.png",
            "Sprites and objects/Skins/Me/Me-right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Me/Me-left1.png",
            "Sprites and objects/Skins/Me/Me-left2.png",
            "Sprites and objects/Skins/Me/Me-left3.png",
            "Sprites and objects/Skins/Me/Me-left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Me/Me_damaged.png",
        "unlock": " ",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Потерянный",
        "unlocked": True,
        "image": "Sprites and objects/Skins/Lost/Lost_Me.png",
        "walk_right": [
            "Sprites and objects/Skins/Lost/Lost-right1.png",
            "Sprites and objects/Skins/Lost/Lost-right2.png",
            "Sprites and objects/Skins/Lost/Lost-right3.png",
            "Sprites and objects/Skins/Lost/Lost-right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Lost/Lost-left1.png",
            "Sprites and objects/Skins/Lost/Lost-left2.png",
            "Sprites and objects/Skins/Lost/Lost-left3.png",
            "Sprites and objects/Skins/Lost/Lost-left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Lost/Lost_Me-Damaged.png",
        "unlock": " ",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Соник",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Sonic/Sonic.png",
        "walk_right": [
            "Sprites and objects/Skins/Sonic/Sonic-right1.png",
            "Sprites and objects/Skins/Sonic/Sonic-right2.png",
            "Sprites and objects/Skins/Sonic/Sonic-right3.png",
            "Sprites and objects/Skins/Sonic/Sonic-right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Sonic/Sonic-left1.png",
            "Sprites and objects/Skins/Sonic/Sonic-left2.png",
            "Sprites and objects/Skins/Sonic/Sonic-left3.png",
            "Sprites and objects/Skins/Sonic/Sonic-left4.png",
        ],
        "unlock": 'Открой способность "Бег"',
        "damaged": "Sprites and objects/Skins/Sonic/Sonic-damaged.png",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Марио",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Mario/Mario.png",
        "walk_right": [
            "Sprites and objects/Skins/Mario/Mario_right1.png",
            "Sprites and objects/Skins/Mario/Mario_right2.png",
            "Sprites and objects/Skins/Mario/Mario_right3.png",
            "Sprites and objects/Skins/Mario/Mario_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Mario/Mario_left1.png",
            "Sprites and objects/Skins/Mario/Mario_left2.png",
            "Sprites and objects/Skins/Mario/Mario_left3.png",
            "Sprites and objects/Skins/Mario/Mario_left4.png",
        ],
        "unlock": 'Открой способность "Двойной прыжок"',
        "damaged": "Sprites and objects/Skins/Mario/Mario_damaged.png",
        "img": pygame.Surface((40, 50)),
    },
]

# Загрузка изображений скинов
for skin in skins:
    try:
        img = pygame.image.load(skin["image"])
        skin["img"] = pygame.transform.scale(img, (40, 50))
    except:
        pass

# Анимации
running_sprites_right = []
running_sprites_left = []
for i in range(1, 5):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Skins/Me/Me-right{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Skins/Me/Me-left{i}.png")
        running_sprites_right.append(pygame.transform.scale(img_right, (70, 80)))
        running_sprites_left.append(pygame.transform.scale(img_left, (70, 80)))
    except:
        running_sprites_right.append(pygame.Surface((70, 80)))
        running_sprites_left.append(pygame.Surface((70, 80)))

running_sprites_right_boss = []
running_sprites_left_boss = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Common/Goomba_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Common/Goomba_left_{i}.png")
        running_sprites_right_boss.append(pygame.transform.scale(img_right, (140, 140)))
        running_sprites_left_boss.append(pygame.transform.scale(img_left, (140, 140)))
    except:
        running_sprites_right_boss.append(pygame.Surface((140, 140)))
        running_sprites_left_boss.append(pygame.Surface((140, 140)))

running_sprites_enemy_right = []
running_sprites_enemy_left = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Common/Goomba_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Common/Goomba_left_{i}.png")
        running_sprites_enemy_right.append(pygame.transform.scale(img_right, (90, 90)))
        running_sprites_enemy_left.append(pygame.transform.scale(img_left, (90, 90)))
    except:
        running_sprites_enemy_right.append(pygame.Surface((90, 90)))
        running_sprites_enemy_left.append(pygame.Surface((90, 90)))

# Переменные текущего скина
current_skin_index = 0
confirmed_skin_index = current_skin_index


# Класс игрока
# Класс игрока - исправленная версия
class Player:
    def __init__(self):
        self.speed = 5
        self.gravity = 0.4
        self.y_speed = 0
        self.is_grounded = False  # Исправлено: убрали лишнюю букву
        self.run_animation_index = 0
        self.last_update_time = pygame.time.get_ticks()
        self.attack = 1
        self.HP = 3
        self.max_HP = 3
        self.running_unlocked = False
        self.double_jump_unlocked = False
        self.shield = 0
        self.is_dead = False
        self.is_out = False
        self.falling_through = False
        self.can_jump = True
        self.jump_flag = False
        self.running_sprites_right = running_sprites_right
        self.running_sprites_left = running_sprites_left
        self.idle_sprite = me_image
        self.damaged_sprite = me_damaged_image
        self.rect = self.idle_sprite.get_rect()
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.image = self.idle_sprite
        self.death_timer = 0
        self.jump_count = 0  # Счетчик прыжков
        self.max_jumps = 2  # Максимум 2 прыжка

    def handle_input(self):
        if self.is_dead:
            return

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
        if self.is_dead:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_UP]:
                self.handle_jump()

    def handle_jump(self):
        if self.is_dead:
            return

        # Если стоит на земле или платформе - можно прыгать
        if self.is_grounded:
            self.jump()
            self.jump_count = 1
        # Если уже в воздухе и есть двойной прыжок - можно сделать второй прыжок
        elif (self.double_jump_unlocked and
              self.jump_count < self.max_jumps and
              not self.is_grounded):
            self.jump()
            self.jump_count += 1

    def update_animation(self):
        if self.is_dead:
            return

        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
        is_running = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.running_unlocked
        animation_delay = 50 if is_running else 70

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
        self.is_grounded = False  # Сразу сбрасываем grounded после прыжка

    def update(self):
        if self.is_out:
            return

        # Гравитация
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        if self.is_dead:
            self.death_timer += 1

            if not self.falling_through:
                if self.rect.bottom >= H - GROUND_H:
                    self.rect.bottom = H - GROUND_H
                    self.falling_through = True
                    self.y_speed = -12
            else:
                self.y_speed += self.gravity * 0.1
                if self.rect.top > H:
                    self.is_out = True
            return

        # Сбрасываем флаг grounded перед проверкой коллизий
        self.is_grounded = False

        # Проверка коллизий с платформами (выполняется в level_manager.check_platform_collisions)
        # После проверки коллизий, если игрок на земле - сбрасываем счетчик прыжков
        if self.is_grounded:
            self.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении

        # Проверка основной земли
        if self.rect.bottom >= H - GROUND_H:
            if not (1505 < level_manager.scroll_pos < 1690):
                self.rect.bottom = H - GROUND_H
                self.is_grounded = True
                self.jump_count = 0  # Сбрасываем счетчик прыжков
            elif 1505 < level_manager.scroll_pos < 1700 and self.rect.bottom > H:
                self.kill(me_image)
            else:
                self.is_grounded = False

        # Границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > W:
            self.rect.right = W

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def respawn(self):
        self.is_out = False
        self.is_dead = False
        self.falling_through = False
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.y_speed = 0
        self.is_grounded = False
        self.jump_count = 0  # Сбрасываем счетчик прыжков
        self.jump_flag = False
        self.image = self.idle_sprite
        self.run_animation_index = 0
        self.death_timer = 0
        self.HP = self.max_HP

    def damaged(self):
        if self.is_dead:
            return

        self.y_speed = -10
        self.is_grounded = False
        self.image = self.damaged_sprite

    def kill(self, dead_image):
        if self.is_dead:
            return
        self.image = dead_image
        self.is_dead = True
        self.y_speed = -15
        self.falling_through = False
        self.death_timer = 0


# Класс врага
class Monster:
    def __init__(self):
        self.running_sprites_enemy_right = running_sprites_enemy_right
        self.running_sprites_enemy_left = running_sprites_enemy_left
        self.current_frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.frame_delay = 90
        self.image = self.running_sprites_enemy_right[0]
        self.rect = self.image.get_rect()
        self.x_speed = 0
        self.y_speed = 0
        self.speed = 5
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -10
        self.gravity = 0.4
        self.is_grounded = False
        self.damage_given = False
        self.HP = 100
        self.spawn()

    def spawn(self):
        direction = random.randint(0, 1)
        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, H - GROUND_H)
            self.image = self.running_sprites_enemy_left[0]
        else:
            self.x_speed = -self.speed
            self.rect.bottomleft = (W, H - GROUND_H)
            self.image = self.running_sprites_enemy_right[0]

    def kill(self):
        try:
            dead_img = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_dead.png")
            self.image = pygame.transform.scale(dead_img, (90, 28))
        except:
            self.image = pygame.Surface((90, 28))
        self.is_dead = True
        self.x_speed = -self.x_speed
        self.y_speed = self.jump_speed

    def update(self):
        now = pygame.time.get_ticks()

        # Анимация
        if not self.is_dead and now - self.last_frame_update > self.frame_delay:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.running_sprites_enemy_right)
            if self.x_speed > 0:
                self.image = self.running_sprites_enemy_right[self.current_frame_index]
            else:
                self.image = self.running_sprites_enemy_left[self.current_frame_index]
            self.last_frame_update = now

        # Движение
        self.rect.x += self.x_speed
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        if self.is_dead:
            if self.rect.top > H:
                self.is_out = True
        else:
            # Отскок от границ
            if self.rect.left < 0:
                self.rect.left = 0
                self.x_speed = abs(self.x_speed)
            elif self.rect.right > W:
                self.rect.right = W
                self.x_speed = -abs(self.x_speed)

            # Земля
            if self.rect.bottom > H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.is_grounded = True
                self.y_speed = 0
            else:
                self.is_grounded = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Boss:
    def __init__(self):
        self.running_sprites_enemy_right = running_sprites_right_boss
        self.running_sprites_enemy_left = running_sprites_left_boss
        self.current_frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.frame_delay = 90
        self.image = pygame.transform.scale(boss_image, (140, 140))
        self.rect = self.image.get_rect()
        self.x_speed = 0
        self.y_speed = 0
        self.speed = 3
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -10
        self.gravity = 0.4
        self.is_grounded = False
        self.damage_given = False

        # Фазы босса (0-2)
        self.phase = 0
        self.HP = 50
        self.max_HP = 50
        self.phase_changed = False  # Флаг смены фазы

        # Таймеры и задержки
        self.spawn_time = pygame.time.get_ticks()
        self.has_started_moving = False
        self.move_delay = 1500
        self.attack_cooldown = 0
        self.behavior_change_time = pygame.time.get_ticks()
        self.behavior_duration = 2000

        # Текущее поведение
        self.current_behavior = "patrol"
        self.charge_direction = 0
        self.jump_ready = True

        # Границы движения
        self.left_boundary = 50
        self.right_boundary = W - 50

        # Атаки и спецспособности
        self.special_attack_cooldown = 0
        self.projectiles = []

        self.spawn()

    def spawn(self):
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.x_speed = 0
        self.has_started_moving = False
        self.HP = self.max_HP
        self.phase = 0
        self.current_behavior = "patrol"
        self.is_dead = False  # ВАЖНО: сбрасываем статус смерти
        self.is_grounded = True  # ВАЖНО: устанавливаем grounded при спавне

    def update_phase(self):
        # Определяем фазу на основе оставшегося HP
        hp_percent = self.HP / self.max_HP
        old_phase = self.phase

        if hp_percent > 0.66:
            new_phase = 0
        elif hp_percent > 0.33:
            new_phase = 1
        else:
            new_phase = 2

        if new_phase != old_phase:
            self.phase = new_phase
            self.phase_changed = True  # Устанавливаем флаг смены фазы
            self.on_phase_change()

    def on_phase_change(self):
        # Увеличиваем сложность при смене фазы
        if self.phase == 1:
            self.speed = 4
            self.behavior_duration = 1800
        elif self.phase == 2:
            self.speed = 5
            self.behavior_duration = 1500

    def choose_behavior(self):
        if self.phase == 0:
            # Фаза 1: базовые поведения
            behaviors = ["patrol", "patrol", "jump", "charge"]
        elif self.phase == 1:
            # Фаза 2: более агрессивная
            behaviors = ["patrol", "charge", "charge", "jump", "special"]
        else:
            # Фаза 3: самая агрессивная - ИСПРАВЛЕНО: убрали лишние patrol
            behaviors = ["charge", "jump", "special", "charge", "jump"]

        self.current_behavior = random.choice(behaviors)
        self.behavior_change_time = pygame.time.get_ticks()

        # Настройка поведения
        if self.current_behavior == "patrol":
            # Случайное направление патрулирования
            self.x_speed = random.choice([-1, 1]) * self.speed
        elif self.current_behavior == "charge":
            # Направление в сторону игрока
            player_center_x = player.rect.centerx
            self.charge_direction = 1 if player_center_x > self.rect.centerx else -1
            self.x_speed = self.charge_direction * self.speed * 2
        elif self.current_behavior == "jump" and self.is_grounded:
            self.y_speed = self.jump_speed * (0.8 + 0.2 * self.phase)
        elif self.current_behavior == "special":
            self.prepare_special_attack()

    def prepare_special_attack(self):
        # Останавливаемся для спецатаки
        self.x_speed = 0
        # Здесь можно добавить анимацию подготовки

    def execute_special_attack(self):
        # Различные спецатаки в зависимости от фазы
        if self.phase >= 1 and self.is_grounded:
            # Мощный прыжок в фазе 2 и 3
            self.y_speed = self.jump_speed * (1.2 + 0.3 * self.phase)

    def check_boundaries(self):
        """Проверка и коррекция границ движения"""
        boundary_hit = False

        # Левая граница
        if self.rect.left <= self.left_boundary:
            self.rect.left = self.left_boundary
            boundary_hit = True
            # Разворачиваем вправо
            self.x_speed = abs(self.speed)

        # Правая граница
        elif self.rect.right >= self.right_boundary:
            self.rect.right = self.right_boundary
            boundary_hit = True
            # Разворачиваем влево
            self.x_speed = -abs(self.speed)

        return boundary_hit

    def handle_boundary_collision(self):
        """Обработка столкновения с границами"""
        if self.check_boundaries():
            # Если это была атака charge, отменяем ее
            if self.current_behavior == "charge":
                self.current_behavior = "patrol"
                self.choose_behavior()

    def take_damage(self, damage):
        self.HP -= damage
        if self.HP <= 0:
            self.kill()
        else:
            print(f"Босс получил урон! Осталось HP: {self.HP}")

    def kill(self):
        try:
            dead_img = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_dead.png")
            self.image = pygame.transform.scale(dead_img, (140, 38))
        except:
            self.image = pygame.Surface((140, 38))

        # СОХРАНЯЕМ текущую позицию низа спрайта перед изменением rect
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        # ОБНОВЛЯЕМ rect чтобы соответствовать новому изображению
        self.rect = self.image.get_rect()

        # ВОССТАНАВЛИВАЕМ позицию так, чтобы босс стоял на земле
        self.rect.centerx = old_centerx
        self.rect.bottom = old_bottom  # Нижняя граница остается на том же уровне

        self.is_dead = True
        self.x_speed = 0
        self.y_speed = self.jump_speed * 0.5
        self.is_grounded = False

    def update(self):
        now = pygame.time.get_ticks()

        # Если босс мертв - применяем только физику падения
        if self.is_dead:
            # Гравитация для мертвого босса
            self.y_speed += self.gravity
            self.rect.y += self.y_speed

            # Проверяем землю для мертвого босса
            if self.rect.bottom >= H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_grounded = True
            else:
                self.is_grounded = False

            # Если босс ушел за нижнюю границу экрана
            if self.rect.top > H:
                self.is_out = True
            return

        # ОБНОВЛЕНИЕ ДЛЯ ЖИВОГО БОССА:

        # Обновляем фазу
        self.update_phase()

        # Запуск движения после задержки
        if not self.has_started_moving and now - self.spawn_time >= self.move_delay:
            self.x_speed = -self.speed
            self.has_started_moving = True
            self.choose_behavior()

        # Смена поведения по таймеру
        if self.has_started_moving and now - self.behavior_change_time > self.behavior_duration:
            self.choose_behavior()

        # Выполнение спецатаки
        if self.current_behavior == "special" and now - self.behavior_change_time > 500:
            self.execute_special_attack()
            self.current_behavior = "patrol"  # Возвращаемся к патрулированию

        # Анимация
        if now - self.last_frame_update > self.frame_delay:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.running_sprites_enemy_right)
            if self.x_speed > 0:
                self.image = self.running_sprites_enemy_right[self.current_frame_index]
            else:
                self.image = self.running_sprites_enemy_left[self.current_frame_index]
            self.last_frame_update = now

        # Движение и границы
        self.rect.x += self.x_speed
        self.handle_boundary_collision()

        # Гравитация
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        # Проверка земли
        if self.rect.bottom >= H - GROUND_H:
            self.rect.bottom = H - GROUND_H
            self.y_speed = 0
            self.is_grounded = True
            self.jump_ready = True
        else:
            self.is_grounded = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        if self.is_dead:  # Не показываем HP бар для мертвого босса
            return

        bar_width = 200
        bar_height = 20
        bar_x = W // 2 - bar_width // 2
        bar_y = 20

        # Фон бара
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Текущее HP
        hp_width = int((self.HP / self.max_HP) * bar_width)

        # Цвет в зависимости от фазы
        if self.phase == 0:
            color = (0, 255, 0)  # Зеленый
        elif self.phase == 1:
            color = (255, 165, 0)  # Оранжевый
        else:
            color = (255, 0, 0)  # Красный

        pygame.draw.rect(surface, color, (bar_x, bar_y, hp_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)


# Создаем игрока
player = Player()


# Функции для работы с базой данных
def save_settings_sql():
    global music_on, sound_on, player_points_easy, player_points_medium, player_points_hard, current_difficulty, pending_mode
    cursor = saving.cursor()
    cursor.execute('DELETE FROM settings')
    points = player_points_easy if current_difficulty == 0 else (
        player_points_medium if current_difficulty == 1 else player_points_hard)
    cursor.execute(
        'INSERT INTO settings (music_on, sound_on, player_points, difficulty_level, dark_mode) VALUES (?, ?, ?, ?, ?)',
        (int(music_on), int(sound_on), int(points), current_difficulty, int(pending_mode)))
    saving.commit()


def load_settings_sql():
    global current_difficulty, difficulty_level, dark_mode, background_image, pending_mode, music_on, sound_on
    cursor = saving.cursor()
    cursor.execute('SELECT music_on, sound_on, player_points, difficulty_level, dark_mode FROM settings LIMIT 1')
    row = cursor.fetchone()
    if row:
        music_on = bool(row[0])
        sound_on = bool(row[1])
        current_difficulty = row[3] if row[3] is not None else 0
        difficulty_level = current_difficulty
        dark_mode = bool(row[4])
        pending_mode = dark_mode
        background_image = (42, 98, 202) if dark_mode else (92, 148, 252)


def save_game_sql(level_number):
    cursor = saving.cursor()
    table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][current_difficulty]
    cursor.execute(f'DELETE FROM {table_name}')
    cursor.execute(f'INSERT INTO {table_name} (player_pos, score, HP, shield, level) VALUES (?, ?, ?, ?, ?)',
                   (level_manager.scroll_pos, score, player.HP, player.shield, level_number))
    saving.commit()


def load_game_sql():
    global score
    cursor = saving.cursor()
    table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][current_difficulty]
    cursor.execute(f'SELECT player_pos, score, HP, shield, level FROM {table_name} LIMIT 1')
    row = cursor.fetchone()
    if row:
        level_manager.scroll_pos = row[0] if row[0] is not None else 0
        score = row[1] if row[1] is not None else 0
        player.HP = row[2] if row[2] is not None else player.HP
        player.shield = row[3] if row[3] is not None else player.shield
        return row[4] if row[4] else 1
    return 1


def save_skin():
    cursor = saving.cursor()
    cursor.execute('DELETE FROM skins')
    cursor.execute('INSERT INTO skins (current_skin_index) VALUES (?)', (current_skin_index,))
    saving.commit()


def load_skin():
    global current_skin_index
    cursor = saving.cursor()
    cursor.execute('SELECT current_skin_index FROM skins LIMIT 1')
    row = cursor.fetchone()
    if row:
        current_skin_index = row[0]


def save_upgrades():
    global player_points_easy, player_points_medium, player_points_hard, player
    cursor = saving.cursor()
    table_name = ['upgrades_easy', 'upgrades_medium', 'upgrades_hard'][current_difficulty]
    cursor.execute(
        f'UPDATE {table_name} SET player_points = ?, attack = ?, HP = ?, running_unlocked = ?, double_jump_unlocked = ?, shield = ? WHERE id=1',
        (
        player_points_easy if current_difficulty == 0 else player_points_medium if current_difficulty == 1 else player_points_hard,
        player.attack, player.HP, int(player.running_unlocked), int(player.double_jump_unlocked), player.shield))
    saving.commit()


def load_upgrades():
    global player_points_easy, player_points_medium, player_points_hard, player
    cursor = saving.cursor()
    table_name = ['upgrades_easy', 'upgrades_medium', 'upgrades_hard'][current_difficulty]
    cursor.execute(
        f'SELECT player_points, attack, HP, running_unlocked, double_jump_unlocked, shield FROM {table_name} LIMIT 1')
    row = cursor.fetchone()
    if row:
        if current_difficulty == 0:
            player_points_easy = row[0]
        elif current_difficulty == 1:
            player_points_medium = row[0]
        elif current_difficulty == 2:
            player_points_hard = row[0]

        player.attack = row[1]
        player.HP = row[2]
        player.running_unlocked = bool(row[3])
        player.double_jump_unlocked = bool(row[4])
        player.shield = row[5]
    return player.HP


def apply_skin(skin_index):
    global me_image, running_sprites_right, running_sprites_left, me_damaged_image
    if skin_index < 0 or skin_index >= len(skins):
        skin_index = 0

    skin = skins[skin_index]
    try:
        me_image = pygame.transform.scale(pygame.image.load(skin["image"]), (70, 80))

        if skin.get("walk_right"):
            running_sprites_right = [pygame.transform.scale(pygame.image.load(fname), (70, 80)) for fname in
                                     skin["walk_right"]]
        else:
            running_sprites_right = [me_image] * 4

        if skin.get("walk_left"):
            running_sprites_left = [pygame.transform.scale(pygame.image.load(fname), (70, 80)) for fname in
                                    skin["walk_left"]]
        else:
            running_sprites_left = [me_image] * 4

        if skin.get("damaged"):
            me_damaged_image = pygame.transform.scale(pygame.image.load(skin["damaged"]), (70, 80))
        else:
            me_damaged_image = me_image

        player.running_sprites_right = running_sprites_right
        player.running_sprites_left = running_sprites_left
        player.idle_sprite = me_image
        player.damaged_sprite = me_damaged_image
        player.image = player.idle_sprite

    except Exception as e:
        print(f"Ошибка загрузки скина: {e}")
        if skin_index != 0:
            apply_skin(0)


# Вспомогательные функции
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, rect)


def play_menu_music():
    global music_playing
    if not music_playing and music_on:
        try:
            pygame.mixer.music.load(menu_music)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            music_playing = True
        except Exception as e:
            print(f"Ошибка воспроизведения меню: {e}")


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
    save_settings_sql()


def toggle_sound():
    global sound_on
    sound_on = not sound_on
    save_settings_sql()


def show_message(text, duration=2000):
    global message, message_time, MESSAGE_DURATION
    message = text
    message_time = pygame.time.get_ticks()
    MESSAGE_DURATION = duration


def change_difficulty(new_difficulty):
    global current_difficulty, difficulty_level
    current_difficulty = new_difficulty
    difficulty_level = new_difficulty
    save_settings_sql()
    load_upgrades()
    load_skin()
    apply_skin(current_skin_index)


# Игровые меню и экраны
def pause():
    global playing_menu, from_level, from_menu
    load_settings_sql()
    paused = True
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((92, 148, 100, 20))
    selected_idx = 0
    menu_items = ["Музыка", "Звук", "Управление", "Назад"]

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    if music_on:
                        pygame.mixer.music.unpause()
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % len(menu_items)
                elif event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        toggle_music()
                    elif selected_idx == 1:
                        toggle_sound()
                    elif selected_idx == 2:
                        management_menu()
                    elif selected_idx == 3:
                        playing_menu = True
                        from_level = True
                        from_menu = False
                        level_menu()

        screen.blit(overlay, (0, 0))
        draw_text("ПАУЗА", font_large, (255, 255, 255), screen, W // 2, H // 4)

        for j, opt in enumerate(menu_items):
            color = (255, 255, 255) if j == selected_idx else (0, 0, 0)
            if j == 0:
                status = "Вкл" if music_on else "Выкл"
                text = f"{opt}: {status}"
            elif j == 1:
                status2 = "Вкл" if sound_on else "Выкл"
                text = f"{opt}: {status2}"
            else:
                text = opt
            draw_text(text, font_small, color, screen, W // 2, H // 2 + j * 50)

        pygame.display.flip()
        clock.tick(FPS)


def management_menu():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        screen.fill(background_image)
        draw_text("Управление", font_large, (255, 255, 255), screen, W // 2, H // 4 - 80)
        controls = [
            "Передвижение: A / ←, D / →",
            "Прыжок: W / ↑",
            "Бег: (A / ←) / (D / →) + Shift",
            "Пауза / выход из меню: ESC",
            "Сохранение: S",
            "Выбор опции: W / ↑, S / ↓",
            "Подтверждение: Enter",
            "Увеличение / уменьшение характеристик: A / ←, D / →"
        ]
        for j, control in enumerate(controls):
            draw_text(control, font_small, (0, 0, 0), screen, W // 2, H // 4 + j * 40)

        pygame.display.flip()
        clock.tick(60)


def main_menu():
    global menu, from_menu, from_level
    load_settings_sql()
    menu = True

    options = [
        "Начать игру",
        "Скины",
        "Улучшение",
        "Настройки",
        "Секреты",
        "Выход из игры",
    ]

    load_game_sql()
    load_skin()
    apply_skin(current_skin_index)
    player.respawn()
    from_level = False

    selected_option = 0
    last_move_time_up = 0
    last_move_time_down = 0
    MOVE_DELAY = 200

    while menu:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings_sql()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        menu = False
                        from_menu = True
                        level_menu()
                    elif selected_option == 1:
                        skin_menu()
                    elif selected_option == 2:
                        upgrade()
                    elif selected_option == 3:
                        settings()
                    elif selected_option == 4:
                        secrets()
                    elif selected_option == 5:
                        pygame.quit()
                        sys.exit()

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_down > MOVE_DELAY:
                selected_option = (selected_option + 1) % len(options)
                last_move_time_down = now
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_up > MOVE_DELAY:
                selected_option = (selected_option - 1) % len(options)
                last_move_time_up = now

        screen.fill(background_image)
        draw_text("Главное меню", font_large, (255, 255, 255), screen, W // 2, H // 4)

        for j, opt in enumerate(options):
            color = (255, 255, 255) if j == selected_option else (0, 0, 0)
            draw_text(opt, font_small, color, screen, W // 2, H // 2 - 90 + j * 50)

        pygame.display.flip()
        clock.tick(60)


def skin_menu():
    global current_skin_index, confirmed_skin_index, message, message_time
    load_upgrades()
    load_skin()
    in_skin_menu = True

    selected_skin_index = confirmed_skin_index
    last_move_time_up_skins = 0
    last_move_time_down_skins = 0
    MOVE_DELAY = 200

    while in_skin_menu:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings_sql()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                if event.key == pygame.K_RETURN:
                    if selected_skin_index < len(skins):
                        skin = skins[selected_skin_index]
                        if skin["unlocked"]:
                            current_skin_index = selected_skin_index
                            apply_skin(current_skin_index)
                            save_game_sql(level_manager.current_level)
                            save_upgrades()
                            save_skin()
                            confirmed_skin_index = selected_skin_index
                        else:
                            show_message(skin["unlock"])

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_down_skins > MOVE_DELAY:
                selected_skin_index = (selected_skin_index + 1) % len(skins)
                last_move_time_down_skins = now
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_up_skins > MOVE_DELAY:
                selected_skin_index = (selected_skin_index - 1) % len(skins)
                last_move_time_up_skins = now

        screen.fill(background_image)
        draw_text("Выбор скина", font_large, (255, 255, 255), screen, W // 2, H // 6 - 40)
        load_upgrades()

        # Обновляем статус разблокировки скинов
        for skin_selected in skins:
            if skin_selected["name"] == "Соник":
                skin_selected["unlocked"] = player.running_unlocked
            if skin_selected["name"] == "Марио":
                skin_selected["unlocked"] = player.double_jump_unlocked

        for idx, skin_0 in enumerate(skins):
            y_pos = H // 4 + (idx % 4) * 60
            x_pos = W // 2 - 250 if idx < 4 else W // 2 + 200
            is_selected = idx == selected_skin_index
            color = (255, 255, 255) if is_selected else (
                (255, 255, 0) if confirmed_skin_index is not None and idx == confirmed_skin_index else (0, 0, 0))

            draw_text(skin_0["name"], font_small, color, screen, x_pos, y_pos)

            if "img" in skin_0:
                img_surface = skin_0["img"]
                if isinstance(img_surface, pygame.Surface):
                    img_rect = img_surface.get_rect(center=(x_pos - 120, y_pos))
                    screen.blit(img_surface, img_rect)

            status = "Открыт" if skin_0["unlocked"] else "Закрыт"
            draw_text(status, font_small, color, screen, x_pos + 150, y_pos)

        if message:
            if now - message_time < 2000:
                message_surface = pygame.Surface((530, 50))
                message_surface.fill((255, 255, 255))
                pygame.draw.rect(message_surface, (0, 0, 0), message_surface.get_rect(), 2)
                draw_text(message, font_small, (0, 0, 0), message_surface, 250, 25)
                screen.blit(message_surface, (W // 2 - 250, H // 2 - 25))
            else:
                message = None

        pygame.display.flip()
        clock.tick(60)


def settings():
    global music_on, sound_on, current_difficulty, dark_mode, background_image, pending_mode, player_points_easy, player_points_medium, player_points_hard, current_skin_index

    load_upgrades()
    last_move_time_settings_up = 0
    last_move_time_settings_down = 0
    MOVE_DELAY = 200
    options_settings = [
        "Уровень сложности",
        "Музыка",
        "Звук",
        "Фон",
        "Сброс прогресса",
        "Сохранить настройки",
        "Отменить",
        "Управление"
    ]
    temp_difficulty = current_difficulty
    selected_idx = 0

    while True:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings_sql()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                if event.key == pygame.K_RETURN:
                    if selected_idx == 0:
                        temp_difficulty = (temp_difficulty + 1) % 3
                    elif selected_idx == 1:
                        toggle_music()
                        if music_on:
                            play_menu_music()
                    elif selected_idx == 2:
                        toggle_sound()
                    elif selected_idx == 3:
                        pending_mode = not pending_mode
                        background_image = (42, 98, 202) if pending_mode else (92, 148, 252)
                    elif selected_idx == 4:
                        cursor = saving.cursor()
                        table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][
                            current_difficulty]
                        upgrades_table = ['upgrades_easy', 'upgrades_medium', 'upgrades_hard'][current_difficulty]
                        levels_table = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]

                        cursor.execute(f'DELETE FROM {table_name}')
                        cursor.execute(f'DELETE FROM {upgrades_table}')
                        cursor.execute(f'DELETE FROM {levels_table}')

                        if current_difficulty == 0:
                            player_points_easy = 0
                        elif current_difficulty == 1:
                            player_points_medium = 0
                        elif current_difficulty == 2:
                            player_points_hard = 0

                        saving.commit()
                    elif selected_idx == 5:
                        current_difficulty = temp_difficulty
                        current_skin_index = 0
                        apply_skin(current_skin_index)
                        save_settings_sql()
                        save_skin()
                        load_upgrades()
                        if dark_mode != pending_mode:
                            dark_mode = pending_mode
                        background_image = (42, 98, 202) if dark_mode else (92, 148, 252)
                    elif selected_idx == 6:
                        temp_difficulty = 0
                        save_settings_sql()
                        save_game_sql(level_manager.current_level)
                        dark_mode = False
                        pending_mode = dark_mode
                        background_image = (42, 98, 202) if dark_mode else (92, 148, 252)
                        if not music_on:
                            toggle_music()
                            if music_on:
                                play_menu_music()
                        if not sound_on:
                            toggle_sound()
                        save_skin()
                    elif selected_idx == 7:
                        management_menu()

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_settings_down > MOVE_DELAY:
                selected_idx = (selected_idx + 1) % len(options_settings)
                last_move_time_settings_down = now
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_settings_up > MOVE_DELAY:
                selected_idx = (selected_idx - 1) % len(options_settings)
                last_move_time_settings_up = now

        screen.fill(background_image)
        draw_text("Настройки", font_large, (255, 255, 255), screen, W // 2, H // 6)

        for idx, opt in enumerate(options_settings):
            color = (255, 255, 255) if idx == selected_idx else (0, 0, 0)

            if opt == "Музыка":
                status = "Вкл" if music_on else "Выкл"
                draw_text(f"Музыка: {status}", font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)
            elif opt == "Звук":
                status2 = "Вкл" if sound_on else "Выкл"
                draw_text(f"Звук: {status2}", font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)
            elif opt == "Фон":
                status3 = "Тёмный" if pending_mode else "Светлый"
                draw_text(f"Фон: {status3}", font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)
            elif opt == "Уровень сложности":
                levels = ["Легко", "Средне", "Сложно"]
                level_text = f"Уровень сложности: {levels[temp_difficulty]}"
                draw_text(level_text, font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)
            else:
                draw_text(opt, font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)

        if current_difficulty == 0:
            draw_text(f"Очки: {player_points_easy}", font_small, (255, 255, 255), screen, W - 100, 50)
        elif current_difficulty == 1:
            draw_text(f"Очки: {player_points_medium}", font_small, (255, 255, 255), screen, W - 100, 50)
        elif current_difficulty == 2:
            draw_text(f"Очки: {player_points_hard}", font_small, (255, 255, 255), screen, W - 100, 50)

        pygame.display.flip()
        clock.tick(60)


def upgrade():
    global current_player_points, player_points_easy, player_points_medium, player_points_hard, \
        current_difficulty, unlock_message, unlock_message_time

    load_upgrades()

    if current_difficulty == 0:
        current_player_points = player_points_easy
    elif current_difficulty == 1:
        current_player_points = player_points_medium
    elif current_difficulty == 2:
        current_player_points = player_points_hard

    selected_idx = 0
    last_move_time_up = 0
    last_move_time_down = 0
    MOVE_DELAY = 300

    options = ["Атака", "HP", "Бег", "Двойной прыжок", "Щит"]
    upgrade_chars = [
        player.attack,
        player.HP,
        player.running_unlocked,
        player.double_jump_unlocked,
        player.shield,
    ]

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_difficulty == 0:
                        player_points_easy = current_player_points
                    elif current_difficulty == 1:
                        player_points_medium = current_player_points
                    elif current_difficulty == 2:
                        player_points_hard = current_player_points
                    save_upgrades()
                    load_upgrades()
                    main_menu()
                    return
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    j = selected_idx
                    if j == 4:
                        if current_player_points >= 3:
                            if sound_on:
                                Unlock_skin_sound.play()
                            upgrade_chars[j] += 1
                            player.shield += 1
                            current_player_points -= 3
                            save_upgrades()
                        elif current_player_points < 3:
                            unlock_message = "Нужно минимум 3 очка"
                            unlock_message_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            if now - last_move_time_down > MOVE_DELAY:
                selected_idx = (selected_idx + 1) % len(options)
                last_move_time_down = now
        elif keys[pygame.K_UP]:
            if now - last_move_time_up > MOVE_DELAY:
                selected_idx = (selected_idx - 1) % len(options)
                last_move_time_up = now

        screen.fill(background_image)
        draw_text("Улучшение", font_large, (255, 255, 255), screen, W // 2, H // 6)
        draw_text(f"Очки: {current_player_points}", font_small, (255, 255, 255), screen, W - 100, 50)

        for j, opt in enumerate(options):
            text_color = (255, 255, 255) if j == selected_idx else (0, 0, 0)
            y_pos = H // 3 + 20 + j * 70
            x_pos = W // 3 - 100
            draw_text(opt, font_small, text_color, screen, x_pos, y_pos)

            if opt == "Бег" or opt == "Двойной прыжок":
                if upgrade_chars[j]:
                    draw_text("Открыт", font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)
                else:
                    draw_text("Закрыт", font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)
            else:
                draw_text(str(upgrade_chars[j]), font_medium, (0, 0, 0), screen, W // 3 + 250, H // 3 + 20 + j * 70)

        if unlock_message:
            current_time = pygame.time.get_ticks()
            if current_time - unlock_message_time < UNLOCK_MESSAGE_DURATION:
                message_surface = pygame.Surface((400, 50))
                message_surface.fill((255, 255, 255))
                pygame.draw.rect(message_surface, (0, 0, 0), message_surface.get_rect(), 2)
                draw_text(unlock_message, font_small, (0, 0, 0), message_surface, 200, 25)
                screen.blit(message_surface, (W // 2 - 200, H // 2 - 25))
            else:
                unlock_message = None

        pygame.display.flip()
        clock.tick(60)


def secrets():
    # Заглушка для секретов
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        screen.fill(background_image)
        draw_text("Секреты", font_large, (255, 255, 255), screen, W // 2, H // 4)
        draw_text("Здесь будут секреты и достижения", font_medium, (255, 255, 255), screen, W // 2, H // 2)
        draw_text("Нажмите ESC для возврата", font_small, (255, 255, 255), screen, W // 2, H // 2 + 50)

        pygame.display.flip()
        clock.tick(60)


def level_menu():
    global level1_cleared, level2_cleared, level3_cleared, level4_cleared, level5_cleared, level6_cleared,\
        from_menu, from_level, message, playing_menu
    if from_level and not from_menu:
        stop_music()
        play_menu_music()
    cursor = saving.cursor()
    table_name = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]

    # Получаем статус уровней
    for level_num in range(1, 7):
        cursor.execute(f'SELECT cleared FROM {table_name} WHERE level_number = ?', (level_num,))
        row = cursor.fetchone()
        if row:
            if level_num == 1:
                level1_cleared = bool(row[0])
            elif level_num == 2:
                level2_cleared = bool(row[0])
            elif level_num == 3:
                level3_cleared = bool(row[0])
            elif level_num == 4:
                level4_cleared = bool(row[0])
            elif level_num == 5:
                level5_cleared = bool(row[0])
            elif level_num == 6:
                level6_cleared = bool(row[0])

    load_skin()
    options = ["Уровень 1", "Уровень 2", "Уровень 3", "Уровень 4", "Уровень 5", "Уровень 6"]
    selected_idx = 0

    last_move_time_up = 0
    last_move_time_down = 0
    MOVE_DELAY = 200
    x_pos = None
    y_pos = None

    while True:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
                    return
                if event.key == pygame.K_RETURN:
                    level_num = selected_idx + 1
                    if level_num == 1 or (level_num == 2 and level1_cleared) or (level_num == 3 and level2_cleared) or (
                            level_num == 4 and level3_cleared) or (
                            level_num == 5 and level4_cleared) or (
                            level_num == 6 and level5_cleared):
                        run_level(level_num)
                    else:
                        show_message("Сначала пройдите предыдущий уровень!")

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_down > MOVE_DELAY:
                selected_idx = (selected_idx + 1) % len(options)
                last_move_time_down = now
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_up > MOVE_DELAY:
                selected_idx = (selected_idx - 1) % len(options)
                last_move_time_up = now

        screen.fill(background_image)
        draw_text("Выбор уровня", font_large, (255, 255, 255), screen, W // 2, H // 6)

        for j, opt in enumerate(options):
            is_selected = (j == selected_idx)
            color = (255, 255, 255) if is_selected else (0, 0, 0)

            # Проверяем доступность уровня
            if j == 0:
                available = True
                status_color = (0, 255, 0) if level1_cleared and not is_selected else color
            elif j == 1:
                available = level1_cleared
                status_color = (0, 255, 0) if level2_cleared and not is_selected else color
            elif j == 2:
                available = level2_cleared
                status_color = (0, 255, 0) if level3_cleared and not is_selected else color
            elif j == 3:
                available = level3_cleared
                status_color = (0, 255, 0) if level4_cleared and not is_selected else color
            elif j == 4:
                available = level4_cleared
                status_color = (0, 255, 0) if level5_cleared and not is_selected else color
            elif j == 5:
                available = level5_cleared
                status_color = (0, 255, 0) if level6_cleared and not is_selected else color
            else:
                available = False
                status_color = (255, 0, 0) if not is_selected else color# Красный для недоступных

            if 0 <= j < 3:
                x_pos = W // 3 - 100
                y_pos = H // 3 + j * 70
            elif 3 <= j < 6:
                x_pos = W // 2
                y_pos = H // 3 + (j - 3) * 70
            elif 6 <= j <= 9:
                x_pos = W // 3 * 2 + 100
                y_pos = H // 3 + (j - 6) * 70

            if available:
                draw_text(opt, font_small, status_color, screen, x_pos, y_pos)
            else:
                draw_text(f"{opt}", font_small, (255, 0, 0) if not is_selected else color, screen, x_pos, y_pos)
        if message:
            current_time = pygame.time.get_ticks()
            if current_time - message_time < MESSAGE_DURATION:
                # Нарисовать прямоугольник с текстом
                message_surface = pygame.Surface((500, 50))
                message_surface.fill((255, 255, 255))
                pygame.draw.rect(message_surface, (0, 0, 0), message_surface.get_rect(), 2)
                # Отрисовка текста
                draw_text(message, font_small, (0, 0, 0), message_surface, 250, 25)
                # Разместить поверх экрана по центру
                screen.blit(
                    message_surface,
                    (W // 2 - 250, H // 2 - 25)
                )
            else:
                message = None
        pygame.display.flip()
        clock.tick(60)


# Основные игровые функции
def run_level(level_num):
    global monsters, boss, score, player, save_message_displayed, save_message_timer, Level

    if not level_manager.load_level(level_num):
        show_message(f"Ошибка загрузки уровня {level_num}")
        return
    level_data = level_manager.levels[level_num]
    load_upgrades()
    HP = player.HP
    if level_num == Level:
        load_game_sql()
    player.respawn()
    player.rect.midbottom = (W // 2, H - GROUND_H)

    monsters = []
    boss = []
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause()
                elif event.key == pygame.K_s:
                    save_game_sql(level_num)
                    Level = level_num
                    save_message_displayed = True
                    save_message_timer = pygame.time.get_ticks()
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    player.handle_jump()  # Обрабатываем прыжок при нажатии
                elif player.is_out:
                    load_game_sql()
                    if 1505 < level_manager.scroll_pos < 1690 and level_num == 1:
                        level_manager.scroll_pos = 1300
                    load_upgrades()
                    player.respawn()
                    player.rect.midbottom = (W // 2, H - GROUND_H)
                    monsters.clear()
                    boss.clear()

        # Обновление игрока
        player.handle_input()
        player.update()

        # ИСПРАВЛЕННЫЙ СКРОЛЛИНГ (рабочая версия из вашего кода)
        keys = pygame.key.get_pressed()

        # Движение вправо
        if (player.rect.centerx > W // 2 and
                level_manager.scroll_pos < level_data["width"] - W):

            scroll_amount = player.rect.centerx - W // 2
            scroll_speed = 5  # Скорость скролла
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                scroll_speed *= 2

            # Фиксируем игрока в центре и двигаем фон
            player.rect.centerx = W // 2
            new_scroll_pos = level_manager.scroll_pos + min(scroll_amount, scroll_speed)
            if new_scroll_pos > level_data["width"] - W:
                new_scroll_pos = level_data["width"] - W
            level_manager.scroll_pos = new_scroll_pos

        # Движение влево
        elif (player.rect.centerx < W // 2 and
              level_manager.scroll_pos > 0):

            scroll_amount = W // 2 - player.rect.centerx
            scroll_speed = 5  # Скорость скролла
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                scroll_speed *= 2

            # Фиксируем игрока в центре и двигаем фон
            player.rect.centerx = W // 2
            new_scroll_pos = level_manager.scroll_pos - min(scroll_amount, scroll_speed)
            if new_scroll_pos < 0:
                new_scroll_pos = 0
            level_manager.scroll_pos = new_scroll_pos

        # Проверка коллизий с платформами
        level_manager.check_platform_collisions(player, level_num)

        # Проверка достижения портала
        if level_manager.check_portal_collision(player.rect):
            save_game_sql(level_num)
            if level_data["has_boss"]:
                run_boss_fight(level_num)
            else:
                run_enemy_wave(level_num, level_data["enemy_count"])
            running = False

        # Отрисовка
        screen.fill((0, 0, 0))
        level_manager.draw(screen)
        player.draw(screen)

        # UI
        draw_text(f"Уровень: {level_num}", font_small, (255, 255, 255), screen, 100, 20)
        draw_text(f"HP: {HP}", font_small, (255, 255, 255), screen, W // 3, 20)
        draw_text(f"Щиты: {player.shield}", font_small, (255, 255, 255), screen, W // 3 * 2, 20)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        if player.is_out:
            draw_text("Нажмите любую клавишу для возрождения", font_small, (255, 255, 255), screen, W // 2, H // 2)

        pygame.display.flip()
        clock.tick(FPS)


def run_enemy_wave(level_num, enemy_count):
    global monsters, score, player, save_message_displayed, save_message_timer
    load_game_sql()
    player.HP = load_upgrades()
    HP = player.HP
    Start_HP = HP
    player.respawn()
    monsters = []
    last_spawn_time = pygame.time.get_ticks()
    spawn_delay = 2000
    Shield = player.shield
    invincible = False
    invincible_end_time = 0
    level_manager.scroll_pos = 0

    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game_sql(level_num)
                    save_message_displayed = True
                    save_message_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    player.handle_jump()
                elif player.is_out:
                    # Полное восстановление при возрождении
                    load_game_sql()
                    load_upgrades()
                    player.respawn()  # Используем respawn
                    HP = Start_HP
                    Shield = player.shield
                    monsters.clear()
                    score = 0  # Сбрасываем счет при смерти

        # Обновление игрока (только если не мертв)
        if not player.is_dead:
            player.handle_input()
        player.update()

        # Если игрок мертв и вылетел, ждем возрождения
        if player.is_out:
            continue

        # Спавн врагов (только если игрок жив)
        if len(monsters) < 5 and now - last_spawn_time > spawn_delay and score < enemy_count and not player.is_dead:
            monsters.append(Monster())
            last_spawn_time = now

        # Обновление врагов
        for monster in list(monsters):
            monster.update()

            # Проверка коллизий (только если игрок жив)
            if not player.is_dead and player.rect.colliderect(monster.rect) and not monster.is_dead:
                if (player.rect.bottom < monster.rect.centery and
                        player.y_speed > 0 and
                        abs(player.rect.centerx - monster.rect.centerx) < monster.rect.width / 2):
                    # Игрок прыгает на врага
                    monster.kill()
                    player.y_speed = -10
                    player.is_grounded = False
                    score += 1
                elif not monster.damage_given and not invincible:
                    # Игрок получает урон
                    if Shield >= 1:
                        Shield -= 1
                        player.shield -= 1
                        save_upgrades()
                        invincible = True
                        invincible_end_time = now + 1000
                    else:
                        HP -= 1
                        player.damaged()
                        monster.damage_given = True
                        invincible = True
                        invincible_end_time = now + 1000
                    if HP <= 0:
                        player.kill(player.damaged_sprite)
                        show_message("Вы погибли!")
            else:
                monster.damage_given = False

            if monster.is_out:
                monsters.remove(monster)

        # Снятие неуязвимости
        if invincible and now >= invincible_end_time:
            invincible = False
            if not player.is_dead:
                player.image = player.idle_sprite
                player.speed = 5

        # Отрисовка
        screen.fill(level_manager.levels[level_num]["bg_color"])
        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(ground_image, (500, H - GROUND_H))

        for monster in monsters:
            monster.draw(screen)

        player.draw(screen)

        # UI
        draw_text(f"Счет: {score}/{enemy_count}", font_large, (255, 255, 255), screen, W // 2, 30)
        draw_text(f"HP: {HP}", font_medium, (255, 255, 255), screen, 100, 30)
        draw_text(f"Щиты: {Shield}", font_medium, (255, 255, 255), screen, W - 100, 30)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        # Сообщения о состоянии игрока
        if player.is_out:
            draw_text("Вы погибли! Нажмите любую клавишу для возрождения", font_medium, (255, 0, 0), screen, W // 2,
                      H // 2)
        elif player.is_dead and not player.is_out:
            # Показываем сообщение во время анимации смерти
            if player.falling_through:
                draw_text("Вы погибли!", font_medium, (255, 0, 0), screen, W // 2, H // 3)
            else:
                draw_text("Вы погибли!", font_medium, (255, 0, 0), screen, W // 2, H // 3)

        # Проверка завершения волны
        if score >= enemy_count:
            complete_level(level_num)
            running = False

        pygame.display.flip()
        clock.tick(FPS)


def run_boss_fight(level_num):
    global boss, score, player, save_message_displayed, save_message_timer

    player.rect.midbottom = (W // 3, H - GROUND_H)
    boss = [Boss()]
    player.HP = load_upgrades()
    HP = player.HP
    Shield = player.shield
    invincible = False
    invincible_end_time = 0
    invincible_boss = False
    invincible_end_time_boss = 0
    boss_phase_transition = False  # Флаг перехода фазы босса
    boss_phase_transition_end = 0  # Время окончания перехода фазы

    show_message("Победи босса!")

    running = True
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_game_sql(level_num)
                    save_message_displayed = True
                    save_message_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_ESCAPE:
                    pause()
                    return
                elif event.key in [pygame.K_w, pygame.K_UP]:
                    # Игрок может прыгать только если жив
                    if not player.is_dead and not player.is_out:
                        player.handle_jump()
                # ВОССТАНОВЛЕНИЕ ПРИ СМЕРТИ - ДОБАВЛЕНА ПРОВЕРКА ЛЮБОЙ КЛАВИШИ
                elif player.is_out:
                    # Любая клавиша для возрождения
                    load_game_sql()
                    load_upgrades()
                    HP = player.HP
                    player.respawn()
                    player.rect.midbottom = (W // 3, H - GROUND_H)
                    boss.clear()
                    boss.append(Boss())
                    score = 0
                    boss_phase_transition = False  # Сбрасываем флаг перехода фазы
                    Shield = player.shield  # Восстанавливаем щиты

        # Обновление игрока (только если не мертв)
        if not player.is_dead and not player.is_out:
            player.handle_input()
        player.update()

        # Если игрок мертв и вылетел, ждем возрождения
        if player.is_out:
            # ПРОДОЛЖАЕМ ОБНОВЛЯТЬ ЭКРАН ДАЖЕ КОГДА ИГРОК МЕРТВ
            # Отрисовка фона
            screen.fill(level_manager.levels[level_num]["bg_color"])
            screen.blit(ground_image, (0, H - GROUND_H))
            screen.blit(ground_image, (500, H - GROUND_H))

            # Отрисовка босса (если еще жив)
            for boss_obj in boss:
                boss_obj.update()
                boss_obj.draw(screen)

            # Отрисовка игрока (даже если он "вылетел")
            player.draw(screen)

            # UI
            draw_text("БОСС БИТВА", font_large, (255, 0, 0), screen, W // 2, 30)
            if boss and not boss[0].is_dead:
                # Полоска HP босса
                hp_percent = boss[0].HP / 50
                bar_width = 400
                pygame.draw.rect(screen, (255, 0, 0), (W // 2 - bar_width // 2, 70, bar_width, 20))

                # Меняем цвет полоски в зависимости от фазы и неуязвимости
                if boss_phase_transition:
                    color = (255, 255, 0)  # Желтый во время перехода фазы
                elif boss[0].phase == 0:
                    color = (0, 255, 0)  # Зеленый
                elif boss[0].phase == 1:
                    color = (255, 165, 0)  # Оранжевый
                else:
                    color = (255, 0, 0)  # Красный

                pygame.draw.rect(screen, color, (W // 2 - bar_width // 2, 70, bar_width * hp_percent, 20))
                pygame.draw.rect(screen, (255, 255, 255), (W // 2 - bar_width // 2, 70, bar_width, 20), 2)
                draw_text(f"HP: {boss[0].HP}/50", font_small, (255, 255, 255), screen, W // 2, 80)

            draw_text(f"HP игрока: 0", font_medium, (255, 0, 0), screen, 100, 30)  # Показываем 0 HP
            draw_text(f"Щиты: {Shield}", font_medium, (255, 255, 255), screen, W - 100, 30)
            draw_text(f"Атака: {player.attack}", font_small, (255, 255, 255), screen, W // 2, H - 50)

            # СООБЩЕНИЕ О ВОЗРОЖДЕНИИ - ВСЕГДА ПОКАЗЫВАЕМ КОГДА ИГРОК is_out
            draw_text("Нажмите любую клавишу для возрождения", font_medium, (255, 255, 255), screen, W // 2, H // 2)

            pygame.display.flip()
            clock.tick(FPS)
            continue  # Пропускаем остальную логику, пока игрок мертв

        # ОБНОВЛЕНИЕ ДЛЯ ЖИВОГО ИГРОКА:

        # Обновление босса
        for boss_obj in list(boss):
            boss_obj.update()

            # Проверка коллизий с боссом (только если игрок жив и босс жив)
            if (not player.is_dead and not player.is_out and
                    player.rect.colliderect(boss_obj.rect) and
                    not boss_obj.is_dead and
                    not boss_phase_transition):  # Не проверяем коллизии во время перехода фазы

                # Проверяем, прыгнул ли игрок на босса сверху
                if (player.rect.bottom <= boss_obj.rect.centery and
                        player.y_speed > 0 and
                        abs(player.rect.centerx - boss_obj.rect.centerx) < boss_obj.rect.width / 2):

                    # Игрок прыгает на босса
                    boss_obj.HP -= player.attack

                    # Отскок игрока
                    player.y_speed = -12
                    player.is_grounded = False

                    # Визуальный эффект удара
                    invincible_boss = True
                    invincible_end_time_boss = now + 200

                    # Проверяем, умер ли босс
                    if boss_obj.HP <= 0:
                        boss_obj.kill()
                        score += 1
                        show_message("Босс побежден!")

                elif not boss_obj.damage_given and not invincible:
                    # Игрок получает урон от босса
                    if Shield >= 1:
                        Shield -= 1
                        player.shield -= 1
                        save_upgrades()
                        invincible = True
                        invincible_end_time = now + 1000
                    else:
                        HP -= 2  # Босс наносит больше урона
                        player.damaged()
                        boss_obj.damage_given = True
                        invincible = True
                        invincible_end_time = now + 1000
                    if HP <= 0:
                        player.kill(player.damaged_sprite)
                        show_message("Вы погибли!")
            else:
                boss_obj.damage_given = False

            # Проверяем переход фазы босса
            if not boss_obj.is_dead and boss_obj.phase_changed:
                boss_phase_transition = True
                boss_phase_transition_end = now + 1500  # 1.5 секунды неуязвимости
                boss_obj.phase_changed = False  # Сбрасываем флаг
                show_message(f"Босс входит в фазу {boss_obj.phase + 1}!")

            # Снимаем неуязвимость после перехода фазы
            if boss_phase_transition and now >= boss_phase_transition_end:
                boss_phase_transition = False

            # Удаляем босса, если он ушел за экран
            if boss_obj.is_out:
                boss.remove(boss_obj)

        # Снятие неуязвимости игрока
        if invincible and now >= invincible_end_time:
            invincible = False
            if not player.is_dead:
                player.image = player.idle_sprite
                player.speed = 5

        # Снятие неуязвимости босса (мигание при получении урона)
        if invincible_boss and now >= invincible_end_time_boss:
            invincible_boss = False

        # Визуальные эффекты при получении урона
        if invincible and not player.is_dead:
            if now % 200 < 100:  # Мигание каждые 200 мс
                player.image = player.damaged_sprite
            else:
                player.image = player.idle_sprite

        if invincible_boss:
            if now % 100 < 50:  # Быстрое мигание для босса
                # Можно добавить эффект для босса, если есть поврежденная текстура
                pass

        # Отрисовка для живого игрока
        screen.fill(level_manager.levels[level_num]["bg_color"])
        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(ground_image, (500, H - GROUND_H))

        for boss_obj in boss:
            boss_obj.draw(screen)

        player.draw(screen)

        # UI для живого игрока
        draw_text("БОСС БИТВА", font_large, (255, 0, 0), screen, W // 2, 30)
        if boss and not boss[0].is_dead:
            # Полоска HP босса
            hp_percent = boss[0].HP / 50
            bar_width = 400
            pygame.draw.rect(screen, (255, 0, 0), (W // 2 - bar_width // 2, 70, bar_width, 20))

            # Меняем цвет полоски в зависимости от фазы и неуязвимости
            if boss_phase_transition:
                color = (255, 255, 0)  # Желтый во время перехода фазы
            elif boss[0].phase == 0:
                color = (0, 255, 0)  # Зеленый
            elif boss[0].phase == 1:
                color = (255, 165, 0)  # Оранжевый
            else:
                color = (255, 0, 0)  # Красный

            pygame.draw.rect(screen, color, (W // 2 - bar_width // 2, 70, bar_width * hp_percent, 20))
            pygame.draw.rect(screen, (255, 255, 255), (W // 2 - bar_width // 2, 70, bar_width, 20), 2)
            draw_text(f"HP: {boss[0].HP}/50", font_small, (255, 255, 255), screen, W // 2, 80)

            # Показываем сообщение о неуязвимости во время перехода фазы
            if boss_phase_transition:
                draw_text("НЕУЯЗВИМОСТЬ!", font_medium, (255, 255, 0), screen, W // 2, 110)

        draw_text(f"HP игрока: {HP}", font_medium, (255, 255, 255), screen, 100, 30)
        draw_text(f"Щиты: {Shield}", font_medium, (255, 255, 255), screen, W - 100, 30)
        draw_text(f"Атака: {player.attack}", font_small, (255, 255, 255), screen, W // 2, H - 50)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text("Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2)

        # Проверка завершения боя
        if score >= 1:
            # Даем время на анимацию смерти босса
            end_delay = 2000
            end_time = now + end_delay

            while pygame.time.get_ticks() < end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Продолжаем обновлять анимации
                for boss_obj in boss:
                    boss_obj.update()
                    if boss_obj.is_out:
                        boss.remove(boss_obj)

                player.update()

                # Отрисовка
                screen.fill(level_manager.levels[level_num]["bg_color"])
                screen.blit(ground_image, (0, H - GROUND_H))
                screen.blit(ground_image, (500, H - GROUND_H))
                for boss_obj in boss:
                    boss_obj.draw(screen)

                player.draw(screen)
                draw_text("БОСС ПОБЕЖДЕН!", font_large, (255, 215, 0), screen, W // 2, H // 3)

                pygame.display.flip()
                clock.tick(FPS)

            complete_level(level_num, is_boss=True)
            running = False

        pygame.display.flip()
        clock.tick(FPS)


def complete_level(level_num, is_boss=False):
    global current_difficulty, player_points_easy, player_points_medium, player_points_hard, player, \
        playing_menu, from_level, from_menu, message

    # Награда за уровень
    points_reward = {0: 3, 1: 4, 2: 5}
    reward = points_reward.get(current_difficulty, 5)

    if current_difficulty == 0:
        player_points_easy += reward
    elif current_difficulty == 1:
        player_points_medium += reward
    elif current_difficulty == 2:
        player_points_hard += reward

    # Отмечаем уровень как пройденный
    cursor = saving.cursor()
    table_name = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]
    cursor.execute(f'UPDATE {table_name} SET cleared=1 WHERE level_number=?', (level_num,))

    # Открываем улучшения для определенных уровней
    if level_num == 1:
        player.running_unlocked = True
        if player.HP <= 5:
            player.HP = 5
        if player.attack < 2:
            player.attack = 2
        message = "Открыты навык: бег, скин 'Соник', +2HP, +1ATK"
    elif level_num == 2:
        player.double_jump_unlocked = True
        if player.HP <= 8:
            player.HP = 8
        message = "Открыты навык: двойной прыжок, скин 'Марио', +3HP"
    elif level_num == 3 and is_boss:
        # Дополнительная награда за победу над боссом
        if player.HP <= 10:
            player.HP = 10
        if player.attack < 3:
            player.attack = 3
        message = f"Босс побежден! +{reward+1} очков, +2HP, +1ATK"
        if current_difficulty == 0:
            player_points_easy += reward
        elif current_difficulty == 1:
            player_points_medium += reward
        elif current_difficulty == 2:
            player_points_hard += reward
    elif level_num == 4:
        player.running_unlocked = True
        if player.HP <= 12:
            player.HP = 12
        if player.attack < 4:
            player.attack = 4
        message = "+2HP, +1ATK"
    elif level_num == 5:
        player.double_jump_unlocked = True
        if player.HP <= 13:
            player.HP = 13
        message = "+1HP"
    elif level_num == 6 and is_boss:
        # Дополнительная награда за победу над боссом
        if player.HP <= 15:
            player.HP = 15
        if player.attack < 5:
            player.attack = 5
        message = f"Босс побежден! +{reward+1} очков, +2HP, +1ATK"
        if current_difficulty == 0:
            player_points_easy += reward
        elif current_difficulty == 1:
            player_points_medium += reward
        elif current_difficulty == 2:
            player_points_hard += reward

    saving.commit()
    save_upgrades()
    load_upgrades()
    save_settings_sql()

    # Показываем экран завершения
    end_time = pygame.time.get_ticks() + 4000  # Увеличим время показа
    while pygame.time.get_ticks() < end_time:
        screen.fill(level_manager.levels[level_num]["bg_color"])
        if is_boss:
            draw_text("БОСС ПОБЕЖДЕН!", font_large, (255, 215, 0), screen, W // 2, H // 3)
        else:
            draw_text("Уровень пройден!", font_large, (255, 255, 255), screen, W // 2, H // 3)
        draw_text(message, font_medium, (255, 255, 255), screen, W // 2, H // 2 + 50)
        pygame.display.flip()
        clock.tick(FPS)
    cursor = saving.cursor()
    if current_difficulty == 0:
        cursor.execute('DELETE FROM game_progress_easy')
    elif current_difficulty == 1:
        cursor.execute('DELETE FROM game_progress_medium')
    elif current_difficulty == 2:
        cursor.execute('DELETE FROM game_progress_hard')
    from_level = True
    from_menu = False
    playing_menu = True
    # Возвращаемся в меню уровней
    level_menu()


# Запуск игры
if __name__ == "__main__":
    load_settings_sql()
    Level = load_game_sql()
    load_skin()
    load_upgrades()
    apply_skin(current_skin_index)
    play_menu_music()
    main_menu()
    pygame.quit()