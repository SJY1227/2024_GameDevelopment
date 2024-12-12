import pygame
import random
import sys
import math

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("야구")

background = pygame.image.load("resources/bg.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

FPS = 60
clock = pygame.time.Clock()

class Count(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.ballcount = 0
        self.strikecount = 0
        self.outcount = 0
        self.ball_max = 3
        self.strike_max = 2
        self.out_max = 2

    def draw(self, screen):
        radius = 10
        spacing = 20

        for i in range(self.ball_max):
            color = GREEN if i < self.ballcount else WHITE
            x = 40 + (radius * 2 + spacing) * i
            y = 70
            pygame.draw.circle(screen, color, (x, y), radius)

        for i in range(self.strike_max):
            color = YELLOW if i < self.strikecount else WHITE
            x = 40 + (radius * 2 + spacing) * i
            y = 110
            pygame.draw.circle(screen, color, (x, y), radius)

        for i in range(self.out_max):
            color = RED if i < self.outcount else WHITE
            x = 40 + (radius * 2 + spacing) * i
            y = 150
            pygame.draw.circle(screen, color, (x, y), radius)

    def strike(self):
        self.strikecount += 1
        if self.strikecount == 3:   
            self.out()
            message.show("Strike Out!")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
        else:
            message.show("Strike")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
    
    def ball(self):
        self.ballcount += 1
        if self.ballcount == 4:
            self.ballcount = 0
            self.strikecount = 0
            message.show("Base on Balls!")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
        else:
            message.show("Ball")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))

    def out(self):
        self.ballcount = 0
        self.strikecount = 0
        self.outcount += 1

    def hit(self):
        self.ballcount = 0
        self.strikecount = 0

class Bat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("resources/bat.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (116.3, 20))
        self.rect = pygame.Rect(0, 0, 120, 25)
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 * 2)
        self.speed = 7

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y -5))

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.size = 5
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(300, 500), 50)
        
        self.ySpeed = 2
        self.xSpeed = 0

    def update(self):
        self.xSpeed += random.uniform(-0.3, 0.3) # 랜덤 가속도
        self.ySpeed += random.uniform(0.01, 0.2)
        if random.uniform(0, 10) > 9.8:
            self.xSpeed = 0
        self.rect.y += self.ySpeed
        self.rect.x += self.xSpeed 

        self.size += random.uniform(0, 0.45)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=self.rect.center)
        

    def reset(self):
        self.rect.center = (random.randint(300, 500), 50)
        self.ySpeed = 2
        self.xSpeed = 0
        self.size = 5

class StrikeZone(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 200
        self.rect = pygame.Rect(
            (SCREEN_WIDTH // 2 - self.width // 2, SCREEN_HEIGHT // 2),
            (self.width, self.height)
        )

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect, 3) 


def drawInfo(score):
    font = pygame.font.SysFont(None, 36)
    text_score = font.render(f"Score : {score}", True, WHITE)
    screen.blit(text_score, (20, 20))

def aabb(rect1, rect2):
        if (rect1.right > rect2.left and
        rect2.right > rect1.left and
        rect1.bottom > rect2.top and
        rect2.bottom > rect1.top): #aabb
            return True 
        else:
            return False

def hitResult(rect1, rect2):
    if rect2.width < 15:
        return 0
    
    w = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
    h = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)   
    # w * h : 배트와 공이 겹친 면적

    d1 = math.sqrt(
        (strikeZone.rect.centerx - rect2.centerx) ** 2 +
        (strikeZone.rect.centery - rect2.centery) ** 2
    )
    # d1 : 스트라이크 존 중심으로부터의 거리
    if (d1 > 210):
        return 1
    
    d2 = math.sqrt(
        (rect1.centerx + 30 - rect2.centerx) ** 2 +
        (rect1.centery - rect2.centery) ** 2
    )
    # d2 : 배트 스윗 스팟으로부터의 거리
    if (d2 > 50):
        return 1
    
    return math.pow(w * h, 1) * math.pow(210 - d1, 0.9) * math.pow(50 - d2, 0.6) / 1000
    
bat = Bat()
ball = Ball()
strikeZone = StrikeZone()
count = Count()

allSprite = pygame.sprite.Group()
allSprite.add(ball) # 편한 draw를 위해


swinged = False

baseBG = pygame.image.load("resources/baseBG.png").convert_alpha()
baseBG = pygame.transform.scale(baseBG, (100, 100))
baseOff = pygame.image.load("resources/baseOff.png").convert_alpha()
baseOff = pygame.transform.scale(baseOff, (30, 30))
baseOn = pygame.image.load("resources/baseOn.png").convert_alpha()
baseOn = pygame.transform.scale(baseOn, (30, 30))


aBase = baseOff
bBase = baseOff
cBase = baseOff

