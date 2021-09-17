"""
(c) 2021 Zachary Stewart
"""
import pygame
import classes
import math
import random
import sys
import time

screen = pygame.display.set_mode([800, 400])
screen.fill([255, 255, 255])

def vec_to_coord(magnitude, direction):
    y = magnitude * math.sin(math.radians(direction))
    x = magnitude * math.cos(math.radians(direction))

    return [x, y]

def coord_to_vec(x, y):
    magnitude = math.sqrt(x**2 + y**2)
    direction = math.degrees(math.atan2(y/x))
    return [magnitude, direction]

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p1[1])**2)

class Robot():
    def __init__(self, health, x, y, direction, speed, turret_dir, computer):
        self.health = health
        self.x = x
        self.y = y
        self.speed = speed
        self.turret_dir = turret_dir
        self.direction = direction
        self.computer = computer

        self.next_action = 0

        self.MAX_SPEED = 3
        self.MOVE_COST = 1
        self.FIRE_COST = 1
        self.BULLET_DAMAGE = 5

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def move(self, distance, direction):
        delta = vec_to_coord(distance, direction)
        #print(delta)
        self.x += delta[0]
        self.y += delta[1]

    def aim_turret(self, angle):
        if angle < 0: angle = 0
        elif angle > 360: angle = 360
        self.turret_dir = angle

    def read_data(self):
        if self.computer.data[0] < 0:
            self.speed = 0
        elif self.computer.data[0] > self.MAX_SPEED:
            self.speed = self.MAX_SPEED
        else:
            self.speed = self.computer.data[0]

        self.direction = self.computer.data[1]
        self.turret_dir = self.computer.data[2]
        self.next_action = self.computer.data[6]

    def write_data(self):
        self.computer.data[0] = self.speed
        self.computer.data[1] = self.direction
        self.computer.data[2] = self.turret_dir
        self.computer.data[3] = self.x
        self.computer.data[4] = self.y
        self.computer.data[5] = self.health
        self.computer.data[6] = self.next_action


    def tick(self, items, bullets):
        #print("IN TICK speed =", self.speed)
        self.read_data()
        if self.next_action == 1: #scan
            scan_result = self.scan(self.turret_dir, items)
            self.computer.data[7] = scan_result[0]
        elif self.next_action == 2: #fire
            self.fire(self.turret_dir, bullets)
        self.move(self.speed, self.direction)
        self.next_action = 0
        self.write_data()

    def scan(self, direction, item_rects):
        #return values: [type, distance]
        #types: 0 = nothing, 1 = wall, 2 = bot
        #todo: rewrite so it doesn't freeze!
        return [1, 0] #placeholder
        delta = vec_to_coord(1, direction)
        arena = pygame.Rect(0, 0, 800, 400)
        point = [self.x, self.y]
        while True:
            if not arena.collidepoint(point[0], point[1]):
                dist = distance(point, [self.x, self.y])
                result = [1, dist]
                break
            for rect in item_rects:
                if rect.collidepoint(point[0], point[1]):
                    dist = dist = distance(point, [self.x, self.y])
                    result = [2, dist]
                    break
        return result

    def fire(self, direction, bullets):
        rect = self.get_rect()
        turret_end_x, turret_end_y = [rect.centerx + vec_to_coord(17, self.turret_dir)[0],
                      rect.centery + vec_to_coord(17, self.turret_dir)[1]]
        self.health -= self.FIRE_COST
        bullets.append(Bullet(turret_end_x, turret_end_y, self.turret_dir, 1, self.BULLET_DAMAGE))

    def render(self, screen):
        rect = pygame.Rect(0, 0, 20, 20)
        rect.center = [self.x, self.y]
        pygame.draw.rect(screen, [0, 0, 0], rect, 1)
        turret_start = rect.center
        turret_end = [rect.centerx + vec_to_coord(17, self.turret_dir)[0], rect.centery + vec_to_coord(17, self.turret_dir)[1]]
        pygame.draw.line(screen, [0, 0, 0], turret_start, turret_end)

    def get_rect(self):
        rect = pygame.Rect(0, 0, 20, 20)
        rect.center = [self.x, self.y]
        return rect

class Bullet():
    def __init__(self, x, y, direction, speed, damage):
        self.x, self.y = x, y
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def move(self, direction, speed):
        delta = vec_to_coord(speed, direction)
        self.x += delta[0]
        self.y += delta[1]

    def render(self, screen):
        pygame.draw.circle(screen, [0,0,0], [self.x, self.y], 1)

code = [
    "write 5 0",
    "write 12 1",
    "cmp @0 0",
    "jumpz :end",
    "cmp @1 0",
    "jumpz :end",
    "load 0",
    ":loop",
    "add @2 @0",
    "write @a 2",
    "sub @1 1",
    "write @a 1",
    "cmp 0 @1",
    "jumpnz :loop",
    ":end",
    "halt"]
"""
code = [
    "add @a 2",
    "write @a 2",
    "write 2 6",
    "jump 0",
]
code = ["logchar 65", "logchar 65", "logchar 65", "logchar 10", "logchar 65"]
"""

c = classes.Computer(code, 10, 0)
r = Robot(100, 400, 200, 0, 0, 0, c)
r2 = Robot(100, 200, 100, 0, 0, 0, c)
b = Bullet(200, 200, 0, 1, 1)
r.render(screen)
b.render(screen)
pygame.display.flip()

robots = [r, r2]
bullets = [b]
#input()
print(r.speed)

while c.running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill([255,255,255])
    for robot in robots:
        robot.render(screen)
    for bullet in bullets:
        bullet.move(bullet.direction, bullet.speed)
        bullet.render(screen)

    pygame.display.flip()
    print(c.code[c.pc])
    for robot in robots:
        robot.computer.execute_next()
        robot.tick([], bullets)
    #r.fire(r.turret_dir, bullets)
    #r.scan(r.turret_dir, [])
    #time.sleep(0.01)
    #print(r.computer.data[5])
    """
    try: line = c.code[c.pc]
    except: break
    c.execute(line)
    print(line)
    print(c.accumulator)
    print(c.data)
    print(c.flags)
    #input()
    """
print("\nFinal state:")
print(c.accumulator)
print(c.data)
print(c.flags)
print(c.log)
