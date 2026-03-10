# Quinn Dawson and Jamie Duersch

import pygame
import math
import random

class Enemy:
    def __init__(self, width, height, center, enemy_type_list, health_multiplier, speed_multiplier):
        enemy_type = random.choice(enemy_type_list)

        # ADD THIS LINE:
        self.name = enemy_type["name"] 

        self.frames = enemy_type["frames"]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        # ... rest of your code ...

        self.width = width
        self.height = height
        self.center = center

        self.x = random.choice([0, width])
        self.y = random.randint(0, height)

        self.speed = enemy_type["speed"] * speed_multiplier
        self.health = enemy_type["health"] * health_multiplier
        self.max_health = self.health
        self.reward = enemy_type["reward"]

        self.animation_timer = 0

    def move(self):
        dx = self.center[0] - self.x
        dy = self.center[1] - self.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            self.x += self.speed * dx / distance
            self.y += self.speed * dy / distance

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer > 15:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.animation_timer = 0

    def reached_base(self, base_radius):
        distance = math.hypot(self.x - self.center[0], self.y - self.center[1])
        return distance <= base_radius

    def draw(self, win):
        # 1. Determine if we need to flip the image
        flip_x = False
        
        # Get the enemy name from the type list (assumes you saved self.name in __init__)
        if self.name in ["Mage", "Knight"]:
            if self.x > self.center[0]:  # On the right side
                flip_x = True
                
        elif self.name == "Hobbit":
            if self.x < self.center[0]:  # On the left side
                flip_x = True

        # 2. Create the (potentially) flipped image
        # pygame.transform.flip(surface, flip_x, flip_y)
        draw_image = pygame.transform.flip(self.image, flip_x, False)

        # 3. Handle the Y-offset for the Hobbit frame 2 if needed
        draw_y = self.y
        draw_x = self.x
        if self.name == "Hobbit" and self.frame_index == 1:
            draw_y -= 3.5
            draw_x -= -15
        if self.name == "Knight" and self.frame_index == 1:
            draw_y -= -10
            draw_x -= -15

        # 4. Draw to the screen
        rect = draw_image.get_rect(center=(self.x, draw_y))
        win.blit(draw_image, rect)

        # -------- HEALTH BAR --------
        bar_width = 40
        bar_height = 6

        health_ratio = self.health / self.max_health
        current_width = bar_width * health_ratio

        bar_x = rect.centerx - bar_width // 2
        bar_y = rect.top - 10

        # background
        pygame.draw.rect(win, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # current health
        pygame.draw.rect(win, (0, 200, 0), (bar_x, bar_y, current_width, bar_height))

        # border
        pygame.draw.rect(win, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
