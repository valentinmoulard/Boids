import sys, pygame, random, math
import numpy as np
from pygame import *

pygame.init()
size = width, height = 800, 600
fond = pygame.image.load("background.jpg")
pygame.mixer.music.load('music.mp3')
spawn = pygame.mixer.Sound('spawn.wav')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(50)

black = 0, 0, 0
maxVelocity = 4
numBoids = 10
boids = []
murs = []
# facteur de regroupement
# si regroupement proche de 0, les boids seront tres rapproché
regroupement = 150
# si facteur_repulsion est faible, les boids ne peuvent pas se superposer
# plus il est élevé, moins les boids vont s'eviter 
facteur_repulsion = 50
# si facteur_direction est faible, les boids vont bouger avec des directions tres rigides
# dans la methode move_with
facteur_direction = 100
vitesse_cible = 15

def out(x,y):
    out = False
    if (x + 30 > width or y + 30 > height):
        out = True
    if (x < 0 or y < 0):
        out = True
    return out

class Mur:
    def __init__(self, x, y, longueur, hauteur):
        self.x = x
        self.y = y
        self.longueur = longueur
        self.hauteur = hauteur

class Boid:
    def __init__(self, x, y, super_boid):
        self.x = x
        self.y = y
        self.super_boid = super_boid
        self.velocityX = random.randint(1, 4) / 4.0
        self.velocityY = random.randint(1, 4) / 4.0

    #donne la distance entre le boid courant et un autre boid
    def distance(self, boid):
        distX = self.x - boid.x
        distY = self.y - boid.y
        return np.sqrt(distX * distX + distY * distY)

    #methode d'attraction
    def moveCloser(self, boids):
        if len(boids) < 1: return
        # calculate the average distances from the other boids
        avgX = 0
        avgY = 0
        for boid in boids:
            if boid.x == self.x and boid.y == self.y:
                continue
            avgX += (self.x - boid.x)
            avgY += (self.y - boid.y)

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others
        self.velocityX -= (avgX / regroupement) 
        self.velocityY -= (avgY / regroupement)
        
    "Move with a set of boids"
    def moveWith(self, boids):
        if len(boids) < 1: return
        # calculate the average velocities of the other boids
        avgX = 0
        avgY = 0
        for boid in boids:
            avgX += boid.velocityX
            avgY += boid.velocityY

        avgX /= len(boids)
        avgY /= len(boids)

        # set our velocity towards the others
        self.velocityX += (avgX / facteur_direction)
        self.velocityY += (avgY / facteur_direction)
    
    "Move away from a set of boids. This avoids crowding"
    def moveAway(self, boids, minDistance):
        if len(boids) < 1: return
        distanceX = 0
        distanceY = 0
        numClose = 0

        for boid in boids:
            distance = self.distance(boid)
            if  distance < minDistance:
                numClose += 1
                xdiff = (self.x - boid.x) 
                ydiff = (self.y - boid.y)
                if xdiff >= 0: xdiff = np.sqrt(minDistance) - xdiff
                elif xdiff < 0: xdiff = -np.sqrt(minDistance) - xdiff
                if ydiff >= 0: ydiff = np.sqrt(minDistance) - ydiff
                elif ydiff < 0: ydiff = -np.sqrt(minDistance) - ydiff

                distanceX += xdiff 
                distanceY += ydiff
        if numClose == 0:
            return
        self.velocityX -= distanceX /facteur_repulsion
        self.velocityY -= distanceY /facteur_repulsion


    def move(self):
        if abs(self.velocityX) > maxVelocity or abs(self.velocityY) > maxVelocity:
            scaleFactor = maxVelocity / max(abs(self.velocityX), abs(self.velocityY))
            self.velocityX *= scaleFactor
            self.velocityY *= scaleFactor
        self.x += self.velocityX
        self.y += self.velocityY

    def avoidWalls(self, liste_murs):
        if len(liste_murs) < 1: return
        for mur in liste_murs:
            if (self.x + self.velocityX) <= (mur.x + mur.longueur) and self.x >= (mur.x + mur.longueur) and (self.y + 30) >= mur.y and self.y <= (mur.y + mur.hauteur):
                self.velocityX = -self.velocityX *random.random()
            if (self.x + 30) <= mur.x and (self.x + self.velocityX) + 30 >= mur.x and (self.y + 30) >= mur.y and self.y <=(mur.y + mur.hauteur):             
                self.velocityX = -self.velocityX *random.random()

            if (self.y + 30) <= mur.y and (self.y + self.velocityY) + 30>= mur.y and (self.x + 30) >= mur.x and self.x <= (mur.x + mur.longueur):
                self.velocityY = -self.velocityY *random.random()
            if self.y > (mur.y + mur.hauteur) and (self.y + self.velocityY) <= (mur.y + mur.hauteur) and (self.x + 30) >= mur.x and self.x <= (mur.x + mur.longueur):              
                self.velocityY = -self.velocityY *random.random()

    def followTheLeader(self, boid):
        avgX = self.x - boid.x
        avgY = self.y - boid.y

        self.velocityX -= (avgX / regroupement) 
        self.velocityY -= (avgY / regroupement)


screen = pygame.display.set_mode(size)
# initialisation des sprite et hitbox des boids
ST = pygame.image.load("storm_trooper.png")
STrect = ST.get_rect()
# initialisation du sprite et hitbox de la cible darth vador
DV = pygame.image.load("darth_vador.png")
DVrect = DV.get_rect()
# poistion de darth vador initialisé en x et y : 250
DVrect.x = 250
DVrect.y = 250



