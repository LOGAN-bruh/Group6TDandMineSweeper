# Quinn Dawson and Jamie Duersch | 3/10/26

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

        # 3. Position the sprite and draw it (use fixed center coordinates)
        draw_x = self.x
        # shift running frame slightly upward (Knight barely moves, Hobbit/Mage move more)
        if self.name == "Knight":
            draw_y = self.y + 4 if self.frame_index == 1 else self.y  # Add +2 (or higher number) when running
        else:
            draw_y = self.y - 2 if self.frame_index == 1 else self.y

        rect = draw_image.get_rect(center=(int(draw_x), int(draw_y)))
        win.blit(draw_image, rect)

        # -------- HEALTH BAR --------
        bar_width = 40
        bar_height = 6

        health_ratio = (self.health / self.max_health) if self.max_health > 0 else 0
        health_ratio = max(0.0, min(1.0, health_ratio))
        current_width = int(bar_width * health_ratio)

        # Calculate sprite offset to keep health bar stable
        sprite_offset = 0
        if self.name == "Knight":
            sprite_offset = 4 if self.frame_index == 1 else 0
        else:
            sprite_offset = -2 if self.frame_index == 1 else 0

        # Keep the health bar stable by compensating for sprite offset
        bar_x = rect.centerx - bar_width // 2
        bar_y = rect.top - 12 - sprite_offset

        # background
        pygame.draw.rect(win, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # current health
        pygame.draw.rect(win, (0, 200, 0), (bar_x, bar_y, current_width, bar_height))

        # border
        pygame.draw.rect(win, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
