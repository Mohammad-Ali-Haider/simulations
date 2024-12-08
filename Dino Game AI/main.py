import neat
import pygame
import os
import random

GAME_WIDTH = 800
GAME_HEIGHT = 450

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode([GAME_WIDTH, GAME_HEIGHT])
clock = pygame.time.Clock()
dt = 0


SHOW_COLLISION_BOXES = False
GRAVITY = 3 * 10000
JUMP_VEL = 0.8 * 1000
TYPES = ["cactus", "bird"]
TYPE_SPRITE = [
    [
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus1.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus2.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus3.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus4.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus5.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "cacti", "cactus6.png")),
    ],
    [
        pygame.image.load(os.path.join(os.curdir, "assets", "Ptero1.png")),
        pygame.image.load(os.path.join(os.curdir, "assets", "Ptero2.png")),
    ],
]
LEVELS_OF_FLIGHT = [5, 35, 50]
FONT = pygame.font.Font(os.path.join(os.curdir, "assets", "PressStart2P-Regular.ttf"), 16)
GEN = 0

jump = pygame.mixer.Sound(os.path.join(os.curdir, "assets", "sfx", "jump.mp3"))
lost = pygame.mixer.Sound(os.path.join(os.curdir, "assets", "sfx", "lose.mp3"))
points = pygame.mixer.Sound(os.path.join(os.curdir, "assets", "sfx", "100points.mp3"))

OBSTICLES = list(zip(TYPES, TYPE_SPRITE))

