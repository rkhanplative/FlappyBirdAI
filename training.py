import pygame
from pygame.locals import *
import sys
import random
import neat
import os
import pickle

#Bird Class
class bird:
    def __init__(self, screen):
        self.screen = screen

        #Bird Starting State
        self.height = 100
        self.angle = 0 
        self.alive = True

        #Declaration of original bird image, saved for reusing when rotating
        self.face_original = pygame.image.load("bird.png").convert_alpha()
        self.face = pygame.image.load("bird.png").convert_alpha()

        #Delcaring Distances from Pipe, which will be used by AI
        self.distFromTop, self.distFromBottom = 0,0
    def jump(self):
        #Restraigthens Bird
        self.angle = 0
        #Boosts Bird Height 100 Pixels
        self.height -= 100
    def showBird(self):
        #Puts Bird to Screen
        self.screen.blit(self.face,(80,self.height))
    def gravity(self):
        #If Bird heigth is above ground, lower bird height closer to ground by 5 pixels
        if self.height <= 550:
            self.height += 5    
        #If Bird Hits Ground, declare it dead
        if self.height >= 550:
            self.alive = False
    def rotate(self,angle):
        #While Bird is not at a -90 degree angle, decrement it by the inputted angle
        if self.angle > -90:
            self.angle += angle  
            self.face = pygame.transform.rotate(self.face_original, self.angle)
    def setDists(self, pipe):
        self.distFromTop = ((float(pipe.bottomHeight)-float(self.height))**2 + (float(pipe.x)-float(80))**2) ** 0.5
        self.distFromBotttom = ((float(pipe.topHeight)-float(self.height+35.0))**2 + (float(pipe.x)-float(80))**2) ** 0.5
#Pipe Class
class pipe: 
    def __init__(self,screen,center):
        #loading pygame screen object
        self.screen = screen
         
        #loading original pipe image for manipulation
        self.img = pygame.image.load("pipe.png").convert_alpha()
        
        #Setting of Bottom Pipe and Top Pipe Height, given center, using a gap of 180 pixels between the two pipes (90 from center both ways)
        self.bottomHeight = center + 90
        self.topHeight = center - 90
        
        #Starting Pipe at Right Hand edge of Screen
        self.x = 480

        #Bottom Pipe
        self.bottomPipe = self.img.subsurface((0,0,self.img.get_width(),593-self.bottomHeight))


        #Top Pipe
        self.topPipe = pygame.transform.flip(self.img.subsurface((0,0,self.img.get_width(),self.topHeight)), False, True)

    def show(self):
        #Showing Bottom Pipe 
        self.screen.blit(self.bottomPipe,(self.x,self.bottomHeight))

        #Showing Top Pipe
        self.screen.blit(self.topPipe,(self.x,0))
    def incX(self, x):
        #Move pipe x units to the left
        self.x += x
#Game Class
def main(genomes,config): 
    #Setting Up Basic Pygame Requirements
    pygame.init() 
    pygame.font.init()
    screen = pygame.display.set_mode([480,735])
    clock = pygame.time.Clock()
    #Setting up variables for NEAT implementation
    nets = []
    birds = []
    ge = []

    #Filling NEAT variables
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(bird(screen))
        g.fitness = 0
        ge.append(g)


        
    #Initializing Bird, Pipes, and Player Lebel
    pipes = []
    level = 0

    #Loading In Background Elements
    bottom = pygame.image.load("bottom.png").convert_alpha()
    back = pygame.image.load("background.jpg").convert()
        
    #Initialization of AnimCount, variable that is gradually incremented, and utlized in animation process
    animCount = 0

        #Adding First Pipe
    pipes.append(pipe(screen,random.randint(100,483)))

        #Setting Up Score Level Text
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render('Level 0',False,(255,255,255))

    run = True
    while run:
        animCount += 1
        clock.tick(50)
        if len(birds) < 1: run = False

        for x, b in enumerate(birds):
            ge[x].fitness += 0.1
            
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
                pygame.quit()
                #If Player presses space, the bird should jump
                '''if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and flappy.alive:
                        flappy.jump()
                        
                        #Recalculating Distances to Pipes
                        flappy.setDists(pipes[0])
                '''
                
        for x, b in enumerate(birds):
            out = nets[x].activate((b.height,abs(pipes[0].topHeight-b.height),abs(pipes[0].bottomHeight-b.height),abs(110-pipes[0].x)))
            if out[0] > 0.5: b.jump()
            
        #Blitting City Background
        screen.blit(back,(0,0))

        #Blitting Bottom Portion, which scrolls/moves with player
        screen.blit(bottom,(-((0+3*animCount)%480)+480,583))
        screen.blit(bottom,(-((0+3*animCount)%480),583))

        #Move Pipes to the left by 2.5 units, and show them
        for element in pipes:
            element.incX(-2.5)
            element.show()
            
        #If a pipe has passed the middle point, append a new pipe to pipes list
        if pipes[0].x == 190:
            pipes.append(pipe(screen,random.randint(150,410)))
        
        if level > 100: break
        #If a pipe has passed the screen, remove it from pipe list, and increase player level by 1, and update level score text
        if pipes[0].x < -10: 
            pipes.pop(0)
            level += 1
            for g in ge:
                g.fitness += 1.5
            text = font.render('Level '+str(level),False,(255,255,255))
        
        #If bird collides with pipe, declare it to be dead
        #***reminder, 110 is the center x value of the bird at all times
            
        for x, b in enumerate(birds):
            if 110 in range(int(pipes[0].x),int(pipes[0].x)+70) and (b.height in range  (0,pipes[0].topHeight) or b.height+50 in range(pipes[0].bottomHeight,593)):
                ge[birds.index(b)].fitness -= 1
                nets.pop(birds.index(b))
                ge.pop(birds.index(b))
                birds.pop(birds.index(b))
            if b.height >= 550 or b.height <= 0:
                ge[birds.index(b)].fitness -= 1
                nets.pop(birds.index(b))
                ge.pop(birds.index(b))
                birds.pop(birds.index(b))
        
            #Initialize Flappy's Gravity
            b.gravity()

            #Gradually rotate bird as it falls
            b.rotate(-1.5)

            #Show Bird to Screen
            b.showBird()

        #Show Level Text to screen
        screen.blit(text,(20,20))

        #Update pygame window
        pygame.display.flip()


def run(config_file):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 10)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)