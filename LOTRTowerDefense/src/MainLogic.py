
import pygame
import math
import random
import time
pygame.init()
FONT = pygame.font.SysFont("arial", 24)
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("360 Defense")

CLOCK = pygame.time.Clock()
FPS = 60

CENTER = (WIDTH // 2, HEIGHT // 2)

WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)

BASE_RADIUS = 40

# ---------------- ENEMY ----------------
class Enemy:
    def __init__(self, health_multiplier=1, speed_multiplier=1):
        self.x, self.y = self.spawn_position()
        self.base_speed = 3
        self.base_health = 100

        self.speed = self.base_speed * speed_multiplier
        self.health = self.base_health * health_multiplier
        self.radius = 10

    def spawn_position(self):
        directions = [
            (WIDTH//2, 0),                  # N
            (WIDTH, 0),                     # NE
            (WIDTH, HEIGHT//2),             # E
            (WIDTH, HEIGHT),                # SE
            (WIDTH//2, HEIGHT),             # S
            (0, HEIGHT),                    # SW
            (0, HEIGHT//2),                 # W
            (0, 0)                          # NW
        ]
        return random.choice(directions)

    def move(self):
        dx = CENTER[0] - self.x
        dy = CENTER[1] - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.x += self.speed * dx / distance
            self.y += self.speed * dy / distance

    def reached_base(self):
        return math.hypot(self.x - CENTER[0], self.y - CENTER[1]) <= BASE_RADIUS

    def draw(self, win):
        pygame.draw.circle(win, RED, (int(self.x), int(self.y)), self.radius)

# ---------------- TOWER ----------------
class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.cooldown = 0

    def draw(self, win):
        pygame.draw.circle(win, BLUE, (self.x, self.y), 15)

    def shoot(self, enemies, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance <= self.range:
                bullets.append(Bullet(self.x, self.y, enemy))
                self.cooldown = 30
                break

# ---------------- BULLET ----------------
class Bullet:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5

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
            self.target.health -= 50
            return True

        return False

    def draw(self, win):
        pygame.draw.circle(win, BLACK, (int(self.x), int(self.y)), 5)

# ---------------- MAIN ----------------
def main():
    
    enemies = []
    towers = []
    bullets = []
    killcount = 0
    spawn_timer = 0
    base_health = 2
    money = 200
    TOWER_COST = 50
    # After enemy updates, after killcount increases
    # difficulty_level = killcount // 10
    # multiplier = 1 + (difficulty_level * 0.05)
    # spawn_interval = max(90 - difficulty_level * 5, 15)
    error_message = ""
    error_timer = 0
    running = True
    
    while running:
        CLOCK.tick(FPS)
        WIN.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            def can_place_tower(x, y):
                dx = x - CENTER[0]
                dy = y - CENTER[1]
                distance = math.hypot(dx, dy)
                return 75 < distance < 150
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                if can_place_tower(x, y):
                    if money >= TOWER_COST:
                        towers.append(Tower(x, y))
                        money -= TOWER_COST
                    else:
                        error_message = "Not Enough Money!"
                        error_timer = 60   # show for 60 frames (1 second at 60 FPS)


        pygame.draw.circle(WIN, (180, 180, 180), CENTER, 150, 2)
        pygame.draw.circle(WIN, (180, 180, 180), CENTER, 75, 2)
        # Spawn enemies
        

        # Update enemies
        for enemy in enemies[:]:
            enemy.move()
            if enemy.reached_base():
                base_health -= 1
                enemies.remove(enemy)
            elif enemy.health <= 0:
                enemies.remove(enemy)
                killcount += 1
                money += 25
        # After enemy updates, after killcount increases
        difficulty_level = killcount // 10
        multiplier = 1 + (difficulty_level * 0.05)
        spawn_interval = max(90 - difficulty_level * 5, 15)        

        spawn_timer += 1
        if spawn_timer > spawn_interval:
            enemies.append(Enemy(multiplier, multiplier))
            spawn_timer = 0
        # Towers
        for tower in towers:
            tower.shoot(enemies, bullets)

        # Bullets
        for bullet in bullets[:]:
            if bullet.move():
                bullets.remove(bullet)

        # Draw base
        pygame.draw.circle(WIN, GREEN, CENTER, BASE_RADIUS)

        # Draw objects
        for tower in towers:
            tower.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)

        for bullet in bullets:
            bullet.draw(WIN)
        money_text = FONT.render(f"Money: ${money}", True, BLACK)
        WIN.blit(money_text, (10, 10))
        health_text = FONT.render(f"Health: {base_health}", True, BLACK)
        WIN.blit(health_text, (10, 40))
        kill_count_text = FONT.render(f"Kills: {killcount}", True, BLACK)
        WIN.blit(kill_count_text, (10, 70))
        difficulty_text = FONT.render(f"Difficulty: {difficulty_level}", True, BLACK)
        WIN.blit(difficulty_text, (10, 100))
        if error_timer > 0:
            error_text = FONT.render(error_message, True, (255, 0, 0))
            WIN.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, 50))
            error_timer -= 1
        # pygame.display.update()

        if base_health <= 0:
            print("Game Over")
            error_text = FONT.render("Game Over", True, (255, 0, 0))
            WIN.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, 50))
            error_timer -= 1
            pygame.display.update()
            time.sleep(2)
            running = False
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()
