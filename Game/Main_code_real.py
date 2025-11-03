# Импорт необходимых библиотек
import random
import sqlite3
import sys
import pygame
from pygame import Surface

pygame.init()

# Настройки игры
font_path = "caviar-dreams.ttf"
try:
    font_large = pygame.font.Font(font_path, 48)
    font_medium = pygame.font.Font(font_path, 36)
    font_small = pygame.font.Font(font_path, 24)
    font_dialogue = pygame.font.Font(font_path, 20)
except:
    font_large = pygame.font.SysFont("arial", 48)
    font_medium = pygame.font.SysFont("arial", 36)
    font_small = pygame.font.SysFont("arial", 24)
    font_dialogue = pygame.font.SysFont("arial", 20)

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
unlock_message = ""

# Секретные предметы и зоны
secret_items_collected = []
secret_points_collected = []
all_secrets_found = False
secret_sound = None
secret_message = None
secret_message_time = 0
SECRET_MESSAGE_DURATION = 3000

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
pygame.display.set_caption("Platformer Game")
FPS = 60
clock = pygame.time.Clock()
GROUND_H = 60

# Загрузка изображений с обработкой ошибок
try:
    ground_image: Surface = pygame.image.load("Sprites and objects/Objects, background and other/2d-Pixel-Grass.png")
    ground_image = pygame.transform.scale(ground_image, (500, GROUND_H))
except:
    ground_image = pygame.Surface((500, GROUND_H))
    ground_image.fill((100, 200, 100))

try:
    me_image = pygame.image.load("Sprites and objects/Skins/Me/Me.png")
    me_image = pygame.transform.scale(me_image, (70, 80))
except:
    me_image = pygame.Surface((70, 80))
    me_image.fill((255, 0, 0))

try:
    portal_image = pygame.image.load("Sprites and objects/Objects, background and other/p2.gif")
    portal_image = pygame.transform.scale(portal_image, (80, 90))
except:
    portal_image = pygame.Surface((80, 90))
    portal_image.fill((0, 255, 255))

try:
    me_damaged_image = pygame.image.load("Sprites and objects/Skins/Me/Me_damaged.png")
    me_damaged_image = pygame.transform.scale(me_damaged_image, (70, 80))
except:
    me_damaged_image = pygame.Surface((70, 80))
    me_damaged_image.fill((200, 0, 0))

# Загрузка изображений для секретных предметов
try:
    secret_coin_image = pygame.image.load("Sprites and objects/Objects, background and other/coin.png")
    secret_coin_image = pygame.transform.scale(secret_coin_image, (30, 30))
except:
    secret_coin_image = pygame.Surface((30, 30))
    secret_coin_image.fill((255, 215, 0))

try:
    secret_star_image = pygame.image.load("Sprites and objects/Objects, background and other/star.png")
    secret_star_image = pygame.transform.scale(secret_star_image, (35, 35))
except:
    secret_star_image = pygame.Surface((35, 35))
    secret_star_image.fill((255, 255, 0))

try:
    secret_heart_image = pygame.image.load("Sprites and objects/Objects, background and other/heart.png")
    secret_heart_image = pygame.transform.scale(secret_heart_image, (35, 35))
except:
    secret_heart_image = pygame.Surface((35, 35))
    secret_heart_image.fill((255, 0, 0))

# Загрузка изображений для катсцен
try:
    parents_image = pygame.image.load("Sprites and objects/Parents/parents.png")
    parents_image = pygame.transform.scale(parents_image, (400, 300))
except:
    parents_image = pygame.Surface((400, 300))
    parents_image.fill((150, 150, 200))

try:
    home_background = pygame.image.load("Sprites and objects/Objects, background and other/home_bg.png")
    home_background = pygame.transform.scale(home_background, (W, H))
except:
    home_background = pygame.Surface((W, H))
    home_background.fill((180, 160, 140))

# Настройки звука
music_on = True
sound_on = True
music_playing = False
menu_music = "Music/day_of_chaos.mp3"
level_1_part_1_music = "Music/kevin-macleod-machine.mp3"
level_2_part_1_music = "Music/Echoes-of-Time-v2(chosic.com).mp3"
level_3_part_1_music = "Music/riding-into-the-sunset-20240527-202603.mp3"
level_4_part_1_music = "Music/Ghost-Story(chosic.com).mp3"
level_5_part_1_music = "Music/Horror-Long-Version(chosic.com).mp3"
level_6_part_1_music = "Music/Starset_-_My_Demons_56774126.mp3"

try:
    Unlock_skin_sound = pygame.mixer.Sound("Sounds/mixkit-unlock-new-item-game-notification-254.wav")
except:
    Unlock_skin_sound = None

# Звук для секретов
try:
    secret_sound = pygame.mixer.Sound("Sounds/mixkit-achievement-bell-600.wav")
except:
    secret_sound = None

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


# Система катсцен
class CutsceneManager:
    def __init__(self):
        self.current_cutscene = None
        self.current_dialogue_index = 0
        self.dialogue_timer = 0
        self.dialogue_speed = 2  # Символов за кадр
        self.current_text = ""
        self.full_text = ""
        self.show_skip_prompt = False
        self.skip_prompt_timer = 0

    def start_cutscene(self, cutscene_data):
        self.current_cutscene = cutscene_data
        self.current_dialogue_index = 0
        self.dialogue_timer = 0
        self.current_text = ""
        self.full_text = ""
        self.show_skip_prompt = False
        self.skip_prompt_timer = 0

        if self.current_cutscene and self.current_dialogue_index < len(self.current_cutscene["dialogues"]):
            self.full_text = self.current_cutscene["dialogues"][self.current_dialogue_index]["text"]

    def update(self):
        if not self.current_cutscene:
            return False

        # Показ подсказки пропуска
        self.skip_prompt_timer += 1
        if self.skip_prompt_timer > 60:  # Показывать через 1 секунду
            self.show_skip_prompt = True

        # Постепенное появление текста
        if len(self.current_text) < len(self.full_text):
            self.dialogue_timer += 1
            if self.dialogue_timer >= self.dialogue_speed:
                self.dialogue_timer = 0
                self.current_text = self.full_text[:len(self.current_text) + 1]

        return True

    def next_dialogue(self):
        if not self.current_cutscene:
            return False

        self.current_dialogue_index += 1
        if self.current_dialogue_index < len(self.current_cutscene["dialogues"]):
            self.current_text = ""
            self.full_text = self.current_cutscene["dialogues"][self.current_dialogue_index]["text"]
            return True
        else:
            self.current_cutscene = None
            return False

    def skip(self):
        if self.current_cutscene and self.current_dialogue_index < len(self.current_cutscene["dialogues"]):
            # Показываем весь текст текущей реплики
            self.current_text = self.full_text

    def finish_current(self):
        if self.current_cutscene and self.current_dialogue_index < len(self.current_cutscene["dialogues"]):
            if len(self.current_text) < len(self.full_text):
                # Показываем весь текст текущей реплики
                self.current_text = self.full_text
                return True
            else:
                # Переходим к следующей реплике
                return self.next_dialogue()
        return False

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw(self, screen):
        if not self.current_cutscene:
            return

        # Фон катсцены
        if self.current_cutscene["background"]:
            screen.blit(self.current_cutscene["background"], (0, 0))
        else:
            screen.fill((0, 0, 0))

        # Текущий диалог
        dialogue = self.current_cutscene["dialogues"][self.current_dialogue_index]

        # Отрисовка персонажа (если есть)
        if dialogue.get("character_image"):
            char_img = dialogue["character_image"]
            char_rect = char_img.get_rect(center=(W // 2, H // 3))
            screen.blit(char_img, char_rect)

        # Окно диалога
        dialog_rect = pygame.Rect(50, H - 200, W - 100, 150)
        pygame.draw.rect(screen, (0, 0, 0, 180), dialog_rect)
        pygame.draw.rect(screen, (255, 255, 255), dialog_rect, 2)

        # Имя персонажа
        name_text = font_dialogue.render(dialogue["character"], True, (255, 215, 0))
        screen.blit(name_text, (dialog_rect.x + 20, dialog_rect.y + 15))

        # Текст диалога
        text_lines = self.wrap_text(self.current_text, font_dialogue, dialog_rect.width - 40)
        for i, line in enumerate(text_lines):
            text_surface = font_dialogue.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (dialog_rect.x + 20, dialog_rect.y + 50 + i * 30))

        # Индикатор продолжения (если весь текст показан)
        if len(self.current_text) >= len(self.full_text):
            continue_text = font_small.render("Нажмите ПРОБЕЛ для продолжения...", True, (200, 200, 200))
            screen.blit(continue_text, (dialog_rect.centerx - continue_text.get_width() // 2, dialog_rect.bottom - 30))

        # Подсказка пропуска
        if self.show_skip_prompt:
            skip_text = font_small.render("Нажмите ESC для пропуска катсцены", True, (150, 150, 150))
            screen.blit(skip_text, (W - skip_text.get_width() - 20, 20))


# Создаем менеджер катсцен
cutscene_manager = CutsceneManager()

# Определяем катсцены
cutscenes = {
    "intro": {
        "background": home_background,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": parents_image,
                "text": "Мне родители только мешают! Я пытаюсь жить и радоваться жизни! "
                        "А им лишь бы меня ругать и заставлять что-то делать!..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "'Я всегда виноват', да?! 'Плохо себя веду и вообще я плохой'! Ничего они не понимают!"
            },
            {
                "character": "",
                "character_image": None,
                "text": "*Я захожу к себе в спальню, пиная дверь, и ложусь на кровать с ужасным настроением*"
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Сон - единственное место, где никто, ничего и никогда не скажет плохого мне в лицо..."
            }
        ]
    },
    "level1_complete": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Помнишь, как мы ездили на озеро тем летом? Папа учил меня плавать... Мама готовила бутерброды..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Тогда все было проще. Они ссорились и тогда, но всегда мирились к вечеру... Почему сейчас все по-другому?"
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Может быть... Может быть, они просто устали? Взрослые ведь тоже иногда ломаются..."
            }
        ]
    },
    "level2_complete": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Первые соревнования по плаванию... Мама шептала мне перед началом: 'Ты сможешь, я в тебя верю'..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Мама плакала от гордости у бассейна. После объявления у меня 1-го места она обняла меня так крепко..."
                        "Папа тоже..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Они всегда верили в меня... Даже когда я сам в себя не верил. А я... я перестал верить в них."
            }
        ]
    },
    "level3_complete": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Тот день, когда папа потерял работу... Я видел, как он плакал в гараже. Думал, я не заметил..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Мама взяла вторую работу. Они перестали разговаривать за ужином... А я злился на них за это."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Но сейчас я понимаю... Они не злые. Они просто сломленные. И им тоже больно."
            }
        ]
    },
    "boss_defeated": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Страх... Гнев... Одиночество... Эти монстры в моих снах - это же мои же эмоции."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Я так долго носил в себе эту злость на них... Думал, они специально разрушают нашу семью."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Но они просто люди... Со своими слабостями, страхами, неудачами. Как и я."
            }
        ]
    },
    "level4_complete": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Помнишь наши субботние завтраки? Мама готовила оладьи, папа рассказывал смешные истории..."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Иногда он задерживался на работе, и мама грустила... Но когда он возвращался, она снова улыбалась."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Они всегда находили способ быть вместе... Даже когда было трудно. Может, и сейчас найдут?"
            }
        ]
    },
    "level5_complete": {
        "background": None,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Тот вечер, когда я заболел... Мама не отходила от моей кровати всю ночь."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "В самые трудные моменты они всегда были рядом... А сейчас их трудный момент. И где же я?"
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Я прячусь в своих снах... В своих обидах... А им, наверное, так же страшно и одиноко, как мне."
            }
        ]
    },
    "game_complete": {
        "background": home_background,
        "dialogues": [
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Эти сны... Они не просто воспоминания. Они напоминали мне, кто мы на самом деле. Семья."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Не идеальная, не всегда счастливая... Но настоящая. Со своими ранами и шрамами, но и с любовью тоже."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Папа не злой... Он напуган. Мама не холодная... Она устала. А я... я был слеп."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Завтра утром я подойду к ним. Просто обниму. Скажу, что люблю их. Несмотря ни на что."
            },
            {
                "character": "Внутренний голос",
                "character_image": None,
                "text": "Потому что семья - это не когда все идеально. Семья - это когда прощают, даже когда больно."
            }
        ]
    },
    "final_awakening": {
        "background": home_background,
        "dialogues": [
            {
                "character": "Мама",
                "character_image": parents_image,
                "text": "Сынок?..."
            },
            {
                "character": "Папа",
                "character_image": parents_image,
                "text": "Сын..., прости..., я накричал на тебя..."
            },
            {
                "character": "Главный герой",
                "character_image": None,
                "text": "Я вас понимаю... И я вас люблю. Мы справимся. Вместе."
            },
            {
                "character": "Мама",
                "character_image": parents_image,
                "text": "*обнимает* Мы тоже тебя любим, солнышко. Больше всего на свете."
            },
            {
                "character": "Папа",
                "character_image": parents_image,
                "text": "Да... Вместе. Как раньше. Мы найдем выход. Главное, что у нас есть ты."
            }
        ]
    }
}


# Класс для управления уровнями
def save_secret_points():
    global secret_points_collected
    """Сохраняет секреты с очками в базу данных для текущей сложности"""
    cursor = saving.cursor()
    table_name = f"secret_points_{['easy', 'medium', 'hard'][current_difficulty]}"
    cursor.execute(f'DELETE FROM {table_name}')
    for point_id in secret_points_collected:
        cursor.execute(f'INSERT INTO {table_name} (point_id, collected) VALUES (?, ?)', (point_id, 1))
    saving.commit()