# Generation des obstacles, leurs sprites et leurs hitbox
# les murs
mur_I = pygame.image.load("murV.png")
mur_Irect = mur_I.get_rect()
mur_Irect.x = 350
mur_Irect.y = 0

mur_L = pygame.image.load("murH.png")
mur_Irect3 = mur_L.get_rect()
mur_Irect3.x = 0
mur_Irect3.y = 180
mur_Irect2 = mur_L.get_rect()
mur_Irect2.x = 0
mur_Irect2.y = 450

# les generateurs
generator = pygame.image.load("generator.png")
generator_rect1 = generator.get_rect()
generator_rect1.x = 550
generator_rect1.y = 300
generator_rect2 = generator.get_rect()
generator_rect2.x = 350
generator_rect2.y = 300

# initialisation de mes obstacles
m1 = Mur(mur_Irect.x, mur_Irect.y, mur_Irect[2], mur_Irect[3])
m2 = Mur(mur_Irect2.x, mur_Irect2.y, mur_Irect2[2], mur_Irect2[3])
m3 = Mur(mur_Irect3.x, mur_Irect3.y, mur_Irect3[2], mur_Irect3[3])
g1 = Mur(generator_rect1.x, generator_rect1.y, generator_rect1[2], generator_rect1[3])
g2 = Mur(generator_rect2.x, generator_rect2.y, generator_rect2[2], generator_rect2[3])
# j'ajoute mes objets murs qui sont des obstacles dans ma liste d'obstacles
murs.append(m1)
murs.append(m2)
murs.append(m3)
murs.append(g1)
murs.append(g2)


# create boids at random positions
for i in range(numBoids):
    boids.append(Boid(random.randint(0, width), random.randint(0, height), False))   
# création du boid cible darth vador
Darth_vador = Boid(DVrect.x, DVrect.x, True)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        # gestion du déplacement du boid cible
        if event.type == KEYDOWN :
            if event.key == K_DOWN:
                if out(DVrect[0], DVrect[1] + vitesse_cible) == False:
                    DVrect = DVrect.move(0, vitesse_cible)
                    Darth_vador.y = Darth_vador.y + vitesse_cible
            if event.key == K_UP:
                if out(DVrect[0], DVrect[1] -vitesse_cible) == False:
                    DVrect = DVrect.move(0, -vitesse_cible)
                    Darth_vador.y = Darth_vador.y + vitesse_cible
            if event.key == K_RIGHT:
                if out (DVrect[0] + vitesse_cible, DVrect[1]) == False:
                    DVrect = DVrect.move(vitesse_cible, 0)
                    Darth_vador.x = Darth_vador.x + vitesse_cible
            if event.key == K_LEFT:
                if out(DVrect[0], DVrect[1] - vitesse_cible) == False:
                    DVrect = DVrect.move(-vitesse_cible, 0)
                    Darth_vador.x = Darth_vador.x + vitesse_cible
            # lorsqu'on appuie sur 'espace' ou 'tab' on fait apparaitre de nouveau boids
            if event.key == K_SPACE:
                spawn.play()
                boids.append(Boid(100, 250, False))
                boids.append(Boid(100, 400, False))
            if event.key == K_TAB:
                spawn.play()
                boids.append(Boid(850, 250, False))
                boids.append(Boid(850, 400, False))
        # deplacement de la cible avec la souris
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 3:
                DVrect = (event.pos[0],event.pos[1])
                Darth_vador.x = DVrect[0]
                Darth_vador.y = DVrect[1]

    for boid in boids:
        closeBoids = []
        for otherBoid in boids:
            if otherBoid == boid: continue
            distance = boid.distance(otherBoid)
            if distance < 200:
                closeBoids.append(otherBoid)

        boid.followTheLeader(Darth_vador)
        boid.moveCloser(closeBoids)
        boid.moveWith(closeBoids)
        boid.moveAway(closeBoids, 30)
        # appel de la methode d'evitement des obstacles
        boid.avoidWalls(murs)

        # ensure they stay within the screen space
        # if we roubound we can lose some of our velocity
        border = 25
        if boid.x < border and boid.velocityX < 0:
            boid.velocityX = -boid.velocityX * random.random()
        if boid.x > width - border and boid.velocityX > 0:
            boid.velocityX = -boid.velocityX * random.random()
        if boid.y < border and boid.velocityY < 0:
            boid.velocityY = -boid.velocityY * random.random()
        if boid.y > height - border and boid.velocityY > 0:
            boid.velocityY = -boid.velocityY * random.random()

        boid.move()
    
    # gestion de l'affichage et updates
    # affichage des sprites des boids, du boid cible et des obstacles
    screen.fill(black)
    screen.blit(fond, (0,0))
    for boid in boids:
        boidRect = pygame.Rect(STrect)
        boidRect.x = boid.x
        boidRect.y = boid.y
        screen.blit(ST, boidRect)


    screen.blit(DV, DVrect)

    screen.blit(mur_I, mur_Irect)
    screen.blit(mur_I, mur_Irect2)
    screen.blit(mur_L, mur_Irect3)
    screen.blit(generator, generator_rect1)
    screen.blit(generator, generator_rect2)

    pygame.display.flip()
    pygame.time.delay(10)
