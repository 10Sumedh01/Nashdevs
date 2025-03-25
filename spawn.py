import pygame
import random
import math
from constants import PLAYER_SIZE, ZOMBIE_SIZE

def load_spawn_zones(tmx_data):
    """
    Load spawn zones from the Tiled map's "spawn" layer.
    Returns two lists: one for player spawn zones and one for zombie spawn zones.
    Each zone is a pygame.Rect.
    """
    player_zones = []
    zombie_zones = []
    try:
        spawn_layer = tmx_data.get_layer_by_name("spawn")
    except Exception as e:
        print("Error: 'spawn' layer not found in map.", e)
        return player_zones, zombie_zones

    for obj in spawn_layer:
        # For zombie spawn zones:
        if obj.properties.get("spawn_z") in [True, "true", "True"]:
            # Create a rect using the object's x, y, width, and height.
            zombie_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        # For player spawn zones:
        if obj.properties.get("spawn_p") in [True, "true", "True"]:
            player_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
    return player_zones, zombie_zones

def random_point_in_rect(rect):
    """Return a random point (pygame.Vector2) inside the given rect."""
    x = random.uniform(rect.x, rect.x + rect.width)
    y = random.uniform(rect.y, rect.y + rect.height)
    return pygame.Vector2(x, y)

def spawn_zombie(speed_multiplier=1.0, tmx_data=None,current_level=1):
    """
    Spawns a zombie from a random zombie spawn zone.
    If spawn zones are not available, falls back to a random position.
    """
    pos = None
    if tmx_data:
        _, zombie_zones = load_spawn_zones(tmx_data)
        if zombie_zones:
            zone = random.choice(zombie_zones)
            pos = random_point_in_rect(zone)
    if pos is None:
        # Fallback: choose a random position relative to (0,0) (or adjust as needed)
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(500, 800)
        pos = pygame.Vector2(math.cos(angle) * distance, math.sin(angle) * distance)

    from Zombie import Zombie
    from PoliceZombie import PoliceZombie
    from ArmyZombie import ArmyZombie
    # rand_value = random.random()
    # if rand_value < 1/3:
    #     return Zombie(pos, speed_multiplier)
    # elif rand_value < 2/3:
    #     from PoliceZombie import PoliceZombie
    #     return PoliceZombie(pos, speed_multiplier)
    # else:
    #     from ArmyZombie import ArmyZombie
    #     return ArmyZombie(pos, speed_multiplier)
    
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

def find_player_spawn(tmx_data):
    """
    Finds a spawn position for the player from the spawn_p zones.
    Falls back to (0,0) if none are found.
    """
    player_zones, _ = load_spawn_zones(tmx_data)
    if player_zones:
        zone = random.choice(player_zones)
        return random_point_in_rect(zone)
    return pygame.Vector2(0, 0)