def load_secret_points():
    """Загружает секреты с очками из базы данных для текущей сложности"""
    global secret_points_collected
    cursor = saving.cursor()
    table_name = f"secret_points_{['easy', 'medium', 'hard'][current_difficulty]}"
    cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                point_id TEXT PRIMARY KEY, 
                collected INTEGER
            )
        ''')
    cursor.execute(f'SELECT point_id FROM {table_name}')
    results = cursor.fetchall()
    secret_points_collected = [row[0] for row in results]


class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.levels = {
            1: {
                "name": "Уровень 1",
                "width": 5000,
                "music": level_1_part_1_music,
                "bg_gradient": [(92, 148, 252), (45, 85, 205), (30, 144, 255)],
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
                "enemy_count": 10,
                "secret_rooms": [
                    {
                        "rect": pygame.Rect(4000, 300, 50, 50),
                        "type": "hidden",
                        "required_ability": None,
                        "reward": "points",
                        "value": 5,
                        "found": False,
                        "message": "Найдена скрытая комната! +5 очков",
                        "image": secret_coin_image
                    },
                    {
                        "rect": pygame.Rect(4900, 650, 60, 60),
                        "type": "breakable",
                        "required_ability": None,
                        "reward": "item",
                        "value": "secret_coin_1",
                        "found": False,
                        "message": "Найден секретный предмет: Золотая монета!",
                        "image": secret_coin_image
                    }
                ]
            },
            2: {
                "name": "Уровень 2",
                "width": 5000,
                "music": level_2_part_1_music,
                "bg_gradient": [(186, 85, 211), (153, 50, 204), (106, 13, 173)],
                "platforms": [
                    pygame.Rect(150, 630, 120, 20),
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
                "enemy_count": 15,
                "secret_rooms": [
                    {
                        "rect": pygame.Rect(1200, 200, 60, 60),
                        "type": "breakable",
                        "required_ability": "running",
                        "reward": "item",
                        "value": "secret_star_1",
                        "found": False,
                        "message": "Найден секретный предмет: Сияющая звезда!",
                        "image": secret_star_image
                    }
                ]
            },
            3: {
                "name": "Уровень 3",
                "width": 5000,
                "music": level_3_part_1_music,
                "bg_gradient": [(148, 150, 92), (107, 142, 35), (154, 205, 50)],
                "has_boss": True,
                "enemy_count": 1,
                "secret_rooms": []
            },
            4: {
                "name": "Уровень 4",
                "width": 5000,
                "music": level_4_part_1_music,
                "bg_gradient": [(150, 150, 150), (42, 81, 189), (13, 90, 205)],
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
                    pygame.Rect(4200, 440, 140, 20)
                ],
                "has_boss": False,
                "enemy_count": 20,
                "secret_rooms": [
                    {
                        "rect": pygame.Rect(2500, 100, 70, 70),
                        "type": "hidden",
                        "required_ability": "double_jump",
                        "reward": "easter_egg",
                        "value": "sonic_reference",
                        "found": False,
                        "message": "Пасхалка: Отсылка к Starset!",
                        "image": secret_star_image
                    }
                ]
            },
            5: {
                "name": "Уровень 5",
                "width": 5000,
                "music": level_5_part_1_music,
                "bg_gradient": [(100, 100, 150), (135, 206, 235), (176, 224, 230)],
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
                ],
                "has_boss": False,
                "enemy_count": 20,
                "secret_rooms": [
                    {
                        "rect": pygame.Rect(3200, 150, 65, 65),
                        "type": "breakable",
                        "required_ability": "double_jump",
                        "reward": "points",
                        "value": 10,
                        "found": False,
                        "message": "Секретная сокровищница! +10 очков",
                        "image": secret_coin_image
                    },
                    {
                        "rect": pygame.Rect(4000, 100, 80, 80),
                        "type": "hidden",
                        "required_ability": "running",
                        "reward": "easter_egg",
                        "value": "mario_reference",
                        "found": False,
                        "message": "Пасхалка: Время Марио!",
                        "image": secret_star_image
                    }
                ]
            },
            6: {
                "name": "Уровень 6",
                "width": 5000,
                "music": level_6_part_1_music,
                "bg_gradient": [(100, 100, 150), (178, 34, 34), (220, 20, 60)],
                "has_boss": True,
                "enemy_count": 1,
                "secret_rooms": []
            }
        }
        self.scroll_pos = 0
        self.level_surface = None
        self.portal_rect = None
        self.gradient_cache = {}

    def load_level(self, level_num):
        if level_num in self.levels:
            self.current_level = level_num
            self.scroll_pos = 0
            level_data = self.levels[level_num]

            # Загружаем прогресс секретных комнат для текущей сложности
            self.load_secret_progress(level_num)

            # Создаем поверхность для уровня с градиентом
            self.level_surface = pygame.Surface((level_data["width"], H))

            # Создаем градиентный фон
            if "bg_gradient" in level_data:
                gradient_key = f"{level_num}_{level_data['width']}_{H}"
                if gradient_key not in self.gradient_cache:
                    self.gradient_cache[gradient_key] = create_gradient_surface(
                        level_data["width"], H, level_data["bg_gradient"]
                    )
                self.level_surface.blit(self.gradient_cache[gradient_key], (0, 0))
            else:
                # Фулбэк на старый цвет, если градиента нет
                self.level_surface.fill(level_data.get("bg_color", (92, 148, 252)))

            # Рисуем землю (остальной код без изменений)
            if level_num == 1:
                for x in range(0, 1800, ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
                for x in range(2200, level_data["width"], ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
            elif level_num == 2 or level_num == 4 or level_num == 5:
                for x in range(0, 800, ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
                for x in range(4100, level_data["width"], ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))
            else:
                for x in range(0, level_data["width"], ground_image.get_width()):
                    self.level_surface.blit(ground_image, (x, H - GROUND_H))

            # Создаем портал (без изменений)
            self.portal_rect = portal_image.get_rect(center=(level_data["width"] - 200, H - GROUND_H - 45))

            # Загружаем музыку уровня (без изменений)
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

        # Отрисовываем секретные комнаты (если не найдены)
        if self.current_level in self.levels:
            for secret in self.levels[self.current_level]["secret_rooms"]:
                if not secret["found"]:
                    secret_rect_on_screen = secret["rect"].move(-self.scroll_pos, 0)

                    # Визуализация секретной комнаты
                    if secret["type"] == "hidden":
                        # Скрытые комнаты - полупрозрачные
                        secret_surface = pygame.Surface((secret_rect_on_screen.width, secret_rect_on_screen.height),
                                                        pygame.SRCALPHA)
                        secret_surface.fill((255, 255, 255, 100))  # Полупрозрачный белый
                        screen_0.blit(secret_surface, secret_rect_on_screen)
                        pygame.draw.rect(screen_0, (255, 255, 0, 150), secret_rect_on_screen, 2)
                    elif secret["type"] == "breakable":
                        # Разрушаемые стены - коричневые
                        pygame.draw.rect(screen_0, (101, 67, 33), secret_rect_on_screen)
                        pygame.draw.rect(screen_0, (139, 69, 19), secret_rect_on_screen, 2)

                    # Отрисовываем иконку награды
                    if "image" in secret:
                        img_rect = secret["image"].get_rect(center=secret_rect_on_screen.center)
                        screen_0.blit(secret["image"], img_rect)

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

        # Временно сбрасываем статус
        player_0.is_grounded = False

        for platform in self.levels[self.current_level]["platforms"]:
            platform_on_screen = platform.move(-self.scroll_pos, 0)

            # Улучшенная проверка коллизии сверху
            if (player_0.rect.right > platform_on_screen.left + 10 and
                    player_0.rect.left < platform_on_screen.right - 10 and
                    platform_on_screen.top <= player_0.rect.bottom <= platform_on_screen.top + 15 and  # Более широкая зона обнаружения
                    player_0.y_speed >= 0):
                player_0.rect.bottom = platform_on_screen.top
                player_0.y_speed = 0
                player_0.is_grounded = True
                player_0.jump_count = 0
                break  # Важно: выходим после первой успешной коллизии

        # Если не на платформе, проверяем основную землю
        if not player_0.is_grounded and player_0.rect.bottom >= H - GROUND_H:  # Исправлено: убрали лишнюю букву
            if level_num == 1:
                if not (1505 < self.scroll_pos < 1690):  # Исправлено: self.scroll_pos вместо level_manager.scroll_pos
                    player_0.rect.bottom = H - GROUND_H
                    player_0.y_speed = 0
                    player_0.is_grounded = True
                    player_0.jump_count = 0
                elif 1505 < self.scroll_pos < 1690 and player_0.rect.bottom > H:
                    player_0.kill(me_image)
                else:
                    player_0.is_grounded = False  # Исправлено: убрали лишнюю букву
            elif level_num == 2 or level_num == 4 or level_num == 5:
                if not (505 < self.scroll_pos < 3600):  # Исправлено: self.scroll_pos вместо level_manager.scroll_pos
                    player_0.rect.bottom = H - GROUND_H
                    player_0.y_speed = 0
                    player_0.is_grounded = True
                    player_0.jump_count = 0
                elif 505 < self.scroll_pos < 3600 and player_0.rect.bottom > H:
                    player_0.kill(me_image)
                else:
                    player_0.is_grounded = False  # Исправлено: убрали лишнюю букву
            else:
                player_0.rect.bottom = H - GROUND_H
                player_0.y_speed = 0
                player_0.is_grounded = True
                player_0.jump_count = 0

    def check_secret_rooms(self, player_rect):
        global secret_items_collected, secret_points_collected, player_points_easy, player_points_medium, player_points_hard, player, secret_message, secret_message_time

        if self.current_level not in self.levels:
            return False

        level_data = self.levels[self.current_level]
        secret_found = False
        first_secret_found = False

        for secret in level_data["secret_rooms"]:
            # Пропускаем пустые или неполные секреты
            if not secret or "rect" not in secret:
                continue

            if secret["found"]:
                continue

            # Проверяем требования к способностям
            if secret["required_ability"] == "double_jump" and not player.double_jump_unlocked:
                continue
            if secret["required_ability"] == "running" and not player.running_unlocked:
                continue

            # Проверяем коллизию с игроком
            secret_rect_on_screen = secret["rect"].move(-self.scroll_pos, 0)
            if player_rect.colliderect(secret_rect_on_screen):
                secret["found"] = True
                secret_found = True

                # Проверяем, это первый найденный секрет
                if len(secret_items_collected) == 0 and len(secret_points_collected) == 0 and secret["reward"] in [
                    "item", "easter_egg"]:
                    first_secret_found = True

                # Воспроизводим звук
                if sound_on and secret_sound:
                    secret_sound.play()

                # Выдаем награду
                if secret["reward"] == "points":
                    points = secret["value"]
                    if current_difficulty == 0:
                        player_points_easy += points
                    elif current_difficulty == 1:
                        player_points_medium += points
                    elif current_difficulty == 2:
                        player_points_hard += points

                    # Сохраняем ID секрета с очками
                    secret_id = f"points_{self.current_level}_{secret['rect'].x}_{secret['rect'].y}"
                    if secret_id not in secret_points_collected:
                        secret_points_collected.append(secret_id)

                    secret_message = secret["message"]

                elif secret["reward"] == "item":
                    if secret["value"] not in secret_items_collected:
                        secret_items_collected.append(secret["value"])
                    secret_message = secret["message"]

                elif secret["reward"] == "easter_egg":
                    if secret["value"] not in secret_items_collected:
                        secret_items_collected.append(secret["value"])
                    secret_message = secret["message"]

                # Добавляем специальное сообщение для первого секрета
                if first_secret_found:
                    secret_message += " Раздел 'Секреты' теперь открыт!"

                secret_message_time = pygame.time.get_ticks()

                # Сохраняем прогресс
                self.save_secret_progress()
                save_upgrades()
                save_secret_items()  # Сохраняем сразу при нахождении
                save_secret_points()  # Сохраняем секреты с очками
                load_secret_items()
                load_secret_points()

                if check_all_secrets_found(current_difficulty):
                    # Разблокируем скин "Искатель секретов" только для текущей сложности
                    for skin in skins:
                        if skin["name"] == "Искатель секретов":
                            if not skin["unlocked"]:  # Только если скин еще не был разблокирован
                                skin["unlocked"] = True
                                save_unlocked_skins()
                                # Специальное сообщение с поздравлением
                                secret_message = ("ПОЗДРАВЛЯЕМ! Вы нашли ВСЕ секреты на этой сложности!\n"
                                                  "Разблокирован эксклюзивный скин 'Искатель секретов'!")
                                secret_message_time = pygame.time.get_ticks()
                                # Воспроизводим специальный звук, если есть
                                if sound_on and secret_sound:
                                    secret_sound.play()

        return secret_found

    def save_secret_progress(self):
        cursor = saving.cursor()

        # Создаем таблицу для секретов с учетом сложности, если её нет
        difficulty_suffix = ['_easy', '_medium', '_hard'][current_difficulty]
        table_name = f"secrets{difficulty_suffix}"

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                level_number INTEGER,
                secret_index INTEGER,
                found INTEGER,
                PRIMARY KEY (level_number, secret_index)
            )
        ''')

        # Сохраняем найденные секретные комнаты для текущей сложности
        for level_num, level_data in self.levels.items():
            for x, secret in enumerate(level_data["secret_rooms"]):
                cursor.execute(f'''
                    INSERT OR REPLACE INTO {table_name} 
                    (level_number, secret_index, found) 
                    VALUES (?, ?, ?)
                ''', (level_num, x, int(secret["found"])))

        saving.commit()

    def load_secret_progress(self, level_num):
        cursor = saving.cursor()

        # Создаем таблицу для секретов с учетом сложности, если её нет
        difficulty_suffix = ['_easy', '_medium', '_hard'][current_difficulty]
        table_name = f"secrets{difficulty_suffix}"

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                level_number INTEGER,
                secret_index INTEGER,
                found INTEGER,
                PRIMARY KEY (level_number, secret_index)
            )
        ''')

        # Загружаем прогресс для текущего уровня и сложности
        cursor.execute(f'''
            SELECT secret_index, found FROM {table_name} 
            WHERE level_number = ?
        ''', (level_num,))

        results = cursor.fetchall()

        # Сначала сбрасываем все секреты на уровне как не найденные
        if level_num in self.levels:
            for secret in self.levels[level_num]["secret_rooms"]:
                secret["found"] = False

        # Затем применяем сохраненные данные
        for secret_index, found in results:
            if (level_num in self.levels and
                    secret_index < len(self.levels[level_num]["secret_rooms"])):
                self.levels[level_num]["secret_rooms"][secret_index]["found"] = bool(found)

    def get_level_secrets_count(self, level_num):
        """Возвращает количество секретов на уровне"""
        if level_num in self.levels:
            # Фильтруем только реальные секреты (не пустые словари)
            real_secrets = [secret for secret in self.levels[level_num]["secret_rooms"]
                            if secret and "rect" in secret]
            return len(real_secrets)
        return 0

    def get_found_secrets_count(self, level_num):
        """Возвращает количество найденных секретов на уровне для текущей сложности"""
        if level_num in self.levels:
            # Фильтруем только реальные секреты
            real_secrets = [secret for secret in self.levels[level_num]["secret_rooms"]
                            if secret and "rect" in secret and secret.get("found", False)]
            return len(real_secrets)
        return 0

    # Обновите функцию reset_all_secrets для сброса и секретов с очками:
    def reset_all_secrets(self):
        """Полностью сбрасывает все секретные комнаты для ТЕКУЩЕЙ сложности"""
        # Сбрасываем секреты в памяти только для текущей сложности
        for level_num, level_data in self.levels.items():
            for secret in level_data["secret_rooms"]:
                secret["found"] = False

        # Сбрасываем массивы секретов
        secret_items_collected.clear()
        secret_points_collected.clear()

        # Сбрасываем прогресс в базе данных только для текущей сложности
        cursor = saving.cursor()
        difficulty_suffix = ['_easy', '_medium', '_hard'][current_difficulty]

        # Сбрасываем таблицы секретов
        cursor.execute(f'DELETE FROM secrets{difficulty_suffix}')
        cursor.execute(f'DELETE FROM secret_items{difficulty_suffix}')
        cursor.execute(f'DELETE FROM secret_points{difficulty_suffix}')

        # БЛОКИРУЕМ СКИН "ИСКАТЕЛЬ СЕКРЕТОВ" ТОЛЬКО ДЛЯ ТЕКУЩЕЙ СЛОЖНОСТИ
        skins_table = f"unlocked_skins_{['easy', 'medium', 'hard'][current_difficulty]}"
        cursor.execute(f'UPDATE {skins_table} SET unlocked = 0 WHERE skin_name = "Искатель секретов"')

        saving.commit()


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

        # Таблицы для скинов для каждой сложности
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS skins_{difficulty} (
                id INTEGER PRIMARY KEY,
                current_skin_index INTEGER
            )
        ''')

        # Инициализация скина по умолчанию для каждой сложности
        cursor.execute(f'''
            INSERT OR IGNORE INTO skins_{difficulty} (id, current_skin_index) 
            VALUES (1, 0)
        ''')

    # Таблицы для секретных предметов для каждой сложности
    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS secret_items_{difficulty} (
                item_id TEXT PRIMARY KEY,
                collected INTEGER
            )
        ''')

    # Таблицы для секретов с очками для каждой сложности
    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS secret_points_{difficulty} (
                point_id TEXT PRIMARY KEY,
                collected INTEGER
            )
        ''')

    # Таблицы для статуса разблокировки скинов для каждой сложности
    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS unlocked_skins_{difficulty} (
                skin_name TEXT PRIMARY KEY,
                unlocked INTEGER
            )
        ''')

        # Инициализация стандартных скинов для каждой сложности
        default_skins = ["Классика", "Потерянный", "Селена", "Мона"]
        for skin_name in default_skins:
            cursor.execute(f'''
                INSERT OR IGNORE INTO unlocked_skins_{difficulty} (skin_name, unlocked) 
                VALUES (?, ?)
            ''', (skin_name, 1))

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
        "img": pygame.Surface((40, 50)),
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
    {
        "name": "Фредди",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Freddy the bear/Freddy.png",
        "walk_right": [
            "Sprites and objects/Skins/Freddy the bear/Freddy_right1.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_right2.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_right3.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Freddy the bear/Freddy_left1.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_left2.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_left3.png",
            "Sprites and objects/Skins/Freddy the bear/Freddy_left4.png",
        ],
        "unlock": 'Нужно 2 очка уровней',
        "damaged": "Sprites and objects/Skins/Freddy the bear/Freddy_damaged.png",
        "img": pygame.Surface((90, 50)),
    },
    {
        "name": "Линк",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Link/Link.png",
        "walk_right": [
            "Sprites and objects/Skins/Link/Link_right1.png",
            "Sprites and objects/Skins/Link/Link_right2.png",
            "Sprites and objects/Skins/Link/Link_right3.png",
            "Sprites and objects/Skins/Link/Link_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Link/Link_left1.png",
            "Sprites and objects/Skins/Link/Link_left2.png",
            "Sprites and objects/Skins/Link/Link_left3.png",
            "Sprites and objects/Skins/Link/Link_left4.png",
        ],
        "unlock": 'Нужно 3 очка уровней',
        "damaged": "Sprites and objects/Skins/Link/Link_damaged.png",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Рэд",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Red/Red.png",
        "walk_right": [
            "Sprites and objects/Skins/Red/Red_right1.png",
            "Sprites and objects/Skins/Red/Red_right2.png",
            "Sprites and objects/Skins/Red/Red_right3.png",
            "Sprites and objects/Skins/Red/Red_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Red/Red_left1.png",
            "Sprites and objects/Skins/Red/Red_left2.png",
            "Sprites and objects/Skins/Red/Red_left3.png",
            "Sprites and objects/Skins/Red/Red_left4.png",
        ],
        "unlock": 'Нужно 4 очка уровней',
        "damaged": "Sprites and objects/Skins/Red/Red_damaged.png",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Пикачу",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Pikachu/Pikachu.png",
        "walk_right": [
            "Sprites and objects/Skins/Pikachu/Pikachu_right1.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_right2.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_right3.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Pikachu/Pikachu_left1.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_left2.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_left3.png",
            "Sprites and objects/Skins/Pikachu/Pikachu_left4.png",
        ],
        "unlock": 'Нужно 3 очка уровней',
        "damaged": "Sprites and objects/Skins/Pikachu/Pikachu_damaged.png",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Искатель секретов",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Golden Freddy/Golden_Freddy.png",
        "walk_right": [
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_right1.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_right2.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_right3.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_left1.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_left2.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_left3.png",
            "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_left4.png",
        ],
        "unlock": "Найдите все секретные зоны в игре",
        "damaged": "Sprites and objects/Skins/Golden Freddy/Golden_Freddy_damaged.png",
        "img": pygame.Surface((90, 50)),
    },
    {
        "name": "Бронзовый герой",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Bronze/Bronze_hero.png",
        "walk_right": [
            "Sprites and objects/Skins/Bronze/Bronze_right1.png",
            "Sprites and objects/Skins/Bronze/Bronze_right2.png",
            "Sprites and objects/Skins/Bronze/Bronze_right3.png",
            "Sprites and objects/Skins/Bronze/Bronze_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Bronze/Bronze_left1.png",
            "Sprites and objects/Skins/Bronze/Bronze_left2.png",
            "Sprites and objects/Skins/Bronze/Bronze_left3.png",
            "Sprites and objects/Skins/Bronze/Bronze_left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Bronze/Bronze_damaged.png",
        "unlock": "Пройти все уровни на ЛЁГКОЙ сложности",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Чемпион",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Silver/Silver_champion.png",
        "walk_right": [
            "Sprites and objects/Skins/Silver/Silver_right1.png",
            "Sprites and objects/Skins/Silver/Silver_right2.png",
            "Sprites and objects/Skins/Silver/Silver_right3.png",
            "Sprites and objects/Skins/Silver/Silver_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Silver/Silver_left1.png",
            "Sprites and objects/Skins/Silver/Silver_left2.png",
            "Sprites and objects/Skins/Silver/Silver_left3.png",
            "Sprites and objects/Skins/Silver/Silver_left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Silver/Silver_damaged.png",
        "unlock": "Пройти все уровни на СРЕДНЕЙ сложности",
        "img": pygame.Surface((40, 50)),
    },
    {
        "name": "Золотой легенда",
        "unlocked": False,
        "image": "Sprites and objects/Skins/Gold/Gold_legend.png",
        "walk_right": [
            "Sprites and objects/Skins/Gold/Gold_right1.png",
            "Sprites and objects/Skins/Gold/Gold_right2.png",
            "Sprites and objects/Skins/Gold/Gold_right3.png",
            "Sprites and objects/Skins/Gold/Gold_right4.png",
        ],
        "walk_left": [
            "Sprites and objects/Skins/Gold/Gold_left1.png",
            "Sprites and objects/Skins/Gold/Gold_left2.png",
            "Sprites and objects/Skins/Gold/Gold_left3.png",
            "Sprites and objects/Skins/Gold/Gold_left4.png",
        ],
        "damaged": "Sprites and objects/Skins/Gold/Gold_damaged.png",
        "unlock": "Пройти все уровни на СЛОЖНОЙ сложности",
        "img": pygame.Surface((40, 50)),
    }
]

# Загрузка изображений скинов
for skin in skins:
    try:
        img = pygame.image.load(skin["image"])
        skin["img"] = pygame.transform.scale(img, (40, 50))
    except:
        # Создаем placeholder цвет в зависимости от типа скина
        if "Бронзовый" in skin["name"]:
            skin["img"] = pygame.Surface((40, 50))
            skin["img"].fill((205, 127, 50))  # Бронзовый цвет
        elif "Серебряный" in skin["name"]:
            skin["img"] = pygame.Surface((40, 50))
            skin["img"].fill((192, 192, 192))  # Серебряный цвет
        elif "Золотой" in skin["name"]:
            skin["img"] = pygame.Surface((40, 50))
            skin["img"].fill((255, 215, 0))  # Золотой цвет
        else:
            skin["img"] = pygame.Surface((40, 50))

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

running_sprites_right_boss_2 = []
running_sprites_left_boss_2 = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Speed/Koopa_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Speed/Koopa_left_{i}.png")
        running_sprites_right_boss_2.append(pygame.transform.scale(img_right, (140, 140)))
        running_sprites_left_boss_2.append(pygame.transform.scale(img_left, (140, 140)))
    except:
        running_sprites_right_boss_2.append(pygame.Surface((140, 140)))
        running_sprites_left_boss_2.append(pygame.Surface((140, 140)))

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

running_sprites_enemy_right_2 = []
running_sprites_enemy_left_2 = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Speed/Koopa_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Speed/Koopa_left_{i}.png")
        running_sprites_enemy_right_2.append(pygame.transform.scale(img_right, (90, 90)))
        running_sprites_enemy_left_2.append(pygame.transform.scale(img_left, (90, 90)))
    except:
        running_sprites_enemy_right_2.append(pygame.Surface((90, 90)))
        running_sprites_enemy_left_2.append(pygame.Surface((90, 90)))

# Анимации для дамагера
running_sprites_damager_right = []
running_sprites_damager_left = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Damager/Doomba_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Damager/Doomba_left_{i}.png")
        running_sprites_damager_right.append(pygame.transform.scale(img_right, (90, 90)))
        running_sprites_damager_left.append(pygame.transform.scale(img_left, (90, 90)))
    except:
        running_sprites_damager_right.append(pygame.Surface((90, 90)))
        running_sprites_damager_left.append(pygame.Surface((90, 90)))

# Анимации для прыгуна
running_sprites_jumper_right = []
running_sprites_jumper_left = []
for i in range(1, 4):
    try:
        img_right = pygame.image.load(f"Sprites and objects/Enemies/Jumper/Jumper_right_{i}.png")
        img_left = pygame.image.load(f"Sprites and objects/Enemies/Jumper/Jumper_left_{i}.png")
        running_sprites_jumper_right.append(pygame.transform.scale(img_right, (90, 90)))
        running_sprites_jumper_left.append(pygame.transform.scale(img_left, (90, 90)))
    except:
        running_sprites_jumper_right.append(pygame.Surface((90, 90)))
        running_sprites_jumper_left.append(pygame.Surface((90, 90)))

# Переменные текущего скина
current_skin_index = 0
confirmed_skin_index = current_skin_index


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

    def update(self, level_num):
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
            if level_num == 1:
                if not (1505 < level_manager.scroll_pos < 1690):
                    self.rect.bottom = H - GROUND_H
                    self.y_speed = 0
                    self.is_grounded = True
                    self.jump_count = 0
                elif 1505 < level_manager.scroll_pos < 1690 and self.rect.bottom > H:
                    self.kill(me_image)
                else:
                    self.is_grounded = False  # Исправлено: убрали лишнюю букву
            elif level_num == 2 or level_num == 4 or level_num == 5:
                if not (505 < level_manager.scroll_pos < 3600):
                    self.rect.bottom = H - GROUND_H
                    self.y_speed = 0
                    self.is_grounded = True
                    self.jump_count = 0
                elif 505 < level_manager.scroll_pos < 3600 and self.rect.bottom > H:
                    self.kill(me_image)
                else:
                    self.is_grounded = False  # Исправлено: убрали лишнюю букву
            else:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_grounded = True  # Исправлено: убрали лишнюю букву
                self.jump_count = 0  # Сбрасываем счетчик прыжков при приземлении на землю

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
        global Level
        self.running_sprites_enemy_right = running_sprites_enemy_right
        self.running_sprites_enemy_left = running_sprites_enemy_left
        # По умолчанию обычный враг
        self.enemy_type = "common"

        if self.enemy_type == "speed":
            self.speed = 8
        elif self.enemy_type == "damager":
            self.speed = 4
        elif self.enemy_type == "jumper":
            self.speed = 6
        else:
            self.speed = 5  # Нормальная скорость для обычных врагов

        # Установка спрайтов в зависимости от типа
        self.set_sprites_by_type()

        self.image = self.running_sprites_enemy_right[0]
        self.current_frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.frame_delay = 90
        self.rect = self.image.get_rect()
        self.x_speed = 0
        self.y_speed = 0
        self.is_out = False
        self.is_dead = False
        self.jump_speed = -10
        self.gravity = 0.4
        self.is_grounded = False
        self.damage_given = False
        self.HP = 100
        self.original_size = self.rect.size

        # Для прыгунов
        self.last_jump_time = 0
        self.jump_cooldown = 3000  # 3 секунд между прыжками
        self.can_jump = True

        # Для дамагеров
        self.damage_amount = 2 if self.enemy_type == "damager" else 1

        self.spawn()

    def set_sprites_by_type(self):
        if self.enemy_type == "speed":
            self.running_sprites_enemy_right = running_sprites_enemy_right_2
            self.running_sprites_enemy_left = running_sprites_enemy_left_2
        elif self.enemy_type == "damager":
            self.running_sprites_enemy_right = running_sprites_damager_right
            self.running_sprites_enemy_left = running_sprites_damager_left
        elif self.enemy_type == "jumper":
            self.running_sprites_enemy_right = running_sprites_jumper_right
            self.running_sprites_enemy_left = running_sprites_jumper_left
        else:  # common
            self.running_sprites_enemy_right = running_sprites_enemy_right
            self.running_sprites_enemy_left = running_sprites_enemy_left

    def spawn(self):
        global Level
        direction = random.randint(0, 1)

        # ПЕРЕПРОВЕРЯЕМ тип врага и устанавливаем соответствующие свойства
        if self.enemy_type == "speed":
            self.speed = 8
            self.damage_amount = 1
        elif self.enemy_type == "damager":
            self.speed = 4
            self.damage_amount = 2  # Наносит 2 урона
        elif self.enemy_type == "jumper":
            self.speed = 6
            self.damage_amount = 1
            self.can_jump = True
            self.last_jump_time = pygame.time.get_ticks()
        else:  # common
            self.speed = 5
            self.damage_amount = 1

        # Устанавливаем спрайты
        self.set_sprites_by_type()

        if direction == 0:
            self.x_speed = self.speed
            self.rect.bottomright = (0, H - GROUND_H)
            self.image = self.running_sprites_enemy_left[0]
        else:
            self.x_speed = -self.speed
            self.rect.bottomleft = (W, H - GROUND_H)
            self.image = self.running_sprites_enemy_right[0]

    def jump(self):
        """Прыжок для врагов-прыгунов"""
        if self.enemy_type == "jumper" and self.is_grounded and self.can_jump:
            self.y_speed = self.jump_speed
            self.is_grounded = False
            self.can_jump = False
            self.last_jump_time = pygame.time.get_ticks()

    def kill(self):
        global Level

        # СОХРАНЯЕМ ТЕКУЩУЮ ПОЗИЦИЮ НИЖНЕЙ ЧАСТИ
        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx

        try:
            if self.enemy_type == "speed":
                dead_img = pygame.image.load("Sprites and objects/Enemies/Speed/Koopa_dead.png")
                self.image = pygame.transform.scale(dead_img, (70, 50))
            elif self.enemy_type == "damager":
                dead_img = pygame.image.load("Sprites and objects/Enemies/Damager/Doomba_dead.png")
                self.image = pygame.transform.scale(dead_img, (90, 28))
            elif self.enemy_type == "jumper":
                dead_img = pygame.image.load("Sprites and objects/Enemies/Jumper/Jumper_dead.png")
                self.image = pygame.transform.scale(dead_img, (70, 50))
            else:  # common enemy
                dead_img = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_dead.png")
                self.image = pygame.transform.scale(dead_img, (90, 28))
        except:
            self.image = pygame.Surface((90, 28))
            # Разные цвета для отладки
            if self.enemy_type == "damager":
                self.image.fill((200, 0, 0))  # Темно-красный
            elif self.enemy_type == "jumper":
                self.image.fill((0, 0, 200))  # Темно-синий
            else:
                self.image.fill((100, 100, 100))  # Серый цвет для отладки

        # ВОССТАНАВЛИВАЕМ ПОЗИЦИЮ (сохраняем нижнюю часть на земле)
        self.rect = self.image.get_rect()
        self.rect.centerx = old_centerx
        self.rect.bottom = old_bottom  # Важно: сохраняем позицию низа

        self.is_dead = True
        self.x_speed = 0  # Останавливаем движение при смерти
        self.y_speed = self.jump_speed

    def update(self):
        now = pygame.time.get_ticks()

        # ОБНОВЛЯЕМ скорость в зависимости от типа при каждом обновлении
        if self.enemy_type == "speed":
            target_speed = 8
        elif self.enemy_type == "damager":
            target_speed = 4
        elif self.enemy_type == "jumper":
            target_speed = 6
        else:
            target_speed = 5

        # Плавно изменяем скорость к целевой
        if abs(self.x_speed) != target_speed and not self.is_dead:
            if self.x_speed > 0:
                self.x_speed = target_speed
            elif self.x_speed < 0:
                self.x_speed = -target_speed

        # Для прыгунов - проверяем возможность прыжка
        if (self.enemy_type == "jumper" and
                not self.is_dead and
                not self.can_jump and
                now - self.last_jump_time > self.jump_cooldown):
            self.can_jump = True

        # Случайный прыжок для прыгунов
        if (self.enemy_type == "jumper" and
                self.can_jump and
                self.is_grounded and
                random.random() < 0.02):  # 2% шанс прыгнуть каждый кадр
            self.jump()

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
                self.x_speed = abs(self.speed)
            elif self.rect.right > W:
                self.rect.right = W
                self.x_speed = -abs(self.speed)

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
        current_level = level_manager.current_level
        if current_level == 3:
            boss_img = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_right_1.png")
            self.image = pygame.transform.scale(boss_img, (140, 140))
            self.running_sprites_enemy_right = running_sprites_right_boss
            self.running_sprites_enemy_left = running_sprites_left_boss
        elif current_level == 6:
            boss_img = pygame.image.load("Sprites and objects/Enemies/Speed/Koopa_right_1.png")
            self.image = pygame.transform.scale(boss_img, (140, 140))
            self.running_sprites_enemy_right = running_sprites_right_boss_2
            self.running_sprites_enemy_left = running_sprites_left_boss_2
        else:
            # Fallback для других уровней
            self.image = pygame.Surface((140, 140))
            self.image.fill((150, 75, 0))
        self.current_frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.frame_delay = 90
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
        self.phase_changed = False
        if current_difficulty == 0:  # Легко
            self.attack_damage = 1
        elif current_difficulty == 1:  # Средне
            self.attack_damage = 2
        elif current_difficulty == 2:  # Сложно
            self.attack_damage = 3

        # ИСПРАВЛЕННЫЙ КОД: используем current_level вместо глобальной Level
        boss_hp_values = {
            3: {0: 20, 1: 22, 2: 24},  # Уровень 3
            6: {0: 50, 1: 56, 2: 65}  # Уровень 6 - БОЛЬШЕ HP
        }

        # Значения по умолчанию для других случаев
        default_hp = {0: 20, 1: 23, 2: 25}

        if current_level in boss_hp_values:
            self.HP = boss_hp_values[current_level][current_difficulty]
            self.max_HP = boss_hp_values[current_level][current_difficulty]
        else:
            self.HP = default_hp[current_difficulty]
            self.max_HP = default_hp[current_difficulty]

        # Таймеры и задержки
        self.spawn_time = pygame.time.get_ticks()
        self.has_started_moving = False
        self.move_delay = 1500
        self.behavior_change_time = pygame.time.get_ticks()
        self.behavior_duration = 2000

        # Текущее поведение
        self.current_behavior = "patrol"
        self.charge_direction = 0
        self.jump_ready = True

        # Ускорение при получении удара
        self.is_accelerated = False
        self.acceleration_start_time = 0
        self.acceleration_duration = 3000  # 3 секунды
        self.acceleration_speed_multiplier = 2.0
        self.base_speed = 3  # Базовая скорость без ускорения

        # Границы движения
        self.left_boundary = 50
        self.right_boundary = W - 50

        self.spawn()

    def spawn(self):
        self.rect.midbottom = (W // 2, H - GROUND_H)
        self.x_speed = 0
        self.has_started_moving = False
        self.HP = self.max_HP
        self.phase = 0
        self.current_behavior = "patrol"
        self.is_dead = False
        self.is_grounded = True
        self.is_accelerated = False
        self.base_speed = 3

    def update_phase(self):
        hp_percent = self.HP / self.max_HP
        old_phase = self.phase

        if hp_percent > 0.5:
            new_phase = 0
        elif hp_percent > 0.25:
            new_phase = 1
        else:
            new_phase = 2

        if new_phase != old_phase:
            self.phase = new_phase
            self.phase_changed = True
            self.on_phase_change()

    def get_attack_damage(self):
        base_damage = self.attack_damage
        if self.phase == 0:
            return base_damage
        elif self.phase == 1:
            return int(base_damage * 1.5)
        else:  # phase == 2
            return base_damage * 2

    def on_phase_change(self):
        if self.phase == 1:
            self.base_speed = 4
            self.behavior_duration = 1800
        elif self.phase == 2:
            self.base_speed = 5
            self.behavior_duration = 1500

        # Обновляем текущую скорость с учетом фазы
        self.speed = self.base_speed
        if self.is_accelerated:
            self.speed = self.base_speed * self.acceleration_speed_multiplier

    def start_acceleration(self):
        """Запускает ускорение босса"""
        self.is_accelerated = True
        self.acceleration_start_time = pygame.time.get_ticks()
        self.speed = self.base_speed * self.acceleration_speed_multiplier

        # Немедленно применяем ускорение к текущей скорости
        if self.x_speed != 0:
            if self.x_speed > 0:
                self.x_speed = self.speed
            else:
                self.x_speed = -self.speed

    def stop_acceleration(self):
        """Останавливает ускорение босса"""
        self.is_accelerated = False
        self.speed = self.base_speed

        # Возвращаем нормальную скорость
        if self.x_speed != 0:
            if self.x_speed > 0:
                self.x_speed = self.speed
            else:
                self.x_speed = -self.speed

    def choose_behavior(self):
        if self.phase == 0:
            behaviors = ["patrol", "patrol", "charge"]
        elif self.phase == 1:
            behaviors = ["patrol", "charge", "charge"]
        else:
            behaviors = ["patrol", "charge", "charge"]

        self.current_behavior = random.choice(behaviors)
        self.behavior_change_time = pygame.time.get_ticks()

        # Рассчитываем скорость с учетом ускорения
        current_speed = self.speed

        if self.current_behavior == "patrol":
            self.x_speed = random.choice([-1, 1]) * current_speed
        elif self.current_behavior == "charge":
            player_center_x = player.rect.centerx
            self.charge_direction = 1 if player_center_x > self.rect.centerx else -1
            self.x_speed = self.charge_direction * current_speed * 2
        elif self.current_behavior == "jump" and self.is_grounded:
            self.y_speed = self.jump_speed * (0.8 + 0.2 * self.phase)
        elif self.current_behavior == "special":
            self.x_speed = 0


    def check_boundaries(self):
        if self.rect.left <= self.left_boundary:
            self.rect.left = self.left_boundary
            self.x_speed = abs(self.speed)
            return True
        elif self.rect.right >= self.right_boundary:
            self.rect.right = self.right_boundary
            self.x_speed = -abs(self.speed)
            return True
        return False

    def handle_boundary_collision(self):
        if self.check_boundaries():
            if self.current_behavior == "charge":
                self.current_behavior = "patrol"
                self.choose_behavior()

    def take_damage(self, damage):
        self.HP -= damage

        # Запускаем ускорение при получении урона
        if not self.is_dead:
            self.start_acceleration()

        if self.HP <= 0:
            self.kill()

    def kill(self):
        current_level = level_manager.current_level
        try:
            if current_level == 3:
                dead_img = pygame.image.load("Sprites and objects/Enemies/Common/Goomba_dead.png")
                self.image = pygame.transform.scale(dead_img, (140, 38))
            elif current_level == 6:
                dead_img = pygame.image.load("Sprites and objects/Enemies/Speed/Koopa_dead.png")
                self.image = pygame.transform.scale(dead_img, (140, 38))

        except:
            self.image = pygame.Surface((140, 38))

        old_bottom = self.rect.bottom
        old_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.centerx = old_centerx
        self.rect.bottom = old_bottom

        self.is_dead = True
        self.x_speed = 0
        self.y_speed = self.jump_speed * 0.5
        self.is_grounded = False
        self.is_accelerated = False

        # ОСТАНОВИТЬ ВСЕ АКТИВНЫЕ ДЕЙСТВИЯ
        self.current_behavior = "dead"
        self.has_started_moving = False

    def update(self):
        now = pygame.time.get_ticks()

        # ЕСЛИ БОСС МЕРТВ - ОБРАБАТЫВАЕМ ТОЛЬКО АНИМАЦИЮ СМЕРТИ И ГРАВИТАЦИЮ
        if self.is_dead:
            self.y_speed += self.gravity
            self.rect.y += self.y_speed

            if self.rect.bottom >= H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_grounded = True
            else:
                self.is_grounded = False

            if self.rect.top > H:
                self.is_out = True
            return

        if self.phase == 2 and self.is_grounded:
            # Прыгает каждые 3 секунды в фазе 3
            if pygame.time.get_ticks() % 3000 < 50:  # Каждые ~3 секунды
                self.y_speed = self.jump_speed * 1.5

        # Проверяем окончание ускорения
        if self.is_accelerated and now - self.acceleration_start_time >= self.acceleration_duration:
            self.stop_acceleration()
            # Перевыбираем поведение для применения нормальной скорости
            self.choose_behavior()

        self.update_phase()

        if not self.has_started_moving and now - self.spawn_time >= self.move_delay:
            self.x_speed = -self.speed
            self.has_started_moving = True
            self.choose_behavior()

        if self.has_started_moving and now - self.behavior_change_time > self.behavior_duration:
            self.choose_behavior()

        # Анимация
        if now - self.last_frame_update > self.frame_delay:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.running_sprites_enemy_right)
            if self.x_speed > 0:
                self.image = self.running_sprites_enemy_right[self.current_frame_index]
            else:
                self.image = self.running_sprites_enemy_left[self.current_frame_index]
            self.last_frame_update = now

        # Движение
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
        if self.is_dead:
            return

        bar_width = 200
        bar_height = 20
        bar_x = W // 2 - bar_width // 2
        bar_y = 20

        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        hp_width = int((self.HP / self.max_HP) * bar_width)

        if self.is_accelerated:
            color = (255, 255, 0)  # Желтый при ускорении
        elif self.phase == 0:
            color = (0, 255, 0)
        elif self.phase == 1:
            color = (255, 165, 0)
        else:
            color = (255, 0, 0)

        pygame.draw.rect(surface, color, (bar_x, bar_y, hp_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Показываем индикатор ускорения
        if self.is_accelerated:
            acceleration_time_left = self.acceleration_duration - (
                    pygame.time.get_ticks() - self.acceleration_start_time)
            if acceleration_time_left > 0:
                # Рисуем полоску ускорения под полоской HP
                acceleration_width = int((acceleration_time_left / self.acceleration_duration) * bar_width)
                pygame.draw.rect(surface, (255, 255, 0), (bar_x, bar_y + 25, acceleration_width, 8))
                pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y + 25, bar_width, 8), 1)


# Создаем игрока
player = Player()


def check_all_secrets_found(difficulty=None):
    global current_difficulty
    """Проверяет, найдены ли все секреты для указанной сложности"""
    if difficulty is None:
        difficulty = current_difficulty

    # Временно сохраняем текущую сложность
    original_difficulty = current_difficulty

    try:
        # Устанавливаем нужную сложность для проверки

        current_difficulty = difficulty

        # Загружаем секреты для этой сложности
        load_secret_items()
        load_secret_points()

        total_found = len(secret_items_collected) + len(secret_points_collected)
        total_secrets = sum(level_manager.get_level_secrets_count(i) for i in range(1, 7))
        return total_found >= total_secrets > 0
    finally:
        # Восстанавливаем исходную сложность
        current_difficulty = original_difficulty
        # И загружаем обратно секреты для текущей сложности
        load_secret_items()
        load_secret_points()

def create_gradient_surface(width, height, colors):
    """Создает поверхность с вертикальным градиентом"""
    gradient_surface = pygame.Surface((width, height))

    if len(colors) == 1:
        gradient_surface.fill(colors[0])
        return gradient_surface

    # Создаем вертикальный градиент
    color_count = len(colors)
    segment_height = height // (color_count - 1)

    for i in range(color_count - 1):
        start_color = colors[i]
        end_color = colors[i + 1]
        start_y = i * segment_height
        end_y = (i + 1) * segment_height

        for y in range(start_y, end_y):
            # Интерполяция между цветами
            ratio = (y - start_y) / (end_y - start_y)
            r = start_color[0] + (end_color[0] - start_color[0]) * ratio
            g = start_color[1] + (end_color[1] - start_color[1]) * ratio
            b = start_color[2] + (end_color[2] - start_color[2]) * ratio

            pygame.draw.line(gradient_surface, (int(r), int(g), int(b)),
                             (0, y), (width, y))

    return gradient_surface


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
    return None  # Добавить возврат None если сохранения нет


def save_skin():
    cursor = saving.cursor()
    # Создаем таблицу для скинов с учетом сложности
    table_name = f"skins_{['easy', 'medium', 'hard'][current_difficulty]}"
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            current_skin_index INTEGER
        )
    ''')
    cursor.execute(f'DELETE FROM {table_name}')
    cursor.execute(f'INSERT INTO {table_name} (current_skin_index) VALUES (?)', (current_skin_index,))
    saving.commit()


