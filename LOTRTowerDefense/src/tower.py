import math
import pygame
from bullet import Bullet   # only if Bullet is in separate file

class Tower:
    """
    Tower class with multiple tower types and improved targeting.
    Tower types: 1=Cannon, 2=Fireball Mage, 3=Ice Tower, 4=Rapid Fire
    """
    
    TOWER_TYPES = {
        1: {
            "name": "Cannon",
            "color": (50, 50, 200),
            "damage": 50,
            "cost": 50,
            "range": 150,
            "cooldown": 30,
            "fire_rate": 1.0,
            "penetration": 1,
            "description": "Standard cannon tower"
        },
        2: {
            "name": "Fireball Mage",
            "color": (200, 100, 50),
            "damage": 100,
            "cost": 100,
            "range": 180,
            "cooldown": 45,
            "fire_rate": 0.7,
            "penetration": 1,
            "description": "High damage magical tower"
        },
        3: {
            "name": "Ice Tower",
            "color": (100, 180, 220),
            "damage": 30,
            "cost": 75,
            "range": 200,
            "cooldown": 20,
            "fire_rate": 1.3,
            "penetration": 2,
            "description": "Slows enemies, fast attacks"
        },
        4: {
            "name": "Rapid Fire",
            "color": (180, 100, 50),
            "damage": 20,
            "cost": 60,
            "range": 120,
            "cooldown": 10,
            "fire_rate": 2.0,
            "penetration": 1,
            "description": "Quick successive shots"
        }
    }
    
    def __init__(self, x, y, center=None, tower_type=1, image=None, bullet_image=None):
        self.x = x
        self.y = y
        self.center = center
        self.tower_type = tower_type
        self.image = image
        self.bullet_image = bullet_image
        self.level = 1
        
        # Get tower stats from type definition
        if tower_type in self.TOWER_TYPES:
            tower_stats = self.TOWER_TYPES[tower_type]
            self.color = tower_stats["color"]
            self.damage = tower_stats["damage"]
            self.cost = tower_stats["cost"]
            self.range = tower_stats["range"]
            self.base_cooldown = tower_stats["cooldown"]
            self.fire_rate = tower_stats["fire_rate"]
            self.penetration = tower_stats["penetration"]
        else:
            # Fallback for unknown types
            self.color = (50, 50, 200)
            self.damage = 50
            self.cost = 50
            self.range = 150
            self.base_cooldown = 30
            self.fire_rate = 1.0
            self.penetration = 1
        
        self.cooldown = 0
        self.current_target = None  # Track current target for better aiming

    def get_cannon_mouth(self):
        """
        Calculate the position where bullets should spawn (cannon mouth).
        Accounts for tower orientation and type.
        """
        # Determine if tower is flipped
        flip_x = False
        if self.center is not None and self.x < self.center[0]:
            flip_x = True
        
        # Base offset varies by tower type
        # These offsets represent the cannon mouth position relative to tower center
        if self.tower_type == 1:  # Cannon
            base_offset_x = 25
            base_offset_y = 35
        elif self.tower_type == 2:  # Fireball Mage
            base_offset_x = 20
            base_offset_y = 40
        elif self.tower_type == 3:  # Ice Tower
            base_offset_x = 15
            base_offset_y = 30
        elif self.tower_type == 4:  # Rapid Fire
            base_offset_x = 30
            base_offset_y = 32
        else:
            base_offset_x = 25
            base_offset_y = 35
        
        # Flip the x offset if tower is on left side
        if flip_x:
            spawn_x = self.x - base_offset_x
        else:
            spawn_x = self.x + base_offset_x
        
        spawn_y = self.y + base_offset_y
        
        return spawn_x, spawn_y

    def draw(self, win):
        if self.image:
            # Flip horizontally when tower is on the left side of the center
            flip_x = False
            if self.center is not None and self.x < self.center[0]:
                flip_x = True
            draw_image = pygame.transform.flip(self.image, flip_x, False)
            rect = draw_image.get_rect(center=(self.x, self.y))
            win.blit(draw_image, rect)
            
            # Draw range indicator (optional, for debugging)
            # pygame.draw.circle(win, (self.color[0], self.color[1], self.color[2], 50), 
            #                    (int(self.x), int(self.y)), self.range, 1)
        else:
            # Fallback circle drawing
            pygame.draw.circle(win, self.color, (self.x, self.y), 15)
    
    def upgrade(self):
        """Upgrade tower to next level, improving stats."""
        self.level += 1
        self.damage = int(self.damage * 1.25)  # 25% damage increase
        self.range = int(self.range * 1.1)    # 10% range increase
        self.base_cooldown = max(5, int(self.base_cooldown * 0.85))  # Faster cooldown
        self.cost = int(self.cost * 1.5)  # Cost for next upgrade

    def shoot(self, enemies, bullets):
        """Shoot at the closest enemy within range."""
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        # Find closest enemy within range
        closest_enemy = None
        closest_distance = self.range

        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy

        if closest_enemy:
            # Get cannon mouth position
            spawn_x, spawn_y = self.get_cannon_mouth()
            
            # Create bullet(s) based on penetration stat
            for i in range(self.penetration):
                bullets.append(
                    Bullet(spawn_x, spawn_y, closest_enemy, self.damage, self.bullet_image)
                )
            
            # Apply fire rate modifier to cooldown
            self.cooldown = int(self.base_cooldown / self.fire_rate)
            self.current_target = closest_enemy
