import pygame
import os
from classes import *
import neat

pygame.init()
FONT = pygame.font.SysFont("Arial", 32)
BG = pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "imgs", "bg.png")),1.5)
GAME_RES = (GAME_WIDTH, GAME_HEIGHT) = (BG.get_width(), BG.get_height())
FPS = 60
GEN = 0

class App:
    def __init__(self, config_path) -> None:
        self.screen = pygame.display.set_mode(GAME_RES)
        self.clock = pygame.time.Clock()

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

        p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.run, 1000)

        

    def draw(self, birds, grounds, pipes, GEN, fitness):
        self.screen.fill("white")
        self.screen.blit(BG, (0, 0))
        gen_text = FONT.render(f"Gen: {GEN}", True, (102, 102, 102), None)
        self.screen.blit(gen_text, (10, 10))
        fitness_text = FONT.render(f"Fitness: {int(fitness)}", True, (102, 102, 102), None)
        self.screen.blit(fitness_text, (10, 40))
        for bird in birds:
            bird.draw(self.screen)
        for ground in grounds:
            ground.draw(self.screen)
        for pipe in pipes:
            pipe.draw(self.screen)
        pygame.display.flip()

    def run(self, genomes, config):
        global GEN
        running = True
        GEN += 1

        nets = []
        ge = []
        birds = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            birds.append(Bird())
            g.fitness = 0
            ge.append(g)

        grounds = [Ground(0), Ground(pygame.transform.scale_by(pygame.image.load(os.path.join(os.curdir, "imgs", "base.png")), 1.5).get_width())]
        pipes = [Pipes()]
        dt = 0

        while running:
            [exit() for event in pygame.event.get() if event.type == pygame.QUIT]
            if len(birds) == 0: break

            self.draw(birds, grounds, pipes, GEN, ge[0].fitness)

            for x, bird in enumerate(birds):
                bird.move(dt)
                ge[x].fitness += 0.1

                output = nets[x].activate((bird.y, abs(pipes[0].rect_down.top - bird.rect.bottom), abs(pipes[0].rect_up.bottom - bird.rect.top), bird.x - pipes[0].x))

                if output[0] > 0.5:
                    bird.jump()   

                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] and not bird.jumped and bird.controls:
                    bird.jumped = True
                    bird.jump()
                elif not keys[pygame.K_SPACE]: bird.jumped = False
            for ground in grounds:
                ground.move()
                for x, bird in enumerate(birds):
                    if ground.collided(bird, grounds):
                        ge[x].fitness -= 1
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)

            for pipe in pipes:
                pipe.move()
                for x, bird in enumerate(birds):
                    if pipe.collided(bird, grounds):
                        ge[x].fitness -= 1
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)

                    elif bird.y < 0 or bird.y > GAME_HEIGHT:
                        ge[x].fitness -= 2
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)

                    elif bird.x > pipe.x+pipe.sprite_up.get_width() and not pipe.scored:
                        ge[x].fitness += 5
                        pipe.scored = True

            dt = self.clock.tick(FPS)/1000



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    APP = App(config_path)