def load_skin():
    global current_skin_index
    cursor = saving.cursor()
    table_name = f"skins_{['easy', 'medium', 'hard'][current_difficulty]}"

    # Создаем таблицу если не существует
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            current_skin_index INTEGER
        )
    ''')

    # Инициализируем если пустая
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    if cursor.fetchone()[0] == 0:
        cursor.execute(f'INSERT INTO {table_name} (current_skin_index) VALUES (0)')
        saving.commit()

    cursor.execute(f'SELECT current_skin_index FROM {table_name} LIMIT 1')
    row = cursor.fetchone()
    if row:
        current_skin_index = row[0]
    else:
        current_skin_index = 0
        save_skin()


def save_upgrades():
    global player_points_easy, player_points_medium, player_points_hard, player
    cursor = saving.cursor()
    table_name = ['upgrades_easy', 'upgrades_medium', 'upgrades_hard'][current_difficulty]
    cursor.execute(
        f'UPDATE {table_name} SET player_points = ?, attack = ?, HP = ?, running_unlocked = ?, double_jump_unlocked = ?, shield = ? WHERE id=1',
        (
            player_points_easy if current_difficulty == 0 else player_points_medium if current_difficulty == 1 else player_points_hard,
            player.attack, player.max_HP, int(player.running_unlocked), int(player.double_jump_unlocked),
            player.shield))
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
        player.max_HP = row[2]
        player.running_unlocked = bool(row[3])
        player.double_jump_unlocked = bool(row[4])
        player.shield = row[5]
    return player.HP


def save_secret_items():
    """Сохраняет коллекционные предметы в базу данных для текущей сложности"""
    cursor = saving.cursor()
    table_name = f"secret_items_{['easy', 'medium', 'hard'][current_difficulty]}"
    cursor.execute(f'DELETE FROM {table_name}')
    for item_id in secret_items_collected:
        cursor.execute(f'INSERT INTO {table_name} (item_id, collected) VALUES (?, ?)', (item_id, 1))
    saving.commit()


def load_secret_items():
    """Загружает коллекционные предметы из базы данных для текущей сложности"""
    global secret_items_collected
    cursor = saving.cursor()
    table_name = f"secret_items_{['easy', 'medium', 'hard'][current_difficulty]}"
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (item_id TEXT PRIMARY KEY, collected INTEGER)')
    cursor.execute(f'SELECT item_id FROM {table_name}')
    results = cursor.fetchall()
    secret_items_collected = [row[0] for row in results]


def save_unlocked_skins():
    """Сохраняет статус разблокировки всех скинов для текущей сложности"""
    cursor = saving.cursor()
    table_name = f"unlocked_skins_{['easy', 'medium', 'hard'][current_difficulty]}"

    # Очищаем таблицу для текущей сложности
    cursor.execute(f'DELETE FROM {table_name}')

    # Сохраняем все скины для текущей сложности
    for skin in skins:
        cursor.execute(f'''
            INSERT INTO {table_name} (skin_name, unlocked) 
            VALUES (?, ?)
        ''', (skin["name"], int(skin["unlocked"])))

    saving.commit()


def load_unlocked_skins():
    """Загружает статус разблокировки всех скинов для текущей сложности"""
    cursor = saving.cursor()
    table_name = f"unlocked_skins_{['easy', 'medium', 'hard'][current_difficulty]}"

    # Создаем таблицу если она не существует
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            skin_name TEXT PRIMARY KEY,
            unlocked INTEGER
        )
    ''')

    # Инициализируем стандартные скины если таблица пустая
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    if cursor.fetchone()[0] == 0:
        default_skins = ["Классика", "Потерянный", "Селена", "Мона"]
        for skin_name in default_skins:
            cursor.execute(f'''
                INSERT INTO {table_name} (skin_name, unlocked) 
                VALUES (?, ?)
            ''', (skin_name, 1))
        saving.commit()

    # Загружаем статус разблокировки для текущей сложности
    cursor.execute(f'SELECT skin_name, unlocked FROM {table_name}')
    results = cursor.fetchall()

    unlocked_skins_dict = {row[0]: bool(row[1]) for row in results}

    # Обновляем статус в памяти только для текущей сложности
    for skin in skins:
        if skin["name"] in unlocked_skins_dict:
            skin["unlocked"] = unlocked_skins_dict[skin["name"]]
        else:
            # Если скина нет в базе, он считается заблокированным (кроме стандартных)
            if skin["name"] in ["Классика", "Потерянный", "Селена", "Мона"]:
                skin["unlocked"] = True
            else:
                skin["unlocked"] = False


