from main import GAME_HEIGHT, GAME_WIDTH
import pygame
import os
import random

BIRD_IMGS = [os.path.join(os.curdir, "imgs", "bird1.png"), os.path.join(os.curdir, "imgs", "bird2.png"), os.path.join(os.curdir, "imgs", "bird3.png")]
GRAVITY = 1000
SPEED = 5
DRAW_HITBOX = False

class Bird:

    def __init__(self) -> None:
        self.x = GAME_WIDTH*0.1
        self.y = GAME_HEIGHT/2
        self.jumped = False
        self.jump_vel = 350
        self.movement = True
        self.controls = True
        self.sprites = [pygame.transform.scale_by(pygame.image.load(x), 1.5) for x in BIRD_IMGS]
        self.frame = 0
        self.velocity = 0
        self.rect = pygame.Rect((self.x, self.y), (self.sprites[0].get_width(), self.sprites[0].get_height()))

    def draw(self, screen):
        if DRAW_HITBOX: pygame.draw.rect(screen, "green", self.rect, 2)
        self.sprites = [pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load(x), 1.5), 20-self.velocity/10) for x in BIRD_IMGS]
        if self.frame < 2.9: self.frame += 0.1
        else: self.frame = 0
        if int(self.frame) == 0: screen.blit(self.sprites[0], (self.x, self.y))
        if int(self.frame) == 1: screen.blit(self.sprites[1], (self.x, self.y))
        if int(self.frame) == 2: screen.blit(self.sprites[2], (self.x, self.y))

    def move(self, dt):
        if self.movement:
            self.y += self.velocity * dt + 0.5 * GRAVITY * dt**2
            self.velocity = self.velocity + GRAVITY * dt
            if self.velocity > 1000: self.velocity = 1000
            self.rect = pygame.Rect((self.x, self.y), (self.sprites[0].get_width(), self.sprites[0].get_height()))

    def jump(self):
        if self.movement and self.controls and not self.jumped:
            self.velocity = -self.jump_vel

class Ground:

    def __init__(self, x) -> None:
        self.x = x
        self.y = GAME_HEIGHT - GAME_HEIGHT*0.1
        self.movement = True
        self.sprite = pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "imgs", "base.png")), 1.5)
        self.rect = pygame.Rect((self.x, self.y), (self.sprite.get_width(), self.sprite.get_height()))

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))
        if DRAW_HITBOX: pygame.draw.rect(screen, "red", self.rect, 2)

    def move(self):
        if self.movement:
            if self.x < -self.sprite.get_width(): self.x += 2*self.sprite.get_width()
            self.x -= SPEED
            self.rect = pygame.Rect((self.x, self.y), (self.sprite.get_width(), self.sprite.get_height()))

    def collided(self, bird, grounds):
        if self.rect.colliderect(bird.rect):
            # for ground in grounds: ground.movement = False
            # bird.movement = False
            return True

class Pipes:

    def __init__(self) -> None:
        self.sprite_up = pygame.transform.rotate(pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "imgs", "pipe.png")), 1.5), 180)
        self.sprite_down = pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "imgs", "pipe.png")), 1.5)
        self.x = GAME_WIDTH
        self.y = random.randint(-self.sprite_up.get_height()+100, -100)
        self.distance = 150
        self.movement = True
        self.scored = False
        self.rect_up = pygame.Rect((self.x, self.y), (self.sprite_up.get_width(), self.sprite_up.get_height()))
        self.rect_down = pygame.Rect((self.x, self.y+self.sprite_up.get_height()+self.distance), (self.sprite_down.get_width(), self.sprite_down.get_height()))

    def draw(self, screen):
        screen.blit(self.sprite_up, (self.x, self.y))
        screen.blit(self.sprite_down, (self.x, self.y+self.sprite_up.get_height()+self.distance))

        if DRAW_HITBOX: pygame.draw.rect(screen, "orange", self.rect_up, 2)
        if DRAW_HITBOX: pygame.draw.rect(screen, "orange", self.rect_down, 2)

    def move(self):
        if self.movement:
            if self.x < -self.sprite_up.get_width():
                self.x = GAME_WIDTH
                self.y = random.randint(-self.sprite_up.get_height()+100, -100)
                self.scored = False
            self.x -= SPEED
            self.rect_up = pygame.Rect((self.x, self.y), (self.sprite_up.get_width(), self.sprite_up.get_height()))
            self.rect_down = pygame.Rect((self.x, self.y+self.sprite_up.get_height()+self.distance), (self.sprite_down.get_width(), self.sprite_down.get_height()))

    def collided(self, bird, grounds):
        if self.rect_up.colliderect(bird.rect) or self.rect_down.colliderect(bird.rect):
            # self.movement = False
            bird.controls = False
            # for ground in grounds: ground.movement = False
            return True