import pygame
from pygame.locals import *
import sys
import random
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
        self.distFromTop = (float(pipe.bottomHeight)**2 + float(self.height)**2) ** 0.5
        self.distFromBotttom = (float(pipe.topHeight)**2 + float(self.height+35.00)**2) ** 0.5
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
class game:
    def __init__(self): 
        #Setting Up Basic Pygame Requirements
        pygame.init() 
        pygame.font.init()
        self.screen = pygame.display.set_mode([480,735])

        #Initializing Bird, Pipes, and Player Lebel
        self.flappy = bird(self.screen)
        self.pipes = []
        self.level = 0

        #Loading In Background Elements
        self.bottom = pygame.image.load("bottom.png").convert_alpha()
        self.back = pygame.image.load("background.jpg").convert()
    
    def setup(self):     
        #Initialization of AnimCount, variable that is gradually incremented, and utlized in animation process
        animCount = 0

        #Adding First Pipe
        self.pipes.append(pipe(self.screen,random.randint(100,483)))

        #Setting Up Score Level Text
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Level 0',False,(255,255,255))

        while self.flappy.alive:
            animCount += 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                #If Player presses space, the bird should jump
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.flappy.alive:
                        self.flappy.jump()
                        
                        #Recalculating Distances to Pipes
                        self.flappy.setDists(self.pipes[0])
        
            #Blitting City Background
            self.screen.blit(self.back,(0,0))

            #Blitting Bottom Portion, which scrolls/moves with player
            self.screen.blit(self.bottom,(-((0+3*animCount)%480)+480,583))
            self.screen.blit(self.bottom,(-((0+3*animCount)%480),583))

            #Move Pipes to the left by 2.5 units, and show them
            for element in self.pipes:
                element.incX(-2.5)
                element.show()
            
            #If a pipe has passed the middle point, append a new pipe to pipes list
            if self.pipes[0].x == 190:
                self.pipes.append(pipe(self.screen,random.randint(150,410)))
            
            #If a pipe has passed the screen, remove it from pipe list, and increase player level by 1, and update level score text
            if self.pipes[0].x < -10: 
                self.pipes.pop(0)
                self.level += 1
                text = font.render('Level '+str(self.level),False,(255,255,255))
            
            #If bird collides with pipe, declare it to be dead
            #***reminder, 110 is the center x value of the bird at all times

            if 110 in range(int(self.pipes[0].x),int(self.pipes[0].x)+70) and (self.flappy.height in range  (0,self.pipes[0].topHeight) or self.flappy.height+50 in range(self.pipes[0].bottomHeight,593)):
                self.flappy.alive = False
            
            #Initialize Flappy's Gravity
            self.flappy.gravity()

            #Recalculating Distances to Pipes
            self.flappy.setDists(self.pipes[0])
            
            #Gradually rotate bird as it falls
            self.flappy.rotate(-1.5)

            #Show Bird to Screen
            self.flappy.showBird()

            #Show Level Text to screen
            self.screen.blit(text,(20,20))

            #Update pygame window
            pygame.display.flip()

#Initialize and Start Game         
newGame = game() 
newGame.setup()

#Output Text in Console, after conclusion of game
print('Game Over: Flappy Died\n')
print('Score: '+str(newGame.level))
