
import pygame
import os
import random
import math


pygame.init()


W  = 6
H = 4
SQUARESIZE = 120
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
ACC = 0.15
NBSTARS = 50

WIDTH = W * SQUARESIZE
HEIGTH = H * SQUARESIZE
STAR_SIZE_MAX = 4
STAR_ACC = 0.01
FIRE_COOLDOWN = 125

BOSS_FIRE_COOLDOWN = 1000

MAX_SHIP_SPEED = 8

ENEMY_SPAWN_TIME_DEFAULT = 500
ENEMY_SPAWN_TIME = ENEMY_SPAWN_TIME_DEFAULT
ENEMY_SPAWN_TIME_CAP = 200

TROOPER_LIFE = 3
PLAYER_HEALTH_CAP  = 10

DIFFICULTY_RISE = 100
DIFFICULTY_RISE_TIME = 5000


MAX_ENEMY_ACC = 0.1
DEFAULT_ENEMY_ACC = 0.01
ENEMY_ACC = DEFAULT_ENEMY_ACC

ENEMY_ACC_INC = 0.01

screen = pygame.display.set_mode((WIDTH, HEIGTH))

DEFAULT_POPPING_WINDOW_HEIGTH = HEIGTH / 3
POPPING_WINDOW_HEIGTH = DEFAULT_POPPING_WINDOW_HEIGTH
POPPING_WINDOW_HEIGTH_DEC = 0.1
MIN_POPPING_WINDOW_HEIGHT = HEIGTH / 6

SINGLE_EXPLOSION_FRAME_WIDTH = 128

BOSS_HERE = FALSE

BOSS_SIZE = int((WIDTH+HEIGTH) / 2.5)
BOSS_TIME = 100000


class SpriteSheet:
    def __init__(self, image):
	    self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)

        return image



class Projectile(pygame.sprite.Sprite):    
    def __init__(self,type,x,y,size):
        pygame.sprite.Sprite.__init__(self)  
        self.type = type

        if type == 1:
            self.color = RED
        elif type == 2:
            self.color = BLUE
        elif type == 3:
            self.color = RED
        

        self.size = size
        self.image = pygame.transform.scale(pygame.image.load(f"images/Spaceships/proj{type}.png").convert().convert_alpha(),(self.size,self.size))

        self.image.set_colorkey((255,255,255))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        
        
        self.velx = 5
       

        self.x = x
        self.y = y - 25

        
        


    def update(self):
        self.x += self.velx
        self.rect = pygame.Rect(self.x,self.y,self.size,self.size)

        
    def draw(self):
        screen.blit(self.image,self.rect)



class Enemy(pygame.sprite.Sprite):
    
    def __init__(self,y_start, type):
        pygame.sprite.Sprite.__init__(self)      
        self.x = WIDTH  + SQUARESIZE * 2
        self.y = y_start + random.choice([1,-1]) * random.random() * POPPING_WINDOW_HEIGTH

        self.type = type
        self.size = SQUARESIZE + random.randint(-1,1) * int(random.random() * 0.4 * SQUARESIZE)
        self.y = random.random() * (HEIGTH - self.size)
        
        if self.type == 1:
            self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/enemies/RedTrooper.png").convert().convert_alpha(),(self.size,self.size)),True,False)
            self.image.set_colorkey((255,255,255))
        elif self.type == 2:
            self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/enemies/BlueTrooper.png").convert().convert_alpha(),(self.size,self.size)), True, False)
            self.image.set_colorkey((0,0,0))
        elif self.type == 3:
            self.image = pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"images/enemies/GreenTrooper.png").convert().convert_alpha(),(self.size,self.size)), True, False)
            self.image.set_colorkey((255,255,255))

        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.velx =  - 1 + -random.random() * 4
        
        self.accx = -ENEMY_ACC_INC
    
        
        self.life = TROOPER_LIFE
       

    def update(self):
        self.velx += self.accx

        self.x += self.velx
        self.rect = pygame.Rect(self.x,self.y,SQUARESIZE/2,SQUARESIZE/2)

    def draw(self):
        screen.blit(self.image,self.rect)



class Star:
    def __init__(self):
        self.x = random.random() * WIDTH
        self.y = random.random() * HEIGTH


        self.acc = -STAR_ACC
        self.size = 1+ int(random.random() * STAR_SIZE_MAX)
        self.velx = -1 + int(-3 * self.size / STAR_SIZE_MAX)
        self.color = (random.random() * 255,random.random() * 255,random.random()*255)
        self.px = self.x
        self.py = self.y
        #self.color = (255,255,255)

    def update(self):
        self.px = self.x
        self.py = self.y

        self.velx += self.acc
        self.x += self.velx

        if self.x < 0:
            self.velx = -1 + int(-3 * self.size / STAR_SIZE_MAX)
        
            self.x = WIDTH
            self.y = random.random() * HEIGTH
            self.color = (random.random() * 255,random.random() * 255,random.random()*255)

    def draw(self):
        
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.size)


