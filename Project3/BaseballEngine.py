import pygame
import pygame.gfxdraw
import sys
import math

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Baseball Engine")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (135, 206, 250)

FPS = 60
clock = pygame.time.Clock()

class Ball:
    def __init__(self):
        self.realRadius = 10
        self.radius = 0
        self.x = SCREEN_WIDTH / 2
        self.y = 200
        self.distance = 18.44
        self.maxDistance = 18.44
        self.arrivalPoint = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100]

    def update(self):
        self.distance -= 0.25
        if self.distance > 1:
            scale = 1 / self.distance
        else:
            scale = 1
        self.radius = max(1, self.realRadius * scale)

        # 내분점으로 위치 계산
        t = 1 - self.distance / self.maxDistance
        t = min(max(t, 0), 1)
        self.x = (1 - t) * (SCREEN_WIDTH / 2) + t * self.arrivalPoint[0]
        self.y = (1 - t) * 50 + t * self.arrivalPoint[1]

    def lead(self, x=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT // 2 + 100):
        self.arrivalPoint = [x, y]

    def reset(self):
        self.radius = 0
        self.x = SCREEN_WIDTH / 2
        self.y = 50
        self.distance = 18.44
        self.arrivalPoint = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100]

    def draw(self, screen):
        if self.radius > 0:
            draw_circle(screen, (self.x, self.y), self.radius)      
    
def draw_circle(screen, center, radius):
    cx, cy = center
    for y in range(int(cy - radius - 1), int(cy + radius + 2)):
        for x in range(int(cx - radius - 1), int(cx + radius + 2)):
            distance = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if distance < radius:
                screen.set_at((x, y), WHITE)
            
class StrikeZone:
    def __init__(self):
        self.width = 180 # 실제의 약 4배
        self.height = 208 # 실제의 약 4배 (지면으로부터 하단 49.5cm 상단 101.5cm)
        self.rect = pygame.Rect(
            (SCREEN_WIDTH // 2 - self.width // 2, SCREEN_HEIGHT // 2),
            (self.width, self.height)
        )

    def get_vertices(self):
        return [
            (self.rect.left, self.rect.top),  # 왼쪽 위
            (self.rect.right, self.rect.top),  # 오른쪽 위
            (self.rect.right, self.rect.bottom),  # 오른쪽 아래
            (self.rect.left, self.rect.bottom),  # 왼쪽 아래
        ]

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, 3)

class Bat:
    def __init__(self):
        self.vertices = [  # 상대 좌표
            (0, 0), (-3, 3), (-3, 15), (0, 18), (3, 18), (6, 15), (75, 21),
            (105, 21), (111, 15), (111, 3), (105, -3), (75, -3), (6, 3), (3, 0), (0, 0)
        ]
        self.center = [SCREEN_WIDTH // 2 - 55, SCREEN_HEIGHT // 3 * 2]  # 배트 중심
        self.speed = 3  # 배트 이동 속도

    def get_vertices(self):
        return [
            (self.center[0] + vx, self.center[1] + vy)
            for vx, vy in self.vertices
        ]

    def get_sweetspot(self):
        return (int(self.center[0] + 80), int(self.center[1] + 9))
    
    def get_radius(self, x):
        y_values = []
        bat_vertices = self.get_vertices()
    
        for i in range(len(bat_vertices)):
            x1, y1 = bat_vertices[i]
            x2, y2 = bat_vertices[(i + 1) % len(bat_vertices)]
        
            if (x1 <= x <= x2) or (x2 <= x <= x1):
                if x1 != x2:
                    y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
                    y_values.append(y)
                else:
                    y_values.extend([y1, y2])

    
        if y_values:
            return (max(y_values) - min(y_values)) / 2
        else:
            return 0 

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        self.center[0] += dx
        self.center[1] += dy

    def draw(self, screen):
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, GREEN, vertices, 0)

    def draw_swing(self, screen):
        vertices = self.get_vertices()
        pygame.draw.polygon(screen, YELLOW, vertices, 0) 

        
