from pygame import *
from random import *
from time import time as timer
init()
win_width = 1000
win_height = 600
FPS = 60

# создание окна и создание заднего фона
win = display.set_mode((win_width, win_height), 0, 0)
backgr = transform.scale(image.load('image.jpg'), (win_width, win_height))
display.set_caption('Shuter')
clock = time.Clock()

lost = 0
score = 19

# общий класс спрайтов
class GameSprite(sprite.Sprite):
    def __init__(self, pl_image, x, y, wid, hie, speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(pl_image), (wid, hie))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        win.blit(self.image, (self.rect.x, self.rect.y))

# класс игрока
class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < win_width - 50:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet('bullet.png', self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

# класс врагов
dirs = "left"
class Enemy(GameSprite):
    def __init__(self, pl_image, x, y, wid, hie, speed, HP):
        super().__init__(pl_image, x, y, wid, hie, speed)
        self.HP = HP

    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = randint(80, 620)
            lost += 1

    def boss_update(self):
        global dirs
        if self.rect.x <= 0:
            dirs = "right"
        if self.rect.x >= win_width-250:
            dirs = "left"
        if dirs == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def launch(self):
        meatball = Bullet('meatball.png', self.rect.centerx-50, self.rect.bottom-60, 100, 65, 5)
        meatball.add(meatballs)

# класс пуль
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < -20 or self.rect.y > wid+70:
            self.kill()


# создание игрока и босса
hero = Player('rocket.png', 0, win_height-80, 50, 80, 6)
boss = Enemy('makaron monster.png', win_width/2-125, -25, 250, 250, 4, 50)

# группы
enemis = sprite.Group()
bullets = sprite.Group()
meteorits = sprite.Group()
meatballs = sprite.Group()

# спавн НЛО и метеоритов
for i in range(5):
    enemy = Enemy('ufo.png', randint(80, win_width-80), -50, 80, 50, 1, 1)
    enemis.add(enemy)

for i in range(1):
    meteorit = Enemy('meteorit.png', randint(80, win_width-80), -70, 70, 70, 1, 3)
    meteorits.add(meteorit)

# текст с победой и проигрыша
font.init()
font1 = font.Font(None, 30)
font2 = font.Font(None, 80)
wins = font2.render('YOU WIN', True, (255, 255, 255))
falls = font2.render('YOU LOSE', True, (255, 255, 255))

# сколько пуль, выстрелов, режим перезарядки
bulls = 10
num_fire = 0
rel_time = False

boss_fight = False
finish = False
boss_launch = 0
while True:
    for i in event.get():
        if i.type == QUIT:
            exit()
        if i.type == KEYDOWN:
            if i.key == K_w:
                # проверка на высрелить ли игроку
                if num_fire < bulls and rel_time == False:
                    num_fire += 1
                    hero.fire()
                # проверка к началу перезарядки
                if num_fire >= bulls and rel_time == False:
                    rel_time = True
                    last_time = timer()


    if finish != True:
        win.blit(backgr,(0, 0))
        hero.update()
        hero.reset()

        bullets.update()
        bullets.draw(win)
        # проверка времени перезарядки
        if rel_time == True:
            now_time = timer()
            if now_time - last_time < 2:
                reloads = font1.render('reload', 1, (255, 255, 255))
                win.blit(reloads, (win_width/2-50, win_height-40))
            else:
                rel_time = False
                num_fire = 0

        collides = sprite.groupcollide(enemis, bullets, True, True)
        mcollides = sprite.groupcollide(meteorits, bullets, False, True)
        # столкновение пули с НЛО
        for i in collides:
            enemy = Enemy('ufo.png', randint(80, 700-80), -50, 80, 50, 1, 1)
            enemis.add(enemy)
            score += 1
        # столкновение пули с метеоритом
        for i in mcollides:
            i.HP -= 1
            if i.HP == 0:
                i.kill()
                meteorit = Enemy('meteorit.png', randint(80, 700-80), -70, 70, 70, 1, 3)
                meteorits.add(meteorit)
                score += 1
        # столкновение пули с боссом
        if sprite.spritecollide(boss, bullets, True):
            boss.HP -= 1
            boss.launch()
            if boss.HP == 0:
                win.blit(wins, (win_width/2-130, win_height/2-50))
                finish = True

        enemis.update()
        enemis.draw(win)

        meteorits.update()
        meteorits.draw(win)

        # отображение надписей
        pos = (3, 43)
        if not boss_fight:
            scet = font1.render('Счет: '+str(score), True, (255, 255, 255))
            win.blit(scet, (3, 3))

            scet_other = font1.render('Пропущено: '+str(lost), True, (255, 255, 255))
            win.blit(scet_other, (3, 23))
        else:
            pos = (3, 3)
            boss_lives = font1.render('Осталось ХП у босса: '+str(boss.HP), 1, (255, 255, 255))
            win.blit(boss_lives, (3, 23))
        
        buls = font1.render('Пули: '+str(bulls-num_fire), True, (255, 255, 255))
        win.blit(buls, pos)

        # действия босса
        if boss_fight:
            [i.kill() for i in enemis]
            [i.kill() for i in meteorits]
            boss.reset()
            boss.boss_update()
            meatballs.update()
            meatballs.draw(win)

            if boss_launch == FPS*0.5:
                if randint(0, 100) < 40:
                    boss.launch()
                boss_launch = 0
            else:
                boss_launch += 1
        
        # проверка на проигрышь
        if lost == 5 or\
          sprite.spritecollide(hero, enemis, False) or\
          sprite.spritecollide(hero, meteorits, False) or\
          sprite.spritecollide(hero, meatballs, False):

            win.blit(falls, (win_width/2-130, win_height/2-50))
            finish = True

        if score == 20:
            boss_fight = True

        display.update()
    clock.tick(FPS)