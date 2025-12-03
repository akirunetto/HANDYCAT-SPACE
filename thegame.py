import pygame
import random
import sys
import math
import cv2
import mediapipe as mp
import numpy as np

# --- 1. INISIALISASI MEDIAPIPE & OPENCV ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # Kita hanya butuh 1 tangan untuk kontrol
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# Buka kamera
cap = cv2.VideoCapture(0)
# Set resolusi tinggi agar cropping bagus
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# --- 2. INISIALISASI PYGAME ---
pygame.init()

WIDTH = 800
HEIGHT = 800
GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("HANDYCAT SPACE")

# --- KONFIGURASI GAMEPLAY ---
BOSS_SCORE_THRESHOLD = 10000
UPGRADE_SCORE_THRESHOLD = 5000
BOMB_BOSS_DAMAGE = 100 
PLAYER_MAX_HP = 100
FINAL_STAGE = 10
SURVIVAL_TIME = 60 
HITBOX_RATIO = 0.4 

# --- WARNA NEON ---
BLACK = (5, 5, 10)
WHITE = (220, 220, 255)
NEON_GREEN = (50, 255, 100)
NEON_RED = (255, 50, 80)
NEON_CYAN = (0, 255, 255)
NEON_PURPLE = (200, 50, 255)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 165, 0)
NEON_PINK = (255, 105, 180)
NEON_BLUE = (50, 100, 255) 
DARK_SCANLINE = (0, 0, 0, 100)

# --- FONT ---
try:
    GAME_FONT = pygame.font.SysFont("consolas", 20, bold=True)
    PLAYER_FONT = pygame.font.SysFont("consolas", 12, bold=True) 
    UI_FONT = pygame.font.SysFont("consolas", 16, bold=True)
    TITLE_FONT = pygame.font.SysFont("consolas", 50, bold=True)
    MENU_FONT = pygame.font.SysFont("consolas", 30, bold=True)
    ART_FONT = pygame.font.SysFont("consolas", 14)
except:
    GAME_FONT = pygame.font.SysFont("monospace", 20, bold=True)
    PLAYER_FONT = pygame.font.SysFont("monospace", 12, bold=True) 
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
ENEMY_TANK = [[" [__M__] ", " (O_O_O) "]] 
ENEMY_KAMIKAZE = [[" \!/ ", " (X) "]]     

ROCKS_ASCII = [[" [###] "], [" (@@@) "], [" <%%%> "]]

# 10 BOSS VARIANTS
BOSS_VARIANTS = [
    (["  /\_/\  / \  /\_/\  ", " ( @.@ )|===|( @.@ ) ", "  > ^ <  \_/  > ^ <  ", " /     \_____/     \ ", "|  [  SYSTEM_ERR ]  |", " \_|_|_/     \_|_|_/ "], NEON_PURPLE),
    (["   <[ WARNING ]>   ", "  /  _       _  \  ", " |  (O)     (O)  | ", " |   \_______/   | ", "  \    [FIRE]   /  ", "   \___________/   "], NEON_ORANGE),
    (["   .---.     .---.   ", "  /  X  \___/  X  \  ", " |      (._.)      | ", "  \     /   \     /  ", "   `---'|___|`---'   ", "        /   \        "], NEON_CYAN),
    (["  //  /   \  \\  ", " ((  ( O.O )  )) ", "  \\  \___/  //  ", "   --[CORE]--    ", "     / | \       "], NEON_RED),
    ([" .--.   _   .--. ", " |__|__(_)__|__| ", " /   \ / \ /   \ ", "| [M] | o | [M] |", " \___/ \_/ \___/ "], NEON_GREEN),
    (["  | |         | |  ", "  |O|___   ___|O|  ", "  |_|___|_|___|_|  ", "    /  o   o  \    ", "   /___________\   "], NEON_YELLOW),
    ([" #%^&*(    )*&^%$# ", "  \  ERROR_404  /  ", "   | [X]   [X] |   ", "  /    NULL     \  ", " <____/ \____>   "], WHITE),
    ([" [=]=========[=] ", "  |  _|_|_|_  |  ", "  |  [_O_O_]  |  ", "  |___________|  ", "   V    V    V   "], NEON_ORANGE),
    (["    /^\   /^\    ", "   ( O ) ( O )   ", "    \ /___\ /    ", "    |  _|_  |    ", "   /| |___| |\   ", "  /_|_______|_\  "], NEON_RED),
    ([" .--.SYSTEM_ROOT.--. ", " |  |  \ | /  |  | ", " | [!] ( @ ) [!] | ", " |__|__/ | \__|__| ", "    \ \_|_|_/ /    ", "     \_______/     "], NEON_PINK)
]

ITEM_BOMB = ["[ BOMB ]"]
ITEM_SHIELD = ["[SHIELD]"]
ITEM_HEALTH = ["[ +++ ]"] 

BULLET_CHAR = "|"
ENEMY_BULLET_CHAR = "!" 
BIG_BULLET_CHAR = "(O)" 

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