class Player(pygame.sprite.Sprite):
    """
    Spawn a player
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)        
        self.image = pygame.transform.scale(pygame.image.load("images/Spaceships/2_Red.png").convert().convert_alpha(),(SQUARESIZE,SQUARESIZE))
        self.image.set_colorkey((255,255,255))

        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.vely = 0
        self.accy = 0
        self.x = self.y = 0
        
        self.stopping = False
        self.type = 1
        self.canShoot = True
        self.life = PLAYER_HEALTH_CAP

    def draw(self):
        screen.blit(self.image,self.rect)

        if self.life >= PLAYER_HEALTH_CAP * 2 // 3:
            health_color = GREEN
        elif self.life >= PLAYER_HEALTH_CAP // 3:
            health_color = YELLOW
        else:
            health_color = RED
        

        pygame.draw.rect(screen, health_color, pygame.Rect(self.x,self.y+SQUARESIZE-20,int(SQUARESIZE * self.life/PLAYER_HEALTH_CAP),10))

    def update(self):

        if self.stopping:
            
            self.vely = 0
            
        else:
            self.vely += self.accy


        
        if abs(self.vely) > MAX_SHIP_SPEED:
            if self.vely > 0:
                self.vely = MAX_SHIP_SPEED
            else:
                self.vely = -MAX_SHIP_SPEED


        self.y += self.vely
        if self.y  <= 0:
            self.y = 0
            self.vely = 0
            self.accy = 0
        elif self.y > HEIGTH - SQUARESIZE :
            self.y = HEIGTH - SQUARESIZE
            self.vely = 0
            self.accy = 0

        self.rect = pygame.Rect(self.x,self.y,SQUARESIZE,SQUARESIZE)
    

class BOSS(pygame.sprite.Sprite):
    
    def __init__(self,player):
        pygame.sprite.Sprite.__init__(self)  
        self.image = FINAL_BOSS
        self.size = BOSS_SIZE

        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_rect()
        self.velx = -2
        self.accx = 0.01
        self.accy = 0
        self.y = HEIGTH - self.size
        self.x = WIDTH + self.size
        
        self.vely = 0

        self.stopping = False
        self.type = 4
        #self.canShoot = True
        self.life = 50

        self.player = player
        
    def draw(self):
        screen.blit(self.image,self.rect)

        
        if self.life >=  50 * 2 // 3:
            health_color = GREEN
        elif self.life >= 50 // 3:
            health_color = YELLOW
        else:
            health_color = RED
        
        
        health_bar = pygame.Surface((self.size * self.life/50,100))
        health_bar.fill(health_color)
        screen.blit(health_bar,(0,0))
        print(health_bar.rect)
        
    
    def update(self):

        if self.x < WIDTH - self.size * 0.7:
            self.velx = 0
        else:
            self.velx -= self.accx


        if (self.y - self.player.y) < 0:
            self.accy = 0.005
        
        else:
            self.accy = -0.005
    
        self.x += self.velx

        self.vely += self.accy

        self.y +=  self.vely
        self.rect = pygame.Rect(self.x,self.y,SQUARESIZE/2,SQUARESIZE/2)

        
    def shoot(self):

        if self.velx == 0:
            proj1 = Projectile(random.randint(1,4),self.x,self.y + self.size * 0.22,75)
            proj2 = Projectile(random.randint(1,4),self.x,self.y + self.size * 0.34,75)
            proj3 = Projectile(random.randint(1,4),self.x,self.y + self.size * 0.46,75)


            proj1.velx = -4
            proj2.velx = -4
            proj3.velx = -4
        
            return (proj1,proj2,proj3)

        else:
            return None


score_value = 0
font = pygame.font.Font('arial.ttf', 32)

textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('arial.ttf', 32)


GAME_STARTED = False

def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))



EXPLOSION_SPRITESHEET = SpriteSheet("images/explosionSpriteSheet.png")

BALANCE_OF_POWER = pygame.transform.scale(pygame.image.load("images/balanceOfPower.png").convert().convert_alpha(),(SQUARESIZE,SQUARESIZE))
BALANCE_OF_POWER.set_colorkey((0,0,0))



FINAL_BOSS = pygame.transform.flip(pygame.transform.scale(pygame.image.load("images/FINAL_BOSS2.png").convert().convert_alpha(),(BOSS_SIZE,BOSS_SIZE)),True,False)
FINAL_BOSS.set_colorkey((255,255,255))
BALANCE_OF_POWER.set_colorkey((0,0,0))

stars = [Star() for _ in range(NBSTARS)]
last_boss_shoot = 0




done = False

player = Player()

last_added_score = 50


clock = pygame.time.Clock()


last_shoot = 0
last_enemy_spawn = 0


all_projectiles = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()



player.rect = pygame.Rect(WIDTH / 2 , HEIGTH / 2,SQUARESIZE,SQUARESIZE)

player_group = pygame.sprite.GroupSingle()

boss_projectiles  = pygame.sprite.Group()


pygame.display.set_caption("Chromazz s'enfuit!")
added_score = 0

while not done:

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                       
                        player.stopping = False
                        player.accy = -ACC
                    elif event.key == pygame.K_DOWN:
                        player.accy = +ACC
                        player.stopping = False
                    if event.key == pygame.K_1:
                        player.image = pygame.transform.scale(pygame.image.load("images/Spaceships/2_Red.png").convert().convert_alpha(),(SQUARESIZE,SQUARESIZE))
                        player.image.set_colorkey((255,255,255))
                        player.type = 1
                    elif event.key == pygame.K_2:
                        player.image =  pygame.transform.scale(pygame.image.load("images/Spaceships/2_Blue.png").convert().convert_alpha(),(SQUARESIZE,SQUARESIZE))
                        player.image.set_colorkey((255,255,255))
                        player.type = 2
                    elif event.key == pygame.K_3:
                        player.image =  pygame.transform.scale(pygame.image.load("images/Spaceships/2_Green.png").convert().convert_alpha(),(SQUARESIZE,SQUARESIZE))
                        player.image.set_colorkey((255,255,255))
                        player.type = 3
                    if event.key == pygame.K_SPACE:
                        if player.canShoot:
                            #player_projectiles.append(Projectile(player.type,player.y + SQUARESIZE/2))
                            all_projectiles.add(Projectile(player.type,SQUARESIZE,player.y + SQUARESIZE/2,50))
                            last_shoot = pygame.time.get_ticks()
                            player.canShoot = False
                        

                elif event.type == pygame.KEYUP:
                    

                    player.stopping = True  


        
        
        screen.fill((0,0,0))
        
        
        for star in stars:
            
            star.update()
            star.draw()
        
        #screen.blit(BG,(0,0))
        player.draw()
        player.update()

        
        all_enemies.update()
        all_enemies.draw(screen)

        all_projectiles.update()
        all_projectiles.draw(screen)

        boss_projectiles.update()
        boss_projectiles.draw(screen)
            
        

        for bproj in boss_projectiles.sprites()[:]:
            hit = pygame.sprite.spritecollide(bproj,all_projectiles,False,pygame.sprite.collide_mask)

            for proj in hit:
                if proj.type == bproj.type % 3 + 1:
                    all_projectiles.remove(proj)
                    boss_projectiles.remove(bproj) 

    
       


        for enemy in all_enemies.sprites()[:]:
            hit = pygame.sprite.spritecollide(enemy,all_projectiles,True,pygame.sprite.collide_mask)
            for proj in  hit:
                if proj.type == enemy.type:
                    enemy.life -= 2
                elif proj.type == enemy.type % 3 + 1:
                    enemy.life -= 3

                else:
                    enemy.life -= 1
            


            if enemy.life <= 0:
                if proj.type == enemy.type % 3 + 1:
                    player.life += 2
                    if player.life >= PLAYER_HEALTH_CAP:
                        player.life = PLAYER_HEALTH_CAP
                all_enemies.remove(enemy)
                score_value += 20
            
        

        collided_enemy = pygame.sprite.spritecollide(player,all_enemies,True, pygame.sprite.collide_mask)
        if collided_enemy:
            for sp in collided_enemy:
                if sp.type == player.type:
                    player.life -= 2
                elif sp.type == player.type % 3 + 1:
                    player.life -= 1
                else:
                    player.life -=  3

            
        
        
        collided_boss_projectiles = pygame.sprite.spritecollide(player,boss_projectiles,True, pygame.sprite.collide_mask)

        if collided_boss_projectiles:
            for sp in collided_boss_projectiles:
                if sp.type == player.type:
                    player.life -= 2
                elif sp.type == player.type % 3 + 1:
                    player.life -= 1
                else:
                    player.life -=  3


        

        if player.life <= 0:
            done = True
                
        current_time = pygame.time.get_ticks()
        if current_time - last_shoot > FIRE_COOLDOWN:
            
            last_shoot = current_time
            player.canShoot = True

        current_time = pygame.time.get_ticks()
        if current_time < BOSS_TIME and current_time - last_enemy_spawn > ENEMY_SPAWN_TIME:
            last_enemy_spawn = current_time

            r = random.random()
            if r < 0.5:
                #enemies.append(Enemy(player.type))
                all_enemies.add(Enemy(player.y,player.type))
            elif r < 0.8:
                #enemies.append(Enemy(player.type % 3 + 1))
                all_enemies.add(Enemy(player.y,player.type % 3 + 1))
            else :
                if player.type == 1:
                    #enemies.append(Enemy(3))
                    all_enemies.add(Enemy(player.y,3))
                else:
                    #enemies.append(Enemy(player.type -  1))
                    all_enemies.add(Enemy(player.y,player.type - 1))


        for enemy in all_enemies.sprites()[:]:
            if enemy.x < -enemy.size:

                all_enemies.remove(enemy)
                score_value += 10


        if current_time > BOSS_TIME and len(all_enemies.sprites()) == 0 :
            all_enemies.add(BOSS(player))
            BOSS_HERE = True

        if BOSS_HERE:
            if all_enemies.sprites():
                if isinstance(all_enemies.sprites()[0],BOSS):
                    all_enemies.sprites()[0].accy = (all_enemies.sprites()[0].y - player.y ) / 200


                    if current_time - last_boss_shoot > BOSS_FIRE_COOLDOWN:
                        last_boss_shoot = current_time
                        
                        projectiles = all_enemies.sprites()[0].shoot()

                        print(projectiles)
                        if projectiles:
                            for proj in projectiles:
                                boss_projectiles.add(proj)

                    collided_boss = pygame.sprite.spritecollide(all_enemies.sprites()[0],all_projectiles,True, pygame.sprite.collide_mask)

                    all_enemies.sprites()[0].life -= 2 * len(collided_boss)

                    if all_enemies.sprites()[0].life <= 0:
                        done = True
                        score_value += 100000
            
                    

        

        ENEMY_SPAWN_TIME = ENEMY_SPAWN_TIME_DEFAULT - DIFFICULTY_RISE * math.floor(current_time / DIFFICULTY_RISE_TIME) 
        
        ENEMY_ACC = DEFAULT_ENEMY_ACC -ENEMY_ACC_INC * math.floor(current_time / DIFFICULTY_RISE_TIME)

        POPPING_WINDOW_HEIGHT = (1 - POPPING_WINDOW_HEIGTH_DEC * math.floor(current_time / DIFFICULTY_RISE_TIME) ) * DEFAULT_POPPING_WINDOW_HEIGTH 

        if ENEMY_SPAWN_TIME < ENEMY_SPAWN_TIME_CAP:
            ENEMY_SPAWN_TIME = ENEMY_SPAWN_TIME_CAP

        if ENEMY_ACC > MAX_ENEMY_ACC:
            ENEMY_ACC = MAX_ENEMY_ACC

        if POPPING_WINDOW_HEIGHT < MIN_POPPING_WINDOW_HEIGHT:
            POPPING_WINDOW_HEIGHT = MIN_POPPING_WINDOW_HEIGHT



        

        if current_time - last_added_score > 100:
            last_added_score = current_time

            score_value += 1


        
        

        screen.blit(BALANCE_OF_POWER,(WIDTH-SQUARESIZE,0))
        show_score(textX,testY)
        if done == True:

            screen.fill((0,0,0))
            for star in stars:
                
                star.update()
                star.draw()
            
            #screen.blit(BG,(0,0))
            player.draw()
            player.update()

            
            all_enemies.update()
            all_enemies.draw(screen)

            all_projectiles.update()
            all_projectiles.draw(screen)

            boss_projectiles.update()
            boss_projectiles.draw(screen)
            if player.life <= 0:
                over_text = over_font.render("Destruction du Ranbowzz...",True,(255,255,255))
                screen.blit(over_text,(WIDTH/2 - 200,HEIGTH/2))
            elif len(all_enemies.sprites()) == 0:
                over_text = over_font.render("Victoire de Chromazz!",True,(255,255,255))
                screen.blit(over_text,(WIDTH/2 - 180,HEIGTH/2))

            screen.blit(BALANCE_OF_POWER,(WIDTH-SQUARESIZE,0))
            show_score(textX,testY)

            player.draw()
            player.update()
        pygame.display.flip()
        if done == True:
            pygame.time.wait(2000)

        clock.tick(120)

