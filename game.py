import pygame
import random
import math
import sys
from pygame.locals import *

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
GRID_SPACING = 100

# Gameplay constants
PLAYER_MAX_HEALTH = 100
PLAYER_START_AMMO = 50
HEALTH_PACK_AMOUNT = 25
AMMO_PACK_AMOUNT = 10
BULLET_SPEED = 15
BULLET_RANGE = 500

# Maze settings
MAZE_REGION_SIZE = 2000  
MAZE_CELL_SIZE = 200     
MAZE_FILL_PROB = 0.3     
SAFE_ZONE_MARGIN = 150   

# Colors
BLACK = (0, 0, 0)
RED = (200, 0, 0)         # For levels 1,2,4,5 background
MAROON = (128, 0, 0)      # For level 3 (Nightmare) background
PLAYER_COLOR = (0, 200, 0)
# Zombies: drawn in RED in level 3, BLACK in other levels.
ZOMBIE_COLOR = (150, 50, 50)   # not directly used in draw now
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
BASE_ZOMBIE_SIZE = 30
BASE_ZOMBIE_SPEED = 2.5
ZOMBIE_SIZE = BASE_ZOMBIE_SIZE
ZOMBIE_SPEED = BASE_ZOMBIE_SPEED
SPAWN_INTERVAL = 3000  # ms
MIN_SPAWN_DIST = 500
SPECIAL_ZOMBIE_PROXIMITY_RADIUS = 150  
SPECIAL_ZOMBIE_IMMOBILE_DURATION = 3000  
COLLISION_THRESHOLD = 35

# Level settings
LEVEL_DURATION = 30000         # Normal levels: 30 sec
NIGHTMARE_LEVEL_DURATION = 60000 # Level 3 lasts 60 sec
NIGHTMARE_TRANSITION_DELAY = 3000  # 3 sec transition delay before level 3
FINAL_LEVEL = 5                # Game ends at level 5

# Flashlight settings
DEFAULT_FLASHLIGHT_RADIUS = 250
NIGHTMARE_FLASHLIGHT_RADIUS = int(DEFAULT_FLASHLIGHT_RADIUS * 0.85)  # 15% reduction

# Stamina settings (levels 4 and 5)
STAMINA_IDLE_TIME = 5000     # in ms (cumulative idle time)
MAX_STAMINA = 100

# Fire element settings (levels 4 and 5)
FIRE_DAMAGE = 5
FIRE_SIZE = 30

# Dynamic obstacle event
DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2

# --- Classes ---
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
        self.idle_timer = 0

    def take_damage(self, damage):
        if not self.invincible:
            self.health = max(0, self.health - damage)
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_duration:
            self.invincible = False

    def shoot(self, target_pos, current_level):
        if current_level < 5:
            return None
        if self.ammo > 0:
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        return None

    def update(self, obstacles, dt):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[K_LEFT] or keys[K_a]:
            move.x -= self.speed
        if keys[K_RIGHT] or keys[K_d]:
            move.x += self.speed
        if keys[K_UP] or keys[K_w]:
            move.y -= self.speed
        if keys[K_DOWN] or keys[K_s]:
            move.y += self.speed
        if move.length() > 0:
            move = move.normalize() * self.speed
        old_pos = self.pos.copy()
        self.pos += move
        for obs in obstacles:
            if self.get_rect().colliderect(obs.get_rect()):
                self.pos = old_pos
                break
        # Accumulate idle time (cumulative, not reset on movement)
        if move.length() < 0.1:
            self.idle_timer += dt
            if self.idle_timer > STAMINA_IDLE_TIME:
                self.idle_timer = STAMINA_IDLE_TIME

    def get_stamina(self):
        return int((self.idle_timer / STAMINA_IDLE_TIME) * MAX_STAMINA)

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                           self.pos.y - self.size//2,
                           self.size, self.size)

    def draw(self, surface, offset, flashlight_radius):
        rect = self.get_rect().move(-offset.x, -offset.y)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)
        if self.flashlight:
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

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def update(self, player_pos, obstacles):
        old_pos = self.pos.copy()
        direction = player_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
        for obs in obstacles:
            if self.get_rect().colliderect(obs.get_rect()):
                self.pos = old_pos
                break

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                           self.pos.y - self.size//2,
                           self.size, self.size)

    def draw(self, surface, offset, level):
        rect = self.get_rect().move(-offset.x, -offset.y)
        color = RED if level == 3 else BLACK
        pygame.draw.rect(surface, color, rect)

