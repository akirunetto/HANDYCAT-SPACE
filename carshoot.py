import pygame
import random
import sys
import math

# Inisialisasi Pygame
pygame.init()

# --- KONFIGURASI LAYAR ---
WIDTH = 800
HEIGHT = 800
GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TERMINAL SHOOTER: SYSTEM ROOT")

# --- KONFIGURASI GAMEPLAY ---
BOSS_SCORE_THRESHOLD = 10000
UPGRADE_SCORE_THRESHOLD = 5000
BOMB_BOSS_DAMAGE = 1500
PLAYER_MAX_HP = 100

# --- WARNA NEON ---
BLACK = (5, 5, 10)
WHITE = (220, 220, 255)
NEON_GREEN = (50, 255, 100)
NEON_RED = (255, 50, 80)
NEON_CYAN = (0, 255, 255)
NEON_PURPLE = (200, 50, 255)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 165, 0)
DARK_SCANLINE = (0, 0, 0, 100)

# --- FONT ---
try:
    GAME_FONT = pygame.font.SysFont("consolas", 20, bold=True)
    UI_FONT = pygame.font.SysFont("consolas", 16, bold=True)
    TITLE_FONT = pygame.font.SysFont("consolas", 50, bold=True)
    MENU_FONT = pygame.font.SysFont("consolas", 30, bold=True)
    ART_FONT = pygame.font.SysFont("consolas", 14)
except:
    GAME_FONT = pygame.font.SysFont("monospace", 20, bold=True)
    UI_FONT = pygame.font.SysFont("monospace", 16, bold=True)
    TITLE_FONT = pygame.font.SysFont("monospace", 50, bold=True)
    MENU_FONT = pygame.font.SysFont("monospace", 30, bold=True)
    ART_FONT = pygame.font.SysFont("monospace", 14)

# --- ASET ASCII ---
PLAYER_ASCII = [" /^\ ", "| A |", "/_|_|_\ "]
PLAYER_SHIELD_ASCII = [" ( /^\ ) ", "(| A |)", "(/_|_|_\)"]

# MUSUH VARIAN
ENEMY_BASIC = [[" ^._.^ ", " (ooo) "]]
ENEMY_SHOOTER = [[" /o.o\ ", " [!!!] "]]
ENEMY_DASHER = [[" >^_^< ", "  / \  "]]
ENEMY_TANK = [[" [__M__] ", " (O_O_O) "]] # New Tank Enemy
ENEMY_KAMIKAZE = [[" \!/ ", " (X) "]]     # New Kamikaze Enemy

ROCKS_ASCII = [[" [###] "], [" (@@@) "], [" <%%%> "]]

# BOSS VARIAN
BOSS_1_ASCII = [
    "  /\_/\  / \  /\_/\  ",
    " ( @.@ )|===|( @.@ ) ",
    "  > ^ <  \_/  > ^ <  ",
    " /     \_____/     \ ",
    "|  [  SYSTEM_ERR ]  |",
    " \_|_|_/     \_|_|_/ "
]
BOSS_2_ASCII = [
    "   <[ WARNING ]>   ",
    "  /  _       _  \  ",
    " |  (O)     (O)  | ",
    " |   \_______/   | ",
    "  \    [FIRE]   /  ",
    "   \___________/   "
]
BOSS_3_ASCII = [
    "   .---.     .---.   ",
    "  /  X  \___/  X  \  ",
    " |      (._.)      | ",
    "  \     /   \     /  ",
    "   `---'|___|`---'   ",
    "        /   \        "
]

ITEM_BOMB = ["[ BOMB ]"]
ITEM_SHIELD = ["[SHIELD]"]
ITEM_HEALTH = ["[ +++ ]"] # New Health Item

BULLET_CHAR = "|"
ENEMY_BULLET_CHAR = "!" 

# --- CRT EFFECT ASSETS ---
SCANLINE_SURF = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 4):
    pygame.draw.line(SCANLINE_SURF, (0, 0, 0, 80), (0, y), (WIDTH, y), 1)

