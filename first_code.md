    


    import pygame
    import random
    import json
    
    from pygame import Surface
    
    pygame.init()
    W = 800
    H = 600
    screen = pygame.display.set_mode((W, H))
    FPS = 60
    clock = pygame.time.Clock()
    font_path = 'caviar-dreams.ttf'
    font_large = pygame.font.Font(font_path, 48)
    font_small = pygame.font.Font(font_path, 24)
    
    ground_image: Surface = pygame.image.load('ground.jpg')
    ground_image = pygame.transform.scale(ground_image, (804, 60))
    GROUND_H = ground_image.get_height()
    
    me_image = pygame.image.load('Me.png')
    me_image = pygame.transform.scale(me_image, (70, 80))
    
    portal_image = pygame.image.load('p2.gif')  # Замените на изображение флага
    portal_image = pygame.transform.scale(portal_image, (80, 90))  # Подберите подходящий размер флага
    
    def save_game(play):
        game_state = {
            'player_pos': (play.rect.x, play.rect.y),
        }
        with open('last.json', 'w') as f:
            json.dump(game_state, f)
    
    def load_game(play):
        try:
            with open('last.json', 'r') as f:
                game_state = json.load(f)
                play.rect.midbottom = game_state['player_pos']  # Загружаем позицию игрока
                return play.rect.midbottom
        except (FileNotFoundError, json.JSONDecodeError):
            play.rect.midbottom = (W - 700, H - GROUND_H - 50)
            return play.rect.midbottom
    
    class Player:
    
        def __init__(self):
            self.running_sprites_right = [pygame.transform.scale(pygame.image.load(f'right{i}.png'), (70, 80))
                                          for i in range(1, 4)]
            self.running_sprites_left = [pygame.transform.scale(pygame.image.load(f'left{i}.png'), (70, 80))
                                         for i in range(1, 4)]
            self.idle_sprite = me_image
            self.image = self.idle_sprite
            self.rect = self.image.get_rect()
            self.rect.center = (100, H - GROUND_H - self.rect.height)
            self.speed = 5
            self.gravity = 0.4
            self.y_speed = 0
            self.is_grounded = False
            self.run_animation_index = 0
            self.last_update_time = pygame.time.get_ticks()
    
        def handle_input(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                self.update_animation()
            elif keys[pygame.K_d]:
                self.rect.x += self.speed
                self.update_animation()
            else:
                self.image = self.idle_sprite
                self.run_animation_index = 0
            if self.is_grounded and keys[pygame.K_SPACE]:
                self.jump()
    
        def update_animation(self):
            keys = pygame.key.get_pressed()
            now = pygame.time.get_ticks()
            if now - self.last_update_time > 70:
                if keys[pygame.K_a]:
                    self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_left)
                    self.image = self.running_sprites_left[self.run_animation_index]
                    self.last_update_time = now
                elif keys[pygame.K_d]:
                    self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_right)
                    self.image = self.running_sprites_right[self.run_animation_index]
                    self.last_update_time = now
    
        def jump(self):
            self.y_speed = -10
            self.is_grounded = False
    
        def update(self):
            if self.rect.left < 0:
                self.rect.left = W - 70
                portal_rect.center = (W - 500, H - GROUND_H - 45)
            elif self.rect.right > W:
                self.rect.right = 70
                portal_rect.center = (W - 300, H - GROUND_H - 45)
            self.y_speed += self.gravity
            self.rect.y += self.y_speed
    
            # Приземление
            if self.rect.bottom > H - GROUND_H:
                self.rect.bottom = H - GROUND_H
                self.y_speed = 0
                self.is_grounded = True
    
        def draw(self, surface):
            surface.blit(self.image, self.rect)
    
    
    # Инициализация игрока
    player = Player()
    
    # Точка перехода (флаг)
    portal_rect = portal_image.get_rect()
    portal_rect.center = (W - 300, H - GROUND_H - 45)  # Позиция флага
    player_rect = me_image.get_rect()
    player_rect.midbottom = load_game(player)
    save_message_displayed = False
    save_message_timer = 0
    running = True
    while running:
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s:  # Клавиша для сохранения
                    save_game(player)  # Сохраняем положение игрока
                    save_message_displayed = True
                    save_message_timer = pygame.time.get_ticks()  # Запоминаем время сохранения
        screen.fill((92, 148, 252))  # Цвет фона
        screen.blit(ground_image, (0, H - GROUND_H))
        screen.blit(portal_image, portal_rect.topleft)
        player.draw(screen)
        if save_message_displayed:
            save_message_text = font_small.render("Игра сохранена", True, (255, 255, 255))
            save_message_rect = save_message_text.get_rect(center=(W // 2, H // 2))
            screen.blit(save_message_text, save_message_rect)
            if now - save_message_timer > 2000:
                save_message_displayed = False
        player.handle_input()
        player.update()
    
        # Переход через портал
        if player.rect.colliderect(portal_rect):
            # Сохраняем положение игрока перед переходом
            save_game(player)
    
            # Переход на второй уровень
            player.rect.midbottom = (W // 2, H // 2)
            clock = pygame.time.Clock()
            font_path = 'caviar-dreams.ttf'
            font_large = pygame.font.Font(font_path, 48)
            font_small = pygame.font.Font(font_path, 24)
            game_over = False
            retry_text = font_small.render('PRESS ANY KEY', True, (255, 255, 255))
            retry_rect = retry_text.get_rect()
            retry_rect.midtop = (W // 2, H // 2)
    
            ground_image = pygame.image.load('ground.jpg')
            ground_image = pygame.transform.scale(ground_image, (804, 60))
            GROUND_H = ground_image.get_height()
    
            monster2_image = pygame.image.load('Enemyleft.png')
            monster2_image = pygame.transform.scale(monster2_image, (90, 90))
    
            monster_image = pygame.image.load('Enemy.png')
            monster_image = pygame.transform.scale(monster_image, (90, 90))
    
            died_image = pygame.image.load('EnemyDead.png')
            died_image = pygame.transform.scale(died_image, (90, 90))
    
    
            def save_game(score):
                game_state = {
                    'player_pos': (W // 2, H - GROUND_H),
                    'score': score,
                    'delay': spawn_delay
                }
                with open('save_game.json', 'w') as f:
                    json.dump(game_state, f)
    
    
            def load_game(play):
                try:
                    with open('save_game.json', 'r') as f:
                        game_state = json.load(f)
                        play.rect.midbottom = game_state['player_pos']
                        play.is_dead = False
                        score = game_state['score']
                        return score
                except (FileNotFoundError, json.JSONDecodeError):
                    print("Не удалось загрузить сохранённую игру, начинается новая игра.")
                    return 0
    
    
            class Entity:
                def __init__(self, image):
                    self.image = image
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
    
                def handle_input(self):
                    pass
    
                def kill(self, dead_image):
                    self.image = dead_image
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
                        self.handle_input()
    
                        if self.rect.bottom > H - GROUND_H:
                            self.is_grounded = True
                            self.jump_num = 0
                            self.y_speed = 0
                            self.rect.bottom = H - GROUND_H
    
                def draw(self, surface):
                    surface.blit(self.image, self.rect)
    
    
            class Player(Entity):
                def __init__(self):
                    super().__init__(me_image)
                    self.running_sprites_right = [pygame.transform.scale(pygame.image.load(f'right{i}.png'), (70, 80))
                                                  for i in range(1, 5)]
                    self.running_sprites_left = [pygame.transform.scale(pygame.image.load(f'left{i}.png'), (70, 80))
                                                 for i in range(1, 5)]
                    self.idle_sprite = me_image
                    self.image = self.idle_sprite
                    self.rect = self.image.get_rect()
                    self.rect.center = (100, H - GROUND_H - self.rect.height)
                    self.speed = 5
                    self.gravity = 0.4
                    self.y_speed = 0
                    self.run_animation_index = 0
                    self.last_update_time = pygame.time.get_ticks()
                    self.respawn()
    
                def handle_input(self):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_a]:
                        self.rect.x -= self.speed
                        self.update_animation()
                    elif keys[pygame.K_d]:
                        self.rect.x += self.speed
                        self.update_animation()
                    else:
                        self.image = self.idle_sprite
                        self.run_animation_index = 0
                    if self.is_grounded and keys[pygame.K_SPACE]:
                        self.jump()
    
                def update_animation(self):
                    keys = pygame.key.get_pressed()
                    now = pygame.time.get_ticks()
                    if now - self.last_update_time > 70:
                        if keys[pygame.K_a]:
                            self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_left)
                            self.image = self.running_sprites_left[self.run_animation_index]
                            self.last_update_time = now
                        elif keys[pygame.K_d]:
                            self.run_animation_index = (self.run_animation_index + 1) % len(self.running_sprites_right)
                            self.image = self.running_sprites_right[self.run_animation_index]
                            self.last_update_time = now
    
                def respawn(self):
                    self.is_out = False
                    self.is_dead = False
                    self.rect.midbottom = (W // 2, H - GROUND_H)
    
                def jump(self):
                    self.y_speed = -10
                    self.is_grounded = False
    
                def update(self):
                    super().update()
                    if self.rect.left < 0:
                        self.rect.left = 0
                    elif self.rect.right > W:
                        self.rect.right = W
    
    
            class Monster(Entity):
                def __init__(self):
                    super().__init__(monster_image)
                    self.spawn()
    
                def spawn(self):
                    direction = random.randint(0, 1)
                    if direction == 0:
                        self.x_speed = self.speed
                        self.rect.bottomright = (0, 0)
                        self.image = pygame.transform.scale(monster2_image, (90, 90))
                    else:
                        self.x_speed = -self.speed
                        self.rect.bottomright = (W, 0)
                        self.image = pygame.transform.scale(monster_image, (90, 90))
    
                def update(self):
                    super().update()
                    if (self.x_speed > 0 and self.rect.left > W) or (self.x_speed < 0 and self.rect.right < 0):
                        self.is_out = True
    
    
            player = Player()
            score = 0
    
            monsters = []
            INIT_DELAY = 2000
            spawn_delay = INIT_DELAY
            DECREASE_BASE = 1.01
            last_spawn_time = pygame.time.get_ticks()
    
            save_message_displayed = False
            save_message_timer = 0
            now = pygame.time.get_ticks()
    
            running = True
            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                    elif e.type == pygame.KEYDOWN:
                        if player.is_out:
                            score = load_game(player)
                            spawn_delay = INIT_DELAY
                            last_spawn_time = pygame.time.get_ticks()
                            player.respawn()
                            monsters.clear()
                        elif e.key == pygame.K_s:  # Клавиша для сохранения
                            save_game(score)
                            save_message_displayed = True
                            save_message_timer = pygame.time.get_ticks()  # Запоминаем время сохранения
    
                clock.tick(FPS)
                screen.fill((92, 148, 252))
    
                screen.blit(ground_image, (0, H - GROUND_H))
    
                score_text = font_large.render(str(score), True, (255, 255, 255))
                score_rect = score_text.get_rect()
                if player.is_out:
                    score_rect.midbottom = (W // 2, H // 2)
                    screen.blit(retry_text, retry_rect)
                else:
                    player.update()
                    player.draw(screen)
                    now = pygame.time.get_ticks()
                    elapsed = now - last_spawn_time
                    if elapsed > spawn_delay:
                        last_spawn_time = now
                        monsters.append(Monster())
    
                    for monster in list(monsters):
                        if monster.is_out:
                            monsters.remove(monster)
                        else:
                            monster.update()
                            monster.draw(screen)
                        if not player.is_dead and not monster.is_dead and player.rect.colliderect(monster.rect):
                            if player.rect.bottom - player.y_speed < monster.rect.top:
                                monster.kill(died_image)
                                player.jump()
                                score += 1
                                spawn_delay = INIT_DELAY / (DECREASE_BASE ** score)
                            else:
                                player.kill(me_image)
    
                    score_rect.midtop = (W // 2, 5)
    
                if save_message_displayed:
                    save_message_text = font_small.render("Игра сохранена", True, (255, 255, 255))
                    save_message_rect = save_message_text.get_rect(center=(W // 2, H // 2))
                    screen.blit(save_message_text, save_message_rect)
                    if now - save_message_timer > 2000:
                        save_message_displayed = False
                if score == 30:
                    win_text = font_small.render("Уровень пройден!", True, (255, 255, 255))
                    win_rect = win_text.get_rect(center=(W // 2, H // 2))
                    screen.blit(win_text, win_rect)
                    monsters.clear()
                    with open('save_game.json', 'w') as f:
                        pass
                    with open('last.json', 'w') as d:
                        pass
                screen.blit(score_text, score_rect)
                pygame.display.flip()
            quit()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
