import pygame
import random
import math
from constants import PLAYER_SIZE, ZOMBIE_SIZE

# Global flag to track boss spawn
boss_spawned = False

def load_spawn_zones(tmx_data):
    """
    Load spawn zones from the Tiled map's "spawn" layer.
    Returns two lists: one for player spawn zones and one for spawn zones.
    Each zone is a pygame.Rect.
    """
    player_zones = []
    spawn_zones = []
    boss_zones = []  # New list to specifically track boss spawn zones
    try:
        spawn_layer = tmx_data.get_layer_by_name("spawn")
    except Exception as e:
        print("Error: 'spawn' layer not found in map.", e)
        return player_zones, spawn_zones, boss_zones

    for obj in spawn_layer:
        # For human/zombie spawn zones:
        if obj.properties.get("spawn_z") in [True, "true", "True"]:
            spawn_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        if obj.properties.get("spawn_h") in [True, "true", "True"]:
            spawn_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        if obj.properties.get("spawn_b") in [True, "true", "True"]:
            boss_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))  # Specifically track boss zones
        # For player spawn zones:
        if obj.properties.get("spawn_p") in [True, "true", "True"]:
            player_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    return player_zones, spawn_zones, boss_zones

def random_point_in_rect(rect):
    """Return a random point (pygame.Vector2) inside the given rect."""
    x = random.uniform(rect.x, rect.x + rect.width)
    y = random.uniform(rect.y, rect.y + rect.height)
    return pygame.Vector2(x, y)

def spawn_enemy(speed_multiplier=1.0, tmx_data=None, current_level=1):
    """
    Spawns an enemy (zombie or human) based on the current level.
    Specifically uses spawn_b zones for boss spawning.
    """
    global boss_spawned
    pos = None
    if tmx_data:
        _, spawn_zones, boss_zones = load_spawn_zones(tmx_data)
        
        # Boss spawns only ONCE, specifically in boss zones on level 7
        if current_level == 7 and not boss_spawned and boss_zones:
            zone = random.choice(boss_zones)
            pos = random_point_in_rect(zone)
            boss_spawned = True  # Set flag to prevent future spawns
            
            from BossZombie import BossZombie
            return BossZombie(pos, speed_multiplier)
        
        # Use existing spawn zones for other enemies if no specific zone found
        if spawn_zones:
            zone = random.choice(spawn_zones)
            pos = random_point_in_rect(zone)
    
    if pos is None:
        # Fallback: choose a random position relative to (0,0)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(500, 800)
        pos = pygame.Vector2(math.cos(angle) * distance, math.sin(angle) * distance)

    from Zombie import Zombie
    from PoliceZombie import PoliceZombie
    from ArmyZombie import ArmyZombie
    from human import Human
    
    # Specifically for level 4, spawn only humans
    if current_level == 4:
        return Human(pos, speed_multiplier)
    
    # For other levels, use existing zombie spawning logic
    if current_level < 2:
        return Zombie(pos, speed_multiplier)
    else:
        rand_value = random.random()
        if rand_value < 1/3:
            return Zombie(pos, speed_multiplier)
        elif rand_value < 2/3:
            return PoliceZombie(pos, speed_multiplier)
        else:
            return ArmyZombie(pos, speed_multiplier)

def spawn_all_enemies_equally(speed_multiplier=1.0, tmx_data=None):
    """
    Spawns all enemy types with equal probability including bosses.
    """
    # Get a spawn position
    pos = None
    if tmx_data:
        _, spawn_zones, _ = load_spawn_zones(tmx_data)
        if spawn_zones:
            zone = random.choice(spawn_zones)
            pos = random_point_in_rect(zone)
    
    if pos is None:
        # Fallback: random position
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(500, 800)
        pos = pygame.Vector2(math.cos(angle) * distance, math.sin(angle) * distance)

    # Import all enemy types
    from Zombie import Zombie
    from PoliceZombie import PoliceZombie
    from ArmyZombie import ArmyZombie
    from BossZombie import BossZombie
    from human import Human
    
    # Define all enemy types with equal probability
    enemy_types = [Zombie, PoliceZombie, ArmyZombie, BossZombie, Human]
    
    # Choose a random enemy type
    EnemyClass = random.choice(enemy_types)
    
    # Return the new enemy instance
    return EnemyClass(pos, speed_multiplier)

def find_player_spawn(tmx_data):
    """
    Finds a spawn position for the player from the spawn_p zones.
    Falls back to (0,0) if none are found.
    """
    player_zones, _, _ = load_spawn_zones(tmx_data)
    if player_zones:
        zone = random.choice(player_zones)
        return random_point_in_rect(zone)
    return pygame.Vector2(0, 0)