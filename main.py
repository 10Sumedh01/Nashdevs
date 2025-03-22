import pygame
import random
import math
import sys
from pygame.locals import *

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
GRID_SPACING = 100
PLAYER_MAX_HEALTH = 100
PLAYER_START_AMMO = 20
HEALTH_PACK_AMOUNT = 25
AMMO_PACK_AMOUNT = 10
BULLET_SPEED = 15
BULLET_RANGE = 500

# Asset paths
ZOMBIE_IMAGE_PATH = "assets/zombie.png"
SPECIAL_ZOMBIE_IMAGE_PATH = "assets/special_zombie.png"

# Maze settings
MAZE_REGION_SIZE = 2000  
MAZE_CELL_SIZE = 200     
MAZE_FILL_PROB = 0.3     
DESTRUCTIBLE_PROB = 0.3  
DYNAMIC_PROB = 0.1       
SAFE_ZONE_MARGIN = 150   

# Colors
BLACK = (0, 0, 0)
DARK_RED = (100, 0, 0)
PLAYER_COLOR = (0, 200, 0)
ZOMBIE_COLOR = (150, 50, 50)
SPECIAL_ZOMBIE_COLOR = (255, 100, 0)
OBSTACLE_COLOR = (80, 80, 80)
DESTRUCTIBLE_COLOR = (150, 80, 80)
DYNAMIC_COLOR = (70, 130, 180)
GRID_COLOR = (40, 40, 60)
TEXT_COLOR = (240, 240, 240)

# Player settings
PLAYER_SIZE = 30
PLAYER_SPEED = 5

# Zombie settings
BASE_ZOMBIE_SIZE = 77
BASE_ZOMBIE_SPEED = 2.5
ZOMBIE_SIZE = BASE_ZOMBIE_SIZE
ZOMBIE_SPEED = BASE_ZOMBIE_SPEED
SPAWN_INTERVAL = 3000
MIN_SPAWN_DIST = 500
SPECIAL_ZOMBIE_PROXIMITY_RADIUS = 150  
SPECIAL_ZOMBIE_IMMOBILE_DURATION = 3000  
COLLISION_THRESHOLD = 35

# Level settings
LEVEL_DURATION = 30000
MINI_GAME_DURATION = 120000
DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2
DYNAMIC_OBSTACLE_INTERVAL = 2000

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
        self.speed = PLAYER_SPEED
        self.size = PLAYER_SIZE
        self.health = PLAYER_MAX_HEALTH
        self.ammo = PLAYER_START_AMMO
        self.last_hit = 0
        self.invincible = False
        self.invincible_duration = 1000
        self.flashlight = True

    def take_damage(self, damage):
        if not self.invincible:
            self.health = max(0, self.health - damage)
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_duration:
            self.invincible = False

    def shoot(self, target_pos):
        if self.ammo > 0:
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        return None

    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[K_LEFT] or keys[K_a]: move.x -= self.speed
        if keys[K_RIGHT] or keys[K_d]: move.x += self.speed
        if keys[K_UP] or keys[K_w]: move.y -= self.speed
        if keys[K_DOWN] or keys[K_s]: move.y += self.speed

        if move.length() > 0:
            move = move.normalize() * self.speed

        old_pos = self.pos.copy()
        self.pos += move
        for obs in obstacles:
            if self.get_rect().colliderect(obs.get_rect()):
                self.pos = old_pos
                break

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                         self.pos.y - self.size//2,
                         self.size, self.size)

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)
        
        if self.flashlight:
            flashlight_radius = 250
            mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 200))
            pygame.draw.circle(mask, (0, 0, 0, 0), 
                             (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), 
                             flashlight_radius)
            surface.blit(mask, (0, 0))

class Bullet:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.speed = BULLET_SPEED
        self.distance_traveled = 0
        self.size = 5

    def update(self):
        self.pos += self.direction * self.speed
        self.distance_traveled += self.speed

    def draw(self, surface, offset):
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), 
                          self.size)

class Pickup:
    def __init__(self, pos, pickup_type):
        self.pos = pos
        self.type = pickup_type
        self.size = 20
        self.colors = {'health': (0, 255, 0), 'ammo': (255, 165, 0)}

    def draw(self, surface, offset):
        color = self.colors.get(self.type, (255, 255, 255))
        pygame.draw.rect(surface, color, (self.pos.x - offset.x - self.size//2,
                                        self.pos.y - offset.y - self.size//2,
                                        self.size, self.size))

