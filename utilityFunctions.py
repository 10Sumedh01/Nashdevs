# utilityFunctions.py
import math
import random
import pygame
from DynamicObstacle import DynamicObstacle
from Obstacle import Obstacle
from SpecialZombie import SpecialZombie
from Zombie import Zombie
from constants import DESTRUCTIBLE_PROB, DYNAMIC_PROB, GRID_COLOR, GRID_SPACING, HEIGHT, MAZE_CELL_SIZE, MAZE_FILL_PROB, MAZE_REGION_SIZE, MIN_SPAWN_DIST, SAFE_ZONE_MARGIN, SPECIAL_ZOMBIE_IMMOBILE_DURATION, SPECIAL_ZOMBIE_PROXIMITY_RADIUS, WIDTH

def draw_grid(surface, offset):
    start_x = int(offset.x // GRID_SPACING * GRID_SPACING)
    start_y = int(offset.y // GRID_SPACING * GRID_SPACING)
    end_x = start_x + WIDTH + GRID_SPACING
    end_y = start_y + HEIGHT + GRID_SPACING
    for x in range(start_x, end_x, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (x - offset.x, 0), (x - offset.x, HEIGHT))
    for y in range(start_y, end_y, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (0, y - offset.y), (WIDTH, y - offset.y))

def generate_maze_obstacles(reference_pos, level=1):
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
    # For levels 4 & 5, add moving fire obstacles that drain life.
    if level in [4, 5]:
        for i in range(3):
            fire_x = random.randint(start_x, end_x - MAZE_CELL_SIZE)
            fire_y = random.randint(start_y, end_y - MAZE_CELL_SIZE)
            fire = DynamicObstacle((fire_x, fire_y), (MAZE_CELL_SIZE, MAZE_CELL_SIZE), [(fire_x, fire_y), (fire_x + MAZE_CELL_SIZE, fire_y)], speed=2)
            fire.is_fire = True  # Mark as fire obstacle.
            obstacles.append(fire)
    return obstacles

def reposition_maze_obstacles(obstacles, reference_pos, level=1):
    return generate_maze_obstacles(reference_pos, level)

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
