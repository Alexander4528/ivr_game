# Импорт необходимых библиотек
import pygame
import sqlite3
import sys
import random
from pygame import Surface


pygame.init()

# Настройки игры
font_path = "caviar-dreams.ttf"
font_large = pygame.font.Font(font_path, 48)
font_medium = pygame.font.Font(font_path, 36)
font_small = pygame.font.Font(font_path, 24)
player_points_easy = 0
player_points_medium = 0
player_points_hard = 0
current_player_points = 0
difficulty_level = 0
current_difficulty = 0
dark_mode = False
pending_mode = dark_mode
background_color = (62, 118, 222) if dark_mode else (92, 148, 252)

# Игровые переменные
monsters = []
last_spawn_time = 0
spawn_delay = 3000
score = 0
boss = None

# Переменные для активации разделов игры(уровни, меню, настройки и т.д.)
menu = False
level_1_part_1_in = False
level_2_part_1_in = False
level_3_part_1_in = False
levels_in = False
Level1 = False
Level2 = False
Level3 = False
level = 1

# Переменные меню
playing_menu = True
playing_level = False
from_menu = False
from_level = False
menu_move_up = False
menu_move_down = False
menu_last_move_time = 0
MENU_MOVE_DELAY = 300

# Переменные для скроллинга
level_1_part_1_WIDTH = 5000
level_1_part_1_scroll_pos = 0
W, H = 1000, 800
screen = pygame.display.set_mode((W, H))
FPS = 60
clock = pygame.time.Clock()

# Экран при отсутствии изображения скина
surface_image = pygame.Surface((40, 50))

# Загрузка изображений
ground_image: Surface = pygame.image.load(
    "Sprites and objects/Objects, background and other/ground.jpg"
)
ground_image = pygame.transform.scale(ground_image, (W, 60))
GROUND_H = ground_image.get_height()
me_image = pygame.image.load("Sprites and objects/Skins/Me/Me.png")
me_image = pygame.transform.scale(me_image, (70, 80))
portal_image = pygame.image.load(
    "Sprites and objects/Objects, background and other/p2.gif"
)
portal_image = pygame.transform.scale(portal_image, (80, 90))
me_damaged_image = pygame.image.load("Sprites and objects/Skins/Me/Me_damaged.png")
me_damaged_image = pygame.transform.scale(me_damaged_image, (70, 80))

# Переключение музыки
music_on = True
menu_music = "Music/Carmen_Twillie_The_Lion_King_-_Circle_Of_Life_48727462.mp3"
level_1_part_1_music = "Music/Смешарики - Погоня.mp3"
level_2_part_1_music = "Music/Geometry_Dash_-_Geometrical_Dominator_67148396.mp3"

# Переключение звука
sound_on = True
Unlock_skin_sound = pygame.mixer.Sound("Sounds/mixkit-unlock-new-item-game-notification-254.wav")

# Переменные сообщения об открытии нового скина / улучшения навыка
unlock_message = None
unlock_message_time = 0
UNLOCK_MESSAGE_DURATION = 3000  # Время отображения в миллисекундах

message = None
message_time = 0
MESSAGE_DURATION = 3000

level1_cleared = False
level2_cleared = False

