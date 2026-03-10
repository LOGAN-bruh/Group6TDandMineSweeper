# Logan Bywater | 3/10/26
import math
import pygame

class Bullet:
    def __init__(self, x, y, target, damage, image):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.damage = damage
        self.image = image

    def move(self):
        if self.target.health <= 0:
            return True

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return True

        self.x += self.speed * dx / distance
        self.y += self.speed * dy / distance

        if distance < 5:
            self.target.health -= self.damage
            return True

        return False

    def draw(self, win):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        win.blit(self.image, rect)