def lock_secret_hunter_skin():
    """Блокирует скин 'Искатель секретов' только на текущей сложности"""
    cursor = saving.cursor()
    table_name = f"unlocked_skins_{['easy', 'medium', 'hard'][current_difficulty]}"

    # Блокируем скин в базе данных
    cursor.execute(f'UPDATE {table_name} SET unlocked = 0 WHERE skin_name = "Искатель секретов"')

    # Блокируем скин в памяти
    for skin in skins:
        if skin["name"] == "Искатель секретов":
            skin["unlocked"] = False
            break

    saving.commit()


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


def draw_text_with_background(text, font, text_color, bg_color, surface, x, y, padding=10):
    """Рисует текст с фоном и рамкой, центрируя по координатам (x, y)"""
    text_obj = font.render(text, True, text_color)
    text_rect = text_obj.get_rect(center=(x, y))

    # Создаем поверхность для фона с отступами
    bg_rect = pygame.Rect(0, 0, text_rect.width + padding * 2, text_rect.height + padding * 2)
    bg_rect.center = (x, y)

    # Рисуем фон
    pygame.draw.rect(surface, bg_color, bg_rect)
    # Рисуем рамку
    pygame.draw.rect(surface, (0, 0, 0), bg_rect, 2)
    # Рисуем текст
    surface.blit(text_obj, text_rect)


