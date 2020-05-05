import pygame
import random
import os
import time

pygame.init()

pygame.mixer.music.load("music.wav")
pygame.mixer.music.play(-1)

player_gun = pygame.mixer.Sound("player_gun.wav")
enemy_death = pygame.mixer.Sound("enemy_death.wav")


pygame.font.init()

width, height = 750, 750
score = -100
highscore = 0

win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Alien Invasion")

bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")),(width, height))

tutorial = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tutorial.png")), (width, height))

player = pygame.image.load(os.path.join("assets", "player.png"))

enemy1 = pygame.image.load(os.path.join("assets", "enemy1.png"))
enemy2 = pygame.image.load(os.path.join("assets", "enemy2.png"))
enemy3 = pygame.image.load(os.path.join("assets", "enemy3.png"))
enemy4 = pygame.image.load(os.path.join("assets", "enemy4.png"))

player_laser = pygame.image.load(os.path.join("assets", "player_laser.png"))
enemy_laser = pygame.image.load(os.path.join("assets", "enemy_laser.png"))

class Player:

    COOLDOWN = 45
     
    def __init__(self):
    
        self.x = 375
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
        if self.cool_down_counter >= self.COOLDOWN:
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

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
        

def main():

    global highscore
    fps = 60
    user_vel = 5
    run = True
    clock = pygame.time.Clock()
    wave = 0
    global score
    font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 100)
    user = Player()
    enemies = []
    wave_lenght = 2
    enemy_vel = 1
    lost = False
    laser_vel = 8
    lost_count = 0


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
        user.draw(win)
        if lost:
            lost_label = lost_font.render("Game Over", 1, (255, 255, 255))
            win.blit(lost_label, (width/2 - lost_label.get_width()/2, height/2 - lost_label.get_height()/2))
        pygame.display.update()
        

    while run:
        
        clock.tick(fps)

        redraw()

        if score > highscore:
            highscore = score

        
        if user.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps*3:
                score = -100
                run = False
                
                
            else:
                continue
        

        if len(enemies) == 0:
            wave_lenght += 2
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

        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, user)
            if random.randrange(0, 60*3) ==1:
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
        tutorial_label = title_font.render("(T)utorial", 1, (0,200,200))
        win.blit(start_label, (width/2 - start_label.get_width()/2, 350))
        win.blit(highscore_label, (20, 20))
        win.blit(tutorial_label, (width/2 - start_label.get_width()/2, 500))
        win.blit(title_label, (width/2 - title_label.get_width()/2, 150))
        score = -100
        pygame.display.update()

        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                
        if keys[pygame.K_s]:
                main()

        if keys[pygame.K_t]:
            win.blit(tutorial, (0,0))
            pygame.display.update()
            time.sleep(3)

            



menu()
                

    