VIGNETTE_SURF = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(VIGNETTE_SURF, (0,0,0,50), (0,0,WIDTH,HEIGHT), 0)
pygame.draw.circle(VIGNETTE_SURF, (0,0,0,0), (WIDTH//2, HEIGHT//2), 450)

# --- HELPER FUNCTION ---
def create_ascii_surface(ascii_list, color, font=GAME_FONT):
    max_width = 0
    lines = []
    for line in ascii_list:
        rendered = font.render(line, True, color)
        lines.append(rendered)
        if rendered.get_width() > max_width:
            max_width = rendered.get_width()
    total_height = len(lines) * lines[0].get_height()
    surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
    y_offset = 0
    for line_surf in lines:
        x_offset = (max_width - line_surf.get_width()) // 2
        surface.blit(line_surf, (x_offset, y_offset))
        y_offset += line_surf.get_height()
    return surface

def draw_text_centered(surface, text, font, color, y_offset):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y_offset))
    surface.blit(render, rect)

# --- CLASSES ---
class Shockwave(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.center = center
        self.radius = 10
        self.max_radius = WIDTH
        self.speed = 40
        self.thickness = 50
        self.image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.color = NEON_CYAN
    def update(self):
        self.radius += self.speed
        self.thickness = max(1, self.thickness - 3)
        if self.radius >= self.max_radius or self.thickness <= 1:
            self.kill()
        else:
            self.image.fill((0,0,0,0)) 
            pygame.draw.circle(self.image, (*self.color, 150), self.center, int(self.radius), int(self.thickness))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(2, 8)
        self.char = random.choice([".", ",", "`", "'"])
        self.color = (random.randint(50,100), random.randint(50,100), random.randint(50,100))
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0; self.x = random.randint(0, WIDTH)
    def draw(self, surface):
        text = ART_FONT.render(self.char, True, self.color)
        surface.blit(text, (self.x, self.y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = create_ascii_surface(PLAYER_ASCII, NEON_GREEN)
        self.shield_image = create_ascii_surface(PLAYER_SHIELD_ASCII, NEON_CYAN)
        self.hurt_image = create_ascii_surface(PLAYER_ASCII, NEON_RED) # Visual saat kena damage
        self.image = self.original_image
        self.rect = self.image.get_rect(centerx=WIDTH//2, bottom=HEIGHT-50)
        self.speed = 7; self.shoot_delay = 300; self.damage = 1; self.crit_rate = 0.0
        self.last_shot = 0; self.shield_active = False; self.shield_timer = 0
        
        # Health System
        self.max_hp = PLAYER_MAX_HP
        self.current_hp = self.max_hp
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.blink_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed
        
        self.auto_shoot()
        
        # Handle Invulnerability & Shield blinking
        current_time = pygame.time.get_ticks()
        
        if self.invulnerable:
            if current_time > self.invulnerable_timer:
                self.invulnerable = False
                self.image = self.original_image
            else:
                # Blink effect
                if (current_time // 100) % 2 == 0:
                    self.image = self.hurt_image
                else:
                    self.image = self.original_image
                    
        elif self.shield_active:
            remaining = self.shield_timer - current_time
            self.image = self.original_image if remaining < 1000 and (remaining // 100) % 2 == 0 else self.shield_image
            if current_time > self.shield_timer: self.deactivate_shield()
        else:
            self.image = self.original_image

    def auto_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, self.damage, self.crit_rate)
            all_sprites.add(bullet); bullets.add(bullet)
            
    def take_damage(self, amount):
        if self.shield_active or self.invulnerable:
            return
        
        self.current_hp -= amount
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks() + 1000 # 1 detik invul
        
        # Trigger screen shake global
        global shake_timer
        shake_timer = 10
        
    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def activate_shield(self):
        self.shield_active = True; self.image = self.shield_image; self.shield_timer = pygame.time.get_ticks() + 5000
        self.rect = self.image.get_rect(center=self.rect.center)
    def deactivate_shield(self):
        self.shield_active = False; self.image = self.original_image
        self.rect = self.image.get_rect(center=self.rect.center)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, crit_rate):
        super().__init__()
        self.damage = damage; self.is_crit = random.random() < crit_rate
        color = NEON_RED if self.is_crit else WHITE
        if self.is_crit: self.damage *= 2
        self.image = GAME_FONT.render(BULLET_CHAR, True, color)
        self.rect = self.image.get_rect(centerx=x, bottom=y); self.speed = -12
    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0: self.kill()

class Item(pygame.sprite.Sprite):
    def __init__(self, type_item):
        super().__init__()
        self.type = type_item
        if self.type == 'BOMB': color = NEON_RED; art = ITEM_BOMB
        elif self.type == 'SHIELD': color = NEON_CYAN; art = ITEM_SHIELD
        else: color = NEON_GREEN; art = ITEM_HEALTH # Health type
        
        self.image = create_ascii_surface(art, color)
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-50), y=-50); self.speed_y = 3
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level, player_target=None):
        super().__init__()
        self.player_target = player_target
        roll = random.randint(1, 100)
        self.enemy_type = "BASIC"
        art = random.choice(ENEMY_BASIC)
        color = WHITE
        self.collision_damage = 10 # Damage jika nabrak player
        
        # Enemy Variety Logic
        if level >= 2 and roll > 80:
            self.enemy_type = "SHOOTER"; art = random.choice(ENEMY_SHOOTER); color = NEON_RED
            self.collision_damage = 15
        elif level >= 3 and roll > 90:
            self.enemy_type = "DASHER"; art = random.choice(ENEMY_DASHER); color = NEON_CYAN
            self.collision_damage = 20
        elif level >= 4 and roll > 92: # New: Tank
            self.enemy_type = "TANK"; art = random.choice(ENEMY_TANK); color = NEON_ORANGE
            self.collision_damage = 30
        elif level >= 5 and roll > 95: # New: Kamikaze
            self.enemy_type = "KAMIKAZE"; art = random.choice(ENEMY_KAMIKAZE); color = NEON_YELLOW
            self.collision_damage = 40
            
        self.image = create_ascii_surface(art, color)
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-50), y=random.randint(-150, -50))
        
        # Stats Scaling
        hp_scale = 1 + int(level * 0.5)
        self.hp = random.randint(1, hp_scale)
        if self.enemy_type == "DASHER": self.hp = 1 
        if self.enemy_type == "TANK": self.hp = hp_scale * 3 # Tank tebal
        
        speed_mult = 1 + (level * 0.1)
        self.speed_y = random.randint(2, 5) * speed_mult; self.speed_x = 0
        if self.enemy_type == "DASHER": self.speed_y = 7 * speed_mult; self.speed_x = random.choice([-3, 3])
        if self.enemy_type == "TANK": self.speed_y = 1.5 * speed_mult # Tank lambat
        if self.enemy_type == "KAMIKAZE": self.speed_y = 6 * speed_mult
        
        self.last_shot = pygame.time.get_ticks(); self.shoot_delay = random.randint(1500, 3000)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.kill(); return True
        return False
        
    def update(self):
        self.rect.y += self.speed_y; self.rect.x += self.speed_x
        
        if self.enemy_type == "DASHER" and (self.rect.left <= 0 or self.rect.right >= WIDTH): 
            self.speed_x *= -1
            
        # Kamikaze Tracking Logic
        if self.enemy_type == "KAMIKAZE" and self.player_target:
            if self.rect.centerx < self.player_target.rect.centerx:
                self.rect.x += 2
            elif self.rect.centerx > self.player_target.rect.centerx:
                self.rect.x -= 2

        if self.enemy_type == "SHOOTER" or self.enemy_type == "TANK":
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet_dmg = 10 if self.enemy_type == "SHOOTER" else 20
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, bullet_dmg)
                all_sprites.add(bullet); enemy_bullets.add(bullet)
                
        if self.rect.top > HEIGHT: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=10):
        super().__init__()
        self.damage = damage
        color = NEON_RED if damage <= 10 else NEON_ORANGE
        self.image = GAME_FONT.render(ENEMY_BULLET_CHAR, True, color)
        self.rect = self.image.get_rect(centerx=x, top=y); self.speed = 7
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        # Variasi Boss berdasarkan level
        self.boss_variant = (level % 3)
        if self.boss_variant == 0: self.boss_variant = 3
        
        ascii_art = BOSS_1_ASCII
        color = NEON_PURPLE
        if self.boss_variant == 2:
            ascii_art = BOSS_2_ASCII; color = NEON_ORANGE
        elif self.boss_variant == 3:
            ascii_art = BOSS_3_ASCII; color = NEON_CYAN

        self.image = create_ascii_surface(ascii_art, color, font=GAME_FONT)
        self.rect = self.image.get_rect(centerx=WIDTH//2, y=-200)
        self.target_y = 50; self.entering = True
        self.max_hp = 50 + (level * 40); self.current_hp = self.max_hp
        self.speed_x = 3 + (level * 0.3); self.direction = 1
        self.last_shot = 0; self.shoot_delay = max(400, 1500 - (level * 100))
        self.collision_damage = 50 # Sakit kalau ditabrak
        
    def take_damage(self, amount): self.current_hp -= amount
    
    def update(self):
        if self.entering:
            self.rect.y += 2
            if self.rect.y >= self.target_y: self.entering = False
            return
        self.rect.x += self.speed_x * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0: self.direction *= -1
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay: self.shoot(); self.last_shot = now
        
    def shoot(self):
        # Pola tembakan boss berbeda tiap varian
        if self.boss_variant == 1:
            b = EnemyBullet(self.rect.centerx, self.rect.bottom, 15)
            all_sprites.add(b); enemy_bullets.add(b)
            # Shotgun spread
            b_l = EnemyBullet(self.rect.left + 40, self.rect.bottom, 15); b_l.speed_x = -2
            b_r = EnemyBullet(self.rect.right - 40, self.rect.bottom, 15); b_r.speed_x = 2
            all_sprites.add(b_l, b_r); enemy_bullets.add(b_l, b_r)
            
        elif self.boss_variant == 2: # Heavy Hitter
            b1 = EnemyBullet(self.rect.left + 20, self.rect.bottom, 25)
            b2 = EnemyBullet(self.rect.right - 20, self.rect.bottom, 25)
            all_sprites.add(b1, b2); enemy_bullets.add(b1, b2)
            
        elif self.boss_variant == 3: # Bullet Hell Lite
            for i in range(-2, 3):
                b = EnemyBullet(self.rect.centerx + (i*20), self.rect.bottom, 10)
                all_sprites.add(b); enemy_bullets.add(b)

    def draw_health(self, surface):
        bar_width, bar_height = 400, 20
        fill = max(0, (self.current_hp / self.max_hp) * bar_width)
        pygame.draw.rect(surface, NEON_PURPLE, ((WIDTH//2)-(bar_width//2), 60, bar_width, bar_height), 2)
        pygame.draw.rect(surface, NEON_RED, ((WIDTH//2)-(bar_width//2), 60, fill, bar_height))
        text = UI_FONT.render(f"BOSS HP: {int(self.current_hp)}/{self.max_hp}", True, WHITE)
        surface.blit(text, (WIDTH//2 - text.get_width()//2, 85))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = create_ascii_surface(random.choice(ROCKS_ASCII), (100, 100, 100))
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-50), y=-100); self.speed_y = random.randint(2, 5)
        self.collision_damage = 5
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT: self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, is_big=False, text=None):
        super().__init__()
        if text: self.frames = [text]; self.frame_rate = 300; self.color = NEON_RED
        else:
            self.frames = ["#", "##", "###", "%", "::", " "] if not is_big else [" [#] ", "[###]", "[%%%]", "[:::]", "[...]", " "]
            self.frame_rate = 40; self.color = NEON_CYAN
        self.frame_index = 0; self.image = GAME_FONT.render(self.frames[0], True, self.color)
        self.rect = self.image.get_rect(center=center); self.last_update = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now; self.frame_index += 1
            if self.frame_index < len(self.frames): self.image = GAME_FONT.render(self.frames[self.frame_index], True, self.color); self.rect = self.image.get_rect(center=self.rect.center)
            else: self.kill()

# --- GROUP SETUP ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
items = pygame.sprite.Group()
player = None
stars = [Star() for _ in range(80)]

# --- GAME STATE VARIABLES ---
score = 0
level = 1
next_boss_score = BOSS_SCORE_THRESHOLD
next_upgrade_score = UPGRADE_SCORE_THRESHOLD
boss_active = False
current_boss = None
state = "MENU" # MENU, TUTORIAL, PLAYING, PAUSED, UPGRADE, GAMEOVER
shake_timer = 0
menu_selection = 0

# --- FUNCTIONS ---
def reset_game():
    global score, level, next_boss_score, next_upgrade_score, boss_active, current_boss, player
    score = 0; level = 1
    next_boss_score = BOSS_SCORE_THRESHOLD
    next_upgrade_score = UPGRADE_SCORE_THRESHOLD
    boss_active = False; current_boss = None
    all_sprites.empty(); enemies.empty(); obstacles.empty(); bullets.empty(); enemy_bullets.empty(); items.empty()
    player = Player(); all_sprites.add(player)

def draw_main_menu(surface):
    draw_text_centered(surface, "TERMINAL SHOOTER", TITLE_FONT, NEON_GREEN, 150)
    draw_text_centered(surface, "SYSTEM REBOOT", UI_FONT, NEON_CYAN, 200)

    options = ["INITIATE LAUNCH", "TRAINING MODULE", "TERMINATE SYSTEM"]
    for i, option in enumerate(options):
        color = NEON_RED if i == menu_selection else WHITE
        prefix = "> " if i == menu_selection else "  "
        suffix = " <" if i == menu_selection else "  "
        draw_text_centered(surface, prefix + option + suffix, MENU_FONT, color, 350 + (i * 60))
    
    draw_text_centered(surface, "[UP/DOWN] Select  [ENTER] Confirm", UI_FONT, NEON_PURPLE, HEIGHT - 100)

def draw_tutorial(surface):
    draw_text_centered(surface, "TRAINING MODULE", TITLE_FONT, NEON_CYAN, 80)
    info = [
        "CONTROLS:", "ARROWS - Move", "AUTO - Fire", "[ESC] - Pause",
        "", "ENEMIES:",
        "BASIC (White) - Weak", "SHOOTER (Red) - Fires",
        "TANK (Orange) - High HP/Dmg", "KAMIKAZE (Yellow) - Explodes",
        "", "ITEMS:",
        "[BOMB] - Clear Screen", "[SHIELD] - Invincible", "[+] - Heal HP",
        "", "UPGRADE EVERY 5000 POINTS"
    ]
    for i, line in enumerate(info):
        color = NEON_GREEN if "CONTROLS" in line or "ENEMIES" in line or "ITEMS" in line else WHITE
        draw_text_centered(surface, line, UI_FONT, color, 150 + (i * 25))
    draw_text_centered(surface, "PRESS [SPACE] TO RETURN", MENU_FONT, NEON_RED, HEIGHT - 80)

def draw_upgrade_menu(surface, player_stats):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0,0))
    draw_text_centered(surface, ">> UPGRADE PROTOCOL <<", TITLE_FONT, NEON_GREEN, 200)
    
    opt1 = f"[1] OVERCLOCK (FireRate: {player_stats.shoot_delay}ms)"
    opt2 = f"[2] POWER SURGE (Dmg: {player_stats.damage})"
    opt3 = f"[3] TARGET SYSTEM (Crit: {int(player_stats.crit_rate * 100)}%)"
    
    draw_text_centered(surface, opt1, GAME_FONT, WHITE, 350)
    draw_text_centered(surface, opt2, GAME_FONT, WHITE, 450)
    draw_text_centered(surface, opt3, GAME_FONT, WHITE, 550)

def draw_pause_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0,0))
    draw_text_centered(surface, "SYSTEM PAUSED", TITLE_FONT, NEON_YELLOW, HEIGHT//2 - 20)
    draw_text_centered(surface, "Press [ESC] to Resume", UI_FONT, WHITE, HEIGHT//2 + 30)

def draw_player_health(surface, player):
    # Health Bar Background
    bar_width = 200
    bar_height = 15
    pygame.draw.rect(surface, BLACK, (20, 20, bar_width, bar_height))
    pygame.draw.rect(surface, WHITE, (20, 20, bar_width, bar_height), 2)
    
    # Health Bar Fill
    hp_percent = max(0, player.current_hp / player.max_hp)
    fill_width = int(bar_width * hp_percent)
    
    color = NEON_GREEN
    if hp_percent < 0.3: color = NEON_RED
    elif hp_percent < 0.6: color = NEON_ORANGE
        
    pygame.draw.rect(surface, color, (20, 20, fill_width, bar_height))
    
    hp_text = UI_FONT.render(f"HP: {int(player.current_hp)}%", True, WHITE)
    surface.blit(hp_text, (20 + bar_width + 10, 20))

# --- MAIN LOOP ---
clock = pygame.time.Clock()
running = True

while running:
    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if state == "MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: menu_selection = (menu_selection - 1) % 3
                elif event.key == pygame.K_DOWN: menu_selection = (menu_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if menu_selection == 0: # PLAY
                        reset_game()
                        state = "PLAYING"
                    elif menu_selection == 1: # TUTORIAL
                        state = "TUTORIAL"
                    elif menu_selection == 2: # QUIT
                        running = False

        elif state == "TUTORIAL":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "MENU"
        
        elif state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "PAUSED"

        elif state == "PAUSED":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "PLAYING"

        elif state == "GAMEOVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # Retry
                    reset_game()
                    state = "PLAYING"
                elif event.key == pygame.K_m: # Menu
                    state = "MENU"

        elif state == "UPGRADE":
            if event.type == pygame.KEYDOWN:
                upgraded = False
                if event.key == pygame.K_1: player.shoot_delay = max(50, player.shoot_delay - 40); upgraded = True
                elif event.key == pygame.K_2: player.damage += 1; upgraded = True
                elif event.key == pygame.K_3: player.crit_rate = min(1.0, player.crit_rate + 0.15); upgraded = True
                if upgraded: state = "PLAYING"; next_upgrade_score += UPGRADE_SCORE_THRESHOLD

    # 2. UPDATE LOGIC
    for star in stars: star.update() # Bintang selalu jalan untuk efek visual

    if state == "PLAYING":
        if score >= next_upgrade_score and not boss_active: state = "UPGRADE"
        all_sprites.update()
        
        # Boss Logic
        if score >= next_boss_score and not boss_active:
            boss_active = True
            for e in enemies: e.kill()
            current_boss = Boss(level); all_sprites.add(current_boss)

        if boss_active and current_boss:
            hits = pygame.sprite.spritecollide(current_boss, bullets, True)
            for hit in hits:
                current_boss.take_damage(hit.damage)
                expl_text = "CRIT!" if hit.is_crit else None
                all_sprites.add(Explosion(hit.rect.center, text=expl_text))
            
            if current_boss.current_hp <= 0:
                score += 5000; next_boss_score += BOSS_SCORE_THRESHOLD; level += 1
                current_boss.kill(); boss_active = False; current_boss = None
                
                # Drop items (garansi HP setelah boss)
                item = Item('HEALTH'); item.rect.center = (WIDTH//2 - 50, 200)
                item2 = Item(random.choice(['SHIELD', 'BOMB'])); item2.rect.center = (WIDTH//2 + 50, 200)
                all_sprites.add(item, item2); items.add(item, item2)
                
                for _ in range(15): all_sprites.add(Explosion((WIDTH//2 + random.randint(-60, 60), 100 + random.randint(-60, 60)), is_big=True))

        elif not boss_active:
            spawn_rate = 2 + (level * 0.5)
            if len(enemies) < (8 + level) and random.randint(0, 100) < spawn_rate: 
                enemy = Enemy(level, player_target=player); all_sprites.add(enemy); enemies.add(enemy)
            if len(obstacles) < (3 + level) and random.randint(0, 100) < 1:
                rock = Obstacle(level); all_sprites.add(rock); obstacles.add(rock)
            if random.randint(0, 2000) < 5:
                # Chance drop health lebih besar jika sekarat
                drop_type = 'HEALTH' if player.current_hp < 50 and random.random() > 0.5 else random.choice(['SHIELD', 'BOMB', 'HEALTH'])
                item = Item(drop_type); all_sprites.add(item); items.add(item)

            # Bullet Collision
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for bullet in bullet_list:
                    if enemy.take_damage(bullet.damage): score += 100
                    expl_text = "CRIT!" if bullet.is_crit else None
                    all_sprites.add(Explosion(enemy.rect.center, text=expl_text))

            hits = pygame.sprite.groupcollide(obstacles, bullets, True, True)
            for hit in hits: all_sprites.add(Explosion(hit.rect.center))

            # Item Collision
            hits = pygame.sprite.spritecollide(player, items, True)
            for hit in hits:
                if hit.type == 'SHIELD': player.activate_shield()
                elif hit.type == 'HEALTH': player.heal(30)
                elif hit.type == 'BOMB':
                    shake_timer = 20
                    all_sprites.add(Shockwave(player.rect.center))
                    all_sprites.add(Explosion(player.rect.center, is_big=True))
                    if boss_active and current_boss: current_boss.take_damage(BOMB_BOSS_DAMAGE)
                    for e in enemies: Explosion(e.rect.center, is_big=True); e.kill(); score += 50
                    for eb in enemy_bullets: eb.kill()

        # PLAYER DAMAGE LOGIC (Tidak lagi langsung Game Over)
        if not player.shield_active:
            # 1. Kena Musuh (Tabrakan)
            hits = pygame.sprite.spritecollide(player, enemies, True) # Musuh hancur jika nabrak
            for hit in hits:
                player.take_damage(hit.collision_damage)
                all_sprites.add(Explosion(hit.rect.center))
                
            # 2. Kena Obstacle
            hits = pygame.sprite.spritecollide(player, obstacles, True)
            for hit in hits:
                player.take_damage(hit.collision_damage)
                all_sprites.add(Explosion(hit.rect.center))
                
            # 3. Kena Peluru Musuh
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for hit in hits:
                player.take_damage(hit.damage)
                all_sprites.add(Explosion(player.rect.center))
            
            # 4. Kena Boss
            if boss_active and current_boss and pygame.sprite.collide_rect(player, current_boss):
                player.take_damage(2) # Kena damage terus menerus kalau nempel boss

            # Cek HP Player
            if player.current_hp <= 0:
                state = "GAMEOVER"

    # 3. DRAWING
    render_offset = [0, 0]
    if shake_timer > 0:
        shake_timer -= 1
        render_offset = [random.randint(-15, 15), random.randint(-15, 15)]

    GAME_SURFACE.fill(BLACK)
    for star in stars: star.draw(GAME_SURFACE)
    pygame.draw.rect(GAME_SURFACE, NEON_GREEN, (0, 0, WIDTH, HEIGHT), 2)

    if state == "MENU":
        draw_main_menu(GAME_SURFACE)
    elif state == "TUTORIAL":
        draw_tutorial(GAME_SURFACE)
    elif state == "PLAYING" or state == "UPGRADE" or state == "GAMEOVER" or state == "PAUSED":
        all_sprites.draw(GAME_SURFACE)
        
        # UI Elements
        draw_player_health(GAME_SURFACE, player)
        
        score_text = UI_FONT.render(f"SCORE: {score}", True, NEON_GREEN)
        level_text = UI_FONT.render(f"LEVEL: {level}", True, NEON_GREEN)
        GAME_SURFACE.blit(score_text, (20, 45)); GAME_SURFACE.blit(level_text, (20, 65))
        stats_text = UI_FONT.render(f"DMG: {player.damage} | CRIT: {int(player.crit_rate*100)}%", True, NEON_CYAN)
        GAME_SURFACE.blit(stats_text, (20, 85))
        if boss_active and current_boss: current_boss.draw_health(GAME_SURFACE)

        if state == "UPGRADE":
            draw_upgrade_menu(GAME_SURFACE, player)
        elif state == "PAUSED":
            draw_pause_screen(GAME_SURFACE)
        elif state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220)) 
            GAME_SURFACE.blit(overlay, (0,0))
            draw_text_centered(GAME_SURFACE, "SYSTEM FAILURE", TITLE_FONT, NEON_RED, HEIGHT//2 - 80)
            draw_text_centered(GAME_SURFACE, f"FINAL SCORE: {score}", MENU_FONT, WHITE, HEIGHT//2)
            draw_text_centered(GAME_SURFACE, "[R] RETRY    [M] MENU", UI_FONT, NEON_GREEN, HEIGHT//2 + 80)

    # POST PROCESSING
    glow_surf = pygame.transform.smoothscale(GAME_SURFACE, (WIDTH//4, HEIGHT//4))
    glow_surf = pygame.transform.smoothscale(glow_surf, (WIDTH, HEIGHT))
    SCREEN.fill((0,0,0))
    SCREEN.blit(GAME_SURFACE, render_offset)
    SCREEN.blit(glow_surf, render_offset, special_flags=pygame.BLEND_RGB_ADD)
    SCREEN.blit(SCANLINE_SURF, (0,0))
    SCREEN.blit(VIGNETTE_SURF, (0,0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()