# --- HAND TRACKING HELPER ---
def is_hand_open(landmarks, width, height):
    """
    Sederhana: Cek apakah ujung jari berada di atas knuckle (sendi jari)
    Ingat koordinat Y: 0 ada di atas, Height ada di bawah.
    Jadi 'lebih tinggi' secara visual berarti nilai Y lebih KECIL.
    """
    fingers_open = 0
    
    # Koordinat Ujung Jari (Tip) vs Sendi (PIP)
    # Index (8 vs 6)
    if landmarks[8].y < landmarks[6].y: fingers_open += 1
    # Middle (12 vs 10)
    if landmarks[12].y < landmarks[10].y: fingers_open += 1
    # Ring (16 vs 14)
    if landmarks[16].y < landmarks[14].y: fingers_open += 1
    # Pinky (20 vs 18)
    if landmarks[20].y < landmarks[18].y: fingers_open += 1
    
    # Thumb (4 vs 3) - Agak beda karena menyamping, kita skip agar lebih stabil
    
    # Jika 3 atau lebih jari terbuka, kita anggap tangan terbuka (untuk BOM)
    return fingers_open >= 3

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
        self.original_image = create_ascii_surface(PLAYER_ASCII, NEON_GREEN, font=PLAYER_FONT)
        self.shield_image = create_ascii_surface(PLAYER_SHIELD_ASCII, NEON_CYAN, font=PLAYER_FONT)
        self.hurt_image = create_ascii_surface(PLAYER_ASCII, NEON_RED, font=PLAYER_FONT) 
        self.image = self.original_image
        self.rect = self.image.get_rect(centerx=WIDTH//2, bottom=HEIGHT-50)
        self.speed = 7; self.shoot_delay = 300; self.damage = 1; self.crit_rate = 0.0
        self.last_shot = 0; self.shield_active = False; self.shield_timer = 0
        
        self.max_hp = PLAYER_MAX_HP
        self.current_hp = self.max_hp
        self.bombs = 2 
        
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # State tangan untuk mencegah spam bom
        self.was_hand_open = True 

    def update(self, hand_coords=None, is_open=False):
        # --- KONTROL TANGAN ---
        if hand_coords:
            target_x, target_y = hand_coords
            
            # Smoothing movement (LERP) agar tidak jittery
            self.rect.centerx += (target_x - self.rect.centerx) * 0.2
            self.rect.centery += (target_y - self.rect.centery) * 0.2
            
            # Batasi agar tidak keluar layar
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(WIDTH, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(HEIGHT, self.rect.bottom)

            # --- LOGIKA BOM (Trigger saat transisi Tutup -> Buka) ---
            if is_open and not self.was_hand_open:
                self.trigger_bomb()
            
            self.was_hand_open = is_open

        # --- KONTROL KEYBOARD (Fallback) ---
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.x += self.speed
            if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
            if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT: self.rect.y += self.speed
        
        self.auto_shoot()
        
        current_time = pygame.time.get_ticks()
        if self.invulnerable:
            if current_time > self.invulnerable_timer:
                self.invulnerable = False
                self.image = self.original_image
            else:
                if (current_time // 100) % 2 == 0: self.image = self.hurt_image
                else: self.image = self.original_image
        elif self.shield_active:
            remaining = self.shield_timer - current_time
            self.image = self.original_image if remaining < 1000 and (remaining // 100) % 2 == 0 else self.shield_image
            if current_time > self.shield_timer: self.deactivate_shield()
        else:
            self.image = self.original_image

    def trigger_bomb(self):
        if self.bombs > 0:
            self.bombs -= 1
            global shake_timer, score
            shake_timer = 20
            all_sprites.add(Shockwave(self.rect.center))
            all_sprites.add(Explosion(self.rect.center, is_big=True))
            
            if boss_active and current_boss: 
                current_boss.take_damage(BOMB_BOSS_DAMAGE)
                all_sprites.add(Explosion(current_boss.rect.center, is_big=True))
            
            for e in enemies:
                Explosion(e.rect.center, is_big=True)
                e.kill()
                score += 50
            
            for eb in enemy_bullets:
                Explosion(eb.rect.center)
                eb.kill()

    def auto_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, self.damage, self.crit_rate)
            all_sprites.add(bullet); bullets.add(bullet)
            
    def take_damage(self, amount):
        if self.shield_active or self.invulnerable: return
        self.current_hp -= amount
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks() + 1000 
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
        else: color = NEON_GREEN; art = ITEM_HEALTH
        self.image = create_ascii_surface(art, color)
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-50), y=-50); self.speed = 3
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT: self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=10, dx=0, dy=6, color=NEON_RED):
        super().__init__()
        self.damage = damage
        self.dx = dx
        self.dy = dy
        self.image = GAME_FONT.render(ENEMY_BULLET_CHAR, True, color)
        self.rect = self.image.get_rect(centerx=x, top=y)
        
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

class BigEnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage=25, dx=0, dy=3, color=NEON_ORANGE):
        super().__init__()
        self.damage = damage
        self.dx = dx
        self.dy = dy
        self.image = TITLE_FONT.render(BIG_BULLET_CHAR, True, color)
        self.rect = self.image.get_rect(centerx=x, top=y)
        
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > HEIGHT or self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, thickness=30, duration=2000, orientation='VERTICAL'):
        super().__init__()
        self.damage = 50 
        self.orientation = orientation
        self.thickness = thickness
        self.spawn_time = pygame.time.get_ticks()
        self.active_time = self.spawn_time + 1000 
        self.end_time = self.active_time + duration 
        self.is_active = False
        
        if self.orientation == 'VERTICAL':
            self.image = pygame.Surface((self.thickness, HEIGHT), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(pos, 0))
        else: # HORIZONTAL
            self.image = pygame.Surface((WIDTH, self.thickness), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=(0, pos))
            
        self.update_visual()

    def update_visual(self):
        self.image.fill((0,0,0,0)) 
        alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.02) * 100)
        
        if self.orientation == 'VERTICAL':
            if not self.is_active:
                pygame.draw.rect(self.image, (*NEON_RED, alpha), (self.thickness//2 - 1, 0, 2, HEIGHT))
            else:
                pygame.draw.rect(self.image, NEON_BLUE, (0, 0, self.thickness, HEIGHT))
                pygame.draw.rect(self.image, WHITE, (self.thickness//4, 0, self.thickness//2, HEIGHT))
        else: # HORIZONTAL
            if not self.is_active:
                pygame.draw.rect(self.image, (*NEON_RED, alpha), (0, self.thickness//2 - 1, WIDTH, 2))
            else:
                pygame.draw.rect(self.image, NEON_BLUE, (0, 0, WIDTH, self.thickness))
                pygame.draw.rect(self.image, WHITE, (0, self.thickness//4, WIDTH, self.thickness//2))

    def update(self):
        now = pygame.time.get_ticks()
        if now > self.end_time:
            self.kill()
        elif now > self.active_time:
            self.is_active = True
        self.update_visual()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, score, fr_lvl, dmg_lvl, crit_lvl, player_target=None):
        super().__init__()
        self.player_target = player_target
        roll = random.randint(1, 100)
        self.enemy_type = "BASIC"
        art = random.choice(ENEMY_BASIC)
        color = WHITE
        self.collision_damage = 10
        if score > 1500 and roll > 70: 
            self.enemy_type = "SHOOTER"; art = random.choice(ENEMY_SHOOTER); color = NEON_RED; self.collision_damage = 15
        elif score > 3000 and roll > 65:
            self.enemy_type = "DASHER"; art = random.choice(ENEMY_DASHER); color = NEON_CYAN; self.collision_damage = 20
        elif score > 5000 and roll > 75:
            self.enemy_type = "TANK"; art = random.choice(ENEMY_TANK); color = NEON_ORANGE; self.collision_damage = 30
        elif score > 7500 and roll > 85: 
            self.enemy_type = "KAMIKAZE"; art = random.choice(ENEMY_KAMIKAZE); color = NEON_YELLOW; self.collision_damage = 40
        self.image = create_ascii_surface(art, color)
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-50), y=random.randint(-150, -50))
        base_hp = 1 
        power_scaling = (dmg_lvl * 0.8) + (crit_lvl * 0.5)
        if self.enemy_type == "BASIC": self.hp = base_hp + power_scaling
        elif self.enemy_type == "SHOOTER": self.hp = base_hp + 1 + power_scaling
        elif self.enemy_type == "DASHER": self.hp = 1 + (power_scaling * 0.2)
        elif self.enemy_type == "TANK": self.hp = (base_hp * 3) + (power_scaling * 2.5) 
        elif self.enemy_type == "KAMIKAZE": self.hp = base_hp + power_scaling
        speed_bonus = min(3, fr_lvl * 0.15)
        self.speed_y = random.randint(2, 5) + speed_bonus
        self.speed_x = 0
        if self.enemy_type == "DASHER": self.speed_y = (6 + speed_bonus); self.speed_x = random.choice([-3, 3])
        if self.enemy_type == "TANK": self.speed_y = (1 + (speed_bonus * 0.5))
        if self.enemy_type == "KAMIKAZE": self.speed_y = (5 + speed_bonus)
        self.last_shot = pygame.time.get_ticks(); self.shoot_delay = random.randint(2000, 4000)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.kill(); return True
        return False
        
    def update(self):
        self.rect.y += self.speed_y; self.rect.x += self.speed_x
        if self.enemy_type == "DASHER" and (self.rect.left <= 0 or self.rect.right >= WIDTH): self.speed_x *= -1
        if self.enemy_type == "KAMIKAZE" and self.player_target:
            if self.rect.centerx < self.player_target.rect.centerx: self.rect.x += 1
            elif self.rect.centerx > self.player_target.rect.centerx: self.rect.x -= 1
        if self.enemy_type in ["SHOOTER", "TANK"]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                if self.enemy_type == "SHOOTER":
                    if self.player_target:
                        dx = self.player_target.rect.centerx - self.rect.centerx
                        dy = self.player_target.rect.centery - self.rect.centery
                        dist = math.hypot(dx, dy)
                        if dist != 0:
                            dx, dy = (dx/dist) * 6, (dy/dist) * 6
                            b = EnemyBullet(self.rect.centerx, self.rect.bottom, 10, dx, dy)
                            all_sprites.add(b); enemy_bullets.add(b)
                    else:
                         b = EnemyBullet(self.rect.centerx, self.rect.bottom, 10, 0, 6)
                         all_sprites.add(b); enemy_bullets.add(b)
                elif self.enemy_type == "TANK":
                    b1 = EnemyBullet(self.rect.centerx, self.rect.bottom, 20, 0, 5)
                    b2 = EnemyBullet(self.rect.centerx, self.rect.bottom, 20, -2, 5)
                    b3 = EnemyBullet(self.rect.centerx, self.rect.bottom, 20, 2, 5)
                    all_sprites.add(b1, b2, b3); enemy_bullets.add(b1, b2, b3)
        if self.rect.top > HEIGHT: self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, stage, fr_lvl, dmg_lvl, crit_lvl, player_target):
        super().__init__()
        self.stage = stage
        self.player_target = player_target
        idx = min(len(BOSS_VARIANTS) - 1, (stage - 1))
        ascii_art, color = BOSS_VARIANTS[idx]
        self.image = create_ascii_surface(ascii_art, color, font=GAME_FONT)
        self.rect = self.image.get_rect(centerx=WIDTH//2, y=-200)
        self.target_y = 50; self.entering = True
        base_boss_hp = 300 + (stage * 200)
        upgrade_scaling = (dmg_lvl * 100) + (crit_lvl * 50)
        self.max_hp = base_boss_hp + upgrade_scaling
        self.current_hp = self.max_hp
        self.speed_x = 2 + (stage * 0.2); self.direction = 1 
        self.last_shot = 0; self.shoot_delay = 50 
        self.collision_damage = 50 
        self.survival_mode = False
        self.survival_start_time = 0
        self.angle = 0; self.spiral_angle = 0; self.timer = 0 
        self.current_pattern = 0
        self.pattern_timer = pygame.time.get_ticks(); self.pattern_duration = 4000 
        
        # New movement
        self.move_timer = 0
        self.move_delay = 2000
        self.target_pos = (WIDTH//2, 100)
        self.move_speed = 3

    def take_damage(self, amount):
        if self.survival_mode: return 
        self.current_hp -= amount
    
    def update(self):
        if self.entering:
            self.rect.y += 2
            if self.rect.y >= self.target_y: self.entering = False
            return
        
        if self.stage == FINAL_STAGE and not self.survival_mode and self.current_hp <= (self.max_hp * 0.5):
            self.survival_mode = True
            self.survival_start_time = pygame.time.get_ticks()
            global shake_timer
            shake_timer = 30 

        # Movement Logic
        if not self.survival_mode:
            now = pygame.time.get_ticks()
            if now - self.move_timer > self.move_delay:
                self.target_pos = (random.randint(100, WIDTH-100), random.randint(50, 300))
                self.move_timer = now
            
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > self.move_speed:
                self.rect.x += (dx/dist) * self.move_speed
                self.rect.y += (dy/dist) * self.move_speed
        
        now = pygame.time.get_ticks()
        if now - self.pattern_timer > self.pattern_duration:
            self.current_pattern = (self.current_pattern + 1) % 5 
            self.pattern_timer = now
        self.shoot(now)
        
    def shoot(self, now):
        cx, cy = self.rect.centerx, self.rect.bottom
        self.timer += 1
        
        def spawn_bullet(x, y, speed, angle, color, size="SMALL"):
            rad = math.radians(angle)
            dx, dy = math.cos(rad)*speed, math.sin(rad)*speed
            if size == "BIG":
                b = BigEnemyBullet(x, y, 35, dx, dy, color)
                all_sprites.add(b); enemy_bullets.add(b)
            else:
                b = EnemyBullet(x, y, 10, dx, dy, color)
                all_sprites.add(b); enemy_bullets.add(b)

        if self.survival_mode:
            if self.timer % 5 == 0:
                self.angle = (self.angle + 17) % 360
                spawn_bullet(cx, cy, 6, self.angle, NEON_RED)
                spawn_bullet(cx, cy, 6, self.angle + 120, NEON_RED)
                spawn_bullet(cx, cy, 6, self.angle + 240, NEON_RED)
            if self.timer % 30 == 0 and self.player_target:
                dx = self.player_target.rect.centerx - cx
                dy = self.player_target.rect.centery - cy
                angle_to_player = math.degrees(math.atan2(dy, dx))
                for spread in [-10, 0, 10]:
                    spawn_bullet(cx, cy, 8, angle_to_player + spread, NEON_PURPLE)
            return

        # Randomize pattern switch logic
        if self.timer % 120 == 0:
             self.current_pattern = random.randint(0, 4)

        s = self.stage
        p = self.current_pattern
        
        # Reuse logic from prev but with movement support
        if s == 1: 
            if p == 0: 
                if self.timer % 40 == 0:
                    for i in range(0, 360, 15): spawn_bullet(cx, cy, 4, i, NEON_PURPLE)
            elif p == 1: 
                if self.timer % 5 == 0:
                    self.angle += 10
                    spawn_bullet(cx, cy, 6, self.angle, NEON_PURPLE)
            elif p == 2: 
                if self.timer % 60 == 0 and self.player_target:
                    dx = self.player_target.rect.centerx - cx
                    dy = self.player_target.rect.centery - cy
                    base_ang = math.degrees(math.atan2(dy, dx))
                    for i in range(-20, 21, 5): spawn_bullet(cx, cy, 5, base_ang + i, WHITE)
            elif p == 3: 
                if self.timer % 10 == 0:
                    self.angle += 5
                    for off in [0, 90, 180, 270]: spawn_bullet(cx, cy, 5, self.angle + off, NEON_CYAN)
            elif p == 4: 
                if self.timer % 5 == 0:
                    EnemyBullet(random.randint(0, WIDTH), 0, 10, 0, 5, NEON_PURPLE).add(all_sprites, enemy_bullets)

        else: # Generic patterns for other stages
            t = self.timer
            if p == 0: 
                if t % 5 == 0:
                    ang = self.angle + math.sin(t * 0.1) * 30
                    spawn_bullet(cx, cy, 5, ang, NEON_CYAN)
                    spawn_bullet(cx, cy, 5, ang + 90, NEON_CYAN)
                    spawn_bullet(cx, cy, 5, ang + 180, NEON_CYAN)
                    spawn_bullet(cx, cy, 5, ang + 270, NEON_CYAN)
                    self.angle += 3
            elif p == 1: 
                if t % 8 == 0:
                    offset = math.sin(t * 0.1) * 30
                    spawn_bullet(cx + offset, cy, 6, 90, NEON_GREEN)
                    spawn_bullet(cx - offset, cy, 6, 90, NEON_GREEN)
            elif p == 2: 
                if t % 40 == 0 and self.player_target:
                    dx = self.player_target.rect.centerx - cx
                    dy = self.player_target.rect.centery - cy
                    base_ang = math.degrees(math.atan2(dy, dx))
                    for i in range(-30, 31, 10): spawn_bullet(cx, cy, 7, base_ang + i, NEON_RED)
            elif p == 3: # LASER STRIKE (INTENSIFIED)
                if t % 60 == 0: 
                    if random.choice([True, False]):
                        lx = random.randint(50, WIDTH-50)
                        Laser(lx, thickness=40, orientation='VERTICAL').add(all_sprites, enemy_bullets)
                        if self.player_target:
                            aim_x = self.player_target.rect.centerx
                            Laser(aim_x-20, thickness=40, orientation='VERTICAL').add(all_sprites, enemy_bullets)
                    else:
                        ly = random.randint(50, HEIGHT-50)
                        Laser(ly, thickness=40, orientation='HORIZONTAL').add(all_sprites, enemy_bullets)
                        if self.player_target:
                            aim_y = self.player_target.rect.centery
                            Laser(aim_y-20, thickness=40, orientation='HORIZONTAL').add(all_sprites, enemy_bullets)

            elif p == 4: # Big Bullet
                if t % 60 == 0:
                    spawn_bullet(cx, cy, 4, 90, NEON_ORANGE, "BIG")
                    spawn_bullet(cx, cy, 4, 70, NEON_ORANGE, "BIG")
                    spawn_bullet(cx, cy, 4, 110, NEON_ORANGE, "BIG")

    def draw_health(self, surface):
        bar_width, bar_height = 400, 20
        if self.survival_mode:
            elapsed = (pygame.time.get_ticks() - self.survival_start_time) / 1000
            remaining = max(0, SURVIVAL_TIME - elapsed)
            fill = (remaining / SURVIVAL_TIME) * bar_width
            pygame.draw.rect(surface, WHITE, ((WIDTH//2)-(bar_width//2), 60, bar_width, bar_height), 2)
            pygame.draw.rect(surface, NEON_RED, ((WIDTH//2)-(bar_width//2), 60, fill, bar_height))
            text = UI_FONT.render(f"SURVIVE: {remaining:.1f}s", True, NEON_RED)
        else:
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
upgrade_fr_count = 0 
upgrade_dmg_count = 0
upgrade_crit_count = 0
next_boss_score = BOSS_SCORE_THRESHOLD
next_upgrade_score = UPGRADE_SCORE_THRESHOLD
boss_active = False
current_boss = None
state = "MENU" 
shake_timer = 0
menu_selection = 0
pause_selection = 0
flash_alpha = 0
boss_death_timer = 0 # Timer untuk delay musuh

# --- CRT EFFECT ASSETS ---
SCANLINE_SURF = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 4):
    pygame.draw.line(SCANLINE_SURF, (0, 0, 0, 80), (0, y), (WIDTH, y), 1)

VIGNETTE_SURF = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(VIGNETTE_SURF, (0,0,0,50), (0,0,WIDTH,HEIGHT), 0)
pygame.draw.circle(VIGNETTE_SURF, (0,0,0,0), (WIDTH//2, HEIGHT//2), 450)

# --- FUNCTIONS ---
def reset_game():
    global score, level, upgrade_fr_count, upgrade_dmg_count, upgrade_crit_count, next_boss_score, next_upgrade_score, boss_active, current_boss, player, boss_death_timer, flash_alpha
    score = 0; level = 1
    upgrade_fr_count = 0; upgrade_dmg_count = 0; upgrade_crit_count = 0
    next_boss_score = BOSS_SCORE_THRESHOLD
    next_upgrade_score = UPGRADE_SCORE_THRESHOLD
    boss_active = False; current_boss = None
    boss_death_timer = 0
    flash_alpha = 0 # Reset flash
    all_sprites.empty(); enemies.empty(); obstacles.empty(); bullets.empty(); enemy_bullets.empty(); items.empty()
    player = Player(); all_sprites.add(player)

def draw_main_menu(surface):
    draw_text_centered(surface, "HANDYCAT SPACE", TITLE_FONT, NEON_GREEN, 150)
    draw_text_centered(surface, "FIGHT ALIEN CATS!!!", UI_FONT, NEON_CYAN, 200)
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
        "HAND CONTROLS:", 
        "FIST (KEPAL) -> MOVE SHIP", 
        "OPEN HAND (BUKA) -> TRIGGER BOMB",
        "", "KEYBOARD FALLBACK:",
        "ARROWS - Move", "[B] - Bomb",
        "", "ADAPTIVE DIFFICULTY:",
        "UPGRADE FIRE RATE -> MORE ENEMIES",
        "UPGRADE DAMAGE -> TOUGHER ENEMIES",
        "", "BOSS:", "10 STAGES, 5 PATTERNS EACH"
    ]
    for i, line in enumerate(info):
        color = NEON_GREEN if "CONTROLS" in line or "ADAPTIVE" in line or "ITEMS" in line else WHITE
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
    
    warn_text = ""
    if upgrade_fr_count > upgrade_dmg_count: warn_text = "WARNING: HIGH ENEMY ACTIVITY DETECTED"
    elif upgrade_dmg_count > upgrade_fr_count: warn_text = "WARNING: HEAVY ARMOR ENEMIES DETECTED"
    else: warn_text = "WARNING: DIFFICULTY INCREASING"
    draw_text_centered(surface, warn_text, UI_FONT, NEON_RED, 650)

def draw_pause_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0,0))
    draw_text_centered(surface, "SYSTEM PAUSED", TITLE_FONT, NEON_YELLOW, 200)
    options = ["RESUME", "RESTART", "MAIN MENU"]
    for i, option in enumerate(options):
        color = NEON_GREEN if i == pause_selection else WHITE
        prefix = "> " if i == pause_selection else "  "
        suffix = " <" if i == pause_selection else "  "
        draw_text_centered(surface, prefix + option + suffix, MENU_FONT, color, 350 + (i * 60))

def draw_player_health(surface, player):
    bar_width, bar_height = 200, 15
    pygame.draw.rect(surface, BLACK, (20, 20, bar_width, bar_height))
    pygame.draw.rect(surface, WHITE, (20, 20, bar_width, bar_height), 2)
    hp_percent = max(0, player.current_hp / player.max_hp)
    fill_width = int(bar_width * hp_percent)
    color = NEON_GREEN if hp_percent > 0.6 else NEON_ORANGE if hp_percent > 0.3 else NEON_RED
    pygame.draw.rect(surface, color, (20, 20, fill_width, bar_height))
    hp_text = UI_FONT.render(f"HP: {int(player.current_hp)}%", True, WHITE)
    surface.blit(hp_text, (20 + bar_width + 10, 20))
    bomb_text = UI_FONT.render(f"BOMBS: {player.bombs}", True, NEON_YELLOW)
    surface.blit(bomb_text, (20, 40))

def win_game_screen(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220)) 
    surface.blit(overlay, (0,0))
    draw_text_centered(surface, "MISSION ACCOMPLISHED", TITLE_FONT, NEON_CYAN, HEIGHT//2 - 80)
    draw_text_centered(surface, f"FINAL SCORE: {score}", MENU_FONT, WHITE, HEIGHT//2)
    draw_text_centered(surface, "SYSTEM SECURE", UI_FONT, NEON_GREEN, HEIGHT//2 + 80)
    draw_text_centered(surface, "[M] MENU", UI_FONT, WHITE, HEIGHT//2 + 120)

# --- MAIN LOOP ---
clock = pygame.time.Clock()
running = True

TARGET_SIZE = 800

while running:
    # --- 0. PROSES KAMERA (OPENCV) ---
    success, img = cap.read()
    hand_pos_game = None
    hand_is_open = False
    
    # Texture kamera untuk background (efek hologram)
    cam_surface = None

    if success:
        # Mirror image
        img = cv2.flip(img, 1)
        
        # Crop & Resize logic (sama seperti di main.py Anda)
        h, w, _ = img.shape
        if w < h: scale = TARGET_SIZE / w
        else: scale = TARGET_SIZE / h
        new_w, new_h = int(w * scale), int(h * scale)
        img_resized = cv2.resize(img, (new_w, new_h))
        start_x = (new_w - TARGET_SIZE) // 2
        start_y = (new_h - TARGET_SIZE) // 2
        img_cropped = img_resized[start_y:start_y+TARGET_SIZE, start_x:start_x+TARGET_SIZE]
        
        # MediaPipe Process
        img_rgb = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Ambil koordinat titik tengah telapak tangan (WRIST + MIDDLE_FINGER_MCP) / 2
                # Atau sederhananya pakai titik 9 (Middle Finger MCP)
                lm = hand_landmarks.landmark[9]
                h_final, w_final, _ = img_cropped.shape
                cx, cy = int(lm.x * w_final), int(lm.y * h_final)
                
                hand_pos_game = (cx, cy)
                
                # Cek Gesture (Buka/Tutup)
                hand_is_open = is_hand_open(hand_landmarks.landmark, w_final, h_final)
                
                # Visualisasi Debug di gambar kamera
                color = (0, 255, 0) if hand_is_open else (0, 0, 255)
                status = "OPEN (BOMB)" if hand_is_open else "FIST (MOVE)"
                cv2.circle(img_cropped, (cx, cy), 15, color, cv2.FILLED)
                # Gambar koneksi tangan
                mp_draw.draw_landmarks(img_cropped, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Konversi gambar OpenCV ke Pygame Surface untuk background
        # Kita beri efek kehijauan agar sesuai tema
        img_cropped = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
        img_cropped = np.rot90(img_cropped) # Pygame rotation fix
        img_cropped = np.flipud(img_cropped)
        cam_surface = pygame.surfarray.make_surface(img_cropped)
        cam_surface.set_alpha(80) # Transparan

    # 1. EVENT HANDLING PYGAME
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if state == "MENU":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: menu_selection = (menu_selection - 1) % 3
                elif event.key == pygame.K_DOWN: menu_selection = (menu_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if menu_selection == 0: reset_game(); state = "PLAYING"
                    elif menu_selection == 1: state = "TUTORIAL"
                    elif menu_selection == 2: running = False

        elif state == "TUTORIAL":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: state = "MENU"
        
        elif state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    state = "PAUSED"
                    pause_selection = 0
                elif event.key == pygame.K_b:
                    player.trigger_bomb()

        elif state == "PAUSED":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: pause_selection = (pause_selection - 1) % 3
                elif event.key == pygame.K_DOWN: pause_selection = (pause_selection + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if pause_selection == 0: state = "PLAYING" # Resume
                    elif pause_selection == 1: reset_game(); state = "PLAYING" # Restart
                    elif pause_selection == 2: state = "MENU" # Menu

        elif state == "GAMEOVER" or state == "WIN":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and state == "GAMEOVER": reset_game(); state = "PLAYING"
                elif event.key == pygame.K_m: state = "MENU"

        elif state == "UPGRADE":
            if event.type == pygame.KEYDOWN:
                upgraded = False
                if event.key == pygame.K_1: 
                    player.shoot_delay = max(50, player.shoot_delay - 40)
                    upgrade_fr_count += 1
                    upgraded = True
                elif event.key == pygame.K_2: 
                    player.damage += 1
                    upgrade_dmg_count += 1
                    upgraded = True
                elif event.key == pygame.K_3: 
                    player.crit_rate = min(1.0, player.crit_rate + 0.15)
                    upgrade_crit_count += 1
                    upgraded = True
                    
                if upgraded: 
                    state = "PLAYING"
                    next_upgrade_score += UPGRADE_SCORE_THRESHOLD

    # 2. UPDATE LOGIC
    for star in stars: star.update()

    if state == "PLAYING":
        if score >= next_upgrade_score and not boss_active: state = "UPGRADE"
        
        # --- UPDATE PLAYER DENGAN HAND TRACKING ---
        # Kita pass hand_pos_game dan hand_is_open ke player
        player.update(hand_coords=hand_pos_game, is_open=hand_is_open)
        
        # Update sprites lain
        # Note: Jangan update player lagi via all_sprites.update() karena sudah diupdate di atas
        # Kita bikin grup khusus non-player atau panggil update manual untuk sisanya
        for sprite in all_sprites:
            if sprite != player:
                sprite.update()
        
        if random.randint(0, 2000) < 5:
             drop_type = 'HEALTH' if player.current_hp < 50 and random.random() > 0.5 else random.choice(['SHIELD', 'BOMB', 'HEALTH', 'BOMB'])
             item = Item(drop_type)
             all_sprites.add(item); items.add(item)

        if score >= next_boss_score and not boss_active:
            boss_active = True
            for e in enemies: e.kill()
            current_boss = Boss(level, upgrade_fr_count, upgrade_dmg_count, upgrade_crit_count, player)
            all_sprites.add(current_boss)

        if boss_active and current_boss:
            hits = pygame.sprite.spritecollide(current_boss, bullets, True)
            for hit in hits:
                current_boss.take_damage(hit.damage)
                expl_text = "CRIT!" if hit.is_crit else None
                all_sprites.add(Explosion(hit.rect.center, text=expl_text))
            
            boss_dead = False
            if current_boss.survival_mode:
                elapsed = (pygame.time.get_ticks() - current_boss.survival_start_time) / 1000
                if elapsed >= SURVIVAL_TIME:
                    boss_dead = True
                    state = "WIN" 
            elif current_boss.current_hp <= 0 and not current_boss.survival_mode:
                boss_dead = True
            
            if boss_dead and state != "WIN":
                flash_alpha = 255
                boss_death_timer = pygame.time.get_ticks() + 3000 
                
                score += 5000; next_boss_score += BOSS_SCORE_THRESHOLD; level += 1
                if current_boss: current_boss.kill() 
                boss_active = False; current_boss = None
                
                item = Item('HEALTH'); item.rect.center = (WIDTH//2 - 50, 200)
                item2 = Item(random.choice(['SHIELD', 'BOMB'])); item2.rect.center = (WIDTH//2 + 50, 200)
                all_sprites.add(item, item2); items.add(item, item2)
                for _ in range(30): 
                    all_sprites.add(Explosion((WIDTH//2 + random.randint(-100, 100), 100 + random.randint(-100, 100)), is_big=True))

        elif not boss_active:
            current_time = pygame.time.get_ticks()
            if current_time > boss_death_timer:
                base_spawn_rate = 1.0 + (level * 0.3) + (upgrade_fr_count * 0.5) 
                max_enemies = 5 + level + int(upgrade_fr_count)
                
                if len(enemies) < max_enemies and random.randint(0, 100) < base_spawn_rate: 
                    enemy = Enemy(score, upgrade_fr_count, upgrade_dmg_count, upgrade_crit_count, player_target=player)
                    all_sprites.add(enemy); enemies.add(enemy)
                    
                if len(obstacles) < (3 + level) and random.randint(0, 100) < 1:
                    rock = Obstacle(level); all_sprites.add(rock); obstacles.add(rock)

            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            for enemy, bullet_list in hits.items():
                for bullet in bullet_list:
                    if enemy.take_damage(bullet.damage): score += 100
                    expl_text = "CRIT!" if bullet.is_crit else None
                    all_sprites.add(Explosion(enemy.rect.center, text=expl_text))

            hits = pygame.sprite.groupcollide(obstacles, bullets, True, True)
            for hit in hits: all_sprites.add(Explosion(hit.rect.center))

        hits = pygame.sprite.spritecollide(player, items, True)
        for hit in hits:
            if hit.type == 'SHIELD': player.activate_shield()
            elif hit.type == 'HEALTH': player.heal(30)
            elif hit.type == 'BOMB': 
                player.bombs += 1

        if not player.shield_active:
            hits = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_rect_ratio(HITBOX_RATIO))
            for hit in hits: player.take_damage(hit.collision_damage); all_sprites.add(Explosion(hit.rect.center))
            
            hits = pygame.sprite.spritecollide(player, obstacles, True, pygame.sprite.collide_rect_ratio(HITBOX_RATIO))
            for hit in hits: player.take_damage(hit.collision_damage); all_sprites.add(Explosion(hit.rect.center))
            
            hits = pygame.sprite.spritecollide(player, enemy_bullets, False, pygame.sprite.collide_rect_ratio(HITBOX_RATIO))
            for hit in hits: 
                if isinstance(hit, Laser):
                    if hit.is_active: player.take_damage(hit.damage) 
                else:
                    player.take_damage(hit.damage)
                    all_sprites.add(Explosion(player.rect.center))
                    hit.kill()
            
            if boss_active and current_boss and pygame.sprite.collide_rect_ratio(HITBOX_RATIO)(player, current_boss): 
                player.take_damage(2)
            
            if player.current_hp <= 0: state = "GAMEOVER"

    # 3. DRAWING
    render_offset = [0, 0]
    if shake_timer > 0:
        shake_timer -= 1
        render_offset = [random.randint(-15, 15), random.randint(-15, 15)]

    GAME_SURFACE.fill(BLACK)
    
    # Render Camera Feed Background (Optional - Hapus baris ini jika ingin hitam pekat)
    if cam_surface:
        GAME_SURFACE.blit(cam_surface, (0,0))

    for star in stars: star.draw(GAME_SURFACE)
    
    pygame.draw.rect(GAME_SURFACE, NEON_GREEN, (0, 0, WIDTH, HEIGHT), 2)

    if state == "MENU": draw_main_menu(GAME_SURFACE)
    elif state == "TUTORIAL": draw_tutorial(GAME_SURFACE)
    elif state == "PLAYING" or state == "UPGRADE" or state == "GAMEOVER" or state == "PAUSED":
        all_sprites.draw(GAME_SURFACE)
        draw_player_health(GAME_SURFACE, player)
        score_text = UI_FONT.render(f"SCORE: {score}", True, NEON_GREEN)
        level_text = UI_FONT.render(f"LEVEL: {level}", True, NEON_GREEN)
        GAME_SURFACE.blit(score_text, (20, 60)); GAME_SURFACE.blit(level_text, (20, 80))
        stats_text = UI_FONT.render(f"DMG: {player.damage} | CRIT: {int(player.crit_rate*100)}%", True, NEON_CYAN)
        GAME_SURFACE.blit(stats_text, (20, 100))
        if boss_active and current_boss: current_boss.draw_health(GAME_SURFACE)
        
        # Tampilkan Indikator Tangan jika bermain
        if state == "PLAYING":
            status_color = NEON_RED if hand_is_open else NEON_GREEN
            status_text = "HAND: OPEN (BOMB)" if hand_is_open else "HAND: FIST (MOVE)"
            if not hand_pos_game: 
                status_text = "HAND: NOT DETECTED"
                status_color = WHITE
            draw_text_centered(GAME_SURFACE, status_text, UI_FONT, status_color, HEIGHT - 30)

        if state == "UPGRADE": draw_upgrade_menu(GAME_SURFACE, player)
        elif state == "PAUSED": draw_pause_screen(GAME_SURFACE)
        elif state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220)) 
            GAME_SURFACE.blit(overlay, (0,0))
            draw_text_centered(GAME_SURFACE, "SYSTEM FAILURE", TITLE_FONT, NEON_RED, HEIGHT//2 - 80)
            draw_text_centered(GAME_SURFACE, f"FINAL SCORE: {score}", MENU_FONT, WHITE, HEIGHT//2)
            draw_text_centered(GAME_SURFACE, "[R] RETRY    [M] MENU", UI_FONT, NEON_GREEN, HEIGHT//2 + 80)
    
    elif state == "WIN":
        win_game_screen(GAME_SURFACE)

    if flash_alpha > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT))
        flash_surf.fill(WHITE)
        flash_surf.set_alpha(flash_alpha)
        GAME_SURFACE.blit(flash_surf, (0,0))
        flash_alpha -= 10 

    glow_surf = pygame.transform.smoothscale(GAME_SURFACE, (WIDTH//4, HEIGHT//4))
    glow_surf = pygame.transform.smoothscale(glow_surf, (WIDTH, HEIGHT))
    SCREEN.fill((0,0,0))
    SCREEN.blit(GAME_SURFACE, render_offset)
    SCREEN.blit(glow_surf, render_offset, special_flags=pygame.BLEND_RGB_ADD)
    SCREEN.blit(SCANLINE_SURF, (0,0))
    SCREEN.blit(VIGNETTE_SURF, (0,0))

    pygame.display.flip()
    clock.tick(60)

# CLEANUP
cap.release()
pygame.quit()
sys.exit()