def play_menu_music():
    global music_playing
    if music_on:
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
        # Если музыка включается
        if playing_level and level_manager.current_level in level_manager.levels:
            # Во время уровня - загружаем музыку уровня
            level_data = level_manager.levels[level_manager.current_level]
            try:
                pygame.mixer.music.load(level_data["music"])
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Ошибка загрузки музыки уровня: {e}")
        else:
            # В меню - загружаем музыку меню
            play_menu_music()
    else:
        # Если музыка выключается - ставим на паузу
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


def show_secret_message(text):
    global secret_message, secret_message_time
    secret_message = text
    secret_message_time = pygame.time.get_ticks()


def change_difficulty(new_difficulty):
    global current_difficulty, difficulty_level
    # Сохраняем текущий скин перед сменой сложности
    save_skin()
    current_difficulty = new_difficulty
    difficulty_level = new_difficulty

    # Очищаем текущий прогресс уровня при смене сложности
    cursor = saving.cursor()
    table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][current_difficulty]
    cursor.execute(f'DELETE FROM {table_name}')
    saving.commit()

    # Загружаем все данные для новой сложности
    save_settings_sql()
    load_upgrades()
    load_skin()
    load_unlocked_skins()  # Загружаем скины для новой сложности
    apply_skin(current_skin_index)
    load_secret_items()
    load_secret_points()

    # Сбрасываем позицию игрока
    level_manager.scroll_pos = 0
    player.respawn()

    # Показываем сообщение о смене сложности
    difficulty_names = ["Легко", "Средне", "Сложно"]
    show_message(f"Сложность изменена на: {difficulty_names[current_difficulty]}")


# Функции для проверки завершения всех уровней и разблокировки скинов
def check_all_levels_completed(difficulty):
    """Проверяет, пройдены ли все уровни на указанной сложности"""
    cursor = saving.cursor()
    table_name = ['levels_easy', 'levels_medium', 'levels_hard'][difficulty]

    # Проверяем все 6 уровней
    for level_num in range(1, 7):
        cursor.execute(f'SELECT cleared FROM {table_name} WHERE level_number = ?', (level_num,))
        row = cursor.fetchone()
        if not row or not bool(row[0]):
            return False
    return True


def unlock_completion_skins():
    """Разблокирует скины за прохождение всех уровней и нахождение всех секретов"""
    # Проверяем каждую сложность и разблокируем соответствующие скины
    if check_all_levels_completed(0):  # Легкая сложность
        for skin in skins:
            if skin["name"] == "Бронзовый герой":
                skin["unlocked"] = True

    if check_all_levels_completed(1):  # Средняя сложность
        for skin in skins:
            if skin["name"] == "Чемпион":
                skin["unlocked"] = True

    if check_all_levels_completed(2):  # Сложная сложность
        for skin in skins:
            if skin["name"] == "Золотой легенда":
                skin["unlocked"] = True

    # Проверяем все секреты для каждой сложности отдельно
    for difficulty in [0, 1, 2]:
        if check_all_secrets_found(difficulty):
            for skin in skins:
                if skin["name"] == "Искатель секретов":
                    # Разблокируем только если скин не заблокирован принудительно
                    cursor = saving.cursor()
                    table_name = f"unlocked_skins_{['easy', 'medium', 'hard'][difficulty]}"
                    cursor.execute(f'SELECT unlocked FROM {table_name} WHERE skin_name = "Искатель секретов"')
                    result = cursor.fetchone()
                    if result and bool(result[0]):
                        skin["unlocked"] = True
                    break

    # Сохраняем статус разблокировки
    save_unlocked_skins()


# Игровые меню и экраны
def pause():
    global playing_menu, from_level, from_menu, playing_level
    load_settings_sql()
    paused = True
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((92, 148, 100, 20))
    selected_idx = 0
    menu_items = ["Музыка", "Звук", "Управление", "Назад"]

    # Ставим музыку на паузу при входе в меню паузы
    if music_on and pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    # Продолжаем музыку при выходе из паузы
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
                        playing_level = False
                        save_secret_items()
                        load_secret_items()
                        # Продолжаем музыку при выходе в меню
                        if music_on:
                            pygame.mixer.music.unpause()
                        level_menu()

        # УБИРАЕМ постоянную паузу музыки внутри цикла - это было ошибкой!
        # if music_on and pygame.mixer.music.get_busy():
        #     pygame.mixer.music.pause()

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


def get_secrets_progress(difficulty=None):
    global current_difficulty
    """Возвращает прогресс по секретам для указанной сложности"""
    if difficulty is None:
        difficulty = current_difficulty

    # Временно сохраняем текущую сложность
    original_difficulty = current_difficulty

    try:
        # Устанавливаем нужную сложность для проверки
        current_difficulty = difficulty

        # Загружаем секреты для этой сложности
        load_secret_items()
        load_secret_points()

        total_found = len(secret_items_collected) + len(secret_points_collected)
        total_secrets = sum(level_manager.get_level_secrets_count(i) for i in range(1, 7))
        return total_found, total_secrets
    finally:
        # Восстанавливаем исходную сложность
        current_difficulty = original_difficulty
        # И загружаем обратно секреты для текущей сложности
        load_secret_items()
        load_secret_points()


# Функция для правильного склонения числительных
def format_points(points):
    """Возвращает правильную форму слова 'очко' в зависимости от числа"""
    if points % 10 == 1 and points % 100 != 11:
        return f"{points} очко"
    elif 2 <= points % 10 <= 4 and (points % 100 < 10 or points % 100 >= 20):
        return f"{points} очка"
    else:
        return f"{points} очков"


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