class BaseballField:
    def __init__(self, radius):
        self.center = (SCREEN_WIDTH // 5, SCREEN_HEIGHT - 50)
        self.realRadius = 125 # 야구장 실제 크기
        self.radius = radius  # 야구장 반지름
        self.angle = math.radians(45)  # 좌우 각각 45도

    def draw(self, screen):
        pygame.gfxdraw.filled_polygon(
            screen,
            self.get_vertices(),
            GREEN
        )
        pygame.gfxdraw.aapolygon(
            screen,
            self.get_vertices(),
            WHITE
        )
        
    def get_vertices(self):
        cx, cy = self.center
        vertices = [(cx, cy)]
        for angle in range(0, 91):
            rad = math.radians(135 - angle)
            x = cx + self.radius * math.cos(rad)
            y = cy - self.radius * math.sin(rad)
            vertices.append((int(x), int(y)))
        return vertices

    def get_hit_point(self, distance, horizontal_angle):
        cx, cy = self.center
        scaled_distance = distance / self.realRadius * self.radius
        rad = horizontal_angle + math.pi * 1/2
        x = cx + scaled_distance * math.cos(rad)
        y = cy - scaled_distance * math.sin(rad)
        return (int(x), int(y))


###### 다각형 - 원 SAT 알고리즘 함수 ######
def sat_circle_polygon(circle, polygon):
    cx, cy, radius = circle
    closest_vertex = None
    min_distance = float('inf')

    for vx, vy in polygon:
        distance = math.sqrt((vx - cx) ** 2 + (vy - cy) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_vertex = (vx, vy)

    axes = []

    for i in range(len(polygon)):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % len(polygon)]
        edge = (x2 - x1, y2 - y1)
        normal = (-edge[1], edge[0]) 

        if normal != (0, 0):
            axes.append(normal)

    if closest_vertex:
        axis = (closest_vertex[0] - cx, closest_vertex[1] - cy)
        if axis != (0, 0):
            axes.append(axis)

    for axis in axes:
        circle_proj = project_circle(axis, (cx, cy), radius)
        polygon_proj = project_polygon(axis, polygon)

        if not overlap(circle_proj, polygon_proj):
            return False 
    return True 

def project_circle(axis, center, radius):
    axis_length = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
    normalized_axis = (axis[0] / axis_length, axis[1] / axis_length)

    center_projection = center[0] * normalized_axis[0] + center[1] * normalized_axis[1]
    return center_projection - radius, center_projection + radius

def project_polygon(axis, polygon):
    axis_length = math.sqrt(axis[0] ** 2 + axis[1] ** 2)
    normalized_axis = (axis[0] / axis_length, axis[1] / axis_length)

    projections = [
        vx * normalized_axis[0] + vy * normalized_axis[1]
        for vx, vy in polygon]
    return min(projections), max(projections)

def overlap(proj1, proj2):
    return not (proj1[1] < proj2[0] or proj2[1] < proj1[0])


###### 타구 물리량 계산 함수 ######
def calculate_horizontal_angle(ball_distance, ball_x, sweetspot_x):
    return math.radians(45 * (ball_distance - 1) + 2 * (sweetspot_x - ball_x))

def calculate_vertical_angle(ball_y, sweetspot_y, bat_radius, ball_radius):
    sin_theta = (sweetspot_y - ball_y) / (bat_radius + ball_radius)
    sin_theta = max(min(sin_theta, 1), -1)
    return math.asin(sin_theta)

def calculate_velocity(ball_distance, ball_x, ball_y, sweetspot_x, sweetspot_y):
    base_velocity = 200
    velocity_penalty = (math.fabs(ball_distance - 1)) * 100
    distance_penalty = 4 * math.sqrt((sweetspot_x - ball_x)**2 + (sweetspot_y - ball_y)**2)
    v0 = (base_velocity - velocity_penalty - distance_penalty)
    return v0 / 3.6 # km/h -> m/s 변환

def calculate_launch_height(ball_y, strikezone_bottom_y):
    h = (strikezone_bottom_y - ball_y) / 4 + 49.5  # pygame y축 방향 고려4배 스케일, 좌표계는 실제(cm) 4배 스케일, 스트라이크존 높이 49.5 cm
    return h / 100  # cm -> m 단위 변환


###### 타구 3차원 좌표 계산 함수 ######
def coords3D(v0, vertical_angle, horizontal_angle, h, time, g=9.8):
    horizontal_angleX = math.pi / 2 + horizontal_angle # 12시 방향을 0도로 측정했던 horizontal_angle을 조정
    
    v_xy = v0 * math.cos(vertical_angle) # 수평면 방향 속도
    vx = v_xy * math.cos(horizontal_angleX) # 수평면의 x축 방향
    vy = v_xy * math.sin(horizontal_angleX) # 수평면의 y축 방향
    
    vz = v0 * math.sin(vertical_angle) # 수직 방향 속도

    x = vx * time
    y = vy * time
    z = h + (vz - 0.5 * g * time) * time

    return (x, y, z)


###### 타구 비거리 계산 함수 ######
def calculate_range(v0, vertical_angle, h, g=9.8):
    sin_thetha = math.sin(vertical_angle)
    r = v0 * math.cos(vertical_angle)
    r *= (v0 * sin_thetha + math.sqrt((v0 * sin_thetha) ** 2 + 2 * g * h))
    r /= g
    print(r)
    return r


###### 데모 프로그램 타구 궤적 그리기 함수 ######
def draw_parabola(v0, vertical_angle, horizontal_angle, h, time_start = 0, time_step = 0.1, time_end = 30, z_scale = 1):
    points = []
    time = time_start
    while time <= time_end:
        x, y, z = coords3D(v0, vertical_angle, horizontal_angle, h, time)
        if z >= 0:
            xy_distance = math.sqrt(x**2 + y**2)
            scaled_z = z * z_scale
            points.append((int(xy_distance + 100), int(300 - scaled_z)))  # (100, 300을 원점으로 삼아서 pygame 좌표계 뒤집어서 그림)
        time += time_step
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        bresenham_line(screen, x0, y0, x1, y1, WHITE)

    pygame.draw.line(screen, GREEN, (100, 300), (225, 300), 1) # x축 (야구장 길이만큼만)
    pygame.draw.line(screen, LIGHT_BLUE, (100, 300), (100, 200), 1) # y축

def bresenham_line(surface, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        surface.set_at((x0, y0), color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

        

bat = Bat()
ball = Ball()
strikeZone = StrikeZone()
baseball_field = BaseballField(125)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    bat.update(keys)
    ball.update()

    if ball.distance <= 0:
        screen.fill(BLACK)
        strikeZone.draw(screen)
        bat.draw(screen)
        ball.draw(screen)
        baseball_field.draw(screen)
        pygame.display.flip()
        pygame.time.delay(500)

    
        if sat_circle_polygon((ball.x, ball.y, ball.radius), strikeZone.get_vertices()):
            print("Strike!")
        else:
            print("Ball!")
        ball.reset()


    # 스윙
    elif keys[pygame.K_SPACE]:
        screen.fill(BLACK)
        strikeZone.draw(screen)
        bat.draw_swing(screen)
        ball.draw(screen)
        baseball_field.draw(screen)

        
        if sat_circle_polygon((ball.x, ball.y, ball.radius), bat.get_vertices()):
            if (ball.distance > 2 or ball.distance < 0): # 타격 타이밍이 너무 빠르거나 느린 경우 헛스윙
                print("Miss!")
            else:
                horizontal_angle = calculate_horizontal_angle(ball.distance, ball.x, bat.get_sweetspot()[0])
                vertical_angle = calculate_vertical_angle(ball.y, bat.get_sweetspot()[1], bat.get_radius(ball.x), ball.radius)
                v0 = calculate_velocity(ball.distance, ball.x, ball.y, bat.get_sweetspot()[0], bat.get_sweetspot()[1])
                h = calculate_launch_height(ball.y, strikeZone.rect.bottom)

                if h <= 0 : # 지면에 닿은 투구에 스윙한 경우
                    print("Miss!")
                else:
                    hit_range = calculate_range(v0, vertical_angle, h)
                    x, y = baseball_field.get_hit_point(hit_range, horizontal_angle)
                    pygame.draw.circle(screen, RED, (x, y), 5)
                    
                    draw_parabola(v0, vertical_angle, horizontal_angle, h)
                    print("Hit!")
                    
        else:
            print("Miss!")
        pygame.display.flip()
        pygame.time.delay(1000)
        ball.reset()

    # 화면 그리기
    else:
        screen.fill(BLACK)
        baseball_field.draw(screen)
        strikeZone.draw(screen)
        bat.draw(screen)
        ball.draw(screen)

        pygame.display.flip()
    clock.tick(FPS)