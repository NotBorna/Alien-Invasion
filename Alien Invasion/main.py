import pygame
import random
import os
import time

pygame.init()

pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(-1)

player_gun = pygame.mixer.Sound("player_gun.wav")
enemy_death = pygame.mixer.Sound("enemy_death.wav")
medsound = pygame.mixer.Sound("medsound.wav")
player_hit = pygame.mixer.Sound("player_hit.wav")
gameover = pygame.mixer.Sound("gameover.wav")

pygame.font.init()

width, height = 1000, 780
score = -100
highscore = 0
COOLDOWN = 45

win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Alien Invasion")

bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")),(width, height))

player = pygame.image.load(os.path.join("assets", "player.png"))

enemy1 = pygame.image.load(os.path.join("assets", "enemy1.png"))
enemy2 = pygame.image.load(os.path.join("assets", "enemy2.png"))
enemy3 = pygame.image.load(os.path.join("assets", "enemy3.png"))
enemy4 = pygame.image.load(os.path.join("assets", "enemy4.png"))

player_laser = pygame.image.load(os.path.join("assets", "player_laser.png"))
enemy_laser = pygame.image.load(os.path.join("assets", "enemy_laser.png"))

medkit = pygame.transform.scale(pygame.image.load(os.path.join("assets", "medkit.png")),(80, 60))

class Player:
     
    def __init__(self):
    
        self.x = 430
        self.y = 620
        self.health = 60
        self.img = player
        self.laser_img = player_laser
        self.mask = pygame.mask.from_surface(self.img)
        self.max_health = 60
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
        self.healthbar(window)
        

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        enemy_death.play()
                        objs.remove(obj)
                        global score
                        score += 20
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            player_gun.play()
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width() * (self.health/self.max_health), 10))
        health_font = pygame.font.SysFont("comicsans", 21)
        health_label = health_font.render("health ", 1, (0,0,0))
        win.blit(health_label, (self.x + 25, self.y + 97))
    

class Enemy:
    
    color_map = {
                "purple": (enemy1),
                "green": (enemy2),
                "red": (enemy3),
                "brown": (enemy4)
                }
    def __init__(self, x, y, color):
        
        self.x = x
        self.y = y
        self.laser_img = enemy_laser
        self.img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.img)
        self.lasers = []

    def move(self, vel):
        self.y += vel

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                player_hit.play()
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
            laser = Laser(self.x - 12, self.y + 30, self.laser_img)
            self.lasers.append(laser)

class Laser:
    
    def __init__(self, x, y, img):
        
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y - 20))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= -30)

    def collision(self, obj):
        return collide(self, obj)


class Medkit:

    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = medkit
        self.mask = pygame.mask.from_surface(self.img)


    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def heal(self, player):
        player.health += 20
        if player.health > 60:
            player.health = 60
        


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
        