class Runners:
    def __init__(self):
        self.base = [False, False, False]
        self.score = 0
    def fourBall(self):
        if self.base[0]:
            if self.base[1]:
                if self.base[2]:
                    score += 1
                self.base[2] = True
            self.base[1] = True
        self.base[0] = True
        
    def hit(self):
        if self.base[2]:
            self.base[2] = False
            self.score += 1
        if self.base[1]:
            self.base[1] = False
            self.base[2] = True
        if self.base[0]:
            self.base[0] = False
            self.base[1] = True
        self.base[0] = True

    def double(self):
        if self.base[2]:
            self.base[2] = False
            self.score += 1
        if self.base[1]:
            self.base[1] = False
            self.score += 1
        if self.base[0]:
            self.base[0] = False
            self.base[2] = True
        self.base[1] = True

    def triple(self):
        if self.base[2]:
            self.base[2] = False
            self.score += 1
        if self.base[1]:
            self.base[1] = False
            self.score += 1
        if self.base[0]:
            self.base[0] = False
            self.score += 1
        self.base[2] = True

    def homeRun(self):
        temp = 1
        if self.base[2]:
            self.base[2] = False
            temp += 1
        if self.base[1]:
            self.base[1] = False
            temp += 1
        if self.base[0]:
            self.base[0] = False
            temp += 1
        if temp == 4:
            message.show("GRAND SLAM!!!!")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
        else:
            message.show("Home Run!!!!")
            message.draw(screen)
            pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
        self.score += temp

runners = Runners()

class Message:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 50)
        self.text = ""
        self.color = YELLOW
        self.start_time = 0
        self.duration = 0  # 메시지가 표시될 시간(ms)

    def show(self, text, duration=2000):
        self.text = text
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

    def draw(self, screen):
        if self.text:
            elapsed_time = pygame.time.get_ticks() - self.start_time
            if elapsed_time < self.duration:
                text_surface = self.font.render(self.text, True, self.color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(text_surface, text_rect)
            else:
                self.text = ""  # 메시지 초기화

message = Message()

screen.blit(background, (0, 0))
screen.blit(baseBG, (20, 185))
screen.blit(aBase, (80, 220))
screen.blit(bBase, (55, 195))
screen.blit(cBase, (30, 220))
drawInfo(runners.score)
count.draw(screen)
strikeZone.draw()
bat.draw(screen)
pygame.display.flip()
pygame.time.delay(1000)

while True:
    screen.blit(background, (0, 0))
    screen.blit(baseBG, (20, 185))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if not swinged:
        bat.update(keys)
    ball.update()

    if ball.size > 20:
        swinged = True # 이중 스트라이크 방지
        if aabb(ball.rect, strikeZone.rect):
            count.strike()
        else:
            count.ball()
        ball.reset()
        pygame.time.delay(700)
        swinged = False

    if keys[pygame.K_SPACE]:
        if not swinged:
            swinged = True
            if aabb(bat.rect, ball.rect):
                hitRate = hitResult(bat.rect, ball.rect)
                print(hitRate)
                if hitRate == 0:
                    count.strike()
                elif hitRate < 60: # 뜬공
                    count.out()
                    message.show("Pop Fly!")
                    message.draw(screen)
                    pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
                elif hitRate < 120: # 안타
                    runners.hit()
                    count.hit()
                    message.show("Hit!")
                    message.draw(screen)
                    pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
                elif hitRate < 180: # 2루타
                    runners.double()
                    count.hit()
                    message.show("Double!!")
                    message.draw(screen)
                    pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
                elif hitRate < 240: # 3루타
                    runners.triple()
                    count.hit()
                    message.show("Triple!!!")
                    message.draw(screen)
                    pygame.display.update(pygame.Rect(SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, 100))
                else: # 홈런
                    runners.homeRun() 
                    
            else: # 헛스윙
                count.strike() 

            ball.reset()
            pygame.time.delay(700)
            swinged = False

    if count.outcount == 3:
        screen.fill(BLACK)
        font1 = pygame.font.SysFont(None, 72)
        font2 = pygame.font.SysFont(None, 50)
        overText = font1.render("Game Over", True, RED)
        screen.blit(overText, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80))
        scoreText = font2.render(f"Score : {runners.score}", True, WHITE)
        screen.blit(scoreText, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 30))
        pygame.display.flip()
        pygame.time.delay(3000)
        pygame.quit()
        sys.exit()

    if runners.base[0]:
        aBase = baseOn
    else:
        aBase = baseOff
    if runners.base[1]:
        bBase = baseOn
    else:
        bBase = baseOff
    if runners.base[2]:
        cBase = baseOn
    else:
        cBase = baseOff    
    
    screen.blit(aBase, (80, 220))
    screen.blit(bBase, (55, 195))
    screen.blit(cBase, (30, 220))

    drawInfo(runners.score)
    count.draw(screen)
    strikeZone.draw()
    bat.draw(screen)
    allSprite.draw(screen)

    
    pygame.display.flip()
    clock.tick(FPS)