# Подготовка таблицы с сохранениями
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
    # Таблица для прогресса
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress_easy (
                id INTEGER PRIMARY KEY,
                player_pos INTEGER,
                score INTEGER,
                HP INTEGER,
                shield INTEGER,
                level INTEGER
            )
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress_medium (
                id INTEGER PRIMARY KEY,
                player_pos INTEGER,
                score INTEGER,
                HP INTEGER,
                shield INTEGER,
                level INTEGER
            )
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress_hard (
                id INTEGER PRIMARY KEY,
                player_pos INTEGER,
                score INTEGER,
                HP INTEGER,
                shield INTEGER,
                level INTEGER
            )
        ''')
    # Таблица для скинов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY,
            current_skin_index INTEGER
        )
    ''')
    # Таблица для улучшений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upgrades_easy (
            id INTEGER PRIMARY KEY,
            player_points INTEGER,
            attack INTEGER,
            HP INTEGER,
            running_unlocked INTEGER,
            double_jump_unlocked INTEGER,
            shield INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upgrades_medium (
            id INTEGER PRIMARY KEY,
            player_points INTEGER,
            attack INTEGER,
            HP INTEGER,
            running_unlocked INTEGER,
            double_jump_unlocked INTEGER,
            shield INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS upgrades_hard (
            id INTEGER PRIMARY KEY,
            player_points INTEGER,
            attack INTEGER,
            HP INTEGER,
            running_unlocked INTEGER,
            double_jump_unlocked INTEGER,
            shield INTEGER
        )
    ''')
    # Поменять здесь на 3 таблицы с пройденными уровнями для каждого уровня сложности
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS levels_easy (
            id INTEGER PRIMARY KEY,
            level_number INTEGER,
            cleared INTEGER,
            UNIQUE(level_number)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS levels_medium (
            id INTEGER PRIMARY KEY,
            level_number INTEGER,
            cleared INTEGER,
            UNIQUE(level_number)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS levels_hard (
            id INTEGER PRIMARY KEY,
            level_number INTEGER,
            cleared INTEGER,
            UNIQUE(level_number)
        )
    ''')
    cursor.execute(
        'INSERT OR IGNORE INTO upgrades_easy (id, player_points, attack, HP, running_unlocked, double_jump_unlocked, '
        'shield) VALUES (1, 0, 1, 3, 0, 0, 0)')
    cursor.execute(
        'INSERT OR IGNORE INTO upgrades_medium (id, player_points, attack, HP, running_unlocked, double_jump_unlocked, '
        'shield) VALUES (1, 0, 1, 3, 0, 0, 0)')
    cursor.execute(
        'INSERT OR IGNORE INTO upgrades_hard (id, player_points, attack, HP, running_unlocked, double_jump_unlocked, '
        'shield) VALUES (1, 0, 1, 3, 0, 0, 0)')
    for level_num in range(1, 10):
        cursor.execute('INSERT OR IGNORE INTO levels_easy (level_number, cleared) VALUES (?, ?)',
                       (level_num, 0))
        cursor.execute('''DELETE FROM levels_easy WHERE id NOT IN (
                                                                SELECT id FROM levels_easy ORDER BY id ASC LIMIT 9)
                                                        ''')
        cursor.execute('INSERT OR IGNORE INTO levels_medium (level_number, cleared) VALUES (?, ?)',
                       (level_num, 0))
        cursor.execute('''DELETE FROM levels_medium WHERE id NOT IN (
                                                                SELECT id FROM levels_medium ORDER BY id ASC LIMIT 9)
                                                                ''')
        cursor.execute('INSERT OR IGNORE INTO levels_hard (level_number, cleared) VALUES (?, ?)',
                       (level_num, 0))
        cursor.execute('''DELETE FROM levels_hard WHERE id NOT IN (
                                                                SELECT id FROM levels_hard ORDER BY id ASC LIMIT 9)
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
        "img": surface_image,
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
        "img": surface_image,
    },
    {
        "name": "Селена",
        "unlocked": True,
        "image": "Sprites and objects/Skins/Girlfriend/Girlfriend.png",
        "walk_right": [
            "Sprites and objects/Skins/Girlfriend/Girlfriend_right1.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_right2.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_right3.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Girlfriend/Girlfriend_left1.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_left2.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_left3.png",
            "Sprites and objects/Skins/Girlfriend/Girlfriend_left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Girlfriend/Girlfriend_damaged.png",
        "unlock": " ",
        "img": surface_image,
    },
    {
        "name": "Мона",
        "unlocked": True,
        "image": "Sprites and objects/Skins/Lost_girlfriend/Mona.png",
        "walk_right": [
            "Sprites and objects/Skins/Lost_girlfriend/Mona_right1.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_right2.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_right3.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Lost_girlfriend/Mona_left1.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_left2.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_left3.png",
            "Sprites and objects/Skins/Lost_girlfriend/Mona_left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Lost_girlfriend/Mona_damaged.png",
        "unlock": " ",
        "img": surface_image,
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
        "img": surface_image,
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
        "img": surface_image,
    },
    {
        "name": "Эксклюзивный",
        "unlocked": False,
        "image": "exclusive.png",
        "unlock": "Пройди игру на всех уровнях сложности",
        "img": surface_image,
    },
]

# Анимации
running_sprites_right = []
for i in range(1, 5):
    try:
        img = pygame.image.load(f"Me-right{i}.png")
        running_sprites_right.append(pygame.transform.scale(img, (70, 80)))
    except:
        running_sprites_right.append(pygame.Surface((70, 80)))

running_sprites_left = []
for i in range(1, 5):
    try:
        img = pygame.image.load(f"Me-left{i}.png")
        running_sprites_left.append(pygame.transform.scale(img, (70, 80)))
    except:
        running_sprites_left.append(pygame.Surface((70, 80)))

# Переменные текущего скина
current_skin_index = 0
skin_message_timer = 0

# Загрузка изображений скинов
for skin_number in skins:
    try:
        img = pygame.image.load(skin_number["image"])
        if skin_number["name"] == "Селена" or skin_number["name"] == "Мона":
            skin_number["img"] = pygame.transform.scale(img, (30, 55))
        else:
            skin_number["img"] = pygame.transform.scale(img, (40, 50))
    except:
        pass

def change_difficulty(new_difficulty):
    global current_difficulty, difficulty_level
    current_difficulty = new_difficulty
    difficulty_level = new_difficulty
    save_settings_sql()
    load_upgrades()  # загрузка только для текущего уровня
    load_skin()
    apply_skin(current_skin_index)

# Загрузка скина
def apply_skin(skin_index):
    global me_image, running_sprites_right, running_sprites_left, me_damaged_image
    if skin_index < 0 or skin_index >= len(skins):
        skin_index = 0  # Защита от неверного индекса
    skin = skins[skin_index]
    try:
        # Загружаем основное изображение
        if skin["name"] == "Селена" or skin["name"] == "Мона":
            me_image = pygame.transform.scale(pygame.image.load(skin["image"]), (50, 80))
        else:
            me_image = pygame.transform.scale(pygame.image.load(skin["image"]), (70, 80))
        # Загружаем анимации
        if skin.get("walk_right", []) and skin["name"] != "Селена" and skin["name"] != "Мона":
            running_sprites_right = [
                pygame.transform.scale(pygame.image.load(fname), (70, 80))
                for fname in skin["walk_right"]
            ]
        elif skin.get("walk_right", []) and (skin["name"] == "Селена" or skin["name"] == "Мона"):
            running_sprites_right = [
                pygame.transform.scale(pygame.image.load(fname), (50, 80))
                for fname in skin["walk_right"]
            ]
        else:
            running_sprites_right = [me_image] * 4
        if skin.get("walk_left", []) and skin["name"] != "Селена" and skin["name"] != "Мона":
            running_sprites_left = [
                pygame.transform.scale(pygame.image.load(fname), (70, 80))
                for fname in skin["walk_left"]
            ]
        elif skin.get("walk_left", []) and (skin["name"] == "Селена" or skin["name"] == "Мона"):
            running_sprites_left = [
                pygame.transform.scale(pygame.image.load(fname), (50, 80))
                for fname in skin["walk_left"]
            ]
        else:
            running_sprites_left = [me_image] * 4
        if skin.get("damaged", []):
            if skin["name"] == "Селена" or skin["name"] == "Мона":
                me_damaged_image = pygame.transform.scale(pygame.image.load(skin["damaged"]), (50, 80))
            else:
                me_damaged_image = pygame.transform.scale(pygame.image.load(skin["damaged"]), (70, 80))
        else:
            me_damaged_image = me_image
    except Exception as e:
        print(f"Ошибка загрузки скина: {e}")
        # Загружаем скин по умолчанию при ошибке
        if skin_index != 0:
            apply_skin(0)


# Сохранение настроек
def save_settings_sql():
    global music_on, sound_on, player_points_easy, player_points_medium, player_points_hard, \
        current_difficulty, pending_mode
    cursor = saving.cursor()
    cursor.execute('DELETE FROM settings')
    points = player_points_easy if current_difficulty == 0 else(player_points_medium if
                                                                       current_difficulty == 1 else player_points_hard)
    cursor.execute('INSERT INTO settings (music_on, sound_on, player_points, difficulty_level, dark_mode) '
                   'VALUES (?, ?, ?, ?, ?)',
                   (int(music_on), int(sound_on), int(points), current_difficulty, int(pending_mode)))
    saving.commit()

# Загрузка настроек
def load_settings_sql():
    global current_difficulty, difficulty_level, dark_mode, background_color, pending_mode, music_on, sound_on
    cursor = saving.cursor()
    cursor.execute('SELECT music_on, sound_on, player_points, difficulty_level, dark_mode FROM settings LIMIT 1')
    row = cursor.fetchone()
    if row:
        music_on = bool(row[0])
        sound_on = bool(row[1])
        # Восстановление очков для текущего уровня
        if row[3] is not None:
            current_difficulty = row[3]
            difficulty_level = row[3]
        else:
            current_difficulty = 0
            difficulty_level = 0
        dark_mode = bool(row[4])
        background_color = (62, 118, 222) if dark_mode else (92, 148, 252)
        pending_mode = dark_mode

# Сохранение игры
def save_game_sql(level_number):
    global level_1_part_1_scroll_pos, score, player, current_difficulty
    cursor = saving.cursor()
    if current_difficulty == 0:
        table_name = 'game_progress_easy'
    elif current_difficulty == 1:
        table_name = 'game_progress_medium'
    else:
        table_name = 'game_progress_hard'
    # сохраняете только в таблицу текущей сложности
    cursor.execute(f'DELETE FROM {table_name}')
    cursor.execute(f'INSERT INTO {table_name} (player_pos, score, HP, shield, level) VALUES (?, ?, ?, ?, ?)',
                   (level_1_part_1_scroll_pos, score, player.HP, player.shield, level_number))
    saving.commit()

# Загрузка последнего сохранения
def load_game_sql():
    global level_1_part_1_scroll_pos, score, player, level, current_difficulty
    cursor = saving.cursor()
    if current_difficulty == 0:
        table_name = 'game_progress_easy'
    elif current_difficulty == 1:
        table_name = 'game_progress_medium'
    else:
        table_name = 'game_progress_hard'
    cursor.execute(f'SELECT player_pos, score, HP, shield, level FROM {table_name} LIMIT 1')
    row = cursor.fetchone()
    if row:
        level_1_part_1_scroll_pos = row[0]
        score = row[1]
        player.HP = row[2]
        player.shield = row[3]
        level = row[4]
    else:
        level_1_part_1_scroll_pos = 0
        score = 0
        level = 1
    return level

# Сохранение скина
def save_skin():
    global current_skin_index
    cursor = saving.cursor()
    cursor.execute('DELETE FROM skins')
    cursor.execute('INSERT INTO skins (current_skin_index) VALUES (?)', (current_skin_index,))
    saving.commit()

# Загрузка скина
def load_skin():
    global current_skin_index
    cursor = saving.cursor()
    cursor.execute('SELECT current_skin_index FROM skins LIMIT 1')
    row = cursor.fetchone()
    if row:
        current_skin_index = row[0]
    else:
        current_skin_index = 0

# Сохранение улучшении
def save_upgrades():
    global player_points_easy, player_points_medium, player_points_hard, player
    cursor = saving.cursor()
    if current_difficulty == 0:
        cursor.execute('UPDATE upgrades_easy SET player_points = ?, attack = ?, HP = ?, running_unlocked = ?, double_jump_unlocked = ?, shield = ? WHERE id=1', (
            player_points_easy, player.attack, player.HP, int(player.running_unlocked), int(player.double_jump_unlocked), player.shield))
    elif current_difficulty == 1:
        cursor.execute('UPDATE upgrades_medium SET player_points = ?, attack = ?, HP = ?, running_unlocked = ?, double_jump_unlocked = ?, shield = ? WHERE id=1', (
            player_points_medium, player.attack, player.HP, int(player.running_unlocked), int(player.double_jump_unlocked), player.shield))
    elif current_difficulty == 2:
        cursor.execute('UPDATE upgrades_hard SET player_points = ?, attack = ?, HP = ?, running_unlocked = ?, double_jump_unlocked = ?, shield = ? WHERE id=1', (
            player_points_hard, player.attack, player.HP, int(player.running_unlocked), int(player.double_jump_unlocked), player.shield))
    saving.commit()

def load_upgrades():
    global player_points_easy, player_points_medium, player_points_hard, player
    cursor = saving.cursor()
    cursor.execute('SELECT player_points, attack, HP, running_unlocked, double_jump_unlocked, '
                   'shield FROM upgrades_easy LIMIT 1')
    row_easy = cursor.fetchone()
    cursor.execute('SELECT player_points, attack, HP, running_unlocked, double_jump_unlocked, '
                   'shield FROM upgrades_medium LIMIT 1')
    row_medium = cursor.fetchone()
    cursor.execute('SELECT player_points, attack, HP, running_unlocked, double_jump_unlocked, '
                   'shield FROM upgrades_hard LIMIT 1')
    row_hard = cursor.fetchone()

    if current_difficulty == 0 and row_easy:
        player_points_easy = row_easy[0]
        player.attack = row_easy[1]
        player.HP = row_easy[2]
        player.running_unlocked = bool(row_easy[3])
        player.double_jump_unlocked = bool(row_easy[4])
        player.shield = row_easy[5]
    elif current_difficulty == 1 and row_medium:
        player_points_medium = row_medium[0]
        player.attack = row_medium[1]
        player.HP = row_medium[2]
        player.running_unlocked = bool(row_medium[3])
        player.double_jump_unlocked = bool(row_medium[4])
        player.shield = row_medium[5]
    elif current_difficulty == 2 and row_hard:
        player_points_hard = row_hard[0]
        player.attack = row_hard[1]
        player.HP = row_hard[2]
        player.running_unlocked = bool(row_hard[3])
        player.double_jump_unlocked = bool(row_hard[4])
        player.shield = row_hard[5]

# Текст
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, rect)

# Музыка меню
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

#Музыка уровня
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

# Остановка музыки
def stop_music():
    global music_playing
    pygame.mixer.music.stop()
    music_playing = False

# Переключение музыки
def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()
    save_settings_sql()

# Переключение звука
def toggle_sound():
    global sound_on
    sound_on = not sound_on
    save_settings_sql()

# Пауза
def pause():
    global music_on, playing_menu, from_level, from_menu, score, level_1_part_1_in, level_2_part_1_in
    load_settings_sql()
    options_pause_rects = [
        pygame.Rect(W // 2 - 100, H // 2, 200, 40),
        pygame.Rect(W // 2 - 100, H // 2 + 50, 200, 40),
        pygame.Rect(W // 2 - 100, H // 2 + 100, 200, 40),
        pygame.Rect(W // 2 - 100, H // 2 + 150, 200, 40),
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
                            toggle_sound()
                        elif idx == 2:
                            management_menu()
                        elif idx == 3:
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
        for j, opt in enumerate(["Музыка", "Звук", "Управление", "Назад"]):
            rect = options_pause_rects[j]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)  # выделение при наведении
            else:
                color = (0, 0, 0)  # обычный цвет
            # Центрируем текст по координате
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
    pygame.event.clear(pygame.KEYDOWN)


# Характеристики и функции игрока
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
            if self.running_unlocked and (
                keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            ):
                self.rect.x -= 2 * self.speed
            else:
                self.rect.x -= self.speed
            self.update_animation()
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            if self.running_unlocked and (
                keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            ):
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
                self.run_animation_index = (self.run_animation_index + 1) % len(
                    self.running_sprites_left
                )
                self.image = self.running_sprites_left[self.run_animation_index]
                self.last_update_time = now
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.run_animation_index = (self.run_animation_index + 1) % len(
                    self.running_sprites_right
                )
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

# Характеристика и функции врагов
class Monster:
    def __init__(self):
        global Level1, Level2
        try:
            if Level1:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Common/Enemy.png"), (90, 90)
                )
            elif Level2:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Speed/Speed_enemy_right.png"), (120, 90)
                )
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
        global Level1, Level2
        direction = random.randint(0, 1)
        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, 0)
            try:
                if Level1:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Common/Enemy-left.png"),(90, 90))
                elif Level2:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Speed/Speed_enemy.png"), (120, 90))
            except:
                self.image = pygame.Surface((90, 90))
        else:
            self.x_speed = -self.speed
            self.rect.bottomright = (W, 0)
            try:
                if Level1:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Common/Enemy.png"), (90, 90))
                elif Level2:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Speed/Speed_enemy_right.png"), (120, 90))
            except:
                self.image = pygame.Surface((90, 90))

    def kill(self):
        global Level1, Level2
        try:
            if Level1:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Common/EnemyDead.png"), (90, 90))
            elif Level2:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Speed/Speed_enemy_dead.png"), (120, 90))
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

class Boss:
    def __init__(self):
        global Level3
        try:
            if Level3:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Common/Enemy.png"), (90, 90)
                )
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
        self.HP = 6

    def spawn(self):
        global Level3
        direction = random.randint(0, 1)
        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, 0)
            try:
                if Level3:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Common/Enemy-left.png"),(120, 120))
            except:
                self.image = pygame.Surface((120, 120))
        else:
            self.x_speed = -self.speed
            self.rect.bottomright = (W, 0)
            try:
                if Level3:
                    self.image = pygame.transform.scale(
                        pygame.image.load("Sprites and objects/Enemies/Common/Enemy.png"), (120, 120))
            except:
                self.image = pygame.Surface((120, 120))

    def kill(self):
        global Level3
        try:
            if Level3:
                self.image = pygame.transform.scale(
                    pygame.image.load("Sprites and objects/Enemies/Common/EnemyDead.png"), (120, 120))
        except:
            self.image = pygame.Surface((120, 120))
        self.is_dead = True
        self.x_speed = -self.x_speed
        self.y_speed = self.jump_speed

    def update(self):
        self.y_speed += self.gravity
        self.rect.y += self.y_speed
        if self.rect.left < 0:
            self.rect.x += self.x_speed
        elif self.rect.right > W:
            self.rect.x -= self.x_speed

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

# Активация игрока
player = Player()

# Главное меню
def main_menu():
    global player, menu, levels_in, from_menu, from_level, current_skin_index, background_color
    load_settings_sql()
    menu = True
    options_rects = [
        pygame.Rect(W // 2 - 100, H // 2 - 100, 200, 40),  # "Начать игру"
        pygame.Rect(W // 2 - 100, H // 2 - 50, 200, 40),  # "Скины"
        pygame.Rect(W // 2 - 100, H // 2, 200, 40),  # "Улучшение"
        pygame.Rect(W // 2 - 100, H // 2 + 50, 200, 40),  # "Настройки"
        pygame.Rect(W // 2 - 100, H // 2 + 100, 200, 40),  # "Секреты"
        pygame.Rect(W // 2 - 100, H // 2 + 150, 200, 40),  # "Выход"
    ]
    load_game_sql()
    load_skin()
    apply_skin(current_skin_index)
    player = Player()
    from_level = False
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings_sql()
                pygame.quit()
                sys.exit()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # левый клик
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

        screen.fill(background_color)
        draw_text("Главное меню", font_large, (255, 255, 255), screen, W // 2, H // 4)
        options = [
            "Начать игру",
            "Скины",
            "Улучшение",
            "Настройки",
            "Секреты",
            "Выход из игры",
        ]
        for j, opt in enumerate(options):
            rect = options_rects[j]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            draw_text(opt, font_small, color, screen, W // 2, H // 2 - 90 + j * 50)
        pygame.display.flip()
        clock.tick(60)


# Меню со скинами
def skin_menu():
    global current_skin_index, me_image, running_sprites_right, running_sprites_left, background_color, player
    load_upgrades()
    load_skin()
    in_skin_menu = True

    # Создаем список прямоугольников для областей клика
    skin_rects = []
    for idx in range(len(skins)):
        skin_rects.append(pygame.Rect(W // 2 - 400 if idx < 4 else W // 2 + 50, H // 4 + idx % 4 * 60 - 20, 200, 40))

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

        screen.fill(background_color)
        draw_text(
            "Выбор скина", font_large, (255, 255, 255), screen, W // 2, H // 6 - 40
        )
        load_upgrades()
        for skin in skins:
            if skin["name"] == "Соник":
                skin["unlocked"] = player.running_unlocked
            if skin["name"] == "Марио":
                skin["unlocked"] = player.double_jump_unlocked

        # Отрисовка скинов и обработка кликов
        for idx, skin in enumerate(skins):
            y_pos = H // 4 + idx % 4 * 60
            x_pos = W // 2 - 250 if idx < 4 else W // 2 + 200
            is_hovered = skin_rects[idx].collidepoint(mouse_pos)
            is_selected = idx == current_skin_index
            color = (255, 255, 255) if (is_hovered or is_selected) else (0, 0, 0)

            draw_text(skin["name"], font_small, color, screen, x_pos, y_pos)

            if "img" in skin:
                img_surface = skin["img"]
                if isinstance(img_surface, pygame.Surface):
                    img_rect = img_surface.get_rect(center=(x_pos - 120, y_pos))
                    screen.blit(img_surface, img_rect)
            status = "Открыт" if skin["unlocked"] else "Закрыт"
            if skin["name"] == "Соник":
                status = "Открыт" if player.running_unlocked else "Закрыт"
            if skin["name"] == "Марио":
                status = "Открыт" if player.double_jump_unlocked else "Закрыт"
            draw_text(status, font_small, color, screen, x_pos + 150, y_pos)

            if is_hovered and mouse_clicked and skin["unlocked"]:
                current_skin_index = idx
                apply_skin(current_skin_index)
                player.running_sprites_right = running_sprites_right
                player.running_sprites_left = running_sprites_left
                player.idle_sprite = me_image
                player.image = player.idle_sprite
                player.damaged_sprite = me_damaged_image
                save_game_sql(level)
                save_upgrades()
                save_skin()

            if is_hovered and not skin["unlocked"]:
                draw_text(
                    skin["unlock"],
                    font_small,
                    (255, 255, 255),
                    screen,
                    W // 2,
                    H // 3 * 2 + 130,
                )

        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text("Главное меню", font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            in_skin_menu = False

        pygame.display.flip()
        clock.tick(60)


def settings():
    global music_on, sound_on, current_difficulty, level1_cleared, level2_cleared, dark_mode, \
        background_color, pending_mode, player_points_easy, player_points_medium, player_points_hard, current_skin_index
    load_upgrades()
    options_settings = [
        "Уровень сложности",
        "Музыка",
        "Звук",
        "Фон",
        "Сброс прогресса",
        "Сохранить настройки",
        "Отменить",
        "Управление",
        "Главное меню",
    ]
    options_settings_rects = [
        pygame.Rect(W // 2 - 100, H // 3 - 50, 200, 40),  # "Уровень сложности"
        pygame.Rect(W // 2 - 100, H // 3, 200, 40),  # "Музыка"
        pygame.Rect(W // 2 - 100, H // 3 + 50, 200, 40), # "Звук"
        pygame.Rect(W // 2 - 100, H // 3 + 100, 200, 40), # "Фон"
        pygame.Rect(W // 2 - 100, H // 3 + 150, 200, 40), # "Сброс прогресса"
        pygame.Rect(W // 2 - 100, H // 3 + 200, 200, 40), # "Сохранить настройки"
        pygame.Rect(W // 2 - 100, H // 3 + 250, 200, 40), # "Отменить"
        pygame.Rect(W // 2 - 100, H // 3 + 300, 200, 40), # "Управление"
        pygame.Rect(W // 2 - 100, H // 3 + 350, 200, 40)  # "Главное меню"
    ]
    # Объявляем переменные один раз перед циклом
    temp_difficulty = current_difficulty

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # левый клик
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
                            toggle_sound()
                        elif selected_idx == 3:
                            pending_mode = not pending_mode
                            background_color = (62, 118, 222) if pending_mode else (92, 148, 252)
                        elif selected_idx == 4:
                            cursor = saving.cursor()
                            if difficulty_level == 0:
                                cursor.execute('DELETE FROM game_progress_easy')
                                cursor.execute('DELETE FROM upgrades_easy')
                                cursor.execute('DELETE FROM levels_easy')
                                player_points_easy = 0
                            elif difficulty_level == 1:
                                cursor.execute('DELETE FROM game_progress_medium')
                                cursor.execute('DELETE FROM upgrades_medium')
                                cursor.execute('DELETE FROM levels_medium')
                                player_points_medium = 0
                            elif difficulty_level == 2:
                                cursor.execute('DELETE FROM game_progress_hard')
                                cursor.execute('DELETE FROM upgrades_hard')
                                cursor.execute('DELETE FROM levels_hard')
                                player_points_hard = 0
                            saving.commit()
                            level1_cleared = False
                            level2_cleared = False
                        elif selected_idx == 5:
                            # Обновляем уровень сложности только при сохранении
                            current_difficulty = temp_difficulty
                            current_skin_index = 0
                            apply_skin(current_skin_index)
                            save_settings_sql()
                            save_skin()
                            load_upgrades()
                            if current_difficulty == 0:
                                player_points_easy= player_points_easy
                            elif current_difficulty == 1:
                                player_points_medium = player_points_medium
                            elif current_difficulty == 2:
                                player_points_hard = player_points_hard
                            if dark_mode != pending_mode:
                                dark_mode = pending_mode
                            background_color = (62, 118, 222) if dark_mode else (92, 148, 252)
                        elif selected_idx == 6:
                            temp_difficulty = 0
                            save_settings_sql()
                            save_game_sql(level)
                            dark_mode = False
                            pending_mode = dark_mode
                            background_color = (62, 118, 222) if dark_mode else (92, 148, 252)
                            if not music_on:
                                toggle_music()
                                if music_on:
                                    play_menu_music()
                            if not sound_on:
                                toggle_sound()
                            save_skin()
                        elif selected_idx == 7:
                            management_menu()
                        elif selected_idx == 8:
                            main_menu()
        mouse_pos = pygame.mouse.get_pos()
        # Отрисовка
        screen.fill(background_color)
        draw_text("Настройки", font_large, (255, 255, 255), screen, W // 2, H // 6)
        for idx, opt in enumerate(options_settings):
            rect = options_settings_rects[idx]
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 255)
            else:
                color = (0, 0, 0)
            if options_settings[idx] == "Музыка":
                status = "Вкл" if music_on else "Выкл"
                draw_text(
                    f"Музыка: {status}",
                    font_small,
                    color,
                    screen,
                    W // 2,
                    H // 3 + (idx - 1) * 50,
                )
            elif options_settings[idx] == "Звук":
                status2 = "Вкл" if sound_on else "Выкл"
                draw_text(
                    f"Звук: {status2}",
                    font_small,
                    color,
                    screen,
                    W // 2,
                    H // 3 + (idx - 1) * 50,
                )
            elif options_settings[idx] == "Фон":
                status3 = "Тёмный" if pending_mode else "Светлый"
                draw_text(
                    f"Фон: {status3}",
                    font_small,
                    color,
                    screen,
                    W // 2,
                    H // 3 + (idx - 1) * 50,
                )
            elif options_settings[idx] == "Уровень сложности":
                levels = ["Легко", "Средне", "Сложно"]
                level_text = f"Уровень сложности: {levels[temp_difficulty]}"
                draw_text(
                    level_text, font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50
                )
            else:
                draw_text(opt, font_small, color, screen, W // 2, H // 3 + (idx - 1) * 50)

        # Кол-во очков
        if current_difficulty == 0:
            draw_text(
                f"Очки: {player_points_easy}", font_small, (255, 255, 255), screen, W - 100, 50
            )
        elif current_difficulty == 1:
            draw_text(
                f"Очки: {player_points_medium}", font_small, (255, 255, 255), screen, W - 100, 50
            )
        elif current_difficulty == 2:
            draw_text(
                f"Очки: {player_points_hard}", font_small, (255, 255, 255), screen, W - 100, 50
            )


        pygame.display.flip()
        clock.tick(60)


# Внутренний менеджер управления
def management_menu():
    global background_color
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
        screen.fill(background_color)
        draw_text(
            "Управление", font_large, (255, 255, 255), screen, W // 2, H // 3 - 80
        )
        controls = [
            "Передвижение: A / ←, D / →",
            "Прыжок: W / ↑",
            "Бег: (A / ←) / (D / →) + Shift",
            "Пауза: ESC",
            "Сохранение: S",
        ]
        for h, control in enumerate(controls):
            draw_text(control, font_small, (0, 0, 0), screen, W // 2, H // 3 + h * 40)

        if rect_exit.collidepoint(mouse_pos):
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)
        draw_text("Выход", font_small, color, screen, W // 2, H - 50)
        pygame.display.flip()
        clock.tick(60)


def secrets():
    pass


# Выбор уровней
def level_menu():
    global levels_in, music_playing, from_menu, from_level, level1_cleared, level2_cleared, background_color, current_difficulty
    cursor = saving.cursor()
    if current_difficulty == 0:
        row1 = cursor.execute('SELECT cleared FROM levels_easy WHERE level_number = 1 LIMIT 1').fetchone()
        row2 = cursor.execute('SELECT cleared FROM levels_easy WHERE level_number = 2 LIMIT 1').fetchone()
    elif current_difficulty == 1:
        row1 = cursor.execute('SELECT cleared FROM levels_medium WHERE level_number = 1 LIMIT 1').fetchone()
        row2 = cursor.execute('SELECT cleared FROM levels_medium WHERE level_number = 2 LIMIT 1').fetchone()
    elif current_difficulty == 2:
        row1 = cursor.execute('SELECT cleared FROM levels_hard WHERE level_number = 1 LIMIT 1').fetchone()
        row2 = cursor.execute('SELECT cleared FROM levels_hard WHERE level_number = 2 LIMIT 1').fetchone()
    else:
        row1 = []
        row2 = []
    level1_cleared = bool(row1[0]) if row1 else False
    level2_cleared = bool(row2[0]) if row2 else False
    load_skin()
    # Создаем прямоугольники для кликабельных областей уровней
    level_rects = []
    options = [
        "Уровень 1",
        "Уровень 2",
        "Уровень 3",
        "Уровень 4",
        "Уровень 5",
        "Уровень 6",
        "Уровень 7",
        "Уровень 8",
        "Уровень 9",
    ]

    for j in range(3):  # Первые 3 уровня слева
        level_rects.append(pygame.Rect(W // 3 - 200, H // 3 + j * 70 - 10, 150, 40))
    for j in range(3, 6):  # Следующие 3 уровня посередине
        level_rects.append(
            pygame.Rect(W // 2 - 50, H // 3 + (j - 3) * 70 - 10, 150, 40)
        )
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

        screen.fill(background_color)
        draw_text("Выбор уровня", font_large, (255, 255, 255), screen, W // 2, H // 6)

        # Отрисовка уровней и обработка кликов
        for j, opt in enumerate(options):
            is_hovered = level_rects[j].collidepoint(mouse_pos)
            color = (255, 255, 255) if is_hovered else (0, 0, 0)
            x_pos = (
                W // 3 - 100
                if j < 3
                else (W // 2 if (3 <= j < 6) else W // 3 * 2 + 100)
            )
            if level1_cleared and j == 0:
                color = (255, 255, 255) if is_hovered else (0, 255, 0)
            if level2_cleared and j == 1:
                color = (255, 255, 255) if is_hovered else (0, 255, 0)
            draw_text(opt, font_small, color, screen, x_pos, H // 3 + 20 + (j % 3) * 70)

            if is_hovered and mouse_clicked:
                if j == 0:
                    level_1_part_1()
                elif j == 1 and level1_cleared:
                    level_2_part_1()
                elif j == 2:
                    level_3_part_1()

        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text("Главное меню", font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            main_menu()
            levels_in = False

        pygame.display.flip()
        clock.tick(60)


def upgrade():
    global music_playing, from_menu, from_level, player, unlock_message, \
        unlock_message_time, background_color, player_points_easy, player_points_medium, player_points_hard, \
        current_difficulty, current_player_points
    load_upgrades()
    if current_difficulty == 0:
        current_player_points = player_points_easy
    elif current_difficulty == 1:
        current_player_points = player_points_medium
    elif current_difficulty == 2:
        current_player_points = player_points_hard
    # Создаем прямоугольники для кликабельных областей уровней
    pluses = []
    minuses = []
    options = ["Атака", "HP", "Бег", "Двойной прыжок", "Щит"]
    upgrade_chars = [
        player.attack,
        player.HP,
        player.running_unlocked,
        player.double_jump_unlocked,
        player.shield,
    ]
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

        screen.fill(background_color)
        draw_text("Улучшение", font_large, (255, 255, 255), screen, W // 2, H // 6)

        # Отрисовка уровней и обработка кликов
        for j, opt in enumerate(options):
            is_hovered_pluses = pluses[j].collidepoint(mouse_pos)
            color_pluses = (255, 255, 255) if is_hovered_pluses else (0, 0, 0)
            is_hovered_minuses = minuses[j].collidepoint(mouse_pos)
            color_minuses = (255, 255, 255) if is_hovered_minuses else (0, 0, 0)
            x_pos = W // 3 - 100
            draw_text(opt, font_small, (0, 0, 0), screen, x_pos, H // 3 + 20 + j * 70)
            if j != 2 and j != 3:
                draw_text(
                    "+",
                    font_medium,
                    color_pluses,
                    screen,
                    W // 3 + 60,
                    H // 3 + 20 + j * 70,
                )
                draw_text(
                    "/",
                    font_medium,
                    (0, 0, 0),
                    screen,
                    W // 3 + 100,
                    H // 3 + 20 + j * 70,
                )
                draw_text(
                    "-",
                    font_medium,
                    color_minuses,
                    screen,
                    W // 3 + 140,
                    H // 3 + 20 + j * 70,
                )
            else:
                draw_text(
                    "+",
                    font_medium,
                    color_pluses,
                    screen,
                    W // 3 + 100,
                    H // 3 + 20 + j * 70,
                )
            if opt == "Бег" or opt == "Двойной прыжок":
                if upgrade_chars[j]:
                    draw_text(
                        "Открыт",
                        font_medium,
                        (0, 0, 0),
                        screen,
                        W // 3 + 250,
                        H // 3 + 20 + j * 70,
                    )
                else:
                    draw_text(
                        "Закрыт",
                        font_medium,
                        (0, 0, 0),
                        screen,
                        W // 3 + 250,
                        H // 3 + 20 + j * 70,
                    )
            else:
                draw_text(
                    str(upgrade_chars[j]),
                    font_medium,
                    (0, 0, 0),
                    screen,
                    W // 3 + 250,
                    H // 3 + 20 + j * 70,
                )

            if is_hovered_pluses and mouse_clicked:
                if j == 0:
                    if current_player_points >= 1 and player.attack < 4:
                        if sound_on:
                            Unlock_skin_sound.play()
                        upgrade_chars[j] += 1
                        player.attack += 1
                        current_player_points -= 1
                    elif current_player_points < 1:
                        unlock_message = "Недостаточно очков (минимум 1)"
                        unlock_message_time = pygame.time.get_ticks()
                elif j == 1:
                    if current_player_points >= 1 and player.HP < 10:
                        if sound_on:
                            Unlock_skin_sound.play()
                        upgrade_chars[j] += 1
                        player.HP += 1
                        current_player_points -= 1
                    elif current_player_points < 1:
                        unlock_message = "Недостаточно очков (минимум 1)"
                        unlock_message_time = pygame.time.get_ticks()
                elif j == 2 and not player.running_unlocked:
                    if current_player_points >= 3:
                        if sound_on:
                            Unlock_skin_sound.play()
                        unlock_message = "Открылся скин: Соник"
                        unlock_message_time = pygame.time.get_ticks()
                        upgrade_chars[j] = True
                        player.running_unlocked = True
                        current_player_points -= 3
                    elif current_player_points < 3:
                        unlock_message = "Нужно минимум 3 очка"
                        unlock_message_time = pygame.time.get_ticks()
                elif j == 3 and not player.double_jump_unlocked:
                    if current_player_points >= 4:
                        if sound_on:
                            Unlock_skin_sound.play()
                        unlock_message = "Открылся скин: Марио"
                        unlock_message_time = pygame.time.get_ticks()
                        upgrade_chars[j] = True
                        player.double_jump_unlocked = True
                        current_player_points -= 4
                    elif current_player_points < 4:
                        unlock_message = "Нужно минимум 4 очка"
                        unlock_message_time = pygame.time.get_ticks()
                elif j == 4:
                    if current_player_points >= 3:
                        if sound_on:
                            Unlock_skin_sound.play()
                        upgrade_chars[j] += 1
                        player.shield += 1
                        current_player_points -= 3
                    elif current_player_points < 3:
                        unlock_message = "Нужно минимум 3 очка"
                        unlock_message_time = pygame.time.get_ticks()
                save_upgrades()
                load_upgrades()
            if is_hovered_minuses and mouse_clicked and j != 2 and j != 3:
                if j == 0 and upgrade_chars[j] > 1:
                    if sound_on:
                        Unlock_skin_sound.play()
                    upgrade_chars[j] -= 1
                    player.attack -= 1
                    current_player_points += 1
                elif j == 1 and upgrade_chars[j] > 3:
                    if sound_on:
                        Unlock_skin_sound.play()
                    upgrade_chars[j] -= 1
                    current_player_points += 1
                    player.HP -= 1
                elif j == 4 and upgrade_chars[j] >= 1:
                    if sound_on:
                        Unlock_skin_sound.play()
                    upgrade_chars[j] -= 1
                    current_player_points += 3
                save_upgrades()
                load_upgrades()

        if unlock_message:
            current_time = pygame.time.get_ticks()
            if current_time - unlock_message_time < UNLOCK_MESSAGE_DURATION:
                # Нарисовать прямоугольник с текстом
                message_surface = pygame.Surface((400, 50))
                message_surface.fill((255, 255, 255))
                pygame.draw.rect(message_surface, (0, 0, 0), message_surface.get_rect(), 2)
                # Отрисовка текста
                draw_text(unlock_message,font_small,(0, 0, 0),message_surface,200,25)
                # Разместить поверх экрана по центру
                screen.blit(
                    message_surface,
                    (W // 2 - 200, H // 2 - 25)
                )
            else:
                unlock_message = None  # Сбросить сообщение после времени
        if current_difficulty == 0:
            player_points_easy = current_player_points
        elif current_difficulty == 1:
            player_points_medium = current_player_points
        elif current_difficulty == 2:
            player_points_hard = current_player_points
        save_upgrades()
        # Кнопка "Назад"
        back_hovered = back_rect.collidepoint(mouse_pos)
        back_color = (255, 255, 255) if back_hovered else (0, 0, 0)
        draw_text("Главное меню", font_small, back_color, screen, W // 2, H - 50)

        if back_hovered and mouse_clicked:
            save_upgrades()
            load_upgrades()
            main_menu()
            upgrading = False
        draw_text(
            f"Очки: {current_player_points}", font_small, (255, 255, 255), screen, W - 100, 50
        )
        pygame.display.flip()
        clock.tick(60)


level_part_1 = True
HP = player.HP
Shield = player.shield

# Первая часть уровня
def level_1_part_1():
    global level_part_1, level_1_part_1_scroll_pos, level_1_part_1_in, menu, playing_level, playing_menu, score, level
    portal_rect = portal_image.get_rect(
        center=(level_1_part_1_WIDTH - 200, H - GROUND_H - 45)
    )
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    menu = False
    level_1_part_1_in = True
    playing_menu = False
    playing_level = True
    stop_music()
    play_level_music()
    load_upgrades()
    # Создаем большую поверхность для уровня
    level_surface = pygame.Surface((level_1_part_1_WIDTH, H))
    level_surface.fill((92, 148, 252))  # Основной фон
    level = load_game_sql()
    if level != 1:
        level_1_part_1_scroll_pos = 0
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
                    level = 1
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                if (
                    event.key == pygame.K_w
                    or event.key == pygame.K_UP
                    and player.double_jump_unlocked
                ):
                    player.handle_jump()

        # Очищаем экран
        screen.fill((0, 0, 0))

        # Отрисовываем видимую часть уровня
        screen.blit(level_surface, (0, 0), (level_1_part_1_scroll_pos, 0, W, H))

        # Отрисовываем портал (с учетом скролла)
        screen.blit(
            portal_image, (portal_rect.x - level_1_part_1_scroll_pos, portal_rect.y)
        )

        # Отрисовываем игрока (всегда в центре экрана)
        player.draw(screen)

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )

        if not paused:
            # Обработка ввода и движение
            player.handle_input()
            player.update()
            keys = pygame.key.get_pressed()
            # Обновляем скролл на основе движения игрока
            if (
                player.rect.centerx > W // 2
                and level_1_part_1_scroll_pos < level_1_part_1_WIDTH - W
            ):
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
            if player.rect.colliderect(
                pygame.Rect(
                    portal_rect.x - level_1_part_1_scroll_pos,
                    portal_rect.y,
                    portal_rect.width,
                    portal_rect.height,
                )
            ):
                level_1_part_1_scroll_pos = 3200
                level = 1
                save_game_sql(level)
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


# Вторая часть уровня
def level_1_part_2():
    global monsters, last_spawn_time, spawn_delay, score, level_1_part_1_scroll_pos, \
        HP, from_level, from_menu, playing_menu, Shield, level1_cleared, level2_cleared, Level1, level, \
        current_difficulty, player_points_easy, player_points_medium, player_points_hard, level_1_part_1_in, \
        message, message_time, MESSAGE_DURATION
    load_upgrades()
    HP = player.HP
    Shield = player.shield
    # Обнуляем список врагов и таймеры при входе
    monsters = []
    last_spawn_time = pygame.time.get_ticks()
    message = "Победи 10 врагов"
    message_time = pygame.time.get_ticks()
    player.rect.midbottom = (W // 2, H - GROUND_H)
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    Level1 = True
    invincible = False
    invincible_end_time = 0

    while Level1:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Level1 = False
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
                    level = 1
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif player.is_out:
                    load_game_sql()
                    load_upgrades()
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
        draw_text(
            f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20
        )
        if message:
            current_time = pygame.time.get_ticks()
            if current_time - message_time < MESSAGE_DURATION:
                # Нарисовать прямоугольник с текстом
                message_surface = pygame.Surface((400, 50))
                message_surface.fill((255, 255, 255))
                pygame.draw.rect(message_surface, (0, 0, 0), message_surface.get_rect(), 2)
                # Отрисовка текста
                draw_text(message, font_small, (0, 0, 0), message_surface, 200, 25)
                # Разместить поверх экрана по центру
                screen.blit(
                    message_surface,
                    (W // 2 - 200, H // 2 - 25)
                )
            else:
                message = None
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
                draw_text(
                    "Уровень пройден!",
                    font_small,
                    (255, 255, 255),
                    screen,
                    W // 2,
                    H // 2,
                )
                draw_text(
                    f"Shields: {Shield}",
                    font_large,
                    (255, 255, 255),
                    screen,
                    W // 3 * 2,
                    20,
                )
                level1_cleared = True
                cursor = saving.cursor()
                if current_difficulty == 0:
                    cursor.execute('''
                        UPDATE levels_easy SET cleared=1 WHERE level_number=1
                    ''')
                elif current_difficulty == 1:
                    cursor.execute('''
                        UPDATE levels_medium SET cleared=1 WHERE level_number=1
                    ''')
                elif current_difficulty == 2:
                    cursor.execute('''
                        UPDATE levels_hard SET cleared=1 WHERE level_number=1
                    ''')
                saving.commit()
                pygame.mixer.music.pause()
                pygame.display.flip()
                clock.tick(FPS)

            # Очищаем сохранение и выходим
            cursor = saving.cursor()
            if current_difficulty == 0:
                cursor.execute('DELETE FROM game_progress_easy')
            elif current_difficulty == 1:
                cursor.execute('DELETE FROM game_progress_medium')
            elif current_difficulty == 2:
                cursor.execute('DELETE FROM game_progress_hard')
            if current_difficulty == 0:
                player_points_easy += 3
            elif current_difficulty == 1:
                player_points_medium += 4
            elif current_difficulty == 2:
                player_points_hard += 5
            save_upgrades()
            load_upgrades()
            save_settings_sql()
            pygame.time.wait(2000)
            playing_menu = True
            from_level = True
            from_menu = False
            level_1_part_1_in = False
            print(player_points_easy)
            level_menu()

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )

        if player.is_out:
            draw_text(
                "PRESS ANY KEY", font_small, (255, 255, 255), screen, W // 2, H // 2
            )
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

                        if (
                            player.rect.colliderect(monster.rect)
                            and not monster.is_dead
                        ):
                            if (
                                player.rect.bottom < monster.rect.centery
                                and player.y_speed > 0
                                and abs(player.rect.centerx - monster.rect.centerx)
                                < monster.rect.width / 2
                            ):
                                monster.kill()
                                player.y_speed -= 15
                                player.is_grounded = False
                                player.can_jump = False
                                score += 1
                            elif not monster.damage_given and not invincible:
                                if Shield >= 1:
                                    Shield -= 1
                                    player.shield -= 1
                                    save_upgrades()
                                    load_upgrades()
                                    invincible = True
                                    invincible_end_time = now + 1000
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                                else:
                                    HP -= 1
                                    player.damaged()
                                    monster.damage_given = True
                                    invincible = True
                                    invincible_end_time = (
                                        now + 1000
                                    )  # Устанавливаем время окончания
                                    player.speed = 0
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)

                                if HP <= 0:
                                    player.kill(me_image)
                        else:
                            monster.damage_given = False

        pygame.display.flip()
        clock.tick(FPS)


def level_2_part_1():
    global level_part_1, level_1_part_1_scroll_pos, level_2_part_1_in, menu, playing_level, playing_menu, score, level
    portal_rect = portal_image.get_rect(
        center=(level_1_part_1_WIDTH - 200, H - GROUND_H - 45)
    )
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    menu = False
    level_2_part_1_in = True
    playing_menu = False
    playing_level = True
    stop_music()
    play_level_music()
    load_upgrades()
    # Создаем большую поверхность для уровня
    level_surface = pygame.Surface((level_1_part_1_WIDTH, H))
    level_surface.fill((92, 148, 252))  # Основной фон
    level = load_game_sql()
    if level != 2:
        level_1_part_1_scroll_pos = 0
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
                    level = 2
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                if (
                    event.key == pygame.K_w
                    or event.key == pygame.K_UP
                    and player.double_jump_unlocked
                ):
                    player.handle_jump()

        # Очищаем экран
        screen.fill((0, 0, 0))

        # Отрисовываем видимую часть уровня
        screen.blit(level_surface, (0, 0), (level_1_part_1_scroll_pos, 0, W, H))

        # Отрисовываем портал (с учетом скролла)
        screen.blit(
            portal_image, (portal_rect.x - level_1_part_1_scroll_pos, portal_rect.y)
        )

        # Отрисовываем игрока (всегда в центре экрана)
        player.draw(screen)

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )

        if not paused:
            # Обработка ввода и движение
            player.handle_input()
            player.update()
            keys = pygame.key.get_pressed()
            # Обновляем скролл на основе движения игрока
            if (
                player.rect.centerx > W // 2
                and level_1_part_1_scroll_pos < level_1_part_1_WIDTH - W
            ):
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
            if player.rect.colliderect(
                pygame.Rect(
                    portal_rect.x - level_1_part_1_scroll_pos,
                    portal_rect.y,
                    portal_rect.width,
                    portal_rect.height,
                )
            ):
                level_1_part_1_scroll_pos = 3200
                level = 2
                save_game_sql(level)
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


# Вторая часть уровня
def level_2_part_2():
    global monsters, last_spawn_time, spawn_delay, score, level_1_part_1_scroll_pos, HP, \
        from_level, from_menu, playing_menu, Shield, level2_cleared, level1_cleared, Level2, level, \
        player_points_easy, player_points_medium, player_points_hard, level_2_part_1_in
    load_upgrades()
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
    Level2 = True
    invincible = False
    invincible_end_time = 0

    while Level2:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Level2 = False
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
                    level = 2
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif player.is_out:
                    load_game_sql()
                    load_upgrades()
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
        draw_text(
            f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20
        )

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
                draw_text(
                    "Уровень пройден!",
                    font_small,
                    (255, 255, 255),
                    screen,
                    W // 2,
                    H // 2,
                )
                draw_text(
                    f"Shields: {Shield}",
                    font_large,
                    (255, 255, 255),
                    screen,
                    W // 3 * 2,
                    20,
                )
                level2_cleared = True
                cursor = saving.cursor()
                if current_difficulty == 0:
                    cursor.execute('''
                                        UPDATE levels_easy SET cleared=1 WHERE level_number=2
                                    ''')
                elif current_difficulty == 1:
                    cursor.execute('''
                                        UPDATE levels_medium SET cleared=1 WHERE level_number=2
                                    ''')
                elif current_difficulty == 2:
                    cursor.execute('''
                                        UPDATE levels_hard SET cleared=1 WHERE level_number=2
                                    ''')
                saving.commit()
                pygame.mixer.music.pause()
                pygame.display.flip()
                clock.tick(FPS)

            # Очищаем сохранение и выходим
            cursor = saving.cursor()
            if current_difficulty == 0:
                cursor.execute('DELETE FROM game_progress_easy')
            elif current_difficulty == 1:
                cursor.execute('DELETE FROM game_progress_medium')
            elif current_difficulty == 2:
                cursor.execute('DELETE FROM game_progress_hard')
            if current_difficulty == 0:
                player_points_easy += 3
            elif current_difficulty == 1:
                player_points_medium += 4
            elif current_difficulty == 2:
                player_points_hard += 5
            save_upgrades()
            save_settings_sql()
            pygame.time.wait(2000)
            playing_menu = True
            from_level = True
            from_menu = False
            level_2_part_1_in = False
            level_menu()

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )

        if player.is_out:
            draw_text(
                "PRESS ANY KEY", font_small, (255, 255, 255), screen, W // 2, H // 2
            )
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

                        if (
                            player.rect.colliderect(monster.rect)
                            and not monster.is_dead
                        ):
                            if (
                                player.rect.bottom < monster.rect.centery
                                and player.y_speed > 0
                                and abs(player.rect.centerx - monster.rect.centerx)
                                < monster.rect.width / 2
                            ):
                                monster.kill()
                                player.y_speed -= 15
                                player.is_grounded = False
                                player.can_jump = False
                                score += 1
                            elif not monster.damage_given and not invincible:
                                if Shield >= 1:
                                    Shield -= 1
                                    player.shield -= 1
                                    save_upgrades()
                                    load_upgrades()
                                    invincible = True
                                    invincible_end_time = now + 1000
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                                else:
                                    HP -= 1
                                    player.damaged()
                                    monster.damage_given = True
                                    invincible = True
                                    invincible_end_time = (
                                        now + 1000
                                    )  # Устанавливаем время окончания
                                    player.speed = 0
                                    pygame.time.set_timer(pygame.USEREVENT, 1000)

                                if HP <= 0:
                                    player.kill(me_image)
                        else:
                            monster.damage_given = False

        pygame.display.flip()
        clock.tick(FPS)

def level_3_part_1():
    global level_part_1, level_1_part_1_scroll_pos, level_3_part_1_in, menu, playing_level, playing_menu, score, level
    portal_rect = portal_image.get_rect(
        center=(level_1_part_1_WIDTH - 200, H - GROUND_H - 45)
    )
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    menu = False
    level_3_part_1_in = True
    playing_menu = False
    playing_level = True
    stop_music()
    play_level_music()
    load_upgrades()
    # Создаем большую поверхность для уровня
    level_surface = pygame.Surface((level_1_part_1_WIDTH, H))
    level_surface.fill((92, 148, 252))  # Основной фон
    level = load_game_sql()
    if level != 2:
        level_1_part_1_scroll_pos = 0
    # Рисуем землю
    for x in range(0, level_1_part_1_WIDTH, ground_image.get_width()):
        level_surface.blit(ground_image, (x, H - GROUND_H))

    while level_3_part_1_in:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                level_3_part_1_in = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    level = 3
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                if (
                    event.key == pygame.K_w
                    or event.key == pygame.K_UP
                    and player.double_jump_unlocked
                ):
                    player.handle_jump()

        # Очищаем экран
        screen.fill((0, 0, 0))

        # Отрисовываем видимую часть уровня
        screen.blit(level_surface, (0, 0), (level_1_part_1_scroll_pos, 0, W, H))

        # Отрисовываем портал (с учетом скролла)
        screen.blit(
            portal_image, (portal_rect.x - level_1_part_1_scroll_pos, portal_rect.y)
        )

        # Отрисовываем игрока (всегда в центре экрана)
        player.draw(screen)

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )
        if not paused:
            # Обработка ввода и движение
            player.handle_input()
            player.update()
            keys = pygame.key.get_pressed()
            # Обновляем скролл на основе движения игрока
            if (
                player.rect.centerx > W // 2
                and level_1_part_1_scroll_pos < level_1_part_1_WIDTH - W
            ):
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
            if player.rect.colliderect(
                pygame.Rect(
                    portal_rect.x - level_1_part_1_scroll_pos,
                    portal_rect.y,
                    portal_rect.width,
                    portal_rect.height,
                )
            ):
                level_1_part_1_scroll_pos = 3200
                level = 3
                save_game_sql(level)
                level_part_1 = False
                level_3_part_2()
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

# Вторая часть уровня
def level_3_part_2():
    global monsters, last_spawn_time, spawn_delay, score, level_1_part_1_scroll_pos, HP, \
        from_level, from_menu, playing_menu, Shield, level2_cleared, level1_cleared, Level3, level, \
        player_points_easy, player_points_medium, player_points_hard, level_2_part_1_in, boss
    load_upgrades()
    HP = player.HP
    Shield = player.shield
    player.rect.midbottom = (W // 2, H - GROUND_H)
    save_message_displayed = False
    save_message_timer = 0
    paused = False
    Level3 = True
    boss = Boss()
    invincible = False
    invincible_end_time = 0

    while Level3:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Level3 = False
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
                    level = 3
                    save_game_sql(level)
                    save_message_displayed = True
                    save_message_timer = now
                elif event.key == pygame.K_ESCAPE:
                    pause()
                elif player.is_out:
                    load_game_sql()
                    load_upgrades()
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

        boss.draw(screen)
        player.draw(screen)
        draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
        draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
        draw_text(
            f"Shields: {Shield}", font_large, (255, 255, 255), screen, W // 3 * 2, 20
        )

        if score >= 10:
            # Убиваем всех монстров
            end_time = pygame.time.get_ticks() + 2000  # 2 секунды на завершение

            while pygame.time.get_ticks() < end_time:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Обновляем игрока (чтобы он мог упасть на землю)
                player.handle_input()
                player.update()
                # Отрисовка
                screen.fill((92, 148, 252))
                screen.blit(ground_image, (0, H - GROUND_H))

                player.draw(screen)
                draw_text(str(score), font_large, (255, 255, 255), screen, W // 2, 20)
                draw_text(f"HP: {HP}", font_large, (255, 255, 255), screen, W // 3, 20)
                draw_text(
                    "Уровень пройден!",
                    font_small,
                    (255, 255, 255),
                    screen,
                    W // 2,
                    H // 2,
                )
                draw_text(
                    f"Shields: {Shield}",
                    font_large,
                    (255, 255, 255),
                    screen,
                    W // 3 * 2,
                    20,
                )
                level2_cleared = True
                cursor = saving.cursor()
                if current_difficulty == 0:
                    cursor.execute('''
                                        UPDATE levels_easy SET cleared=1 WHERE level_number=2
                                    ''')
                elif current_difficulty == 1:
                    cursor.execute('''
                                        UPDATE levels_medium SET cleared=1 WHERE level_number=2
                                    ''')
                elif current_difficulty == 2:
                    cursor.execute('''
                                        UPDATE levels_hard SET cleared=1 WHERE level_number=2
                                    ''')
                saving.commit()
                pygame.mixer.music.pause()
                pygame.display.flip()
                clock.tick(FPS)

            # Очищаем сохранение и выходим
            cursor = saving.cursor()
            if current_difficulty == 0:
                cursor.execute('DELETE FROM game_progress_easy')
            elif current_difficulty == 1:
                cursor.execute('DELETE FROM game_progress_medium')
            elif current_difficulty == 2:
                cursor.execute('DELETE FROM game_progress_hard')
            if current_difficulty == 0:
                player_points_easy += 3
            elif current_difficulty == 1:
                player_points_medium += 4
            elif current_difficulty == 2:
                player_points_hard += 5
            save_upgrades()
            save_settings_sql()
            pygame.time.wait(2000)
            playing_menu = True
            from_level = True
            from_menu = False
            level_2_part_1_in = False
            level_menu()

        if save_message_displayed and now - save_message_timer < 2000:
            draw_text(
                "Игра сохранена", font_small, (255, 255, 255), screen, W // 2, H // 2
            )

        if player.is_out:
            draw_text(
                "PRESS ANY KEY", font_small, (255, 255, 255), screen, W // 2, H // 2
            )
        else:
            if not paused:
                player.handle_input()
                player.update()
                if boss.is_out:
                    monsters.remove(boss)
                else:
                    boss.update()
                    if (
                        player.rect.colliderect(boss.rect)
                        and not boss.is_dead
                    ):
                        if (
                            player.rect.bottom < boss.rect.centery
                            and player.y_speed > 0
                            and abs(player.rect.centerx - boss.rect.centerx)
                            < boss.rect.width / 2 and boss.HP > 0
                        ):
                            player.y_speed -= 15
                            player.is_grounded = False
                            player.can_jump = False
                            boss.HP -= 1
                        elif (
                            player.rect.bottom < boss.rect.centery
                            and player.y_speed > 0
                            and abs(player.rect.centerx - boss.rect.centerx)
                            < boss.rect.width / 2 and boss.HP == 0
                        ):
                            boss.kill()
                            player.y_speed -= 15
                            player.is_grounded = False
                            player.can_jump = False
                        elif not boss.damage_given and not invincible:
                            if Shield >= 1:
                                Shield -= 1
                                player.shield -= 1
                                save_upgrades()
                                load_upgrades()
                                invincible = True
                                invincible_end_time = now + 1000
                                pygame.time.set_timer(pygame.USEREVENT, 1000)
                            else:
                                HP -= 1
                                player.damaged()
                                boss.damage_given = True
                                invincible = True
                                invincible_end_time = (
                                    now + 1000
                                )  # Устанавливаем время окончания
                                player.speed = 0
                                pygame.time.set_timer(pygame.USEREVENT, 1000)
                            if HP <= 0:
                                player.kill(me_image)
                    else:
                        boss.damage_given = False

    pygame.display.flip()
    clock.tick(FPS)

# Запуск игры
load_settings_sql()
load_game_sql()
load_skin()
load_upgrades()
music_playing = False
play_menu_music()
main_menu()
pygame.quit()
