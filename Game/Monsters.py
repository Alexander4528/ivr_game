import pygame
import random
import settings

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
            self.rect.bottomright = (settings.W, 0)
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
            if self.rect.top > settings.H - settings.GROUND_H:
                self.is_out = True
        else:
            if self.rect.bottom > settings.H - settings.GROUND_H:
                self.is_grounded = True
                self.jump_num = 0
                self.y_speed = 0
                self.rect.bottom = settings.H - settings.GROUND_H

    def draw(self, surface):
        surface.blit(self.image, self.rect)