def play_cutscene(cutscene_name):
    """Проигрывает указанную катсцену"""
    global playing_level

    if cutscene_name not in cutscenes:
        return

    cutscene_data = cutscenes[cutscene_name]
    cutscene_manager.start_cutscene(cutscene_data)

    playing_cutscene = True
    while playing_cutscene:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Пропуск всей катсцены
                    playing_cutscene = False
                elif event.key == pygame.K_SPACE:
                    # Продолжение к следующему диалогу или завершение катсцены
                    if not cutscene_manager.finish_current():
                        playing_cutscene = False

        # Обновление катсцены
        if not cutscene_manager.update():
            playing_cutscene = False

        # Отрисовка
        cutscene_manager.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def main_menu():
    global menu, from_menu, from_level, message, playing_level
    load_settings_sql()
    load_secret_items()  # Загружаем секретные предметы для текущей сложности
    load_secret_points()  # Загружаем секреты с очками для текущей сложности
    menu = True
    playing_level = False  # Не в уровне

    # Проверяем, открыт ли раздел секретов (учитываем оба типа секретов)
    total_found = len(secret_items_collected) + len(secret_points_collected)
    secrets_unlocked = total_found > 0

    options = [
        "Начать игру",
        "Скины",
        "Улучшение",
        "Настройки",
        "Секреты" if secrets_unlocked else "???",
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
                save_secret_items()  # Сохраняем секретные предметы
                save_secret_points()  # Сохраняем секреты с очками
                save_skin()  # Сохраняем скин перед выходом
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        menu = False
                        from_menu = True
                        save_secret_items()
                        save_secret_points()
                        save_skin()  # Сохраняем скин перед переходом
                        # Воспроизводим вступительную катсцену перед переходом к выбору уровня
                        play_cutscene("intro")
                        level_menu()
                    elif selected_option == 1:
                        skin_menu()
                    elif selected_option == 2:
                        upgrade()
                    elif selected_option == 3:
                        settings()
                    elif selected_option == 4:
                        if secrets_unlocked:
                            secrets()
                        else:
                            show_message("Найдите хотя бы один секрет, чтобы открыть этот раздел!")
                    elif selected_option == 5:
                        save_settings_sql()
                        save_secret_items()  # Сохраняем секретные предметы
                        save_secret_points()  # Сохраняем секреты с очками
                        save_skin()  # Сохраняем скин перед выходом
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
            if j == 4 and not secrets_unlocked:
                color = (100, 100, 100) if j == selected_option else (50, 50, 50)  # Серый для заблокированного
            else:
                color = (255, 255, 255) if j == selected_option else (0, 0, 0)
            draw_text(opt, font_small, color, screen, W // 2, H // 2 - 90 + j * 50)

        # Показываем количество найденных секретов для текущей сложности
        total_found = len(secret_items_collected) + len(secret_points_collected)
        total_secrets = sum(level_manager.get_level_secrets_count(i) for i in range(1, 7))

        if total_found > 0:
            draw_text(f"Найдено секретов: {total_found}/{total_secrets}", font_small, (255, 255, 255), screen, W - 150,
                      30)
        else:
            draw_text("Секреты: ???", font_small, (100, 100, 100), screen, W - 150, 30)

        # Показываем подсказку для открытия секретов
        if not secrets_unlocked:
            draw_text("Найдите секрет в игре, чтобы открыть эту вкладку",
                      font_small, (200, 200, 0), screen, W // 2,
                      H - 50)

        if message:
            current_time = pygame.time.get_ticks()
            if current_time - message_time < MESSAGE_DURATION:
                draw_text_with_background(message, font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)
            else:
                message = None

        pygame.display.flip()
        clock.tick(60)


def skin_menu():
    global current_skin_index, confirmed_skin_index, message, message_time, player_points_easy, player_points_medium, player_points_hard

    load_upgrades()
    load_unlocked_skins()  # Загружаем скины для ТЕКУЩЕЙ сложности
    load_skin()
    unlock_completion_skins()

    # Сбрасываем confirmed_skin_index на актуальный для текущей сложности
    confirmed_skin_index = current_skin_index

    in_skin_menu = True
    points_text = 0
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
                save_secret_items()
                save_skin()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_skin()
                    main_menu()
                    return
                if event.key == pygame.K_RETURN:
                    if selected_skin_index < len(skins):
                        skin = skins[selected_skin_index]

                        if skin["unlocked"]:
                            current_skin_index = selected_skin_index
                            confirmed_skin_index = selected_skin_index
                            apply_skin(current_skin_index)
                            save_skin()
                            show_message(f"Скин '{skin['name']}' выбран!")
                        else:
                            # ПРОВЕРЯЕМ ОЧКИ ТОЛЬКО ДЛЯ ТЕКУЩЕЙ СЛОЖНОСТИ
                            current_points = 0
                            if current_difficulty == 0:
                                current_points = player_points_easy
                            elif current_difficulty == 1:
                                current_points = player_points_medium
                            elif current_difficulty == 2:
                                current_points = player_points_hard

                            if skin["name"] == "Фредди":
                                if current_points >= 2:
                                    skin["unlocked"] = True
                                    # ТРАТИМ ОЧКИ ТОЛЬКО НА ТЕКУЩЕЙ СЛОЖНОСТИ
                                    if current_difficulty == 0:
                                        player_points_easy -= 2
                                    elif current_difficulty == 1:
                                        player_points_medium -= 2
                                    elif current_difficulty == 2:
                                        player_points_hard -= 2

                                    current_skin_index = selected_skin_index
                                    confirmed_skin_index = selected_skin_index
                                    apply_skin(current_skin_index)
                                    save_upgrades()
                                    save_skin()
                                    save_unlocked_skins()  # Сохраняем разблокировку для текущей сложности
                                    show_message(f"Скин 'Фредди' разблокирован! -2 очка")
                                else:
                                    show_message(f"Недостаточно очков! Нужно 2 очка уровня")

                            elif skin["name"] == "Линк":
                                if current_points >= 3:
                                    skin["unlocked"] = True
                                    if current_difficulty == 0:
                                        player_points_easy -= 3
                                    elif current_difficulty == 1:
                                        player_points_medium -= 3
                                    elif current_difficulty == 2:
                                        player_points_hard -= 3

                                    current_skin_index = selected_skin_index
                                    confirmed_skin_index = selected_skin_index
                                    apply_skin(current_skin_index)
                                    save_upgrades()
                                    save_skin()
                                    save_unlocked_skins()
                                    show_message(f"Скин 'Линк' разблокирован! -3 очка")
                                else:
                                    show_message(f"Недостаточно очков! Нужно 3 очка уровня")

                            elif skin["name"] == "Рэд":
                                if current_points >= 4:
                                    skin["unlocked"] = True
                                    if current_difficulty == 0:
                                        player_points_easy -= 4
                                    elif current_difficulty == 1:
                                        player_points_medium -= 4
                                    elif current_difficulty == 2:
                                        player_points_hard -= 4

                                    current_skin_index = selected_skin_index
                                    confirmed_skin_index = selected_skin_index
                                    apply_skin(current_skin_index)
                                    save_upgrades()
                                    save_skin()
                                    save_unlocked_skins()
                                    show_message(f"Скин 'Рэд' разблокирован! -4 очка")
                                else:
                                    show_message(f"Недостаточно очков! Нужно 4 очка уровня")

                            elif skin["name"] == "Пикачу":
                                if current_points >= 3:
                                    skin["unlocked"] = True
                                    if current_difficulty == 0:
                                        player_points_easy -= 3
                                    elif current_difficulty == 1:
                                        player_points_medium -= 3
                                    elif current_difficulty == 2:
                                        player_points_hard -= 3

                                    current_skin_index = selected_skin_index
                                    confirmed_skin_index = selected_skin_index
                                    apply_skin(current_skin_index)
                                    save_upgrades()
                                    save_skin()
                                    save_unlocked_skins()
                                    show_message(f"Скин 'Пикачу' разблокирован! -3 очка")
                                else:
                                    show_message(f"Недостаточно очков! Нужно 3 очка уровня")
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

        # Показываем текущую сложность
        difficulty_names = ["Легко", "Средне", "Сложно"]
        draw_text(f"Сложность: {difficulty_names[current_difficulty]}", font_small, (200, 200, 200), screen, W // 2,
                  H // 6)

        # ПОКАЗЫВАЕМ ПРОГРЕСС ПО УРОВНЯМ ДЛЯ ТЕКУЩЕЙ СЛОЖНОСТИ
        cursor = saving.cursor()
        table_name = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]
        completed_levels = 0
        for level_num in range(1, 7):
            cursor.execute(f'SELECT cleared FROM {table_name} WHERE level_number = ?', (level_num,))
            row = cursor.fetchone()
            if row and bool(row[0]):
                completed_levels += 1

        draw_text(f"Прогресс: {completed_levels}/6 уровней", font_small, (200, 200, 200), screen, W // 2, H // 6 + 30)

        load_upgrades()

        # Обновляем статус разблокировки скинов
        for skin_selected in skins:
            if skin_selected["name"] == "Соник":
                skin_selected["unlocked"] = player.running_unlocked
            elif skin_selected["name"] == "Марио":
                skin_selected["unlocked"] = player.double_jump_unlocked

        for idx, skin_0 in enumerate(skins):
            y_pos = H // 4 + (idx % 7) * 60
            x_pos = W // 2 - 250 if idx < 7 else W // 2 + 200

            # Определяем цвет текста
            is_selected = idx == selected_skin_index
            is_confirmed = idx == confirmed_skin_index  # Текущий выбранный скин для этой сложности

            if is_selected:
                color = (255, 255, 255)  # Белый для выбранного
            elif is_confirmed:
                color = (0, 255, 0)  # Зеленый для активного скина
            else:
                color = (150, 150, 150)  # Серый для остальных

            draw_text(skin_0["name"], font_small, color, screen, x_pos, y_pos)

            if "img" in skin_0:
                img_surface = skin_0["img"]
                if isinstance(img_surface, pygame.Surface):
                    img_rect = img_surface.get_rect(center=(x_pos - 120, y_pos))
                    screen.blit(img_surface, img_rect)

            # Показываем статус и стоимость
            if skin_0["name"] == "Фредди":
                if not skin_0["unlocked"]:
                    status = f"2 очка"
                    status_color = (255, 0, 0)
                else:
                    status = "Открыт"
                    status_color = (0, 255, 0)
            elif skin_0["name"] == "Линк":
                if not skin_0["unlocked"]:
                    status = f"3 очка"
                    status_color = (255, 0, 0)
                else:
                    status = "Открыт"
                    status_color = (0, 255, 0)
            elif skin_0["name"] == "Рэд":
                if not skin_0["unlocked"]:
                    status = f"4 очка"
                    status_color = (255, 0, 0)
                else:
                    status = "Открыт"
                    status_color = (0, 255, 0)
            elif skin_0["name"] == "Пикачу":
                if not skin_0["unlocked"]:
                    status = f"3 очка"
                    status_color = (255, 0, 0)
                else:
                    status = "Открыт"
                    status_color = (0, 255, 0)
            elif skin_0["name"] == "Искатель секретов":
                # Проверяем конкретно для текущей сложности
                if check_all_secrets_found(current_difficulty):
                    status = "Открыт"
                    status_color = (0, 255, 0)
                else:
                    # Показываем прогресс для текущей сложности
                    total_found = len(secret_items_collected) + len(secret_points_collected)
                    total_secrets = sum(level_manager.get_level_secrets_count(i) for i in range(1, 7))
                    status = f"{total_found}/{total_secrets}"
                    status_color = (255, 165, 0)  # Оранжевый для прогресса
            elif skin_0["unlocked"]:
                status = "Открыт"
                status_color = (0, 255, 0)
            else:
                status = "Закрыт"
                status_color = (255, 0, 0)

            # Показываем "ВЫБРАН" для активного скина
            if is_confirmed and skin_0["unlocked"]:
                status = "ВЫБРАН"
                status_color = (0, 255, 255)  # Голубой для выбранного

            draw_text(status, font_small, status_color, screen, x_pos + 150, y_pos)

        # Показываем текущее количество очков для этой сложности
        if current_difficulty == 0:
            points_text = f"Очков: {player_points_easy}"
        elif current_difficulty == 1:
            points_text = f"Очков: {player_points_medium}"
        elif current_difficulty == 2:
            points_text = f"Очков: {player_points_hard}"

        draw_text(points_text, font_small, (255, 255, 255), screen, W // 2, H - 100)
        draw_text("Enter - выбрать, ESC - назад", font_small, (200, 200, 200), screen, W // 2, H - 50)

        if message:
            if now - message_time < 2000:
                draw_text_with_background(message, font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)
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
                save_upgrades()
                save_secret_items()
                save_skin()  # Сохраняем скин перед выходом
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
                    elif selected_idx == 4:  # Сброс прогресса
                        cursor = saving.cursor()
                        table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][
                            current_difficulty]
                        upgrades_table = ['upgrades_easy', 'upgrades_medium', 'upgrades_hard'][current_difficulty]
                        levels_table = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]

                        # 1. Сбрасываем прогресс игры
                        cursor.execute(f'DELETE FROM {table_name}')

                        # 2. Сбрасываем улучшения
                        cursor.execute(f'DELETE FROM {upgrades_table}')
                        cursor.execute(f'''
                                    INSERT INTO {upgrades_table} 
                                    (id, player_points, attack, HP, running_unlocked, double_jump_unlocked, shield) 
                                    VALUES (1, 0, 1, 3, 0, 0, 0)
                                ''')

                        # 3. Сбрасываем уровни
                        cursor.execute(f'DELETE FROM {levels_table}')
                        for level_num in range(1, 10):
                            cursor.execute(f'''
                                        INSERT INTO {levels_table} (level_number, cleared) 
                                        VALUES (?, ?)
                                    ''', (level_num, 0))

                        # 4. Сбрасываем секреты только для текущей сложности
                        difficulty_suffix = ['_easy', '_medium', '_hard'][current_difficulty]
                        cursor.execute(f'DELETE FROM secrets{difficulty_suffix}')
                        cursor.execute(f'DELETE FROM secret_items{difficulty_suffix}')
                        cursor.execute(f'DELETE FROM secret_points{difficulty_suffix}')

                        # 5. Сбрасываем скины только для текущей сложности
                        skins_table = f"unlocked_skins_{['easy', 'medium', 'hard'][current_difficulty]}"
                        cursor.execute(f'DELETE FROM {skins_table}')
                        default_skins = ["Классика", "Потерянный", "Селена", "Мона"]
                        for skin_name in default_skins:
                            cursor.execute(f'''
                                        INSERT INTO {skins_table} (skin_name, unlocked) 
                                        VALUES (?, ?)
                                    ''', (skin_name, 1))

                        # Блокируем все остальные скины для текущей сложности
                        paid_skins = ["Фредди", "Линк", "Рэд", "Пикачу", "Соник", "Марио", "Искатель секретов",
                                      "Бронзовый герой", "Чемпион", "Золотой легенда"]
                        for skin_name in paid_skins:
                            cursor.execute(f'''
                                    INSERT OR REPLACE INTO {skins_table} (skin_name, unlocked) 
                                    VALUES (?, ?)
                                ''', (skin_name, 0))

                        # 6. Сбрасываем глобальные переменные
                        if current_difficulty == 0:
                            player_points_easy = 0
                        elif current_difficulty == 1:
                            player_points_medium = 0
                        elif current_difficulty == 2:
                            player_points_hard = 0

                        # 7. Сбрасываем секреты в памяти
                        secret_items_collected.clear()
                        secret_points_collected.clear()
                        level_manager.reset_all_secrets()

                        # 8. Сбрасываем характеристики игрока
                        player.attack = 1
                        player.HP = 3
                        player.max_HP = 3
                        player.running_unlocked = False
                        player.double_jump_unlocked = False
                        player.shield = 0
                        player.respawn()

                        # 9. Сбрасываем скин на стандартный для текущей сложности
                        current_skin_index = 0
                        apply_skin(current_skin_index)
                        save_skin()

                        saving.commit()
                        save_secret_items()
                        save_secret_points()
                        save_upgrades()
                        save_skin()
                        load_upgrades()
                        load_unlocked_skins()  # Перезагружаем скины

                        show_message("Прогресс сброшен для текущей сложности!")


                    elif selected_idx == 5:  # Сохранить настройки
                        # Сохраняем текущий скин
                        save_skin()
                        current_difficulty = temp_difficulty
                        # Загружаем все данные для новой сложности
                        load_upgrades()
                        load_skin()  # Загружаем скин для новой сложности
                        load_unlocked_skins()
                        apply_skin(current_skin_index)
                        save_settings_sql()
                        save_skin()
                        if dark_mode != pending_mode:
                            dark_mode = pending_mode
                        background_image = (42, 98, 202) if dark_mode else (92, 148, 252)
                        show_message("Настройки сохранены!")
                    elif selected_idx == 6:
                        # Отмена - восстанавливаем исходные настройки
                        temp_difficulty = current_difficulty  # Восстанавливаем исходную сложность
                        pending_mode = dark_mode  # Восстанавливаем исходный режим
                        background_image = (42, 98, 202) if dark_mode else (92, 148, 252)
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

        # Используем правильное склонение для отображения очков
        if current_difficulty == 0:
            draw_text(format_points(player_points_easy), font_small, (255, 255, 255), screen, W - 100, 50)
        elif current_difficulty == 1:
            draw_text(format_points(player_points_medium), font_small, (255, 255, 255), screen, W - 100, 50)
        elif current_difficulty == 2:
            draw_text(format_points(player_points_hard), font_small, (255, 255, 255), screen, W - 100, 50)

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
    load_unlocked_skins()  # ДОБАВЬТЕ ЭТУ СТРОЧКУ
    for skin_selected in skins:
        if skin_selected["name"] == "Соник":
            skin_selected["unlocked"] = player.running_unlocked
        elif skin_selected["name"] == "Марио":
            skin_selected["unlocked"] = player.double_jump_unlocked

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
                    save_skin()  # Сохраняем скин перед выходом
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
                            unlock_message = f"Нужно минимум {format_points(3)}"
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
        # Используем правильное склонение для отображения очков
        draw_text(format_points(current_player_points), font_small, (255, 255, 255), screen, W - 100, 50)

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
                draw_text_with_background(unlock_message, font_small, (0, 0, 0), (255, 255, 255), screen, W // 2,
                                          H // 2)
            else:
                unlock_message = None

        pygame.display.flip()
        clock.tick(60)


def secrets():
    """Меню секретов и коллекционных предметов для текущей сложности"""
    global secret_items_collected, secret_points_collected

    load_secret_items()  # Загружаем актуальные данные для текущей сложности
    load_secret_points()  # Загружаем секреты с очками

    # Дополнительная проверка на случай прямого вызова
    total_found = len(secret_items_collected) + len(secret_points_collected)
    if total_found == 0:
        show_message("Сначала найдите хотя бы один секрет в игре!")
        return

    selected_idx = 0
    last_move_time_up = 0
    last_move_time_down = 0
    MOVE_DELAY = 200

    # Создаем список всех секретов для отображения (предметы + очки)
    secret_list = [
        {"name": "Золотая монета (Уровень 1)", "id": "secret_coin_1", "description": "Спрятана в тайной комнате",
         "type": "item"},
        {"name": "Скрытая комната (Уровень 1)", "id": "points_1_4000_300", "description": "Дает +5 очков",
         "type": "points"},
        {"name": "Сияющая звезда (Уровень 2)", "id": "secret_star_1", "description": "Требует двойного прыжка",
         "type": "item"},
        {"name": "Отсылка к Starset (Уровень 4)", "id": "sonic_reference", "description": "Требует навык 'бег'",
         "type": "item"},
        {"name": "Сокровищница (Уровень 5)", "id": "points_5_3200_150", "description": "Дает +10 очков",
         "type": "points"},
        {"name": "Отсылка к Марио (Уровень 5)", "id": "mario_reference",
         "description": "Секрет для настоящих искателей приключений", "type": "item"},
    ]

    # Статистика по уровням для текущей сложности (только уровни с секретами)
    level_stats = []
    for level_num in range(1, 7):
        total_secrets = level_manager.get_level_secrets_count(level_num)
        # Показываем только уровни, где есть секреты
        if total_secrets > 0:
            level_manager.load_secret_progress(level_num)
            found_secrets = level_manager.get_found_secrets_count(level_num)
            level_stats.append(f"Уровень {level_num}: {found_secrets}/{total_secrets}")

    # Рассчитываем индексы для разных разделов
    ITEMS_HEADER_IDX = 0
    ITEMS_START_IDX = 1
    ITEMS_END_IDX = ITEMS_START_IDX + len(secret_list)
    STATS_HEADER_IDX = ITEMS_END_IDX
    STATS_START_IDX = STATS_HEADER_IDX + 1
    STATS_END_IDX = STATS_START_IDX + len(level_stats)
    TOTAL_ITEMS = STATS_END_IDX

    while True:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    load_secret_items()
                    load_secret_points()
                    return

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_down > MOVE_DELAY:
                selected_idx = (selected_idx + 1) % TOTAL_ITEMS
                last_move_time_down = now
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_up > MOVE_DELAY:
                selected_idx = (selected_idx - 1) % TOTAL_ITEMS
                last_move_time_up = now

        screen.fill(background_image)
        draw_text("Коллекция секретов", font_large, (255, 255, 255), screen, W // 2, H // 6)

        # Показываем общую статистику для текущей сложности
        total_found = len(secret_items_collected) + len(secret_points_collected)
        total_secrets = sum(level_manager.get_level_secrets_count(i) for i in range(1, 7))
        draw_text(f"Найдено: {total_found}/{total_secrets}", font_medium, (255, 255, 255), screen, W // 2, H // 6 + 50)

        # Показываем текущую сложность
        difficulty_names = ["Легко", "Средне", "Сложно"]
        draw_text(f"Сложность: {difficulty_names[current_difficulty]}", font_small, (200, 200, 200), screen, W // 2,
                  H // 6 + 90)

        y_offset = H // 4 + 50

        # Заголовок для предметов
        color = (255, 255, 0) if selected_idx == ITEMS_HEADER_IDX else (200, 200, 200)
        draw_text("=== ВСЕ СЕКРЕТЫ ===", font_small, color, screen, W // 2, y_offset)
        y_offset += 40

        # Список всех секретов (предметы + очки)
        for i, secret in enumerate(secret_list):
            item_idx = ITEMS_START_IDX + i
            is_collected = secret["id"] in (
                secret_items_collected if secret["type"] == "item" else secret_points_collected)
            color = (255, 255, 255) if selected_idx == item_idx else (150, 150, 150)

            if is_collected:
                status = "✓ НАЙДЕНО"
                status_color = (0, 255, 0)
                name = secret["name"]
            else:
                status = "??? НЕИЗВЕСТНО"
                status_color = (255, 0, 0)
                name = "???"  # Скрываем название, если секрет не найден

            draw_text(name, font_small, color, screen, W // 2 - 150, y_offset + i * 40)
            draw_text(status, font_small, status_color, screen, W // 2 + 150, y_offset + i * 40)

            # Показываем описание только для найденных секретов
            if selected_idx == item_idx and is_collected:
                draw_text(secret["description"], font_small, (200, 200, 0), screen, W // 2, y_offset + i * 40 + 60)
            elif selected_idx == item_idx and not is_collected:
                draw_text("Найдите этот секрет в игре, чтобы узнать больше", font_small, (100, 100, 100), screen,
                          W // 2, y_offset + i * 40 + 60)

        y_offset += len(secret_list) * 40 + 40

        # Заголовок для статистики уровней (только если есть уровни с секретами)
        if level_stats:  # Проверяем, есть ли уровни с секретами
            color = (255, 255, 0) if selected_idx == STATS_HEADER_IDX else (200, 200, 200)
            draw_text("=== СТАТИСТИКА УРОВНЕЙ ===", font_small, color, screen, W // 2, y_offset)
            y_offset += 40

            # Статистика по уровням (только уровни с секретами)
            for i, stat in enumerate(level_stats):
                stat_idx = STATS_START_IDX + i
                color = (255, 255, 255) if selected_idx == stat_idx else (150, 150, 150)
                draw_text(stat, font_small, color, screen, W // 2, y_offset + i * 30)

        # Сообщение, если все секреты найдены
        total_found, total_secrets = get_secrets_progress(current_difficulty)

        if total_found >= total_secrets > 0:
            draw_text("ВЫ НАШЛИ ВСЕ СЕКРЕТЫ НА ЭТОЙ СЛОЖНОСТИ! ПОЗДРАВЛЯЕМ!", font_medium, (255, 215, 0), screen,
                      W // 2, H - 100)
            draw_text("Разблокирован скин 'Искатель секретов'!", font_small, (255, 215, 0), screen, W // 2, H - 70)
        else:
            draw_text(f"Найдите все секреты на этой сложности для разблокировки особого скина!", font_small,
                      (200, 200, 0), screen, W // 2, H - 70)

        draw_text("Нажмите ESC для возврата", font_small, (255, 255, 255), screen, W // 2, H - 50)

        pygame.display.flip()
        clock.tick(60)


def level_menu():
    global level1_cleared, level2_cleared, level3_cleared, level4_cleared, level5_cleared, level6_cleared, \
        from_menu, from_level, message, playing_menu, secret_items_collected, playing_level

    playing_level = False  # Не в уровне

    if from_level and not from_menu:
        stop_music()
        play_menu_music()

    load_secret_items()
    load_upgrades()
    cursor = saving.cursor()
    table_name = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]

    # ПРОВЕРЯЕМ И ИНИЦИАЛИЗИРУЕМ ТАБЛИЦУ УРОВНЕЙ
    for level_num in range(1, 7):
        cursor.execute(f'''
            INSERT OR IGNORE INTO {table_name} (level_number, cleared) 
            VALUES (?, ?)
        ''', (level_num, 0))
    saving.commit()

    # ЗАГРУЖАЕМ СТАТУС УРОВНЕЙ ИЗ БАЗЫ ДАННЫХ
    level_status = {}
    for level_num in range(1, 7):
        cursor.execute(f'SELECT cleared FROM {table_name} WHERE level_number = ?', (level_num,))
        row = cursor.fetchone()
        if row:
            level_status[level_num] = bool(row[0])
        else:
            level_status[level_num] = False

    # ОБНОВЛЯЕМ ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
    level1_cleared = level_status.get(1, False)
    level2_cleared = level_status.get(2, False)
    level3_cleared = level_status.get(3, False)
    level4_cleared = level_status.get(4, False)
    level5_cleared = level_status.get(5, False)
    level6_cleared = level_status.get(6, False)

    # ДЕБАГ: выводим статус уровней в консоль

    load_skin()
    options = ["Уровень 1", "Уровень 2", "Уровень 3", "Уровень 4", "Уровень 5", "Уровень 6"]
    selected_idx = 0
    last_move_time_up = 0
    last_move_time_down = 0
    MOVE_DELAY = 200
    x_pos = 0
    y_pos = 0

    # ЗАГРУЖАЕМ ПРОГРЕСС СЕКРЕТОВ ДЛЯ ВСЕХ УРОВНЕЙ
    for level_num in range(1, 7):
        level_manager.load_secret_progress(level_num)

    while True:
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_secret_items()
                    save_skin()  # Сохраняем скин перед выходом
                    main_menu()
                    return
                if event.key == pygame.K_RETURN:
                    level_num = selected_idx + 1

                    # ПРОВЕРЯЕМ ДОСТУПНОСТЬ УРОВНЯ ПО СТАТУСУ ИЗ БАЗЫ ДАННЫХ
                    if level_num == 1:
                        available = True
                    elif level_num == 2:
                        available = level_status.get(1, False)
                    elif level_num == 3:
                        available = level_status.get(2, False)
                    elif level_num == 4:
                        available = level_status.get(3, False)
                    elif level_num == 5:
                        available = level_status.get(4, False)
                    elif level_num == 6:
                        available = level_status.get(5, False)
                    else:
                        available = False

                    if available:
                        if level_num in [3, 6]:  # Уровни с боссами
                            run_boss_preparation(level_num)
                        else:
                            run_level(level_num)
                    else:
                        show_message("Сначала пройдите предыдущий уровень!")

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            if now - last_move_time_down > MOVE_DELAY:
                selected_idx = (selected_idx + 1) % len(options)
                last_move_time_down = now
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            if now - last_move_time_up > MOVE_DELAY:
                selected_idx = (selected_idx - 1) % len(options)
                last_move_time_up = now

        screen.fill(background_image)
        draw_text("Выбор уровня", font_large, (255, 255, 255), screen, W // 2, H // 6)

        for j, opt in enumerate(options):
            is_selected = (j == selected_idx)
            level_num = j + 1

            # ПРОВЕРЯЕМ ДОСТУПНОСТЬ ИЗ БАЗЫ ДАННЫХ
            if level_num == 1:
                available = True
            else:
                available = level_status.get(level_num - 1, False)

            # ЦВЕТА ДЛЯ ОТОБРАЖЕНИЯ
            if available:
                if level_status.get(level_num, False):
                    # Уровень пройден - зеленый
                    color = (0, 255, 0) if not is_selected else (255, 255, 255)
                else:
                    # Уровень доступен, но не пройден - белый/черный
                    color = (255, 255, 255) if is_selected else (0, 0, 0)
            else:
                # Уровень недоступен - красный/серый
                color = (255, 0, 0) if not is_selected else (200, 100, 100)

            # РАСПОЛОЖЕНИЕ
            if 0 <= j < 3:
                x_pos = W // 3
                y_pos = H // 3 + j * 70
            elif 3 <= j < 6:
                x_pos = W // 3 * 2
                y_pos = H // 3 + (j - 3) * 70

            draw_text(opt, font_small, color, screen, x_pos, y_pos)

            # СТАТИСТИКА СЕКРЕТОВ
            if available:
                total_secrets = level_manager.get_level_secrets_count(level_num)
                found_secrets = level_manager.get_found_secrets_count(level_num)
                if total_secrets > 0:
                    secret_text = f"Секреты: {found_secrets}/{total_secrets}"
                    draw_text(secret_text, font_small, (255, 255, 0), screen, x_pos, y_pos + 25)

        if message:
            current_time = pygame.time.get_ticks()
            if current_time - message_time < MESSAGE_DURATION:
                draw_text_with_background(message, font_small, (0, 0, 0),
                                          (255, 255, 255), screen, W // 2, H // 2)
            else:
                message = None

        pygame.display.flip()
        clock.tick(60)


# Основные игровые функции
def run_level(level_num):
    global monsters, boss, score, player, save_message_displayed, save_message_timer, Level, playing_level

    playing_level = True  # Теперь в уровне

    if not level_manager.load_level(level_num):
        show_message(f"Ошибка загрузки уровня {level_num}")
        playing_level = False
        return
    level_data = level_manager.levels[level_num]

    HP = player.HP  # Сначала получаем текущее HP игрока
    loaded_level = load_game_sql()
    if loaded_level == level_num:
        # Если есть сохранение для этого уровня, используем загруженное HP
        HP = player.HP
    else:
        # Иначе начинаем уровень с полным HP
        player.HP = player.max_HP
        HP = player.max_HP
        level_manager.scroll_pos = 0
    load_upgrades()

    player.respawn()
    player.rect.midbottom = (W // 2, H - GROUND_H)

    monsters = []
    boss = []

    # Постоянные таблички для первого уровня
    tutorial_signs = []

    if level_num == 1:
        tutorial_signs = [
            {"text": "ДВИЖЕНИЕ:\n A/D или ←/→", "pos": (300, 640), "width": 200, "height": 60},
            {"text": "ПРЫЖОК:\n W или ↑", "pos": (600, 640), "width": 180, "height": 60},
            {"text": "ОСТОРОЖНО!\nПРОПАСТЬ!", "pos": (1700, 640), "width": 200, "height": 80, "color": (255, 0, 0)},
            {"text": "СЕКРЕТНЫЕ\nПРЕДМЕТЫ", "pos": (3500, 380), "width": 200, "height": 80, "color": (255, 215, 0)},
            {"text": "ПОРТАЛ\nК ВРАГАМ", "pos": (4700, 530), "width": 180, "height": 80, "color": (0, 255, 255)}
        ]
    if level_num == 2:
        tutorial_signs = [
            {"text": "БЕГ:\n Shift + движение", "pos": (700, 640), "width": 220, "height": 60}
        ]

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
                    if 1505 < level_manager.scroll_pos < 1690 and level_num == 1:
                        level_manager.scroll_pos = 1300
                    if 500 < level_manager.scroll_pos < 3600 and level_num != 1:
                        level_manager.scroll_pos = 300
                    player.respawn()
                    player.rect.midbottom = (W // 2, H - GROUND_H)
                    monsters.clear()
                    boss.clear()

        # Обновление игрока
        player.handle_input()
        player.update(level_num)

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

        # Проверка секретных комнат
        level_manager.check_secret_rooms(player.rect)

        # Проверка достижения портала
        if level_manager.check_portal_collision(player.rect):
            # АВТОМАТИЧЕСКОЕ СОХРАНЕНИЕ ПРИ ВХОДЕ В ПОРТАЛ
            save_game_sql(level_num)
            Level = level_num
            save_secret_items()  # Сохраняем секретные предметы
            save_upgrades()  # Сохраняем улучшения
            save_settings_sql()  # Сохраняем настройки
            save_skin()  # Сохраняем скин
            run_enemy_wave(level_num, level_data["enemy_count"])
            running = False

        # Отрисовка - УДАЛЕНО: screen.fill((0, 0, 0))
        level_manager.draw(screen)  # Теперь фон рисуется в level_manager.draw
        player.draw(screen)

        # Отрисовка постоянных табличек для уровня 1
        if level_num == 1 or level_num == 2:
            for sign in tutorial_signs:
                sign_x = sign["pos"][0] - level_manager.scroll_pos
                sign_y = sign["pos"][1]

                # Проверяем, видна ли табличка на экране
                if -sign["width"] < sign_x < W:
                    # Рисуем табличку
                    sign_color = sign.get("color", (200, 200, 100))  # Желтый по умолчанию
                    sign_rect = pygame.Rect(sign_x, sign_y, sign["width"], sign["height"])

                    # Основной фон таблички
                    pygame.draw.rect(screen, sign_color, sign_rect)
                    pygame.draw.rect(screen, (0, 0, 0), sign_rect, 3)  # Рамка

                    # Разделяем текст на строки если есть \n
                    lines = sign["text"].split('\n')
                    for h, line in enumerate(lines):
                        text_surface = font_small.render(line, True, (0, 0, 0))
                        text_rect = text_surface.get_rect(center=(
                            sign_x + sign["width"] // 2,
                            sign_y + sign["height"] // 2 - (len(lines) - 1) * 15 + h * 30
                        ))
                        screen.blit(text_surface, text_rect)

                    # Ножка таблички
                    pole_rect = pygame.Rect(sign_x + sign["width"] // 2 - 5, sign_y + sign["height"], 10, 40)
                    pygame.draw.rect(screen, (139, 69, 19), pole_rect)

        # UI
        draw_text(f"Уровень: {level_num}", font_small, (255, 255, 255), screen, 100, 20)
        draw_text(f"HP: {HP}", font_small, (255, 255, 255), screen, W // 3, 20)  # Теперь HP определена
        draw_text(f"Щиты: {player.shield}", font_small, (255, 255, 255), screen, W // 3 * 2, 20)

        # Показываем сообщение о найденном секрете
        if secret_message and pygame.time.get_ticks() - secret_message_time < SECRET_MESSAGE_DURATION:
            draw_text_with_background(secret_message, font_small, (0, 0, 0), (255, 255, 0), screen, W // 2, H // 3)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text_with_background("Игра сохранена", font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)

        if player.is_out:
            draw_text("Нажмите любую клавишу для возрождения", font_small, (255, 255, 255), screen, W // 2, H // 2)

        pygame.display.flip()
        clock.tick(FPS)

    playing_level = False


def run_boss_preparation(level_num):
    global monsters, score, player, save_message_displayed, save_message_timer, playing_level
    loaded_level = load_game_sql()
    HP = player.HP
    if loaded_level != level_num:
        # Если загружен другой уровень или сложность изменилась
        level_manager.scroll_pos = 0
        score = 0
        player.HP = player.max_HP

    playing_level = True  # Теперь в уровне подготовки к боссу

    if not level_manager.load_level(level_num):
        show_message(f"Ошибка загрузки уровня {level_num}")
        playing_level = False
        return

    # УБЕДИТЕСЬ, что level_manager знает о текущем уровне
    level_manager.current_level = level_num
    if level_num == Level:
        load_game_sql()
    player.respawn()
    player.rect.midbottom = (W // 2, H - GROUND_H)
    # Загружаем данные
    score = 0
    player.HP = load_upgrades()
    HP = player.HP
    Start_HP = HP
    Shield = player.shield

    # Определяем количество врагов в зависимости от сложности
    if level_num == 3:  # Подготовка к первому боссу
        enemy_counts = {
            0: {"common": 5, "speed": 5},
            1: {"common": 7, "speed": 7},
            2: {"common": 10, "speed": 10}
        }
        counts = enemy_counts.get(current_difficulty, enemy_counts[0])
        required_common = counts["common"]
        required_speed = counts["speed"]
        common_killed = 0
        speed_killed = 0
    else:  # Подготовка к финальному боссу (уровень 6)
        enemy_counts = {
            0: {"damager": 5, "jumper": 5},  # Дамагеры и прыгуны
            1: {"damager": 7, "jumper": 7},
            2: {"damager": 10, "jumper": 10}
        }
        counts = enemy_counts.get(current_difficulty, enemy_counts[0])
        required_common = counts["damager"]   # Используем damager вместо common
        required_speed = counts["jumper"]     # Используем jumper вместо speed
        common_killed = 0
        speed_killed = 0

    # Списки врагов
    monsters = []
    last_spawn_time = pygame.time.get_ticks()
    spawn_delay = 2000

    # Портал (изначально неактивен)
    portal_active = False
    portal_rect = portal_image.get_rect(center=(W // 2, H - GROUND_H - 45))

    # Другие переменные
    invincible = False
    invincible_end_time = 0

    # Получаем цвет фона уровня для создания градиента
    level_data = level_manager.levels[level_num]
    level_bg_gradient = level_data.get("bg_gradient", [(92, 148, 252)])

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
                    # Восстановление при смерти
                    load_game_sql()
                    load_upgrades()
                    player.respawn()
                    HP = Start_HP
                    Shield = player.shield
                    monsters.clear()
                    score = 0
                    common_killed = 0
                    speed_killed = 0
                    portal_active = False

        # Обновление игрока
        if not player.is_dead:
            player.handle_input()
        player.update(level_num)

        if player.is_out:
            continue

        # Спавн врагов
        if len(monsters) < 5 and now - last_spawn_time > spawn_delay and not player.is_dead:
            monster = Monster()

            # Определяем тип врага в зависимости от уровня
            if level_num == 3:  # Подготовка к боссу 3 уровня
                # Для 3 уровня оставляем обычных врагов
                if common_killed < required_common:
                    enemy_type = "common"
                else:
                    enemy_type = "speed"
            elif level_num == 6:  # Подготовка к боссу 6 уровня
                # Для 6 уровня используем врагов с соответствующих уровней
                if common_killed < required_common:  # common_killed теперь для дамагеров
                    enemy_type = "damager"
                else:
                    enemy_type = "jumper"
            else:
                enemy_type = "common"

            # Устанавливаем тип врага
            monster.enemy_type = enemy_type

            # ПЕРЕОПРЕДЕЛЯЕМ скорость и спрайты в зависимости от типа
            if enemy_type == "speed":
                monster.speed = 8
                monster.running_sprites_enemy_right = running_sprites_enemy_right_2
                monster.running_sprites_enemy_left = running_sprites_enemy_left_2
            elif enemy_type == "damager":
                monster.speed = 4
                monster.damage_amount = 2
                monster.running_sprites_enemy_right = running_sprites_damager_right
                monster.running_sprites_enemy_left = running_sprites_damager_left
            elif enemy_type == "jumper":
                monster.speed = 6
                monster.running_sprites_enemy_right = running_sprites_jumper_right
                monster.running_sprites_enemy_left = running_sprites_jumper_left
            else:
                monster.speed = 5
                monster.running_sprites_enemy_right = running_sprites_enemy_right
                monster.running_sprites_enemy_left = running_sprites_enemy_left

            # Обновляем изображение согласно типу
            monster.image = monster.running_sprites_enemy_right[0]
            monster.rect = monster.image.get_rect()

            monsters.append(monster)
            last_spawn_time = now

        # Обновление врагов
        for monster in list(monsters):
            monster.update()
            damage_taken = monster.damage_amount

            # Проверка коллизий
            if not player.is_dead and player.rect.colliderect(monster.rect) and not monster.is_dead:
                if (player.rect.bottom < monster.rect.centery and
                        player.y_speed > 0 and
                        abs(player.rect.centerx - monster.rect.centerx) < monster.rect.width / 2):
                    # Игрок прыгает на врага
                    monster.kill()
                    player.y_speed = -10
                    player.is_grounded = False
                    score += 1

                    # Увеличиваем счетчик соответствующего типа
                    if hasattr(monster, 'enemy_type'):
                        if level_num == 3:
                            if monster.enemy_type == "common":
                                common_killed += 1
                            else:
                                speed_killed += 1
                        else:  # level_num == 6
                            if monster.enemy_type == "damager":
                                common_killed += 1  # common_killed для дамагеров
                            else:
                                speed_killed += 1   # speed_killed для прыгунов

                    # Проверяем, активировался ли портал
                    if not portal_active and common_killed >= required_common and speed_killed >= required_speed:
                        portal_active = True
                elif not monster.damage_given and not invincible:
                    # Игрок получает урон
                    if Shield >= 1:
                        Shield -= 1
                        player.shield -= 1
                        save_upgrades()
                        invincible = True
                        invincible_end_time = now + 1000
                    else:
                        HP -= damage_taken
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

        # Проверка коллизии с порталом
        if portal_active and player.rect.colliderect(portal_rect):
            score = 0
            save_game_sql(level_num)
            save_secret_items()  # Сохраняем секретные предметы
            save_skin()  # Сохраняем скин
            run_boss_fight(level_num)

        # Отрисовка - создаем градиентный фон
        gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
        screen.blit(gradient_bg, (0, 0))

        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(ground_image, (500, H - GROUND_H))

        # Отрисовка портала (если активен)
        if portal_active:
            screen.blit(portal_image, portal_rect)

        # Отрисовка врагов
        for monster in monsters:
            monster.draw(screen)

        player.draw(screen)

        # UI
        draw_text("ПОДГОТОВКА К БОССУ", font_large, (255, 255, 255), screen, W // 2, 30)

        # Для 6 уровня показываем соответствующие типы врагов
        if level_num == 6:
            draw_text(f"Думбы: {common_killed}/{required_common}", font_medium, (255, 0, 0), screen, W // 4, 70)
            draw_text(f"Прыгуны: {speed_killed}/{required_speed}", font_medium, (0, 0, 255), screen, 3 * W // 4, 70)
        else:
            draw_text(f"Гумбы: {common_killed}/{required_common}", font_medium, (150, 50, 255), screen, W // 4, 70)
            draw_text(f"Купы: {speed_killed}/{required_speed}", font_medium, (0, 255, 150), screen, 3 * W // 4, 70)

        draw_text(f"HP: {HP}", font_medium, (255, 0, 255), screen, 100, 30)
        draw_text(f"Щиты: {Shield}", font_medium, (0, 0, 255), screen, W - 100, 30)

        # Показываем статус портала
        if portal_active:
            draw_text("Портал активирован!", font_medium, (0, 255, 0), screen, W // 2, 100)
        else:
            draw_text("Портал заблокирован", font_medium, (255, 0, 0), screen, W // 2, 100)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text_with_background("Игра сохранена", font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)

        # Сообщения о состоянии игрока
        if player.is_out:
            draw_text("Вы погибли! Нажмите любую клавишу для возрождения", font_medium, (255, 0, 0), screen, W // 2,
                      H // 2)
        elif player.is_dead and not player.is_out:
            draw_text("Вы погибли!", font_medium, (255, 0, 0), screen, W // 2, H // 3)

        pygame.display.flip()
        clock.tick(FPS)

    playing_level = False  # Выходим из уровня подготовки


def run_enemy_wave(level_num, enemy_count):
    global monsters, score, player, save_message_displayed, save_message_timer, playing_level
    loaded_level = load_game_sql()
    if loaded_level != level_num:
        # Если загружен другой уровень или сложность изменилась
        level_manager.scroll_pos = 0
        score = 0
        player.HP = player.max_HP

    playing_level = True  # Теперь в волне врагов

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
    level_manager.scroll_pos = 4000

    # Получаем градиент фона для уровня
    level_data = level_manager.levels[level_num]
    level_bg_gradient = level_data.get("bg_gradient", [(92, 148, 252)])

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

        # Обновление игрока (только если не мертв)
        if not player.is_dead:
            player.handle_input()
        player.update(level_num)

        # Если игрок мертв и вылетел, ждем возрождения
        if player.is_out:
            continue

        # Спавн врагов (только если игрок жив)
        if len(monsters) < 5 and now - last_spawn_time > spawn_delay and score < enemy_count and not player.is_dead:
            monster = Monster()

            # Устанавливаем тип врага в зависимости от уровня
            if level_num == 2:
                monster.enemy_type = "speed"
            elif level_num == 4:
                monster.enemy_type = "damager"  # Только дамагеры на 4 уровне
            elif level_num == 5:
                monster.enemy_type = "jumper"  # Только прыгуны на 5 уровне
            else:
                # Для других уровней оставляем обычных врагов
                monster.enemy_type = "common"

            # Устанавливаем свойства в зависимости от типа
            if monster.enemy_type == "speed":
                monster.speed = 8
                monster.running_sprites_enemy_right = running_sprites_enemy_right_2
                monster.running_sprites_enemy_left = running_sprites_enemy_left_2
            elif monster.enemy_type == "damager":
                monster.speed = 4
                monster.damage_amount = 2
                monster.running_sprites_enemy_right = running_sprites_damager_right
                monster.running_sprites_enemy_left = running_sprites_damager_left
            elif monster.enemy_type == "jumper":
                monster.speed = 6
                monster.running_sprites_enemy_right = running_sprites_jumper_right
                monster.running_sprites_enemy_left = running_sprites_jumper_left
            else:
                monster.speed = 5
                monster.running_sprites_enemy_right = running_sprites_enemy_right
                monster.running_sprites_enemy_left = running_sprites_enemy_left

            # Обновляем изображение и вызываем спавн
            monster.image = monster.running_sprites_enemy_right[0]
            monster.rect = monster.image.get_rect()
            monster.spawn()

            monsters.append(monster)
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
                    damage_taken = monster.damage_amount  # Используем damage_amount врага

                    if Shield >= 1:
                        Shield -= 1
                        player.shield -= 1
                        save_upgrades()
                        invincible = True
                        invincible_end_time = now + 1000
                    else:
                        HP -= damage_taken  # Используем переменную damage_taken
                        player.damaged()
                        monster.damage_given = True
                        invincible = True
                        invincible_end_time = now + 1000

                        # Показываем сообщение о повышенном уроне
                        if damage_taken > 1:
                            show_message(f"Критический удар! -{damage_taken} HP")

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

        # Отрисовка - создаем градиентный фон
        gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
        screen.blit(gradient_bg, (0, 0))

        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(ground_image, (500, H - GROUND_H))

        for monster in monsters:
            monster.draw(screen)

        player.draw(screen)

        # UI
        draw_text(f"Счет: {score}/{enemy_count}", font_large, (255, 255, 255), screen, W // 2, 30)
        draw_text(f"HP: {HP}", font_medium, (255, 255, 255), screen, 100, 30)
        draw_text(f"Щиты: {Shield}", font_medium, (255, 255, 255), screen, W - 100, 30)

        # Показываем информацию о врагах для уровней 4 и 5
        if level_num == 4:
            draw_text("Осторожно! Думбы наносят 2 единицы урона!", font_small, (255, 0, 0), screen, W // 2, 70)
        elif level_num == 5:
            draw_text("Осторожно! Прыгуны!", font_small, (0, 0, 255), screen, W // 2, 70)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text_with_background("Игра сохранена", font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)

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

    playing_level = False  # Выходим из волны врагов


def run_boss_fight(level_num):
    global boss, score, player, save_message_displayed, save_message_timer, playing_level

    playing_level = True  # Теперь в битве с боссом

    # УБЕДИТЕСЬ, что level_manager знает о текущем уровне
    level_manager.current_level = level_num  # ДОБАВЬТЕ ЭТУ СТРОЧКУ

    player.rect.midbottom = (W // 3, H - GROUND_H)
    boss = [Boss()]  # Теперь Boss будет использовать правильный уровень
    player.HP = load_upgrades()
    HP = player.HP
    Shield = player.shield
    invincible = False
    invincible_end_time = 0
    invincible_boss = False
    invincible_end_time_boss = 0
    boss_phase_transition = False  # Флаг перехода фазы босса
    boss_phase_transition_end = 0  # Время окончания перехода фазы

    # Получаем градиент фона для уровня
    level_data = level_manager.levels[level_num]
    level_bg_gradient = level_data.get("bg_gradient", [(92, 148, 252)])

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
        player.update(level_num)

        # Если игрок мертв и вылетел, ждем возрождения
        if player.is_out:
            # Отрисовка фона с градиентом
            gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
            screen.blit(gradient_bg, (0, 0))

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
                hp_percent = boss[0].HP / boss[0].max_HP
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
                draw_text(f"HP: {boss[0].HP}/{boss[0].max_HP}", font_small, (255, 255, 255), screen, W // 2, 80)

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
                    boss_obj.take_damage(player.attack)

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
                        HP -= boss_obj.get_attack_damage()  # Босс наносит больше урона
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
                boss_phase_transition_end = now + 3000
                boss_obj.phase_changed = False  # Сбрасываем флаг

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

        # Отрисовка для живого игрока - создаем градиентный фон
        gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
        screen.blit(gradient_bg, (0, 0))

        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(ground_image, (500, H - GROUND_H))

        for boss_obj in boss:
            boss_obj.draw(screen)

        player.draw(screen)

        if boss_phase_transition:
            # Эффект покраснения - красная вспышка
            flash_surface = pygame.Surface((W, H), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, 50))  # Полупрозрачный красный
            screen.blit(flash_surface, (0, 0))

        # UI для живого игрока
        draw_text("БОСС БИТВА", font_large, (255, 0, 0), screen, W // 2, 30)
        if boss and not boss[0].is_dead:
            # Полоска HP босса
            hp_percent = boss[0].HP / boss[0].max_HP
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
            draw_text(f"HP: {boss[0].HP}/{boss[0].max_HP}", font_small, (255, 255, 255), screen, W // 2, 80)

            # Показываем сообщение о неуязвимости во время перехода фазы
            if boss_phase_transition:
                draw_text("НЕУЯЗВИМОСТЬ!", font_medium, (255, 255, 0), screen, W // 2, 110)

        draw_text(f"HP игрока: {HP}", font_medium, (255, 255, 255), screen, 140, 30)
        draw_text(f"Щиты: {Shield}", font_medium, (255, 255, 255), screen, W - 100, 30)
        draw_text(f"Атака: {player.attack}", font_small, (255, 255, 255), screen, W // 2, H - 50)

        if save_message_displayed and pygame.time.get_ticks() - save_message_timer < 2000:
            draw_text_with_background("Игра сохранена", font_small, (0, 0, 0), (255, 255, 255), screen, W // 2, H // 2)

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

                player.update(level_num)

                # Отрисовка
                gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
                screen.blit(gradient_bg, (0, 0))
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

    playing_level = False  # Выходим из битвы с боссом


def complete_level(level_num, is_boss=False):
    global current_difficulty, player_points_easy, player_points_medium, player_points_hard, player, \
        playing_menu, from_level, from_menu, message, score, unlock_message, playing_level

    player.HP = load_upgrades()

    # Награда за уровень
    points_reward = {0: 3, 1: 4, 2: 5}
    reward = points_reward.get(current_difficulty, 5)

    if current_difficulty == 0:
        player_points_easy += reward
    elif current_difficulty == 1:
        player_points_medium += reward
    elif current_difficulty == 2:
        player_points_hard += reward

    # СОХРАНЕНИЕ ПРОГРЕССА УРОВНЯ - ОБНОВЛЯЕМ БАЗУ ДАННЫХ
    cursor = saving.cursor()
    table_name = ['levels_easy', 'levels_medium', 'levels_hard'][current_difficulty]

    # УБЕДИТЕСЬ ЧТО УРОВЕНЬ СУЩЕСТВУЕТ В ТАБЛИЦЕ
    cursor.execute(f'''
        INSERT OR IGNORE INTO {table_name} (level_number, cleared) 
        VALUES (?, ?)
    ''', (level_num, 0))

    # ОТМЕЧАЕМ УРОВЕНЬ КАК ПРОЙДЕННЫЙ
    cursor.execute(f'UPDATE {table_name} SET cleared=1 WHERE level_number=?', (level_num,))
    saving.commit()

    # ПРОВЕРЯЕМ И РАЗБЛОКИРУЕМ СКИНЫ ЗА ПОЛНОЕ ПРОХОЖДЕНИЕ
    unlock_completion_skins()

    # Проверяем, был ли разблокирован новый скин за полное прохождение
    completion_skin_unlocked = False
    completion_skin_name = ""

    if check_all_levels_completed(current_difficulty):
        if current_difficulty == 0:
            completion_skin_name = "Бронзовый герой"
        elif current_difficulty == 1:
            completion_skin_name = "Серебряный чемпион"
        elif current_difficulty == 2:
            completion_skin_name = "Золотой легенда"
        completion_skin_unlocked = True

    # Проверяем секреты уровня
    total_secrets = level_manager.get_level_secrets_count(level_num)
    found_secrets = level_manager.get_found_secrets_count(level_num)

    # Дополнительная награда за все секреты уровня
    bonus_reward = 0
    if found_secrets >= total_secrets > 0:
        bonus_reward = 2
        if current_difficulty == 0:
            player_points_easy += bonus_reward
        elif current_difficulty == 1:
            player_points_medium += bonus_reward
        elif current_difficulty == 2:
            player_points_hard += bonus_reward

    # Открываем улучшения для определенных уровней
    unlock_message = ""
    if level_num == 1:
        player.running_unlocked = True
        if player.max_HP < 5:
            player.max_HP += 2
        if player.attack < 2:
            player.attack = 2
        unlock_message = "Открыт навык: бег, +2HP, +1ATK"
    elif level_num == 2:
        player.double_jump_unlocked = True
        if player.max_HP < 8:
            player.max_HP += 3
        unlock_message = "Открыты навык: двойной прыжок, +3HP"
    elif level_num == 3 and is_boss:
        if player.max_HP < 10:
            player.max_HP += 2
        if player.attack < 3:
            player.attack = 3
        if current_difficulty == 0:
            player_points_easy += 1
        elif current_difficulty == 1:
            player_points_medium += 1
        elif current_difficulty == 2:
            player_points_hard += 1
        unlock_message = "Босс побежден! +2HP, +1ATK"
    elif level_num == 4:
        player.running_unlocked = True
        if player.max_HP < 12:
            player.max_HP += 2
        if player.attack < 4:
            player.attack = 4
        unlock_message = "+2HP, +1ATK"
    elif level_num == 5:
        player.double_jump_unlocked = True
        if player.max_HP < 13:
            player.max_HP += 1
        unlock_message = "+1HP"
    elif level_num == 6 and is_boss:
        if player.max_HP < 15:
            player.max_HP += 2
        if player.attack < 5:
            player.attack = 5
        if current_difficulty == 0:
            player_points_easy += 1
        elif current_difficulty == 1:
            player_points_medium += 1
        elif current_difficulty == 2:
            player_points_hard += 1
        unlock_message = "Босс побежден! +2HP, +1ATK"

    # ВТОРОЕ СОХРАНЕНИЕ - ВСЕХ УЛУЧШЕНИЙ
    player.HP = player.max_HP
    save_upgrades()
    save_secret_items()
    save_settings_sql()
    save_skin()  # Сохраняем скин

    # Формируем понятное сообщение с правильным склонением
    if is_boss:
        base_message = f"Кошмар побежден! +{format_points(reward)}"
    else:
        base_message = f"Воспоминание восстановлено! +{format_points(reward)}"

    if bonus_reward > 0:
        base_message += f" +{format_points(bonus_reward)} за секреты"

    if unlock_message:
        base_message += f" | {unlock_message}"

    # Добавляем сообщение о разблокировке скина за полное прохождение
    if completion_skin_unlocked:
        base_message += f" | Разблокирован скин: {completion_skin_name}!"

    if total_secrets > 0:
        base_message += f" | Секреты: {found_secrets}/{total_secrets}"

    message = base_message

    # Воспроизводим соответствующую катсцену
    if is_boss and level_num == 6:
        # Финальная катсцена после победы над последним боссом
        play_cutscene("game_complete")
        # Дополнительная катсцена пробуждения
        play_cutscene("final_awakening")
    elif is_boss:
        # Катсцена после победы над боссом
        play_cutscene("boss_defeated")
    else:
        # Катсцены после прохождения обычных уровней
        if level_num == 1:
            play_cutscene("level1_complete")
        elif level_num == 2:
            play_cutscene("level2_complete")
        elif level_num == 3:
            play_cutscene("level3_complete")
        elif level_num == 4:
            play_cutscene("level4_complete")
        elif level_num == 5:
            play_cutscene("level5_complete")

    # Показываем экран завершения с градиентным фоном
    end_time = pygame.time.get_ticks() + 4000
    while pygame.time.get_ticks() < end_time:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Создаем градиентный фон для экрана завершения
        level_data = level_manager.levels[level_num]
        level_bg_gradient = level_data.get("bg_gradient", [(92, 148, 252)])
        gradient_bg = create_gradient_surface(W, H, level_bg_gradient)
        screen.blit(gradient_bg, (0, 0))

        if is_boss:
            draw_text("КОШМАР ПОБЕЖДЕН!", font_large, (255, 215, 0), screen, W // 2, H // 3 - 50)
        else:
            draw_text("ВОСПОМИНАНИЕ ВОССТАНОВЛЕНО!", font_large, (255, 255, 255), screen, W // 2, H // 3 - 50)

        # Разбиваем длинное сообщение на несколько строк
        lines = []
        current_line = ""
        words = message.split()

        for word in words:
            test_line = current_line + word + " "
            if len(test_line) > 40:  # Ограничение длины строки
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)

        # Отображаем каждую строку
        for i, line in enumerate(lines):
            draw_text(line, font_small, (255, 255, 255), screen, W // 2, H // 2 + i * 30)

        pygame.display.flip()
        clock.tick(FPS)

    # ТРЕТЬЕ СОХРАНЕНИЕ - ОЧИСТКА ПРОГРЕССА УРОВНЯ
    cursor = saving.cursor()
    table_name = ['game_progress_easy', 'game_progress_medium', 'game_progress_hard'][current_difficulty]
    cursor.execute(f'DELETE FROM {table_name}')
    saving.commit()

    from_level = True
    from_menu = False
    playing_menu = True
    playing_level = False  # Выходим из уровня
    score = 0

    # Возвращаемся в меню уровней
    level_menu()


# Запуск игры
if __name__ == "__main__":
    load_settings_sql()
    Level = load_game_sql()
    load_skin()
    load_upgrades()
    load_unlocked_skins()
    load_secret_items()
    load_secret_points()
    apply_skin(current_skin_index)
    play_menu_music()
    main_menu()
    pygame.quit()