class Zombie:
    def __init__(self, spawn_pos, speed_multiplier=1.0):
        self.pos = pygame.Vector2(spawn_pos)
        self.speed = ZOMBIE_SPEED * speed_multiplier
        self.size = ZOMBIE_SIZE
        self.is_special = False
        self.health = 100
        self.angle = 0  # Add angle attribute
        
        # Load and scale zombie image
        self.original_image = pygame.image.load(ZOMBIE_IMAGE_PATH).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.image = self.original_image  # Store original for rotations

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def update(self, player_pos, obstacles):
        old_pos = self.pos.copy()
        direction = player_pos - self.pos
        if direction.length() > 0:
            # Calculate angle to face player (adjusted for right-facing asset)
            self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
            direction = direction.normalize()
            self.pos += direction * self.speed

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                         self.pos.y - self.size//2,
                         self.size, self.size)

    def draw(self, surface, offset):
        # Rotate the original image and get its rect
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        img_rect = rotated_image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(rotated_image, img_rect)

class SpecialZombie(Zombie):
    def __init__(self, spawn_pos, speed_multiplier=1.0, immobile_duration=3000, harmful=True, flicker=False):
        super().__init__(spawn_pos, speed_multiplier)
        self.is_special = True
        self.size = ZOMBIE_SIZE * 2
        self.speed = ZOMBIE_SPEED * speed_multiplier * 1.2
        self.spawn_time = pygame.time.get_ticks()
        self.immobile_duration = immobile_duration
        self.harmful = harmful
        self.flicker = flicker
        self.health = 200
        
        # Load special zombie image
        self.image = pygame.image.load(SPECIAL_ZOMBIE_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.original_image = self.image.copy()
        self.flicker_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

    def update(self, player_pos, obstacles):
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time < self.immobile_duration:
            return
        super().update(player_pos, obstacles)

    def draw(self, surface, offset):
        img_rect = self.image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(self.image, img_rect)
        
        # Handle flicker effect
        if self.flicker and (pygame.time.get_ticks() // 250) % 2 == 0:
            self.flicker_surface.fill((255, 200, 0, 128))
            surface.blit(self.flicker_surface, img_rect)

class Obstacle:
    def __init__(self, pos, size, destructible=False):
        self.pos = pygame.Vector2(pos)
        self.size = size
        self.destructible = destructible
        self.hp = 100 if destructible else None

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        color = DESTRUCTIBLE_COLOR if self.destructible else OBSTACLE_COLOR
        pygame.draw.rect(surface, color, rect)

    def update(self):
        pass

class DynamicObstacle(Obstacle):
    def __init__(self, pos, size, path, speed):
        super().__init__(pos, size, destructible=False)
        self.path = path
        self.speed = speed
        self.current_target_index = 0

    def update(self):
        target = pygame.Vector2(self.path[self.current_target_index])
        direction = target - self.pos
        if direction.length() < self.speed:
            self.pos = target
            self.current_target_index = (self.current_target_index + 1) % len(self.path)
        else:
            self.pos += direction.normalize() * self.speed

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        pygame.draw.rect(surface, DYNAMIC_COLOR, rect)

# --- Utility Functions ---
def draw_grid(surface, offset):
    start_x = int(offset.x // GRID_SPACING * GRID_SPACING)
    start_y = int(offset.y // GRID_SPACING * GRID_SPACING)
    end_x = start_x + WIDTH + GRID_SPACING
    end_y = start_y + HEIGHT + GRID_SPACING
    for x in range(start_x, end_x, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (x - offset.x, 0), (x - offset.x, HEIGHT))
    for y in range(start_y, end_y, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (0, y - offset.y), (WIDTH, y - offset.y))

def generate_maze_obstacles(reference_pos):
    obstacles = []
    region_half = MAZE_REGION_SIZE // 2
    start_x = int(reference_pos.x - region_half)
    start_y = int(reference_pos.y - region_half)
    end_x = int(reference_pos.x + region_half)
    end_y = int(reference_pos.y + region_half)
    safe_zone = pygame.Rect(reference_pos.x - SAFE_ZONE_MARGIN,
                            reference_pos.y - SAFE_ZONE_MARGIN,
                            SAFE_ZONE_MARGIN * 2,
                            SAFE_ZONE_MARGIN * 2)
    x = start_x
    while x < end_x:
        y = start_y
        while y < end_y:
            cell_rect = pygame.Rect(x, y, MAZE_CELL_SIZE, MAZE_CELL_SIZE)
            if cell_rect.colliderect(safe_zone):
                y += MAZE_CELL_SIZE
                continue
            if random.random() < MAZE_FILL_PROB:
                r = random.random()
                if r < DESTRUCTIBLE_PROB:
                    obstacles.append(Obstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE), destructible=True))
                elif r < DESTRUCTIBLE_PROB + DYNAMIC_PROB:
                    path = [(x, y), (x + MAZE_CELL_SIZE, y)]
                    speed = 1
                    obstacles.append(DynamicObstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE), path, speed))
                else:
                    obstacles.append(Obstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE)))
            y += MAZE_CELL_SIZE
        x += MAZE_CELL_SIZE
    return obstacles

