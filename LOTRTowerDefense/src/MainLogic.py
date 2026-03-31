# Lord of the Rings Tower Defense | 3/25/26

# Yicheng Deng and Logan Bywater with UI and logic

import pygame
import math
import random
import time
import os
import json
pygame.init()

# Load Base Sprite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def asset(path):
    # Try direct path relative to this file
    candidate = os.path.join(BASE_DIR, path)
    if os.path.exists(candidate):
        return candidate
    # Check common sibling and project dirs
    candidates = [
        os.path.join(BASE_DIR, '..', path),
        os.path.join(BASE_DIR, 'assets', path),
        os.path.join(BASE_DIR, 'images', path),
        os.path.join(os.getcwd(), path),
        os.path.join(os.getcwd(), 'assets', path),
        os.path.join(os.getcwd(), 'images', path),
    ]
    for c in candidates:
        c_abs = os.path.abspath(c)
        if os.path.exists(c_abs):
            return c_abs
    # Search recursively from BASE_DIR
    for root, dirs, files in os.walk(BASE_DIR):
        if path in files:
            return os.path.join(root, path)
    # Search parent directories up to a few levels
    cur = BASE_DIR
    for _ in range(4):
        for root, dirs, files in os.walk(cur):
            if path in files:
                return os.path.join(root, path)
        cur = os.path.dirname(cur)
    # Fallback: print error and return None
    print(f"Asset not found: {path}")
    return None


def load_image(path, size=None, colorkey=None):
    """Helper to load an image using asset() with safe fallbacks.
    If the file is missing, returns a simple placeholder Surface.
    If size is provided, the surface will be scaled to that size.
    """
    p = asset(path)
    try:
        if p and os.path.exists(p):
            img = pygame.image.load(p).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
    except Exception as e:
        print(f"Warning: failed to load image {path}: {e}")
    # Create placeholder
    if size:
        surf = pygame.Surface(size, pygame.SRCALPHA)
    else:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    surf.fill((200, 0, 0, 255))
    return surf

from enemy import Enemy
from tower import Tower
from bullet import Bullet

FONT = pygame.font.SysFont("arial", 24)
# Title and button fonts - use a serif/fantasy-feel system font if available
TITLE_FONT = pygame.font.SysFont("Georgia", 48, bold=True)
BUTTON_FONT = pygame.font.SysFont("Georgia", 28, bold=True)
STAT_FONT = pygame.font.SysFont("Georgia", 20, bold=True)
UPGRADE_FONT = pygame.font.SysFont("Georgia", 18)
# Smaller font for compact button labels
SMALL_BUTTON_FONT = pygame.font.SysFont("Georgia", 16)
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lord of the Rings Tower Defense | 2026")

CLOCK = pygame.time.Clock()
FPS = 60