class SpecialZombie(Zombie):
    def __init__(self, spawn_pos, speed_multiplier=1.0, immobile_duration=3000, harmful=True, flicker=False):
        super().__init__(spawn_pos, speed_multiplier)
        self.is_special = True
        self.size = ZOMBIE_SIZE * 2
        self.speed = ZOMBIE_SPEED * speed_multiplier * 1.0
        self.spawn_time = pygame.time.get_ticks()
        self.immobile_duration = immobile_duration
        self.harmful = harmful
        self.flicker = flicker
        self.health = 200

    def update(self, player_pos, obstacles):
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time < self.immobile_duration:
            return
        super().update(player_pos, obstacles)

    def draw(self, surface, offset, level):
        rect = self.get_rect().move(-offset.x, -offset.y)
        color = SPECIAL_ZOMBIE_COLOR
        if self.flicker and (pygame.time.get_ticks() // 250) % 2 == 0:
            color = (255, 200, 0)
        pygame.draw.rect(surface, color, rect)

# Obstacle classes
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

# FireElement for levels 4 and 5
class FireElement:
    def __init__(self, pos, path, speed):
        self.pos = pygame.Vector2(pos)
        self.path = path
        self.speed = speed
        self.current_target_index = 0
        self.size = FIRE_SIZE

    def update(self):
        target = pygame.Vector2(self.path[self.current_target_index])
        direction = target - self.pos
        if direction.length() < self.speed:
            self.pos = target
            self.current_target_index = (self.current_target_index + 1) % len(self.path)
        else:
            self.pos += direction.normalize() * self.speed

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2, self.pos.y - self.size//2, self.size, self.size)

    def draw(self, surface, offset):
        pygame.draw.rect(surface, (255, 140, 0), self.get_rect().move(-offset.x, -offset.y))

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

def generate_maze_obstacles(reference_pos, fill_prob):
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
            if random.random() < fill_prob:
                r = random.random()
                if r < 0.3:
                    obstacles.append(Obstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE), destructible=True))
                elif r < 0.3 + 0.1:
                    path = [(x, y), (x + MAZE_CELL_SIZE, y)]
                    speed = 1
                    obstacles.append(DynamicObstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE), path, speed))
                else:
                    obstacles.append(Obstacle((x, y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE)))
            y += MAZE_CELL_SIZE
        x += MAZE_CELL_SIZE
    return obstacles

def reposition_maze_obstacles(obstacles, reference_pos, fill_prob):
    return generate_maze_obstacles(reference_pos, fill_prob)

def spawn_zombie(player_pos, speed_multiplier=1.0):
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(MIN_SPAWN_DIST, MIN_SPAWN_DIST + 300)
    spawn_x = player_pos.x + math.cos(angle) * distance
    spawn_y = player_pos.y + math.sin(angle) * distance
    return Zombie((spawn_x, spawn_y), speed_multiplier)