def reposition_maze_obstacles(obstacles, reference_pos):
    return generate_maze_obstacles(reference_pos)

def spawn_zombie(player_pos, speed_multiplier=1.0):
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(MIN_SPAWN_DIST, MIN_SPAWN_DIST + 300)
    spawn_x = player_pos.x + math.cos(angle) * distance
    spawn_y = player_pos.y + math.sin(angle) * distance
    return Zombie((spawn_x, spawn_y), speed_multiplier)

def spawn_special_zombie(player_pos, speed_multiplier=1.0, level=1):
    if level in [6, 9, 10]:
        distance = random.uniform(150, 250)
        immobile_duration = 3000
        harmful = True
        flicker = True
    else:
        distance = random.uniform(0, SPECIAL_ZOMBIE_PROXIMITY_RADIUS)
        immobile_duration = SPECIAL_ZOMBIE_IMMOBILE_DURATION
        harmful = True
        flicker = False
    angle = random.uniform(0, 2 * math.pi)
    spawn_x = player_pos.x + math.cos(angle) * distance
    spawn_y = player_pos.y + math.sin(angle) * distance
    return SpecialZombie((spawn_x, spawn_y), speed_multiplier, immobile_duration, harmful, flicker)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    player = Player()
    zombies = []
    bullets = []
    pickups = []
    obstacles = generate_maze_obstacles(player.pos)

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
    pygame.time.set_timer(DYNAMIC_OBSTACLE_EVENT, DYNAMIC_OBSTACLE_INTERVAL)

    start_ticks = pygame.time.get_ticks()
    current_level = 1
    zombie_speed_multiplier = 1.0
    level_start_time = pygame.time.get_ticks()
    game_over = False

    while True:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_ticks

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = pygame.Vector2(mouse_pos) + pygame.Vector2(
                    player.pos.x - WIDTH//2,
                    player.pos.y - HEIGHT//2
                )
                bullet = player.shoot(world_mouse_pos)
                if bullet:
                    bullets.append(bullet)
            if event.type == SPAWN_EVENT and not game_over:
                zombies.append(spawn_zombie(player.pos, zombie_speed_multiplier))

        if not game_over:
            player.update(obstacles)
            player.update_invincibility()

            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.distance_traveled > BULLET_RANGE:
                    bullets.remove(bullet)
                    continue
                
                for zombie in zombies[:]:
                    if (bullet.pos - zombie.pos).length() < zombie.size:
                        if zombie.take_damage(50):
                            zombies.remove(zombie)
                            if random.random() < 0.3:
                                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                                pickups.append(Pickup(zombie.pos.copy(), pickup_type))
                        bullets.remove(bullet)
                        break

            # Update pickups
            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)

            # Update zombies
            for zombie in zombies:
                zombie.update(player.pos, obstacles)
                if (player.pos - zombie.pos).length() < COLLISION_THRESHOLD and not player.invincible:
                    player.take_damage(10)
                    if player.health <= 0:
                        game_over = True

            # Update obstacles
            for obs in obstacles:
                if hasattr(obs, 'update'):
                    obs.update()

            # Level progression
            if elapsed_time >= LEVEL_DURATION:
                current_level += 1
                zombie_speed_multiplier *= 1.05
                obstacles = reposition_maze_obstacles(obstacles, player.pos)
                start_ticks = current_time

        # Drawing
        offset = pygame.Vector2(player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)
        screen.fill(DARK_RED)
        draw_grid(screen, offset)
        
        for obs in obstacles:
            obs.draw(screen, offset)
        for pickup in pickups:
            pickup.draw(screen, offset)
        for zombie in zombies:
            zombie.draw(screen, offset)
        for bullet in bullets:
            bullet.draw(screen, offset)
        player.draw(screen, offset)

        # UI Elements
        health_bar_width = 200
        pygame.draw.rect(screen, (255,0,0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(screen, (0,255,0), 
                        (20, 20, health_bar_width * (player.health/PLAYER_MAX_HEALTH), 20))
        
        ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
        screen.blit(ammo_text, (WIDTH - 150, 20))
        
        level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
        screen.blit(level_text, (WIDTH//2 - 50, 20))

        if game_over:
            game_over_text = font.render("GAME OVER - Press R to restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))

        pygame.display.flip()

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[K_r]:
                main()
                return

if __name__ == '__main__':
    main()