class App:

    def __init__(self, config_path) -> None:
        self.screen = pygame.display.set_mode([GAME_WIDTH, GAME_HEIGHT])
        self.clock = pygame.time.Clock()

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

        p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.run, 1000)


    def draw(self, dinos, grounds, obsticles, score, ge, gen):
        self.screen.fill("white")
        score_text = FONT.render(f"Score: {int(score)}", True, (102, 102, 102), (255, 255, 255))
        speed_text = FONT.render(f"Speed: {int(SPEED)}", True, (102, 102, 102), (255, 255, 255))
        gen_text = FONT.render(f"Gen: {gen}", True, (102, 102, 102), (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(speed_text, (20, 40))
        self.screen.blit(gen_text, (20, 80))
        for ground in grounds:
                ground.draw(self.screen)
        for obsticle in obsticles:
                obsticle.draw(self.screen)
        for dino in dinos:
            dino.draw(screen)
        for x in ge:
            fitness_text = FONT.render(f"Fitness: {int(x.fitness)}", True, (102, 102, 102), (255, 255, 255))
            self.screen.blit(fitness_text, (10, 60))
        pygame.display.flip()

    def run(self, genomes, config):

        global SPEED, GEN
        SPEED = 10
        GEN += 1

        nets = []
        ge = []
        dinos = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            dinos.append(Dino())
            g.fitness = 0
            ge.append(g)
        print(len(dinos), len(nets), len(ge))

        running = True
        movement = True
        score = 0

        grounds = [Ground(0), Ground(624*3)]
        obsticles = [Obsticle(700)]

        while running:
            [exit() for event in pygame.event.get() if event.type == pygame.QUIT]
            dt = self.clock.tick(60)/ 1000

            if len(dinos) == 0:
                break

            if movement == True:
                score += 0.25

                for ground in grounds:
                    ground.move(SPEED)

                for obsticle in obsticles:
                    obsticle.move(SPEED)

                for x, dino in enumerate(dinos):

                    ge[x].fitness += 0.1

                    output = nets[x].activate((dino.y, obsticles[0].x - dino.x, abs(dino.y - obsticles[0].y), obsticles[0].y, obsticles[0].type, SPEED, dino.rect.top - obsticles[0].rect.bottom, obsticles[0].rect.width))

                    if output[0] > 0.5:
                        dino.jump()
                    if output[1] > 0.5:
                        if dino.isGrounded: dino.duck()
                    else: dino.reset_collider()
                    if output[2] > 0.5:
                        dino.smash_down()

                    if score % 100 == 0: 
                        ge[x].fitness += 1

                    for ground in grounds:
                        if ground.collide(dino): dino.isGrounded = True
                        dino.move(dt)
                        
                    for obsticle in obsticles:
                        if obsticle.collide(dino): 
                            ge[x].fitness -= 1
                            dinos.pop(x)
                            nets.pop(x)
                            ge.pop(x)

                self.draw(dinos, grounds, obsticles, score, ge, GEN)
                SPEED += 0.0025


class Dino:

    def __init__(self) -> None:
        self.x = 100
        self.y = 325
        self.velocity = 0
        self.frame = 0
        self.isDuck = False
        self.isGrounded = False
        self.sprites = [
            pygame.image.load(os.path.join(os.curdir, "assets", "Dino1.png")),
            pygame.image.load(os.path.join(os.curdir, "assets", "Dino2.png")),
            pygame.image.load(os.path.join(os.curdir, "assets", "DinoJumping.png")),
            pygame.image.load(os.path.join(os.curdir, "assets", "DinoDucking1.png")),
            pygame.image.load(os.path.join(os.curdir, "assets", "DinoDucking2.png"))
        ]
        self.rect = pygame.Rect((self.x, self.y), (self.sprites[0].get_width(), self.sprites[0].get_height()))

    def draw(self, screen):
        self.screen = screen or None
        if int(self.frame) >= 2: self.frame = 0
        if self.isDuck:
            if int(self.frame) == 0: screen.blit(self.sprites[3], (self.x, self.y+self.sprites[0].get_height()/2-10))
            if int(self.frame) == 1: screen.blit(self.sprites[4], (self.x, self.y+self.sprites[0].get_height()/2-10))
        elif self.isGrounded:
            if int(self.frame) == 0: screen.blit(self.sprites[0], (self.x, self.y))
            elif int(self.frame) == 1: screen.blit(self.sprites[1], (self.x, self.y))
        else:
            screen.blit(self.sprites[2], (self.x, self.y))
        self.frame += 0.2

        if SHOW_COLLISION_BOXES: pygame.draw.rect(screen, "green", self.rect, 2)

    def jump(self):
        if self.isGrounded:
            self.isGrounded = False
            self.velocity = -JUMP_VEL
            self.reset_collider()

    def duck(self):
        self.rect = pygame.Rect((self.x, self.y+self.sprites[0].get_height()/2-10), (self.sprites[0].get_width()+10, self.sprites[0].get_height()/2+10))
        self.isDuck = True

    def smash_down(self):
        self.velocity = 1000

    def reset_collider(self):
        self.rect = pygame.Rect((self.x, self.y), (self.sprites[0].get_width(), self.sprites[0].get_height()))
        self.isDuck = False

    def move(self, dt):
        if not self.isGrounded or self.velocity<0:
            s = self.velocity * dt + 0.5 * GRAVITY * dt**2
            self.velocity += GRAVITY/1000
            self.y += s
            if self.y > 329: self.y = 329
            if self.y < 329: self.isGrounded = False
            self.rect = pygame.Rect((self.x, self.y), (self.sprites[0].get_width(), self.sprites[0].get_height()))


class Obsticle:

    def __init__(self, x) -> None:
        self.x = x
        self.y = 375
        self.scaleFactor = 1.25
        self.obsticle = OBSTICLES[random.randint(0, len(OBSTICLES)-1)]
        if random.randint(1, 100) > 25:
            self.obsticle = OBSTICLES[0]
            self.sprite = self.obsticle[1][random.randint(0,5)]
            self.type = 0
        else:
            self.obsticle = OBSTICLES[0]
            self.sprite = self.obsticle[1][0]
            self.y = self.y - LEVELS_OF_FLIGHT[random.randint(0,2)]
            self.type = 1
        self.sprite = pygame.transform.scale_by(self.sprite, self.scaleFactor)
        self.rect_coords = [self.sprite.get_width(), self.sprite.get_height()]
        print(self.rect_coords)
        self.rect = pygame.Rect((self.x, self.y), (self.rect_coords))

    def move(self, SPEED):
        self.x -= SPEED
        self.rect = pygame.Rect((self.x, self.y-self.rect_coords[1]), (self.rect_coords))
        if self.x < -self.rect_coords[0]:
            self.y = 375
            if random.randint(1, 100) > 25:
                self.obsticle = OBSTICLES[0]
                self.sprite = self.obsticle[1][random.randint(0,5)]
                self.sprite = pygame.transform.scale_by(self.sprite, self.scaleFactor)
            else:
                self.obsticle = OBSTICLES[1]
                self.sprite = self.obsticle[1][0]
                self.y = self.y - LEVELS_OF_FLIGHT[random.randint(0,2)]
                self.sprite = pygame.transform.scale_by(self.sprite, 1)
            
            self.rect_coords = [self.sprite.get_width(), self.sprite.get_height()]
            self.x = GAME_WIDTH

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y-self.sprite.get_height()))

        if SHOW_COLLISION_BOXES: pygame.draw.rect(screen, "red", self.rect, 2)

    def collide(self, dino):
        if self.rect.colliderect(dino.rect):
            return True

class Ground:

    def __init__(self, x) -> None:
        self.x = x
        self.y = 375
        self.sprite = pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "assets", "ground.png")).convert_alpha(), 3)
        self.rect = pygame.Rect((self.x, self.y), (GAME_WIDTH, self.sprite.get_height()))

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y-30))

        if SHOW_COLLISION_BOXES: pygame.draw.rect(screen, "blue", self.rect, 2)

    def move(self, SPEED):
        self.x -= SPEED
        if self.x < - self.sprite.get_width(): self.x += 2*self.sprite.get_width()-100

    def collide(self, dino):
        if self.rect.colliderect(dino.rect):
            dino.y = 329
            return True


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    
    app = App(config_path)
