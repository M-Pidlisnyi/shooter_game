from pygame import *
from time import time as timer
from random import randint

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (80, 100))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_RIGHT] and self.rect.x < win_width - 85:
            self.rect.x += self.speed
    def fire(self):
        bullet = Bullet('bullet.png', self.rect.centerx, self.rect.top, 5, 15, 20)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1
    
class Bullet(GameSprite):
    #Додати цей конструктор, щоб змінити розмір кулі
    def __init__(self, bullet_image, bullet_x, bullet_y, bullet_speed,
                bullet_size_x, bullet_size_y):
        super().__init__(bullet_image, bullet_x, bullet_y, bullet_speed)
        self.image = transform.scale(image.load(bullet_image), (bullet_size_x, bullet_size_y))     
    
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

win_width = 1300
win_height = 720

window = display.set_mode(
    (win_width, win_height)
)
display.set_caption("Shooter Game")
background = transform.scale(
    image.load("galaxy.jpg"), 
    (win_width, win_height)
)

player = Player('rocket.png', 5, win_height - 100, 10)

monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy('ufo.png', randint(80, win_width - 80), randint(0, 100), 2)
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1, 3):
    aster = Enemy('asteroid.png', randint(80, win_width - 80), randint(0,100), 1)
    asteroids.add(aster)

bullets = sprite.Group()

font.init()
#текст перемоги і програшу

font1 = font.SysFont("Arial", 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

font2 = font.SysFont("Arial", 36)

finish = False
run = True
clock = time.Clock()
fps = 60

mixer.init()
fire_sound = mixer.Sound('fire.ogg')

#змінні для контролю гри
lost = 0

score = 0
goal = 10
max_lost = 3

num_fire = 0
max_fire = 10
rel_time = False


while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < max_fire and not rel_time:
                    player.fire()
                    num_fire += 1
                elif num_fire >= max_fire and not rel_time:
                    rel_time = True
                    current_time = timer()
            #рестарт на r
            if e.key == K_r:
                if finish:
                    restart = True

    if not finish:
        restart = False
        window.blit(background,(0, 0))

        if rel_time:
            new_current_time = timer()
            if new_current_time - current_time < 3:
                font3 = font.SysFont("Arial", 20)
                text_wait = font3.render("Зачекай! Іде перезарядка", 1, (150, 0, 0))
                window.blit(text_wait, (player.rect.x, player.rect.y))
            else:
                rel_time = False
                num_fire = 0

        #текст із рахунком---
        text = font2.render("Збито: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        monsters.update()
        bullets.update()
        asteroids.update()

        player.update()
        player.reset()
        
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window)

        #перевірка зіткнення кулі і монстра
        collides_monster = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides_monster:   
           score += 1
           monster = Enemy('ufo.png', randint(80, win_width - 80), randint(0, 10), 2)
           monsters.add(monster)
        
        #перевірка зіткнення кулі і монстра
        collides_aster = sprite.groupcollide(asteroids, bullets, True, True)
        for c in collides_aster:   
            score += 1
            aster = Enemy('asteroid.png', randint(80, win_width - 80), randint(0,100), 1)
            asteroids.add(aster)

        #перевірка умови програшу, 
        
        #lose_game = sprite.spritecollide(player, monsters, False) or sprite.spritecollide(player, asteroids, False) or lost >= max_lost
        if sprite.spritecollide(player, monsters, False) or lost >= max_lost:
           finish = True 
           window.blit(lose, (200, 200))
        
        if sprite.spritecollide(player, asteroids, False):
            if player.speed >= 1:
                player.speed -= 1
            elif player.speed == 0:
                finish = True 
                window.blit(lose, (200, 200))
        #перевірка умови виграшу
        
        if score >= goal:
           finish = True
           window.blit(win, (200, 200))

    #рестарт на кнопку
    elif finish and restart:
        finish = False
        score = 0
        lost = 0
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        for a in asteroids:
            a.kill()
    
        for i in range(1, 6):
            monster = Enemy('ufo.png', randint(80, win_width - 80), randint(0, 10), 2)
            monsters.add(monster)
        for i in range(1, 3):
            aster = Enemy('asteroid.png', randint(80, win_width - 80), randint(0,100), 2)
            asteroids.add(aster)
        player.speed = 5
    

    display.update()
    clock.tick(fps) 