def main():

    global highscore
    fps = 60
    user_vel = 6
    run = True
    clock = pygame.time.Clock()
    wave = 0
    global score
    font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 100)
    user = Player()
    enemies = []
    wave_lenght = 3
    enemy_vel = 1
    lost = False
    laser_vel = 9
    lost_count = 0
    med_vel = 2
    medkits = []
    global COOLDOWN


    def redraw():
        
        win.blit(bg, (0,0))
        wave_text = font.render(f"Wave: {wave}", 1, (255,255,255))
        score_text = font.render(f"Score: {score}", 1, (255,255,255))
        highscore_text = font.render(f"HighScore: {highscore}", 1, (255,255,255))
        back_text = font.render("(b)ack", 1, (255,255,255))
        win.blit(wave_text, (10,10))
        win.blit(score_text, (10,50))
        win.blit(highscore_text, (10,90))
        win.blit(back_text, (width - 120, 10))
        for enemy in enemies:
            enemy.draw(win)
        for medkit in medkits:
            medkit.draw(win)
        user.draw(win)
        if lost:
            lost_label = lost_font.render("Game Over", 1, (255, 255, 255))
            win.blit(lost_label, (width/2 - lost_label.get_width()/2, height/2 - lost_label.get_height()/2))
        pygame.display.update()
        

    while run:
        
        clock.tick(fps)

        redraw()

        if random.randrange(0, fps*90) == 1:
            medkit = Medkit(random.randrange(70, width - 70), -100)
            medkits.append(medkit)
            
        if score > highscore:
            highscore = score

        
        if user.health <= 0:
            lost = True
            gameover.play()
            lost_count += 1

        if lost:
            if lost_count > fps*2:
                score = -100
                run = False
                
                
            else:
                continue
        

        if len(enemies) == 0:
            wave_lenght += 3
            wave += 1
            score += 100
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(70, width - 70), random.randrange(-1000 + wave * -100, -200), random.choice(["red", "green", "brown", "purple"]))
                enemies.append(enemy)
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] and user.x + user_vel + 100 < width: # right
            user.x += user_vel

        if keys[pygame.K_LEFT] and user.x - user_vel > 0: # left
            user.x -= user_vel

        if keys[pygame.K_UP] and user.y - user_vel > 0: # up
            user.y -= user_vel

        if keys[pygame.K_DOWN] and user.y + user_vel + 120 < height: # down
            user.y += user_vel

        if keys[pygame.K_b]: # (b)ack
            score = -100
            run = False

        if keys[pygame.K_SPACE]: # shoot with space
            user.shoot()


        for medkit in medkits[:]:
            
            medkit.move(med_vel)
            
            if collide(medkit, user):
                score += 10
                medsound.play()
                medkits.remove(medkit)
                medkit.heal(user)

            elif medkit.y > height:
                medkits.remove(medkit)
                    

        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, user)
            if random.randrange(0, fps*3) == 1:
                enemy.shoot()
            if collide(enemy, user):
                enemy_death.play()
                user.health -= 20
                score += 20
                enemies.remove(enemy)
            elif enemy.y > height:
                enemies.remove(enemy)
            
                
        user.move_lasers(-laser_vel, enemies)

def menu():
    title_font = pygame.font.SysFont("comicsans", 90)
    hs_font = pygame.font.SysFont("comicsans", 50)
    run = True

    while run:
        win.blit(bg, (0,0))
        highscore_label = hs_font.render(f"HighScore: {highscore}", 1, (255,255,255))
        title_label = title_font.render("Alien Invasion", 1, (200,0,0))
        start_label = title_font.render("(S)tart", 1, (0,255,0))
        start_label = title_font.render("(S)tart", 1, (0,255,0))
        instruction_label = title_font.render("(I)nstructions", 1, (200,0,200))
        win.blit(start_label, (width/2 - start_label.get_width()/2, 330))
        win.blit(highscore_label, (20, 20))
        win.blit(title_label, (width/2 - title_label.get_width()/2, 150))
        win.blit(instruction_label, (width/2 - start_label.get_width()/2, 480))
        score = -100
        pygame.display.update()

        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
        if keys[pygame.K_s]:
                main()

        if keys[pygame.K_i]:
                win.blit(bg, (0,0))
                title_label1 = title_font.render("Use arrow keys to move", 1, (255,255,255))
                title_label2 = title_font.render("and space to shoot", 1, (255,255,255))
                title_label3 = title_font.render("health = 60", 1, (255,255,255))
                title_label4 = title_font.render("lasers - 10 health", 1, (255,255,255))
                title_label5 = title_font.render("aliens - 20 health", 1, (255,255,255))
                title_label6 = title_font.render("medkits + 20 health", 1, (255,255,255))
                win.blit(title_label1, (width/2 - title_label1.get_width()/2, 50))
                win.blit(title_label2, (width/2 - title_label2.get_width()/2, 120))
                win.blit(title_label3, (width/2 - title_label3.get_width()/2, 190))
                win.blit(title_label4, (width/2 - title_label4.get_width()/2, 260))
                win.blit(title_label5, (width/2 - title_label5.get_width()/2, 330))
                win.blit(title_label6, (width/2 - title_label6.get_width()/2, 400))
                pygame.display.update()          
                pygame.time.delay(5000)
                

        

            



menu()
                

    