CENTER = (WIDTH // 2, HEIGHT // 2)

WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (72, 105, 74)  # darker, less neon grass (#48694a)
# two grass shades for checkered background
GRASS1 = (86, 153, 90)  # #56995a
GRASS2 = GREEN          # #48694a
TILE_SIZE = 32
BLACK = (0, 0, 0)

# Scale everything down by 50% for a tighter look
SIZE_SCALE = 0.65

BASE_RADIUS = int(60 * SIZE_SCALE)
BASE_IMAGE = load_image("towerlvl1.png", (BASE_RADIUS * 2, BASE_RADIUS * 2))
CANNON_IMAGE = load_image("lvl1TowerCannon.png", (int(80 * SIZE_SCALE), int(80 * SIZE_SCALE)))
FIREBALL_IMAGE = pygame.image.load(asset("FireBall.png")).convert_alpha()
FIREBALL_IMAGE = pygame.transform.scale(FIREBALL_IMAGE, (int(40 * SIZE_SCALE), int(40 * SIZE_SCALE)))
BASEFIREBALL_IMAGE = pygame.image.load(asset("FireBall.png")).convert_alpha()
BASEFIREBALL_IMAGE = pygame.transform.scale(BASEFIREBALL_IMAGE, (max(1, int(12 * SIZE_SCALE)), max(1, int(12 * SIZE_SCALE))))

# Load all tower and base level images
BASE_IMAGES = []
TOWER_IMAGES = []

for i in range(1, 7):  # towerlvl1.png through towerlvl6.png
    try:
        img = pygame.image.load(asset(f"towerlvl{i}.png")).convert_alpha()
        img = pygame.transform.scale(img, (BASE_RADIUS * 2, BASE_RADIUS * 2))
        BASE_IMAGES.append(img)
    except:
        BASE_IMAGES.append(BASE_IMAGE)  # fallback

for i in range(1, 4):  # lvl1TowerCannon.png through lvl3TowerCannon.png
    try:
        img = pygame.image.load(asset(f"lvl{i}TowerCannon.png")).convert_alpha()
        img = pygame.transform.scale(img, (int(80 * SIZE_SCALE), int(80 * SIZE_SCALE)))
        TOWER_IMAGES.append(img)
    except:
        TOWER_IMAGES.append(CANNON_IMAGE)  # fallback

knight_frame1 = pygame.transform.scale(
    pygame.image.load(asset("knightenemy.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

knight_frame2 = pygame.transform.scale(
    pygame.image.load(asset("knightenemyRunning.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

hobbit_frame1 = pygame.transform.scale(
    pygame.image.load(asset("hobbitenemy.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

hobbit_frame2 = pygame.transform.scale(
    pygame.image.load(asset("hobbitenemyRunning.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

mage_frame1 = pygame.transform.scale(
    pygame.image.load(asset("mageenemy.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

mage_frame2 = pygame.transform.scale(
    pygame.image.load(asset("mageenemyRunning.png")).convert_alpha(), (int(60 * SIZE_SCALE), int(60 * SIZE_SCALE))
)

# Enemy definitions. Rarer enemies have higher base health and lower spawn weight.
ENEMY_TYPES = [
    {
        "name": "Knight",
        "frames": [knight_frame1, knight_frame2],
        "health": 300,
        "speed": 0.5,
        "reward": 60,
        "base_weight": 20
    },
    {
        "name": "Hobbit",
        "frames": [hobbit_frame1, hobbit_frame2],
        "health": 60,
        "speed": 1.5,
        "reward": 10,
        "base_weight": 50
    },
    {
        "name": "Mage",
        "frames": [mage_frame1, mage_frame2],
        "health": 220,
        "speed": 1,
        "reward": 40,
        "base_weight": 30
    }
]

# Helper to choose enemy type using weighted probabilities that shift with difficulty
def choose_enemy_type(difficulty_level):
    # compute weights increasing tougher enemy probability with difficulty
    weights = []
    for et in ENEMY_TYPES:
        # start with base weight then add small bonus per difficulty
        w = et.get("base_weight", 10) + difficulty_level * (1 if et["name"] == "Knight" else (0.5 if et["name"] == "Mage" else 0.2))
        weights.append(max(1, w))
    # normalize and choose
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for et, w in zip(ENEMY_TYPES, weights):
        if upto + w >= r:
            return et
        upto += w
    return ENEMY_TYPES[0]

# Maximum number of towers allowed on the map
MAX_TOWERS = 15

tower_img_path = asset("lvl1TowerCannon.png")
if tower_img_path:
    TOWER_IMAGE_1 = pygame.image.load(tower_img_path).convert_alpha()
    TOWER_IMAGE_1 = pygame.transform.scale(TOWER_IMAGE_1, (80,80))
else:
    TOWER_IMAGE_1 = pygame.Surface((80,80))
    TOWER_IMAGE_1.fill((200,0,0))
    print("Warning: lvl1TowerCannon.png missing, using placeholder.")
BASE_BARRIER_COLOR = (125, 110, 80)
BASE_BARRIER_EDGE = (40, 30, 20)
BARRIER_PADDING = 18
BARRIER_THICKNESS = 16
BARRIER_LENGTH = BASE_RADIUS * 2 + 120

_top_y = CENTER[1] - BASE_RADIUS - BARRIER_PADDING - BARRIER_THICKNESS
_bottom_y = CENTER[1] + BASE_RADIUS + BARRIER_PADDING
_left_x = CENTER[0] - BASE_RADIUS - BARRIER_PADDING - BARRIER_THICKNESS
_right_x = CENTER[0] + BASE_RADIUS + BARRIER_PADDING

BARRIERS = [
    pygame.Rect(CENTER[0] - BARRIER_LENGTH // 2, _top_y, BARRIER_LENGTH, BARRIER_THICKNESS),
    pygame.Rect(CENTER[0] - BARRIER_LENGTH // 2, _bottom_y, BARRIER_LENGTH, BARRIER_THICKNESS),
    pygame.Rect(_left_x, CENTER[1] - BARRIER_LENGTH // 2, BARRIER_THICKNESS, BARRIER_LENGTH),
    pygame.Rect(_right_x, CENTER[1] - BARRIER_LENGTH // 2, BARRIER_THICKNESS, BARRIER_LENGTH),
]

def draw_barriers(win):
    # Barriers have been removed from the game
    pass

def save_game(filename, game_state):
    """Atomically save game state to JSON file (writes to a temp file and renames).
    Keeps behavior identical (writes the provided dict) but avoids partial files.
    Returns True on success, False on failure."""
    try:
        save_path = os.path.join(BASE_DIR, f"{filename}.json")
        tmp_path = save_path + ".tmp"
        # write to a temporary file first
        with open(tmp_path, 'w') as f:
            json.dump(game_state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # atomic replace
        os.replace(tmp_path, save_path)
        return True
    except Exception as e:
        print(f"Error saving game atomically: {e}")
        try:
            # fallback: try non-atomic write
            with open(save_path, 'w') as f:
                json.dump(game_state, f, indent=2)
            return True
        except Exception as e2:
            print(f"Fallback save failed: {e2}")
            return False

def load_game(filename):
    """Load game state from JSON file."""
    try:
        save_path = os.path.join(BASE_DIR, f"{filename}.json")
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading game: {e}")
        return None

# Helper to update save file with slots and most_recent without overwriting other sections
# This implements a simple, robust slot system used by the pause save UI and autosave.
# Each slot stores a small metadata envelope {"timestamp": ..., "version": 1, "state": <game_state>}
SAVE_VERSION = 1

def write_save_slot(filename, slot_name, state):
    try:
        data = load_game(filename) or {}
        if not isinstance(data, dict):
            data = {}
        # ensure version and slots structure
        data.setdefault("version", SAVE_VERSION)
        data.setdefault("slots", {})
        envelope = {"timestamp": int(time.time() * 1000), "version": SAVE_VERSION, "state": state}
        if slot_name == "most_recent":
            data["most_recent"] = envelope
        else:
            data["slots"][slot_name] = envelope
        return save_game(filename, data)
    except Exception as e:
        print(f"Error writing save slot: {e}")
        return False

# Write multiple numbered slots at once (slot_list is ordered list for save1..saveN)
def write_save_slots_batch(filename, slot_list):
    try:
        data = load_game(filename) or {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("version", SAVE_VERSION)
        data.setdefault("slots", {})
        for i, st in enumerate(slot_list, start=1):
            if st is None:
                data["slots"][f"save{i}"] = None
            else:
                data["slots"][f"save{i}"] = {"timestamp": int(time.time() * 1000), "version": SAVE_VERSION, "state": st}
        return save_game(filename, data)
    except Exception as e:
        print(f"Error writing save slots batch: {e}")
        return False

class PauseButton:
    """Simple on-screen pause button."""
    def __init__(self, x, y, w=50, h=50):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, win):
        # Draw semi-transparent rounded button with || icon for readability
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((30, 30, 30, 170))
        win.blit(s, (self.rect.x, self.rect.y))
        pygame.draw.rect(win, (200, 180, 100), self.rect, 2, border_radius=8)
        # draw pause icon
        bar_w = 8
        bar_h = self.rect.height - 16
        left_bar = pygame.Rect(self.rect.x + 10, self.rect.y + 8, bar_w, bar_h)
        right_bar = pygame.Rect(self.rect.x + self.rect.width - 10 - bar_w, self.rect.y + 8, bar_w, bar_h)
        pygame.draw.rect(win, (220, 220, 220), left_bar)
        pygame.draw.rect(win, (220, 220, 220), right_bar)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class PauseScreen:
    """Wrapper class exposing a show() method to display pause UI and return a choice."""
    @staticmethod
    def show(money, killcount, difficulty_level, base_level):
        return pause_menu(money, killcount, difficulty_level, base_level)


def pause_menu(money, killcount, difficulty_level, base_level, elapsed_seconds=0):
    """Display pause menu and return user choice. Shows current stats."""
    running = True
    resume_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 300, 50)
    save_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 50)
    home_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 300, 50)
    quit_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 50)
    
    while running:
        CLOCK.tick(FPS)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        WIN.blit(overlay, (0, 0))
        
        # Title
        pause_font = pygame.font.SysFont("Georgia", 60, bold=True)
        pause_text = pause_font.render("PAUSED", True, (220, 180, 100))
        WIN.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, 60))
        
        # Stats display under title
        stats_x = WIDTH//2 - 200
        stats_y = 140
        stat_label_color = (200, 180, 120)
        STAT_BG = pygame.Rect(stats_x - 10, stats_y - 10, 420, 120)
        pygame.draw.rect(WIN, (30, 30, 30), STAT_BG, border_radius=8)
        money_text = STAT_FONT.render(f"Money: ${money}", True, WHITE)
        kills_text = STAT_FONT.render(f"Kills: {killcount}", True, WHITE)
        diff_text = STAT_FONT.render(f"Difficulty: {difficulty_level}", True, WHITE)
        base_lvl_text = STAT_FONT.render(f"Base Level: {base_level}", True, WHITE)
        WIN.blit(money_text, (stats_x, stats_y))
        WIN.blit(kills_text, (stats_x + 210, stats_y))
        WIN.blit(diff_text, (stats_x, stats_y + 40))
        WIN.blit(base_lvl_text, (stats_x + 210, stats_y + 40))
        # Timer in pause stats
        mins = int(elapsed_seconds) // 60
        secs = int(elapsed_seconds) % 60
        timer_text = STAT_FONT.render(f"Time: {mins:02d}:{secs:02d}", True, WHITE)
        WIN.blit(timer_text, (stats_x, stats_y + 80))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Resume button
        resume_hover = resume_button.collidepoint(mouse_pos)
        pygame.draw.rect(WIN, (0, 0, 0), (resume_button.x + 4, resume_button.y + 4, resume_button.width, resume_button.height), border_radius=12)
        pygame.draw.rect(WIN, (100, 170, 100) if resume_hover else (72, 105, 74), resume_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), resume_button, 3, border_radius=12)
        resume_text = BUTTON_FONT.render("Resume", True, WHITE)
        WIN.blit(resume_text, (resume_button.x + resume_button.width//2 - resume_text.get_width()//2,
                              resume_button.y + resume_button.height//2 - resume_text.get_height()//2))
        
        # Save button
        save_hover = save_button.collidepoint(mouse_pos)
        pygame.draw.rect(WIN, (0, 0, 0), (save_button.x + 4, save_button.y + 4, save_button.width, save_button.height), border_radius=12)
        pygame.draw.rect(WIN, (100, 140, 200) if save_hover else (70, 100, 150), save_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), save_button, 3, border_radius=12)
        save_text = BUTTON_FONT.render("Save Game", True, WHITE)
        WIN.blit(save_text, (save_button.x + save_button.width//2 - save_text.get_width()//2,
                            save_button.y + save_button.height//2 - save_text.get_height()//2))
        
        # Home button
        home_hover = home_button.collidepoint(mouse_pos)
        pygame.draw.rect(WIN, (0, 0, 0), (home_button.x + 4, home_button.y + 4, home_button.width, home_button.height), border_radius=12)
        pygame.draw.rect(WIN, (200, 100, 100) if home_hover else (150, 70, 70), home_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), home_button, 3, border_radius=12)
        home_text = BUTTON_FONT.render("Home", True, WHITE)
        WIN.blit(home_text, (home_button.x + home_button.width//2 - home_text.get_width()//2,
                            home_button.y + home_button.height//2 - home_text.get_height()//2))
        
        # Quit button
        quit_hover = quit_button.collidepoint(mouse_pos)
        pygame.draw.rect(WIN, (0, 0, 0), (quit_button.x + 4, quit_button.y + 4, quit_button.width, quit_button.height), border_radius=12)
        pygame.draw.rect(WIN, (200, 100, 100) if quit_hover else (150, 70, 70), quit_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), quit_button, 3, border_radius=12)
        quit_text = BUTTON_FONT.render("Quit", True, WHITE)
        WIN.blit(quit_text, (quit_button.x + quit_button.width//2 - quit_text.get_width()//2,
                            quit_button.y + quit_button.height//2 - quit_text.get_height()//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(mouse_pos):
                    return "resume"
                elif save_button.collidepoint(mouse_pos):
                    return "save"
                elif home_button.collidepoint(mouse_pos):
                    return "home"
                elif quit_button.collidepoint(mouse_pos):
                    return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
        
        pygame.display.update()

def draw_forest_decorations(win):
    """Draw trees and bushes around the game area."""
    tree_foliage = (34, 100, 34)  # Dark green for trees
    tree_trunk = (101, 67, 33)    # Brown trunk
    bush_color = (80, 140, 60)    # Lighter green for bushes
    bush_trunk = (90, 60, 30)     # Darker brown for bush base
    
    # Draw decorative trees around the border and throughout the map
    positions = [
        # Corners
        (40, 40), (760, 40), (40, 760), (760, 760),
        # Top/bottom edges
        (150, 25), (300, 20), (500, 25), (650, 20),
        (150, 775), (300, 780), (500, 775), (650, 780),
        # Left/right edges
        (15, 150), (785, 150), (15, 300), (785, 300),
        (15, 500), (785, 500), (15, 650), (785, 650),
        # Interior scattered trees
        (100, 200), (700, 220), (120, 680), (680, 650),
        (200, 150), (600, 180), (200, 720), (600, 700)
    ]
    
    for x, y in positions:
        # Tree trunk (thick and visible)
        pygame.draw.rect(win, tree_trunk, (x - 6, y + 8, 12, 22))
        # Tree foliage (two triangles overlapping for fuller look)
        pygame.draw.polygon(win, tree_foliage, [(x, y - 18), (x - 16, y + 8), (x + 16, y + 8)])
        pygame.draw.polygon(win, tree_foliage, [(x, y - 3), (x - 14, y + 22), (x + 14, y + 22)])
    
    # Draw bushes scattered around for added variety
    bush_positions = [
        (80, 100), (720, 120), (100, 680), (700, 660),
        (180, 80), (620, 100), (180, 750), (620, 740),
        (50, 300), (750, 320), (60, 500), (740, 480),
        (250, 500), (550, 480), (270, 250), (550, 280),
        (400, 150), (420, 700), (130, 430), (680, 400)
    ]
    
    for x, y in bush_positions:
        # Bush trunk/base
        pygame.draw.ellipse(win, bush_trunk, (x - 5, y + 10, 10, 14))
        # Bush foliage - overlapping circles for rounded appearance
        pygame.draw.circle(win, bush_color, (x - 8, y), 14)
        pygame.draw.circle(win, bush_color, (x + 8, y), 14)
        pygame.draw.circle(win, bush_color, (x, y - 10), 14)
        pygame.draw.circle(win, bush_color, (x - 4, y + 5), 10)
        pygame.draw.circle(win, bush_color, (x + 4, y + 5), 10)

def game_over_screen(killcount, money, difficulty_level, base_level):
    """Display game over screen with stats and options."""
    running = True
    play_again_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 150, 180, 50)
    home_button = pygame.Rect(WIDTH//2 + 40, HEIGHT//2 + 150, 180, 50)
    
    while running:
        CLOCK.tick(FPS)
        
        # Gradient background (game over theme)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(60 + (100 - 60) * ratio)
            g = int(20 + (20 - 20) * ratio)
            b = int(40 + (60 - 40) * ratio)
            pygame.draw.line(WIN, (r, g, b), (0, y), (WIDTH, y))
        
        # Title
        game_over_font = pygame.font.SysFont("Georgia", 72, bold=True)
        game_over_text = game_over_font.render("GAME OVER", True, (220, 50, 50))
        WIN.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 80))
        
        # Stats display
        stats_y = 200
        stat_font = pygame.font.SysFont("Georgia", 32, bold=True)
        
        kills_text = stat_font.render(f"Kills: {killcount}", True, (220, 180, 100))
        WIN.blit(kills_text, (WIDTH//2 - kills_text.get_width()//2, stats_y))
        
        money_text = stat_font.render(f"Gold: ${money}", True, (220, 180, 100))
        WIN.blit(money_text, (WIDTH//2 - money_text.get_width()//2, stats_y + 50))
        
        difficulty_text = stat_font.render(f"Difficulty: {difficulty_level}", True, (220, 180, 100))
        WIN.blit(difficulty_text, (WIDTH//2 - difficulty_text.get_width()//2, stats_y + 100))
        
        base_level_text = stat_font.render(f"Base Level: {base_level}", True, (220, 180, 100))
        WIN.blit(base_level_text, (WIDTH//2 - base_level_text.get_width()//2, stats_y + 150))
        
        # Buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Play Again button
        play_again_hover = play_again_button.collidepoint(mouse_pos)
        play_color = (100, 170, 100) if play_again_hover else (72, 105, 74)
        pygame.draw.rect(WIN, (0, 0, 0), (play_again_button.x + 4, play_again_button.y + 4, play_again_button.width, play_again_button.height), border_radius=12)
        pygame.draw.rect(WIN, play_color, play_again_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), play_again_button, 3, border_radius=12)
        play_text = BUTTON_FONT.render("Play Again", True, WHITE)
        WIN.blit(play_text, (play_again_button.x + play_again_button.width//2 - play_text.get_width()//2, 
                             play_again_button.y + play_again_button.height//2 - play_text.get_height()//2))
        
        # Home button
        home_hover = home_button.collidepoint(mouse_pos)
        home_color = (200, 100, 100) if home_hover else (150, 70, 70)
        pygame.draw.rect(WIN, (0, 0, 0), (home_button.x + 4, home_button.y + 4, home_button.width, home_button.height), border_radius=12)
        pygame.draw.rect(WIN, home_color, home_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), home_button, 3, border_radius=12)
        home_text = BUTTON_FONT.render("Home", True, WHITE)
        WIN.blit(home_text, (home_button.x + home_button.width//2 - home_text.get_width()//2, 
                            home_button.y + home_button.height//2 - home_text.get_height()//2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(mouse_pos):
                    return "play_again"
                elif home_button.collidepoint(mouse_pos):
                    return "home"
        
        pygame.display.update()

def main_menu():
    print("[DEBUG] Entering main_menu", flush=True)
    # flush any pending input events to avoid accidental clicks
    pygame.event.clear()
    # give a short grace period during which clicks are ignored in case the OS
    # queues a mouse event when the window is created or focused.
    start_time = pygame.time.get_ticks()
    ignore_until = start_time + 500  # milliseconds
    menu_running = True
    play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
    load_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50)
    quit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 190, 200, 50)
    button_clicked = None
    saved_game_data = None

    while menu_running:
        # debug show that loop iteration started
        #print("[DEBUG] main_menu loop")
        CLOCK.tick(FPS)
        
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(30 + (60 - 30) * ratio)
            g = int(20 + (30 - 20) * ratio)
            b = int(40 + (80 - 40) * ratio)
            pygame.draw.line(WIN, (r, g, b), (0, y), (WIDTH, y))
        
        # Decorative border lines
        pygame.draw.line(WIN, (200, 160, 80), (50, 80), (750, 80), 3)
        pygame.draw.line(WIN, (200, 160, 80), (50, 720), (750, 720), 3)

        # Title with golden/bronze color
        title_text = TITLE_FONT.render("LORD OF THE RINGS", True, (220, 180, 100))
        WIN.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//3 - 40))
        
        subtitle_font = pygame.font.SysFont("Georgia", 36, bold=True)
        subtitle_text = subtitle_font.render("TOWER DEFENSE", True, (180, 140, 70))
        WIN.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3 + 40))

        # Ownership / credit text at bottom of title screen
        ownership_text = SMALL_BUTTON_FONT.render("Yicheng Deng, Logan Bywater, Quinn Dawson, & Jamie Duersch | Group6 | 2026 ", True, (200, 200, 200))
        WIN.blit(ownership_text, (WIDTH//2 - ownership_text.get_width()//2, HEIGHT - 36))

        # Get mouse position for button hover
        mouse_pos = pygame.mouse.get_pos()
        mouse_over_play = play_button.collidepoint(mouse_pos)
        mouse_over_load = load_button.collidepoint(mouse_pos)
        mouse_over_quit = quit_button.collidepoint(mouse_pos)
        
        # Play Button styling with shadow
        pygame.draw.rect(WIN, (0, 0, 0), (play_button.x + 4, play_button.y + 4, play_button.width, play_button.height), border_radius=12)
        button_color = (100, 170, 100) if mouse_over_play else (72, 105, 74)
        pygame.draw.rect(WIN, button_color, play_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), play_button, 3, border_radius=12)
        play_text = BUTTON_FONT.render("PLAY", True, WHITE)
        WIN.blit(play_text, (play_button.x + play_button.width//2 - play_text.get_width()//2, play_button.y + play_button.height//2 - play_text.get_height()//2))
        
        # Load Button styling with shadow
        load_color = (100, 140, 200) if mouse_over_load else (70, 100, 150)
        pygame.draw.rect(WIN, (0, 0, 0), (load_button.x + 4, load_button.y + 4, load_button.width, load_button.height), border_radius=12)
        pygame.draw.rect(WIN, load_color, load_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), load_button, 3, border_radius=12)
        load_text = BUTTON_FONT.render("LOAD GAME", True, WHITE)
        WIN.blit(load_text, (load_button.x + load_button.width//2 - load_text.get_width()//2, load_button.y + load_button.height//2 - load_text.get_height()//2))
        
        # Quit Button styling with shadow
        quit_color = (200, 100, 100) if mouse_over_quit else (150, 70, 70)
        pygame.draw.rect(WIN, (0, 0, 0), (quit_button.x + 4, quit_button.y + 4, quit_button.width, quit_button.height), border_radius=12)
        pygame.draw.rect(WIN, quit_color, quit_button, border_radius=12)
        pygame.draw.rect(WIN, (200, 180, 100), quit_button, 3, border_radius=12)
        quit_text = BUTTON_FONT.render("QUIT", True, WHITE)
        WIN.blit(quit_text, (quit_button.x + quit_button.width//2 - quit_text.get_width()//2, quit_button.y + quit_button.height//2 - quit_text.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("[DEBUG] main_menu received QUIT event", flush=True)
                menu_running = False
                button_clicked = "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()
                print(f"[DEBUG] main_menu got MOUSEBUTTONDOWN event: pos={event.pos} button={event.button} time={current_time}", flush=True)
                if current_time < ignore_until:
                    print("[DEBUG] Ignoring click during startup grace period", flush=True)
                else:
                    click_pos = pygame.mouse.get_pos()
                    print(f"[DEBUG] mouse.get_pos() returned {click_pos}", flush=True)
                    if play_button.collidepoint(click_pos):
                        print("[DEBUG] play button hit", flush=True)
                        button_clicked = "play"
                        menu_running = False
                    elif load_button.collidepoint(click_pos):
                        print("[DEBUG] load button hit", flush=True)
                        saved_file = load_game("game_save")
                        if saved_file:
                            # support both envelope (with 'most_recent') and raw state
                            if isinstance(saved_file, dict):
                                if "most_recent" in saved_file and isinstance(saved_file["most_recent"], dict):
                                    saved_game_data = saved_file["most_recent"].get("state")
                                elif "state" in saved_file:
                                    saved_game_data = saved_file.get("state")
                                else:
                                    # assume it's raw state dict
                                    saved_game_data = saved_file
                            else:
                                saved_game_data = saved_file
                            button_clicked = "load"
                            menu_running = False
                    elif quit_button.collidepoint(click_pos):
                        print("[DEBUG] quit button hit", flush=True)
                        button_clicked = "quit"
                        menu_running = False

        # end event processing
        pygame.display.update()

    # after menu loop ends
    print(f"[DEBUG] main_menu exiting with button_clicked={button_clicked}, saved_game_data={saved_game_data}", flush=True)
    if button_clicked == "quit":
        pygame.quit()
        quit()
    return button_clicked, saved_game_data

def main(saved_game=None):
    
    enemies = []
    towers = []
    bullets = []
    selected_tower_type = 1  # 1 = blue 2 = purple
    killcount = 0
    spawn_timer = 0
    base_health = 100
    money = 200
    TOWER_COST = 50
    base_range = 500
    base_cooldown = 0
    BASE_FIRE_RATE = int(0.3 * FPS)  # frames between base shots (~0.3 seconds)
    BASE_DAMAGE = 40
    base_level = 1  # Track base level (1-6)
    # Legacy single-slot error fields (many places still set these). New code will
    # transfer these into error_queue each frame so messages don't overlap.
    error_message = ""
    error_timer = 0
    # Queue of active error/status messages shown on screen (each is dict with msg and timer)
    error_queue = []
    def push_error(msg, duration=90):
        # Avoid flooding with identical consecutive messages
        if len(error_queue) == 0 or error_queue[-1]["msg"] != msg:
            error_queue.append({"msg": msg, "timer": duration})

    running = True
    upgrade_mode = False
    paused = False
    game_speed = 1.0  # Speed multiplier (1.0 = normal, 2.0 = 2x faster)
    last_autosave = pygame.time.get_ticks()
    save_history = []  # keep recent snapshots (timestamp_ms, game_state_dict)
    elapsed_time_ms = 0  # game timer in milliseconds
    prev_difficulty = 0

    # Helpers to serialize game entities into JSON-friendly dicts
    def serialize_enemies_list(enemies_list):
        s = []
        for e in enemies_list:
            s.append({
                "name": getattr(e, "name", None),
                "x": int(e.x),
                "y": int(e.y),
                "health": e.health,
                "frame_index": getattr(e, "frame_index", 0)
            })
        return s

    def serialize_bullets_list(bullets_list, enemies_list):
        s = []
        for b in bullets_list:
            target_index = enemies_list.index(b.target) if (b.target in enemies_list) else None
            s.append({"x": int(b.x), "y": int(b.y), "damage": b.damage, "target_index": target_index})
        return s

    def make_game_state():
        return {
            "enemies": serialize_enemies_list(enemies),
            "towers": [{"x": int(t.x), "y": int(t.y), "tower_type": int(t.tower_type), "level": int(t.level)} for t in towers],
            "bullets": serialize_bullets_list(bullets, enemies),
            "money": money,
            "killcount": killcount,
            "base_health": base_health,
            "base_level": base_level,
            "difficulty_level": killcount // 10,
            "purchased_upgrades": {"base_level": base_level}
        }

    # Simple slot chooser UI
    def save_slot_menu():
        buttons = []
        mw = 240
        for i in range(7):
            brect = pygame.Rect(WIDTH//2 - mw//2, 140 + i*70, mw, 50)
            buttons.append(brect)
        running_slot = True
        while running_slot:
            CLOCK.tick(FPS)
            # dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((0,0,0))
            WIN.blit(overlay, (0,0))
            title = BUTTON_FONT.render("Choose Save Slot", True, (220,180,100))
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 60))
            mouse_pos = pygame.mouse.get_pos()
            labels = ["Most Recent"] + [f"Save {i}" for i in range(1,6)] + ["Cancel"]
            for idx, rect in enumerate(buttons):
                hover = rect.collidepoint(mouse_pos)
                color = (100,170,100) if hover else (72,105,74)
                if idx == 0:
                    color = (80,120,200) if hover else (70,90,140)
                pygame.draw.rect(WIN, (0,0,0), (rect.x+4, rect.y+4, rect.width, rect.height), border_radius=12)
                pygame.draw.rect(WIN, color, rect, border_radius=12)
                pygame.draw.rect(WIN, (200,180,100), rect, 3, border_radius=12)
                text = BUTTON_FONT.render(labels[idx], True, WHITE)
                WIN.blit(text, (rect.x + rect.width//2 - text.get_width()//2, rect.y + rect.height//2 - text.get_height()//2))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons[0].collidepoint(mouse_pos):
                        return "most_recent"
                    for i in range(1,6):
                        if buttons[i].collidepoint(mouse_pos):
                            return i
                    if buttons[6].collidepoint(mouse_pos):
                        return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
            pygame.display.update()

    # Load saved game if provided
    if saved_game:
        money = saved_game.get("money", 200)
        killcount = saved_game.get("killcount", 0)
        base_health = saved_game.get("base_health", 100)
        base_level = saved_game.get("base_level", 1)
        # Reconstruct saved enemies
        saved_enemies = saved_game.get("enemies", [])
        for ed in saved_enemies:
            try:
                name = ed.get("name")
                sx = ed.get("x", 0)
                sy = ed.get("y", 0)
                shealth = ed.get("health", 0)
                sframe = ed.get("frame_index", 0)
                # find matching enemy type dict
                etype = None
                for et in ENEMY_TYPES:
                    if et.get("name") == name:
                        etype = et
                        break
                if etype is None:
                    etype = ENEMY_TYPES[0]
                new_e = Enemy(WIDTH, HEIGHT, CENTER, [etype], 1, 1)
                new_e.x = sx
                new_e.y = sy
                new_e.health = shealth
                new_e.max_health = getattr(new_e, "max_health", new_e.health)
                new_e.frame_index = sframe
                if hasattr(new_e, "frames") and len(new_e.frames) > 0:
                    new_e.image = new_e.frames[new_e.frame_index]
                enemies.append(new_e)
            except Exception as e:
                print(f"Failed to load enemy: {e}")

        # Reconstruct saved towers (position, type, level)
        saved_towers = saved_game.get("towers", [])
        for tdata in saved_towers:
            try:
                tx = tdata.get("x")
                ty = tdata.get("y")
                ttype = tdata.get("tower_type", 1)
                tlevel = tdata.get("level", 1)
                new_t = Tower(tx, ty, CENTER, tower_type=ttype, image=TOWER_IMAGES[0] if TOWER_IMAGES else None, bullet_image=FIREBALL_IMAGE)
                # upgrade to saved level
                while new_t.level < tlevel:
                    new_t.upgrade()
                # set image based on level if available
                if new_t.level <= len(TOWER_IMAGES):
                    new_t.image = TOWER_IMAGES[new_t.level - 1]
                towers.append(new_t)
            except Exception as e:
                print(f"Failed to load tower: {e}")

        # Reconstruct bullets (use indexes into the enemies list)
        saved_bullets = saved_game.get("bullets", [])
        for bdata in saved_bullets:
            try:
                bx = bdata.get("x")
                by = bdata.get("y")
                dmg = bdata.get("damage", 0)
                tgt_idx = bdata.get("target_index")
                if enemies and tgt_idx is not None and 0 <= tgt_idx < len(enemies):
                    tgt = enemies[tgt_idx]
                elif enemies:
                    tgt = enemies[0]
                else:
                    tgt = None
                if tgt:
                    new_b = Bullet(bx, by, tgt, dmg, FIREBALL_IMAGE)
                    new_b.x = bx
                    new_b.y = by
                    bullets.append(new_b)
            except Exception as e:
                print(f"Failed to load bullet: {e}")
    
    # UI buttons: move upgrade and tower buttons further left of speed controls for clarity
    pause_button = PauseButton(WIDTH - 60, 10, 50, 50)
    speed_plus_button = pygame.Rect(WIDTH - 150, 10, 40, 40)
    speed_minus_button = pygame.Rect(WIDTH - 190, 10, 40, 40)
    upgrade_button_rect = pygame.Rect(WIDTH - 350, 10, 80, 40)
    button1_rect = pygame.Rect(WIDTH - 430, 10, 80, 40)
    button2_rect = pygame.Rect(WIDTH - 510, 10, 80, 40)
    # Panel selection state for upgrade-side-panel
    selected_panel_tower = None
    selected_panel_prev = None
    panel_scroll = 0.0
    panel_scroll_target = 0.0
    panel_dragging = False
    panel_drag_info = {}
    popup_open = False
    popup_target = None
    SCROLL_STEP = 36  # default scroll step in pixels
    while running:
        dt_ms = CLOCK.tick(int(FPS * game_speed))  # Apply speed multiplier and capture delta ms
        # Freeze timer while upgrade panel is open or game is paused
        if not upgrade_mode and not paused:
            elapsed_time_ms += dt_ms
        # Smooth panel scrolling toward target
        # small easing for smooth feel
        scroll_diff = panel_scroll_target - panel_scroll
        panel_scroll += scroll_diff * 0.18
        if abs(scroll_diff) < 0.5:
            panel_scroll = panel_scroll_target
        # Compute current max towers allowance based on base level (each base level grants +2 towers)
        current_max_towers = MAX_TOWERS + (base_level - 1) * 2

        # --- CLEAR AND SETUP ---
        WIN.fill(GRASS1)
        
        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
            # Mouse wheel scrolling support for the upgrade panel (disabled for non-scrolling UI)
            if event.type == pygame.MOUSEWHEEL and upgrade_mode:
                # Scrolling disabled; ignore mouse wheel
                pass

            # Handle mouse button up to stop dragging the scrollbar
            if event.type == pygame.MOUSEBUTTONUP:
                panel_dragging = False

            # If dragging the scrollbar thumb, update scroll target on mouse motion
            if event.type == pygame.MOUSEMOTION and panel_dragging:
                mx, my = event.pos
                info = panel_drag_info
                sr = info.get("scrollbar_rect")
                thumb_h = info.get("thumb_h", 20)
                max_scroll = info.get("max_scroll", 0)
                # compute position relative to scrollbar top minus click offset
                rel = my - sr.y - info.get("click_offset", 0)
                rel = max(0, min(rel, sr.h - thumb_h))
                # map to scroll target
                denom = max(1, sr.h - thumb_h)
                panel_scroll_target = int((rel / denom) * max_scroll) if max_scroll > 0 else 0

            if paused:
                pause_choice = pause_menu(money, killcount, difficulty_level, base_level, int(elapsed_time_ms//1000))
                if pause_choice == "resume":
                    paused = False
                elif pause_choice == "save":
                    gs = make_game_state()
                    write_save_slot("game_save", "most_recent", gs)
                    error_message = "Game Saved!"
                    error_timer = 120
                    paused = False
                elif pause_choice == "home":
                    # Return to main menu and handle user's menu choice
                    action, saved = main_menu()
                    if action == "play":
                        main()
                        return
                    elif action == "load" and saved:
                        main(saved_game=saved)
                        return
                    elif action == "quit":
                        pygame.quit()
                        quit()
                    else:
                        return
                elif pause_choice == "quit":
                    pygame.quit()
                    quit()
            
            def can_place_tower(x, y):
                dx = x - CENTER[0]
                dy = y - CENTER[1]
                distance = math.hypot(dx, dy)
                inner_base = 75
                outer_base = 150
                inner = int(inner_base * SIZE_SCALE)
                # outer grows slightly with base upgrades
                outer = int(outer_base * SIZE_SCALE + (base_level - 1) * 8)
                return inner < distance < outer
            
            if event.type == pygame.MOUSEBUTTONDOWN and not paused:
                x, y = pygame.mouse.get_pos()


                # Pause button clicked -> show pause menu immediately
                if pause_button.is_clicked((x, y)):
                    pause_choice = pause_menu(money, killcount, difficulty_level, base_level, int(elapsed_time_ms//1000))
                    if pause_choice == "resume":
                        pass
                    elif pause_choice == "save":
                        gs = make_game_state()
                        write_save_slot("game_save", "most_recent", gs)
                        error_message = "Game Saved!"
                        error_timer = 120
                    elif pause_choice == "home":
                        action, saved = main_menu()
                        if action == "play":
                            main()
                            return
                        elif action == "load" and saved:
                            main(saved_game=saved)
                            return
                        elif action == "quit":
                            pygame.quit()
                            quit()
                        else:
                            return
                    elif pause_choice == "quit":
                        pygame.quit()
                        quit()
                    # consume the click
                    continue

                if button1_rect.collidepoint(x, y):
                    selected_tower_type = 1
                    upgrade_mode = False

                elif button2_rect.collidepoint(x, y):
                    selected_tower_type = 2
                    upgrade_mode = False

                elif upgrade_button_rect.collidepoint(x, y):
                    upgrade_mode = not upgrade_mode
                    selected_panel_tower = None
                
                elif speed_minus_button.collidepoint(x, y) and not upgrade_mode:
                    game_speed = max(0.5, game_speed - 0.25)
                
                elif speed_plus_button.collidepoint(x, y) and not upgrade_mode:
                    game_speed = min(4.0, game_speed + 0.25)

                elif upgrade_mode:
                    # Upgrade side-panel rect
                    panel_rect = pygame.Rect(WIDTH-220, 80, 210, HEIGHT-160)
                    # If a popup is open, handle its buttons first
                    if popup_open and popup_target is not None:
                        px_w, px_h = 520, 360
                        px_x = WIDTH//2 - px_w//2 - 100
                        px_y = HEIGHT//2 - px_h//2
                        popup_rect = pygame.Rect(px_x, px_y, px_w, px_h)
                        # popup upgrade button
                        pb_w = 100
                        pb_h = 36
                        pb_x = px_x + px_w - pb_w - 14
                        pb_y = px_y + px_h - pb_h - 14
                        popup_upgrade = pygame.Rect(pb_x, pb_y, pb_w, pb_h)
                        # If click inside popup, check buttons
                        if popup_rect.collidepoint(x, y):
                            # compute popup button rects (mirror drawing)
                            pb_h = 36
                            upgrade_rect = pygame.Rect(px_x + 12, px_y + px_h - pb_h - 14, px_w - 24, pb_h)
                            row2_y = upgrade_rect.y - pb_h - 8
                            row1_y = row2_y - pb_h - 8
                            col_w = (px_w - 36)//2
                            delete_rect = pygame.Rect(px_x + 12, row1_y, col_w, pb_h)
                            downgrade_rect = pygame.Rect(px_x + 24 + col_w, row1_y, col_w, pb_h)
                            type1_rect = pygame.Rect(px_x + 12, row2_y, col_w, pb_h)
                            type2_rect = pygame.Rect(px_x + 24 + col_w, row2_y, col_w, pb_h)
                            # Delete
                            if delete_rect.collidepoint(x, y):
                                if popup_target[0] == "base":
                                    push_error("Cannot delete base!", 60)
                                else:
                                    tidx = popup_target[1]
                                    if isinstance(tidx, int) and 0 <= tidx < len(towers):
                                        tower = towers.pop(tidx)
                                        refund = getattr(tower, 'cost', TOWER_COST) // 2
                                        money += refund
                                        push_error(f"Tower #{tidx+1} deleted. Refunded ${refund}.", 90)
                                        selected_panel_tower = None
                                popup_open = False
                                popup_target = None
                                continue
                            # Downgrade
                            if downgrade_rect.collidepoint(x, y):
                                if popup_target[0] == "base":
                                    push_error("Cannot downgrade base!", 60)
                                else:
                                    tidx = popup_target[1]
                                    if isinstance(tidx, int) and 0 <= tidx < len(towers):
                                        tower = towers[tidx]
                                        if tower.level > 1:
                                            refund = ((tower.level - 1) * 75) // 2
                                            target_level = tower.level - 1
                                            base_stats = tower.TOWER_TYPES.get(tower.tower_type, None)
                                            if base_stats:
                                                tower.damage = base_stats.get('damage', tower.damage)
                                                tower.range = base_stats.get('range', tower.range)
                                                tower.base_cooldown = base_stats.get('cooldown', tower.base_cooldown)
                                                tower.cost = base_stats.get('cost', tower.cost)
                                                tower.penetration = base_stats.get('penetration', tower.penetration)
                                                tower.level = 1
                                                for _ in range(max(0, target_level-1)):
                                                    tower.upgrade()
                                            else:
                                                tower.level = max(1, tower.level - 1)
                                            money += refund
                                            push_error(f"Downgraded Tower #{tidx+1}. Refunded ${refund}.", 90)
                                        else:
                                            push_error("Tower is at minimum level!", 60)
                                popup_open = False
                                popup_target = None
                                continue
                            # Type change
                            if type1_rect.collidepoint(x, y) or type2_rect.collidepoint(x, y):
                                if popup_target[0] == "base":
                                    push_error("Cannot change base type!", 60)
                                else:
                                    tidx = popup_target[1]
                                    if isinstance(tidx, int) and 0 <= tidx < len(towers):
                                        tower = towers[tidx]
                                        if type1_rect.collidepoint(x, y):
                                            tower.tower_type = 1
                                        else:
                                            tower.tower_type = 2
                                        if tower.level <= len(TOWER_IMAGES):
                                            tower.image = TOWER_IMAGES[tower.level - 1]
                                        push_error(f"Tower type set to {tower.tower_type}", 60)
                                popup_open = False
                                popup_target = None
                                continue
                            # Upgrade action
                            if upgrade_rect.collidepoint(x, y):
                                if popup_target[0] == "base":
                                    base_upgrade_cost = base_level * 100
                                    if money >= base_upgrade_cost and base_level < 6:
                                        money -= base_upgrade_cost
                                        base_level += 1
                                        BASE_DAMAGE = int(BASE_DAMAGE * 1.5)
                                        BASE_FIRE_RATE = max(10, int(BASE_FIRE_RATE * 0.8))
                                        base_range += 50
                                        push_error(f"Base upgraded to level {base_level}!", 60)
                                    elif base_level >= 6:
                                        push_error("Base is at maximum level!", 60)
                                    else:
                                        push_error(f"Need ${base_upgrade_cost} to upgrade base!", 60)
                                else:
                                    tidx = popup_target[1]
                                    if isinstance(tidx, int) and 0 <= tidx < len(towers):
                                        tower = towers[tidx]
                                        upgrade_cost = tower.level * 75
                                        if money >= upgrade_cost and tower.level < 3:
                                            money -= upgrade_cost
                                            tower.upgrade()
                                            if tower.level <= len(TOWER_IMAGES):
                                                tower.image = TOWER_IMAGES[tower.level - 1]
                                            push_error(f"Tower upgraded to level {tower.level}!", 60)
                                        elif tower.level >= 3:
                                            push_error("Tower is at maximum level!", 60)
                                        else:
                                            push_error(f"Need ${upgrade_cost} to upgrade tower!", 60)
                                popup_open = False
                                popup_target = None
                                continue
                            # clicked inside popup but not on known buttons
                            pass
                        else:
                            # clicked outside popup -> close it
                            popup_open = False
                            popup_target = None
                        continue
                    # If clicked inside the panel, handle selection or actions
                    if panel_rect.collidepoint(x, y):
                        # base header button area: open base popup
                        base_button_rect = pygame.Rect(panel_rect.x + panel_rect.width - 70, panel_rect.y + 8, 58, 22)
                        if base_button_rect.collidepoint(x, y):
                            popup_open = True
                            popup_target = ("base", None)
                            continue
                        # compute dynamic entry height so panel can fit many towers
                        entries_count = len(towers)
                        action_space = 200
                        panel_y_local = panel_rect.y + 36
                        available_h = max(0, panel_rect.height - 36 - action_space)
                        panel_entry_h_local = max(28, available_h // max(1, max(1, entries_count)))
                        # Precompute action button rects and prioritize them so buttons remain clickable even when many entries are present
                        btn_x = panel_rect.x + 15
                        btn_w = panel_rect.width - 30
                        delete_btn = pygame.Rect(btn_x, panel_rect.y + panel_rect.height - 180, btn_w, 44)
                        downgrade_btn = pygame.Rect(btn_x, panel_rect.y + panel_rect.height - 130, btn_w, 44)
                        upgrade_btn = pygame.Rect(btn_x, panel_rect.y + panel_rect.height - 80, btn_w, 44)
                        type1_btn = pygame.Rect(btn_x, panel_rect.y + panel_rect.height - 40, (btn_w-8)//2, 34)
                        type2_btn = pygame.Rect(btn_x + (btn_w+8)//2, panel_rect.y + panel_rect.height - 40, (btn_w-8)//2, 34)
                        # If a selected entry exists and the click hits one of the action buttons, handle it immediately (only towers)
                        if isinstance(selected_panel_tower, int) and (delete_btn.collidepoint(x, y) or downgrade_btn.collidepoint(x, y) or upgrade_btn.collidepoint(x, y) or type1_btn.collidepoint(x, y) or type2_btn.collidepoint(x, y)):
                            # Delete
                            if delete_btn.collidepoint(x, y):
                                if isinstance(selected_panel_tower, int) and 0 <= selected_panel_tower < len(towers):
                                    tower = towers.pop(selected_panel_tower)
                                    refund = getattr(tower, 'cost', TOWER_COST) // 2
                                    money += refund
                                    push_error(f"Tower #{selected_panel_tower+1} deleted. Refunded ${refund}.", 90)
                                    selected_panel_tower = None
                                else:
                                    push_error("Cannot delete base!", 60)
                                continue
                            # Downgrade
                            if downgrade_btn.collidepoint(x, y):
                                if isinstance(selected_panel_tower, int) and 0 <= selected_panel_tower < len(towers):
                                    tower = towers[selected_panel_tower]
                                    if tower.level > 1:
                                        refund = ((tower.level - 1) * 75) // 2
                                        target_level = tower.level - 1
                                        base_stats = tower.TOWER_TYPES.get(tower.tower_type, None)
                                        if base_stats:
                                            tower.damage = base_stats.get('damage', tower.damage)
                                            tower.range = base_stats.get('range', tower.range)
                                            tower.base_cooldown = base_stats.get('cooldown', tower.base_cooldown)
                                            tower.cost = base_stats.get('cost', tower.cost)
                                            tower.penetration = base_stats.get('penetration', tower.penetration)
                                            tower.level = 1
                                            for _ in range(max(0, target_level-1)):
                                                tower.upgrade()
                                        else:
                                            tower.level = max(1, tower.level - 1)
                                        money += refund
                                        push_error(f"Downgraded Tower #{selected_panel_tower+1}. Refunded ${refund}.", 90)
                                    else:
                                        push_error("Tower is at minimum level!", 60)
                                else:
                                    push_error("Cannot downgrade base!", 60)
                                continue
                            # Upgrade (from action buttons)
                            if upgrade_btn.collidepoint(x, y):
                                # Only towers can be upgraded from the panel actions; base upgrades happen via popup
                                if isinstance(selected_panel_tower, int) and 0 <= selected_panel_tower < len(towers):
                                    tower = towers[selected_panel_tower]
                                    upgrade_cost = tower.level * 75
                                    if money >= upgrade_cost and tower.level < 3:
                                        money -= upgrade_cost
                                        tower.upgrade()
                                        if tower.level <= len(TOWER_IMAGES):
                                            tower.image = TOWER_IMAGES[tower.level - 1]
                                        push_error(f"Tower upgraded to level {tower.level}!", 60)
                                    elif tower.level >= 3:
                                        push_error("Tower is at maximum level!", 60)
                                    else:
                                        push_error(f"Need ${upgrade_cost} to upgrade tower!", 60)
                                else:
                                    push_error("No tower selected to upgrade from panel.", 60)
                                continue
                            # Type change
                            if type1_btn.collidepoint(x, y) or type2_btn.collidepoint(x, y):
                                # Only towers can have their type changed from the panel
                                if isinstance(selected_panel_tower, int) and 0 <= selected_panel_tower < len(towers):
                                    tower = towers[selected_panel_tower]
                                    if type1_btn.collidepoint(x, y):
                                        tower.tower_type = 1
                                    else:
                                        tower.tower_type = 2
                                    if tower.level <= len(TOWER_IMAGES):
                                        tower.image = TOWER_IMAGES[tower.level - 1]
                                        push_error(f"Tower type set to {tower.tower_type}", 60)
                                continue
                        # compute which entry was clicked using variable heights (towers only)
                        rel_y = y - panel_y_local
                        entries = [("tower", t) for t in towers]
                        raw_heights = []
                        for kind, t in entries:
                            lvl = getattr(t, "level", 1)
                            raw_heights.append(44 + (lvl - 1) * 22)
                        total_raw = sum(raw_heights) if raw_heights else 1
                        scale = min(1.0, available_h / total_raw) if total_raw > 0 else 1.0
                        entry_heights = [max(28, int(h * scale)) for h in raw_heights]
                        cum = 0
                        idx = None
                        for i, h in enumerate(entry_heights):
                            if rel_y >= cum and rel_y < cum + h:
                                idx = i
                                break
                            cum += h
                        if idx is None:
                            idx = -1
                        # If clicking within a tower entry, handle sprite upgrade or open popup
                        if 0 <= idx < len(towers):
                            # compute top position using cumulative heights
                            entry_top = panel_y_local + sum(entry_heights[:idx])
                            h = entry_heights[idx]
                            img_size = max(20, min(40, h - 12))
                            sprite_rect = pygame.Rect(panel_rect.x + 6, entry_top + 5, img_size, img_size)
                            # sprite click => immediate upgrade
                            if sprite_rect.collidepoint(x, y):
                                t_idx = idx
                                tower = towers[t_idx]
                                upgrade_cost = tower.level * 75
                                if money >= upgrade_cost and tower.level < 3:
                                    money -= upgrade_cost
                                    tower.upgrade()
                                    if tower.level <= len(TOWER_IMAGES):
                                        tower.image = TOWER_IMAGES[tower.level - 1]
                                    error_message = f"Tower upgraded to level {tower.level}!"
                                    error_timer = 60
                                elif tower.level >= 3:
                                    error_message = "Tower is at maximum level!"
                                    error_timer = 60
                                else:
                                    error_message = f"Need ${upgrade_cost} to upgrade tower!"
                                    error_timer = 60
                                selected_panel_tower = t_idx
                                continue
                            # otherwise, open detailed popup for this tower
                            selected_panel_tower = idx
                            popup_open = True
                            popup_target = ("tower", selected_panel_tower)
                            continue
                        # Panel does not handle upgrade actions; all actions live in the popup. Consume the click.
                        continue
                    # If click was not in panel, fall back to map-based upgrade (legacy behavior)
                    # Handle upgrades in upgrade mode (map click)
                    base_distance = math.hypot(x - CENTER[0], y - CENTER[1])
                    if base_distance <= BASE_RADIUS:
                        base_upgrade_cost = base_level * 100  # Increasing cost per level
                        if money >= base_upgrade_cost and base_level < 6:
                            money -= base_upgrade_cost
                            base_level += 1
                            # Upgrade base stats
                            BASE_DAMAGE = int(BASE_DAMAGE * 1.5)
                            BASE_FIRE_RATE = max(10, int(BASE_FIRE_RATE * 0.8))
                            base_range += 50
                            error_message = f"Base upgraded to level {base_level}!"
                            error_timer = 60
                        elif base_level >= 6:
                            error_message = "Base is at maximum level!"
                            error_timer = 60
                        else:
                            error_message = f"Need ${base_upgrade_cost} to upgrade base!"
                            error_timer = 60
                    else:
                        for tower in towers:
                            tower_distance = math.hypot(x - tower.x, y - tower.y)
                            if tower_distance <= max(8, int(40 * SIZE_SCALE)):  # Click radius for towers scaled
                                upgrade_cost = tower.level * 75  # Increasing cost per level
                                if money >= upgrade_cost and tower.level < 3:
                                    money -= upgrade_cost
                                    tower.upgrade()
                                    # Update tower image based on new level
                                    if tower.level <= len(TOWER_IMAGES):
                                        tower.image = TOWER_IMAGES[tower.level - 1]
                                    error_message = f"Tower upgraded to level {tower.level}!"
                                    error_timer = 60
                                elif tower.level >= 3:
                                    error_message = "Tower is at maximum level!"
                                    error_timer = 60
                                else:
                                    error_message = f"Need ${upgrade_cost} to upgrade tower!"
                                    error_timer = 60
                                break

                elif can_place_tower(x, y) and not upgrade_mode:
                    if len(towers) >= current_max_towers:
                        current_max_towers = MAX_TOWERS + (base_level - 1) * 2
                        error_message = f"Tower limit reached ({current_max_towers})"
                        error_timer = 90
                    else:
                        temp_tower = Tower(x, y, CENTER, tower_type=selected_tower_type, image=TOWER_IMAGES[0] if TOWER_IMAGES else None, bullet_image=FIREBALL_IMAGE)

                        if money >= temp_tower.cost:
                            towers.append(temp_tower)
                            money -= temp_tower.cost
                            error_message = f"Tower placed!"
                            error_timer = 60
                        else:
                            error_message = "Not Enough Money!"
                            error_timer = 60

        # Ensure selected panel entry is visible after processing input (so user doesn't have to scroll to reach action buttons)
        if upgrade_mode and selected_panel_tower != selected_panel_prev:
            try:
                panel_rect_tmp = pygame.Rect(WIDTH-220, 80, 210, HEIGHT-160)
                entries_count_tmp = 1 + len(towers)
                action_space_tmp = 200
                available_h_tmp = max(0, panel_rect_tmp.height - 36 - action_space_tmp)
                ENTRY_PREFERRED_H_tmp = 56
                if entries_count_tmp * ENTRY_PREFERRED_H_tmp <= available_h_tmp:
                    panel_entry_h_tmp = max(28, available_h_tmp // max(1, entries_count_tmp))
                else:
                    panel_entry_h_tmp = ENTRY_PREFERRED_H_tmp
                max_scroll_tmp = max(0, entries_count_tmp * panel_entry_h_tmp - available_h_tmp)
                if isinstance(selected_panel_tower, int):
                    entry_idx_tmp = 1 + selected_panel_tower
                else:
                    entry_idx_tmp = None
                if entry_idx_tmp is not None:
                    top_tmp = entry_idx_tmp * panel_entry_h_tmp
                    panel_scroll_target = max(0, min(max_scroll_tmp, int(top_tmp - (available_h_tmp - panel_entry_h_tmp)//2)))
            except Exception:
                pass
            selected_panel_prev = selected_panel_tower

        # --- GAME LOGIC (only if not paused) ---
        if not paused and not upgrade_mode:
            # Spawn enemies
            # Difficulty scales with kills and elapsed time (slower growth: kills per 15 and every 60s)
            difficulty_level = killcount // 15 + int(elapsed_time_ms // 60000)
            if difficulty_level > prev_difficulty:
                error_message = f"Difficulty increased to {difficulty_level}!"
                error_timer = 180
                prev_difficulty = difficulty_level
            multiplier = 1 + (difficulty_level * 0.05)
            spawn_interval = max(90 - difficulty_level * 5, 10)

            if not upgrade_mode:
                spawn_timer += 1
                if spawn_timer > spawn_interval:
                    enemy_type = choose_enemy_type(difficulty_level)
                    enemies.append(
                        Enemy(WIDTH, HEIGHT, CENTER, [enemy_type], multiplier, multiplier)
                    )
                    spawn_timer = 0
                
                # BASE SHOOTING
                if base_cooldown > 0:
                    base_cooldown -= 1
                else:
                    closest_enemy = None
                    closest_distance = float("inf")

                    for enemy in enemies:
                        distance = math.hypot(enemy.x - CENTER[0], enemy.y - CENTER[1])
                        if distance < closest_distance and distance <= base_range:
                            closest_distance = distance
                            closest_enemy = enemy

                    if closest_enemy:
                        eye_base_offset = int(21 * SIZE_SCALE) + (base_level - 1) * 8
                        spawn_y = CENTER[1] - eye_base_offset
                        bullets.append(
                            Bullet(
                                CENTER[0],
                                spawn_y,
                                closest_enemy,
                                BASE_DAMAGE,
                                BASEFIREBALL_IMAGE
                            )
                        )
                        base_cooldown = BASE_FIRE_RATE
                
                # Update enemies
                for enemy in enemies[:]:
                    enemy.move()
                    enemy.animate()
                    if enemy.reached_base(BASE_RADIUS):
                        # damage per enemy type (percent points)
                        DAMAGE_BY_NAME = {"Knight": 7, "Mage": 4, "Hobbit": 2}
                        damage = DAMAGE_BY_NAME.get(getattr(enemy, 'name', None), 1)
                        base_health -= damage
                        enemies.remove(enemy)
                    elif enemy.health <= 0:
                        enemies.remove(enemy)
                        killcount += 1
                        money += enemy.reward
                
                # Towers
                for tower in towers:
                    tower.shoot(enemies, bullets)

                # Bullets
                for bullet in bullets[:]:
                    if bullet.move():
                        bullets.remove(bullet)

        # --- DRAWING SECTION ---
        # Draw decorative circles and base defense zones
        # Draw placement rings (scaled) - inner and outer radii grow with base upgrades
        inner_base = 75
        outer_base = 150
        inner_radius = int(inner_base * SIZE_SCALE)
        outer_radius = int(outer_base * SIZE_SCALE + (base_level - 1) * 8)
        pygame.draw.circle(WIN, (180, 180, 180), CENTER, outer_radius, 2)
        pygame.draw.circle(WIN, (180, 180, 180), CENTER, inner_radius, 2)

        # Draw Base
        current_base_image = BASE_IMAGES[min(base_level - 1, len(BASE_IMAGES) - 1)]
        base_rect = current_base_image.get_rect(center=(CENTER[0], CENTER[1] - int(40 * SIZE_SCALE)))
        WIN.blit(current_base_image, base_rect)

        # Draw Enemies
        for enemy in enemies:
            enemy.draw(WIN)

        # Draw Towers
        for idx, tower in enumerate(towers):
            tower.draw(WIN)

        # Draw compact markers when in upgrade mode. Cluster close markers to declutter center
        if upgrade_mode:
            cluster_size = max(24, int(40 * SIZE_SCALE))
            clusters = {}
            for idx, tower in enumerate(towers):
                cell = (int(tower.x // cluster_size), int(tower.y // cluster_size))
                clusters.setdefault(cell, []).append((idx, tower))

            for cell, items in clusters.items():
                if len(items) == 1:
                    idx, tower = items[0]
                    try:
                        level_surf = SMALL_BUTTON_FONT.render(f"Lv.{tower.level}", True, BLACK)
                        idx_surf = SMALL_BUTTON_FONT.render(f"#{idx+1}", True, BLACK)
                        lx = int(tower.x - level_surf.get_width() // 2)
                        ly = int(tower.y - 48 * SIZE_SCALE)
                        WIN.blit(level_surf, (lx, ly))
                        WIN.blit(idx_surf, (lx + level_surf.get_width() + 6, ly))
                    except Exception:
                        pass
                else:
                    # aggregated marker for multiple towers
                    avg_x = sum(t.x for _, t in items) / len(items)
                    avg_y = sum(t.y for _, t in items) / len(items)
                    count = len(items)
                    try:
                        agg_surf = SMALL_BUTTON_FONT.render(f"+{count}", True, (40,40,40))
                        WIN.blit(agg_surf, (int(avg_x - agg_surf.get_width() // 2), int(avg_y - 40 * SIZE_SCALE)))
                    except Exception:
                        pass

        # Draw Bullets
        for bullet in bullets:
            bullet.draw(WIN)
        
        # Draw forest decorations on top so trees appear in foreground
        draw_forest_decorations(WIN)
        
        # --- UI DISPLAY ---
        # Corner data display with translucent background for readability
        stat_texts = [
            STAT_FONT.render(f"Money: ${money}", True, WHITE),
            STAT_FONT.render(f"Health: {base_health}%", True, WHITE),
            STAT_FONT.render(f"Kills: {killcount}", True, WHITE),
            STAT_FONT.render(f"Difficulty: {difficulty_level}", True, WHITE),
            STAT_FONT.render(f"Base Level: {base_level}", True, WHITE),
        ]
        padding = 8
        text_spacing = 6
        max_w = max(s.get_width() for s in stat_texts)
        total_h = sum(s.get_height() for s in stat_texts) + text_spacing * (len(stat_texts)-1)
        bg_rect = pygame.Rect(6, 6, max_w + padding*2, total_h + padding*2)
        # translucent background
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((20, 20, 20, 180))
        WIN.blit(bg_surf, (bg_rect.x, bg_rect.y))
        # draw texts
        ty = bg_rect.y + padding
        for s in stat_texts:
            WIN.blit(s, (bg_rect.x + padding, ty))
            ty += s.get_height() + text_spacing

        # Game Timer (mm:ss)
        elapsed_seconds = int(elapsed_time_ms // 1000)
        mins = elapsed_seconds // 60
        secs = elapsed_seconds % 60
        timer_text = STAT_FONT.render(f"Time: {mins:02d}:{secs:02d}", True, BLACK)
        WIN.blit(timer_text, (10, 160))
        
        # Draw Speed Control (hidden while upgrade panel is open)
        if not upgrade_mode:
            # semi-transparent speed minus
            s_minus = pygame.Surface((speed_minus_button.width, speed_minus_button.height), pygame.SRCALPHA)
            s_minus.fill((100, 100, 100, 160))
            WIN.blit(s_minus, (speed_minus_button.x, speed_minus_button.y))
            pygame.draw.rect(WIN, (150, 150, 150), speed_minus_button, 2)
            minus_text = FONT.render("-", True, WHITE)
            WIN.blit(minus_text, (speed_minus_button.x + 15, speed_minus_button.y + 5))
            # semi-transparent speed plus
            s_plus = pygame.Surface((speed_plus_button.width, speed_plus_button.height), pygame.SRCALPHA)
            s_plus.fill((100, 100, 100, 160))
            WIN.blit(s_plus, (speed_plus_button.x, speed_plus_button.y))
            pygame.draw.rect(WIN, (150, 150, 150), speed_plus_button, 2)
            plus_text = FONT.render("+", True, WHITE)
            WIN.blit(plus_text, (speed_plus_button.x + 12, speed_plus_button.y + 6))

            speed_display = FONT.render(f"Speed: {game_speed:.2f}x", True, BLACK)
            WIN.blit(speed_display, (WIDTH - 200, 55))

        # Draw on-screen pause button
        try:
            pause_button.draw(WIN)
        except Exception:
            pass
        
        # Draw Tower Selection Buttons
        button1_color = BLUE if selected_tower_type == 1 else (100, 100, 100)
        button2_color = (150, 50, 200) if selected_tower_type == 2 else (100, 100, 100)
        upgrade_button_color = (255, 200, 0) if upgrade_mode else (100, 100, 100)
        
        # semi-transparent tower selection buttons
        s_b1 = pygame.Surface((button1_rect.width, button1_rect.height), pygame.SRCALPHA)
        s_b1.fill((*button1_color, 160))
        WIN.blit(s_b1, (button1_rect.x, button1_rect.y))
        s_b2 = pygame.Surface((button2_rect.width, button2_rect.height), pygame.SRCALPHA)
        s_b2.fill((*button2_color, 160))
        WIN.blit(s_b2, (button2_rect.x, button2_rect.y))
        s_up = pygame.Surface((upgrade_button_rect.width, upgrade_button_rect.height), pygame.SRCALPHA)
        s_up.fill((*upgrade_button_color, 160))
        WIN.blit(s_up, (upgrade_button_rect.x, upgrade_button_rect.y))

        # Button borders
        pygame.draw.rect(WIN, WHITE, button1_rect, 2)
        pygame.draw.rect(WIN, WHITE, button2_rect, 2)
        pygame.draw.rect(WIN, WHITE, upgrade_button_rect, 2)

        text1 = SMALL_BUTTON_FONT.render("Tower 1", True, WHITE)
        text2 = SMALL_BUTTON_FONT.render("Tower 2", True, WHITE)
        upgrade_text = SMALL_BUTTON_FONT.render("Upgrade", True, BLACK)

        # center text inside buttons for better readability
        WIN.blit(text1, (button1_rect.x + button1_rect.width//2 - text1.get_width()//2, button1_rect.y + button1_rect.height//2 - text1.get_height()//2))
        WIN.blit(text2, (button2_rect.x + button2_rect.width//2 - text2.get_width()//2, button2_rect.y + button2_rect.height//2 - text2.get_height()//2))
        WIN.blit(upgrade_text, (upgrade_button_rect.x + upgrade_button_rect.width//2 - upgrade_text.get_width()//2, upgrade_button_rect.y + upgrade_button_rect.height//2 - upgrade_text.get_height()//2))

        # Transfer any legacy single-slot error into the queue and clear it
        if error_message and error_timer > 0:
            push_error(error_message, error_timer)
            error_message = ""
            error_timer = 0

        # Draw queued error/status messages stacked so they don't overlap
        if error_queue:
            start_y = 90 + (20 if upgrade_mode else 0)
            for i, e in enumerate(list(error_queue)):
                try:
                    error_surf = FONT.render(e["msg"], True, (100, 100, 255))
                    WIN.blit(error_surf, (WIDTH // 2 - error_surf.get_width() // 2 + 15, start_y + i * (error_surf.get_height() + 6)))
                except Exception:
                    pass
                e["timer"] -= 1
            # remove expired messages (in-place)
            error_queue[:] = [x for x in error_queue if x["timer"] > 0]

        if upgrade_mode:
            upgrade_instructions = UPGRADE_FONT.render("UPGRADE MODE: Use panel to the right or click map", True, (255, 100, 100))
            WIN.blit(upgrade_instructions, (WIDTH // 2 - upgrade_instructions.get_width() // 2 - 10, 50))
            
            if base_level < 6:
                base_upgrade_cost = base_level * 100
                base_cost_text = UPGRADE_FONT.render(f"Base Upgrade: ${base_upgrade_cost}", True, (100, 100, 255))
                WIN.blit(base_cost_text, (WIDTH // 2 - base_cost_text.get_width() // 2 - 10, 70))
            else:
                base_max_text = UPGRADE_FONT.render("Base at MAX LEVEL", True, (100, 100, 255))
                WIN.blit(base_max_text, (WIDTH // 2 - base_max_text.get_width() // 2 - 10, 70))
            # Show current max towers allowance
            try:
                max_towers_text = UPGRADE_FONT.render(f"Max Towers: {current_max_towers}", True, (200, 200, 120))
                WIN.blit(max_towers_text, (WIDTH // 2 - max_towers_text.get_width() // 2 - 10, 90))
            except Exception:
                pass
            
            # Show base level in upgrade mode
            base_level_upgrade_display = UPGRADE_FONT.render(f"Base Lv.{base_level}", True, (0, 0, 0))
            WIN.blit(base_level_upgrade_display, (CENTER[0] - int(40 * SIZE_SCALE), CENTER[1] - int(80 * SIZE_SCALE)))

            # Draw right-side upgrade panel
            panel_rect = pygame.Rect(WIDTH-220, 80, 210, HEIGHT-160)
            pygame.draw.rect(WIN, (40,40,40), panel_rect)
            pygame.draw.rect(WIN, (200,180,100), panel_rect, 2)
            title = UPGRADE_FONT.render("Upgrade Menu", True, (220,180,100))
            WIN.blit(title, (panel_rect.x + 10, panel_rect.y + 6))
            # draw a compact base button (no info displayed in panel)
            base_button_rect = pygame.Rect(panel_rect.x + panel_rect.width - 70, panel_rect.y + 8, 58, 22)
            pygame.draw.rect(WIN, (90,90,120), base_button_rect)
            pygame.draw.rect(WIN, (200,180,100), base_button_rect, 2)
            base_btn_txt = UPGRADE_FONT.render("Base", True, WHITE)
            WIN.blit(base_btn_txt, (base_button_rect.x + base_button_rect.width//2 - base_btn_txt.get_width()//2, base_button_rect.y + 3))

            panel_y = panel_rect.y + 36
            # compute per-entry raw heights (variable button sizes based on level), no scrolling
            entries = [("tower", t) for t in towers]
            raw_heights = []
            for kind, t in entries:
                lvl = getattr(t, "level", 1)
                raw_heights.append(44 + (lvl - 1) * 22)
            action_space = 200
            available_h = max(0, panel_rect.height - 36 - action_space)
            total_raw = sum(raw_heights) if raw_heights else 1
            scale = min(1.0, available_h / total_raw) if total_raw > 0 else 1.0
            entry_heights = [max(28, int(h * scale)) for h in raw_heights]
            # draw entries sequentially top-down (no scroll)
            y_cursor = panel_rect.y + 36
            for idx, ((kind, t), h) in enumerate(zip(entries, entry_heights)):
                entry_rect = pygame.Rect(panel_rect.x + 10, y_cursor, panel_rect.width - 20, max(28, h - 6))
                tower = t
                tower_selected = (isinstance(selected_panel_tower, int) and selected_panel_tower == idx)
                color = (100,120,160) if tower_selected else (70,70,70)
                pygame.draw.rect(WIN, color, entry_rect)
                pygame.draw.rect(WIN, (200,180,100), entry_rect, 2)
                try:
                    img_size = max(12, min(36, h - 12))
                    mini = pygame.transform.scale(tower.image, (img_size, img_size))
                    WIN.blit(mini, (entry_rect.x + 6, entry_rect.y + 5))
                except Exception:
                    pass
                txt = UPGRADE_FONT.render(f"Tower #{idx+1}  Lv.{tower.level}", True, WHITE)
                WIN.blit(txt, (entry_rect.x + 12 + img_size, entry_rect.y + max(4, (entry_rect.height - txt.get_height())//2)))
                y_cursor += h



            # Popup detail window when an entry was clicked
            if popup_open and popup_target is not None:
                px_w, px_h = 520, 360
                px_x = WIDTH//2 - px_w//2 - 100
                px_y = HEIGHT//2 - px_h//2
                popup_rect = pygame.Rect(px_x, px_y, px_w, px_h)
                pygame.draw.rect(WIN, (30,30,30), popup_rect)
                pygame.draw.rect(WIN, (200,180,100), popup_rect, 2)
                # prepare button geometry first so info area can avoid overlap
                pb_h = 36
                upgrade_rect = pygame.Rect(px_x + 12, px_y + px_h - pb_h - 14, px_w - 24, pb_h)
                row2_y = upgrade_rect.y - pb_h - 8
                row1_y = row2_y - pb_h - 8
                col_w = (px_w - 36)//2
                delete_rect = pygame.Rect(px_x + 12, row1_y, col_w, pb_h)
                downgrade_rect = pygame.Rect(px_x + 24 + col_w, row1_y, col_w, pb_h)
                type1_rect = pygame.Rect(px_x + 12, row2_y, col_w, pb_h)
                type2_rect = pygame.Rect(px_x + 24 + col_w, row2_y, col_w, pb_h)
                # title and info (render info into a reserved area above buttons so it never overlaps)
                title_surf = None
                if popup_target[0] == "base":
                    title_surf = UPGRADE_FONT.render("Base Details", True, WHITE)
                    lines = [f"Base Level: {base_level}", f"Next Upgrade Cost: ${base_level*100 if base_level<6 else 0}"]
                else:
                    tidx = popup_target[1]
                    tower = towers[tidx] if 0 <= tidx < len(towers) else None
                    title_surf = UPGRADE_FONT.render(f"Tower #{tidx+1} Details", True, WHITE)
                    if tower:
                        # build detailed info lines
                        lines = [f"Level: {tower.level}", f"Damage: {getattr(tower,'damage','?')}", f"Range: {getattr(tower,'range','?')}", f"Cooldown: {getattr(tower,'base_cooldown','?')}", f"Type: {getattr(tower,'tower_type','?')}", f"Cost: ${getattr(tower,'cost','?')}"]
                    else:
                        lines = ["(No tower)"]
                # draw title
                if title_surf is not None:
                    WIN.blit(title_surf, (px_x + 12, px_y + 8))
                # compute available space for info (above first row of buttons) and clamp lines
                info_start_y = px_y + 40
                info_end_y = row1_y - 8
                info_h = max(0, info_end_y - info_start_y)
                line_h = UPGRADE_FONT.get_height() + 4
                max_lines = max(0, info_h // line_h)
                draw_lines = lines[:max_lines]
                if len(lines) > max_lines and max_lines > 0:
                    if max_lines >= 1:
                        draw_lines = lines[:max_lines-1] + ["..."]
                    else:
                        draw_lines = ["..."]
                for i,ln in enumerate(draw_lines):
                    surf = UPGRADE_FONT.render(ln, True, WHITE)
                    WIN.blit(surf, (px_x + 12, info_start_y + i * (surf.get_height() + 4)))
                # draw row buttons
                pygame.draw.rect(WIN, (180,60,60), delete_rect, border_radius=6)
                pygame.draw.rect(WIN, (200,180,100), delete_rect, 2, border_radius=6)
                pygame.draw.rect(WIN, (200,150,50), downgrade_rect, border_radius=6)
                pygame.draw.rect(WIN, (200,180,100), downgrade_rect, 2, border_radius=6)
                if popup_target[0] == "base":
                    pygame.draw.rect(WIN, (90,90,90), type1_rect, border_radius=6)
                    pygame.draw.rect(WIN, (90,90,90), type2_rect, border_radius=6)
                else:
                    pygame.draw.rect(WIN, (150,150,150), type1_rect, border_radius=6)
                    pygame.draw.rect(WIN, (150,150,150), type2_rect, border_radius=6)
                pygame.draw.rect(WIN, (200,180,100), type1_rect, 2, border_radius=6)
                pygame.draw.rect(WIN, (200,180,100), type2_rect, 2, border_radius=6)
                d_txt = UPGRADE_FONT.render("Delete", True, WHITE)
                dn_txt = UPGRADE_FONT.render("Downgrade", True, WHITE)
                t1_txt = UPGRADE_FONT.render("Type 1", True, WHITE)
                t2_txt = UPGRADE_FONT.render("Type 2", True, WHITE)
                WIN.blit(d_txt, (delete_rect.x + delete_rect.width//2 - d_txt.get_width()//2, delete_rect.y + 6))
                WIN.blit(dn_txt, (downgrade_rect.x + downgrade_rect.width//2 - dn_txt.get_width()//2, downgrade_rect.y + 6))
                WIN.blit(t1_txt, (type1_rect.x + type1_rect.width//2 - t1_txt.get_width()//2, type1_rect.y + 6))
                WIN.blit(t2_txt, (type2_rect.x + type2_rect.width//2 - t2_txt.get_width()//2, type2_rect.y + 6))
                # draw upgrade
                pygame.draw.rect(WIN, (100,170,100), upgrade_rect, border_radius=6)
                pygame.draw.rect(WIN, (200,180,100), upgrade_rect, 2, border_radius=6)
                pu_txt = UPGRADE_FONT.render("Upgrade", True, WHITE)
                WIN.blit(pu_txt, (upgrade_rect.x + upgrade_rect.width//2 - pu_txt.get_width()//2, upgrade_rect.y + 6))
        
        # Check for Game Over
        if base_health <= 0:
            # On death: attempt to restore/save the snapshot from 4 seconds before death
            death_time = pygame.time.get_ticks()
            target_time = death_time - 4000
            chosen_snapshot = None
            # iterate from newest to oldest and pick the latest snapshot <= target_time
            for ts, gs in reversed(save_history):
                if ts <= target_time:
                    chosen_snapshot = gs
                    break
            # fallback to earliest snapshot if none found
            if chosen_snapshot is None and save_history:
                chosen_snapshot = save_history[0][1]
            # write chosen snapshot to disk so the saved file reflects -4s state
            if chosen_snapshot is not None:
                try:
                    save_game("game_save", chosen_snapshot)
                except Exception:
                    pass

            result = game_over_screen(killcount, money, difficulty_level, base_level)
            if result == "play_again":
                main()  # Restart game
                return
            elif result == "home":
                # Return to main menu and handle user's menu choice
                action, saved = main_menu()
                if action == "play":
                    main()
                    return
                elif action == "load" and saved:
                    main(saved_game=saved)
                    return
                elif action == "quit":
                    pygame.quit()
                    quit()
                else:
                    return
            else:
                return
        
        # Autosave every 500 milliseconds
        current_time = pygame.time.get_ticks()
        if current_time - last_autosave >= 500:
            game_state = make_game_state()
            # add snapshot to history
            try:
                save_history.append((current_time, game_state))
                # prune old snapshots older than 10 seconds
                cutoff = current_time - 10000
                save_history[:] = [(ts,gs) for (ts,gs) in save_history if ts >= cutoff]
            except Exception:
                pass
            # best-effort save to disk
            try:
                save_game("game_save", game_state)
            except Exception as _:
                pass
            last_autosave = current_time

        pygame.display.update()

def main_menu_launcher():
    """Starts the menu and handles the button results."""
    print("[DEBUG] launching main_menu from launcher", flush=True)
    action, saved_data = main_menu()
    print(f"[DEBUG] launcher got action={action}, saved_data={saved_data}", flush=True)
    if action == "play":
        main()
    elif action == "load":
        main(saved_game=saved_data)


# entry point when run as a script
if __name__ == "__main__":
    main_menu_launcher()


        
