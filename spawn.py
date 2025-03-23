import pygame
import random
import math
from constants import PLAYER_SIZE, ZOMBIE_SIZE

def find_safe_spawn(collision_rects, tmx_data):
    """
    Find a safe spawn position for the player (avoiding collision rectangles).
    """
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    while True:
        pos = pygame.Vector2(random.uniform(0, map_width), random.uniform(0, map_height))
        spawn_rect = pygame.Rect(pos.x - PLAYER_SIZE/2, pos.y - PLAYER_SIZE/2, PLAYER_SIZE, PLAYER_SIZE)
        if not any(spawn_rect.colliderect(rect) for rect in collision_rects):
            return pos

def find_safe_spawn_zombie(collision_rects, tmx_data):
    """
    Find a safe spawn position for a zombie (avoiding collision rectangles).
    """
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    while True:
        pos = pygame.Vector2(random.uniform(0, map_width), random.uniform(0, map_height))
        spawn_rect = pygame.Rect(pos.x - ZOMBIE_SIZE/2, pos.y - ZOMBIE_SIZE/2, ZOMBIE_SIZE, ZOMBIE_SIZE)
        if not any(spawn_rect.colliderect(rect) for rect in collision_rects):
            return pos

def spawn_zombie(player_pos, speed_multiplier=1.0, tmx_data=None, collision_rects=None):
    """
    Spawns a zombie using safe spawn logic if possible.
    If tmx_data and collision_rects are provided, uses find_safe_spawn_zombie.
    Otherwise, spawns relative to the player's position.
    """
    if tmx_data is not None and collision_rects is not None:
        pos = find_safe_spawn_zombie(collision_rects, tmx_data)
    else:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(500, 800)
        pos = pygame.Vector2(player_pos.x + math.cos(angle) * distance,
                             player_pos.y + math.sin(angle) * distance)
    from Zombie import Zombie  # Lazy import
    # Example: Randomly spawn one of three types of zombies.
    rand_value = random.random()
    if rand_value < 1/3:
        return Zombie(pos, speed_multiplier)
    elif rand_value < 2/3:
        from PoliceZombie import PoliceZombie
        return PoliceZombie(pos, speed_multiplier)
    else:
        from ArmyZombie import ArmyZombie
        return ArmyZombie(pos, speed_multiplier)