def spawn_special_zombie(player_pos, speed_multiplier=1.0, level=1):
    if level == 3:
        distance = random.uniform(0, SPECIAL_ZOMBIE_PROXIMITY_RADIUS)
        immobile_duration = 3000
        harmful = True
        flicker = False
    else:
        distance = random.uniform(0, SPECIAL_ZOMBIE_PROXIMITY_RADIUS)
        immobile_duration = SPECIAL_ZOMBIE_IMMOBILE_DURATION
        harmful = True
        flicker = False
    angle = random.uniform(0, 2 * math.pi)
    spawn_x = player_pos.x + math.cos(angle) * distance
    spawn_y = player_pos.y + math.sin(angle) * distance
    return SpecialZombie((spawn_x, spawn_y), speed_multiplier, immobile_duration, harmful, flicker)

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # Intro screen before level 1
    intro_text = font.render("ARC 1: Home Age", True, TEXT_COLOR)
    screen.fill(BLACK)
    screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, HEIGHT//2 - intro_text.get_height()//2))
    pygame.display.flip()
    pygame.time.delay(3000)

    player = Player()
    zombies = []
    bullets = []
    pickups = []
    current_fill_prob = MAZE_FILL_PROB * 0.5
    obstacles = generate_maze_obstacles(player.pos, current_fill_prob)
    fire_elements = []

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
    pygame.time.set_timer(DYNAMIC_OBSTACLE_EVENT, 2000)

    start_ticks = pygame.time.get_ticks()
    current_level = 1
    zombie_speed_multiplier = 1.0
    level_start_time = pygame.time.get_ticks()

    nightmare_transition = False
    nightmare_transition_start = None
    arc2_transition = False
    arc2_transition_start = None

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
                if current_level >= 5:
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse_pos = pygame.Vector2(mouse_pos) + pygame.Vector2(
                        player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)
                    bullet = player.shoot(world_mouse_pos, current_level)
                    if bullet:
                        bullets.append(bullet)
            if event.type == SPAWN_EVENT and not game_over:
                if current_level < 5:
                    zombies.append(spawn_zombie(player.pos, zombie_speed_multiplier))
            if event.type == DYNAMIC_OBSTACLE_EVENT:
                for obs in obstacles:
                    if isinstance(obs, DynamicObstacle):
                        obs.update()

        # LEVEL PROGRESSION LOGIC
        if not game_over:
            if current_level == 2 and elapsed_time >= LEVEL_DURATION:
                if not nightmare_transition:
                    nightmare_transition = True
                    nightmare_transition_start = current_time
                # During transition, continue updating events but draw overlay
                if current_time - nightmare_transition_start >= NIGHTMARE_TRANSITION_DELAY:
                    nightmare_transition = False
                    current_level = 3
                    zombie_speed_multiplier *= 1.05
                    current_fill_prob = MAZE_FILL_PROB
                    obstacles = reposition_maze_obstacles(obstacles, player.pos, current_fill_prob)
                    start_ticks = pygame.time.get_ticks()
                    level_start_time = pygame.time.get_ticks()
            elif current_level == 3 and elapsed_time >= NIGHTMARE_LEVEL_DURATION:
                arc2_transition = True
                arc2_transition_start = current_time
                current_level = 4
                zombie_speed_multiplier *= 1.05
                current_fill_prob = MAZE_FILL_PROB
                obstacles = reposition_maze_obstacles(obstacles, player.pos, current_fill_prob)
                fire_elements = []
                for i in range(3):
                    x = player.pos.x + random.randint(-400, 400)
                    y = player.pos.y + random.randint(-300, 300)
                    path = [(x, y), (x + 200, y)]
                    speed = 2
                    fire_elements.append(FireElement((x, y), path, speed))
                screen.fill(RED)
                transition_text = font.render("ARC 2: City Escape", True, (255, 255, 255))
                screen.blit(transition_text, (WIDTH//2 - transition_text.get_width()//2,
                                              HEIGHT//2 - transition_text.get_height()//2))
                pygame.display.flip()
                pygame.time.delay(3000)
                start_ticks = pygame.time.get_ticks()
                level_start_time = pygame.time.get_ticks()
            elif (not nightmare_transition and not arc2_transition and 
                  elapsed_time >= LEVEL_DURATION and current_level < 5):
                current_level += 1
                zombie_speed_multiplier *= 1.05
                if current_level < 3:
                    current_fill_prob = MAZE_FILL_PROB * 0.5
                else:
                    current_fill_prob = MAZE_FILL_PROB
                obstacles = reposition_maze_obstacles(obstacles, player.pos, current_fill_prob)
                start_ticks = current_time
                level_start_time = pygame.time.get_ticks()

        # Update overlay for nightmare transition (non-blocking)
        if nightmare_transition:
            overlay = font.render("Nightmare Selection", True, (255, 255, 255))
        if arc2_transition:
            overlay = font.render("ARC 2: City Escape", True, (255, 255, 255))

        # Update game elements if not in transition
        if not game_over and not nightmare_transition and not arc2_transition:
            player.update(obstacles, dt)
            player.update_invincibility()

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
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break

            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)

            for zombie in zombies:
                effective_multiplier = zombie_speed_multiplier
                if current_level == 3:
                    effective_multiplier *= 1.05
                zombie.update(player.pos, obstacles)
                if (player.pos - zombie.pos).length() < COLLISION_THRESHOLD and not player.invincible:
                    player.take_damage(10)
                    if player.health <= 0:
                        game_over = True

            if current_level >= 4:
                for fire in fire_elements:
                    fire.update()
                    if player.get_rect().colliderect(fire.get_rect()):
                        player.take_damage(FIRE_DAMAGE)

            for obs in obstacles:
                if hasattr(obs, 'update'):
                    obs.update()

            # Stamina system for levels 4 and 5 (cumulative idle time)
            if current_level >= 4:
                if player.get_stamina() >= MAX_STAMINA:
                    prompt = font.render("Press X to unleash skill!", True, TEXT_COLOR)
                    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 50))
                    if pygame.key.get_pressed()[K_x]:
                        zombies = [z for z in zombies if (z.pos - player.pos).length() > 300]
                        player.idle_timer = 0

        for bullet in bullets:
            bullet.update()

        for obs in obstacles:
            if hasattr(obs, 'update'):
                obs.update()

        offset = pygame.Vector2(player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)

        if current_level == 3:
            bg_color = BLACK
        else:
            bg_color = RED
        screen.fill(bg_color)
        draw_grid(screen, offset)
        for obs in obstacles:
            obs.draw(screen, offset)
        for pickup in pickups:
            pickup.draw(screen, offset)
        for zombie in zombies:
            zombie.draw(screen, offset, current_level)
        for bullet in bullets:
            bullet.draw(screen, offset)
        for fire in fire_elements:
            fire.draw(screen, offset)
        flash_radius = DEFAULT_FLASHLIGHT_RADIUS
        if current_level == 3:
            flash_radius = NIGHTMARE_FLASHLIGHT_RADIUS
        player.draw(screen, offset, flash_radius)

        timer_sec = (pygame.time.get_ticks() - level_start_time) / 1000
        timer_text = font.render(f"Time: {timer_sec:.1f} s", True, TEXT_COLOR)
        screen.blit(timer_text, (20, 50))
        health_bar_width = 200
        pygame.draw.rect(screen, (255,0,0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(screen, (0,255,0), (20, 20, health_bar_width * (player.health/PLAYER_MAX_HEALTH), 20))
        if current_level >= 5:
            ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
            screen.blit(ammo_text, (WIDTH - 150, 20))
        level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
        screen.blit(level_text, (WIDTH//2 - 50, 20))
        if current_level >= 4:
            stamina_bar_width = 200
            pygame.draw.rect(screen, (50, 50, 50), (20, 80, stamina_bar_width, 10))
            pygame.draw.rect(screen, (0, 0, 255), (20, 80, stamina_bar_width * (player.get_stamina()/MAX_STAMINA), 10))

        if nightmare_transition:
            overlay = font.render("Nightmare Selection", True, (255, 255, 255))
            screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - overlay.get_height()//2))
        if arc2_transition:
            overlay = font.render("ARC 2: City Escape", True, (255, 255, 255))
            screen.blit(overlay, (WIDTH//2 - overlay.get_width()//2, HEIGHT//2 - overlay.get_height()//2))

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
