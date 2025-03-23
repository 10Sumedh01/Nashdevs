import math
import random
import pygame
from pytmx import load_pygame
from constants import (
    DESTRUCTIBLE_PROB, DYNAMIC_PROB, GRID_COLOR, GRID_SPACING, HEIGHT,
    MAZE_CELL_SIZE, MAZE_FILL_PROB, MAZE_REGION_SIZE, MIN_SPAWN_DIST,
    SAFE_ZONE_MARGIN, SPECIAL_ZOMBIE_IMMOBILE_DURATION, SPECIAL_ZOMBIE_PROXIMITY_RADIUS, WIDTH
)
from Zombie import Zombie
from PoliceZombie import PoliceZombie  # Add this import

def load_map():
    """
    Load and return the Tiled map (deadvillage3.tmx).
    Ensure that deadvillage3.tmx is in your working directory.
    """
    tmx_data = load_pygame("deadvillage3.tmx")
    return tmx_data

def load_collision_rects(tmx_data):
    """
    Extract collision rectangles from the object layer named "props".
    Only objects with property 'collidable' set to true are used.
    Returns a list of pygame.Rect objects (in world coordinates).
    """
    collision_rects = []
    try:
        layer = tmx_data.get_layer_by_name("props")
    except Exception as e:
        print("Error: 'props' layer not found in map.", e)
        return collision_rects

    for obj in layer:
        prop = obj.properties.get("collidable")
        if prop in [True, "true", "True"]:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            collision_rects.append(rect)
    return collision_rects

def draw_grid(surface, offset):
    start_x = int(offset.x // GRID_SPACING * GRID_SPACING)
    start_y = int(offset.y // GRID_SPACING * GRID_SPACING)
    end_x = start_x + WIDTH + GRID_SPACING
    end_y = start_y + HEIGHT + GRID_SPACING
    for x in range(start_x, end_x, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (x - offset.x, 0), (x - offset.x, HEIGHT))
    for y in range(start_y, end_y, GRID_SPACING):
        pygame.draw.line(surface, GRID_COLOR, (0, y - offset.y), (WIDTH, y - offset.y))

def draw_map(surface, tmx_data, offset):
    """
    Draw all visible tile layers from the Tiled map, applying the camera offset.
    """
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'data'):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth - offset.x,
                                          y * tmx_data.tileheight - offset.y))

def draw_objects(surface, tmx_data, layer_name, offset):
    """
    Draw objects from a specific object layer.
    If an object has a valid gid, draw its associated tile image;
    otherwise, draw a magenta rectangle for debugging.
    """
    try:
        layer = tmx_data.get_layer_by_name(layer_name)
    except Exception as e:
        print(f"Error: Layer '{layer_name}' not found.", e)
        return

    for obj in layer:
        if hasattr(obj, 'gid') and obj.gid:
            tile = tmx_data.get_tile_image_by_gid(obj.gid)
            if tile:
                surface.blit(tile, (obj.x - offset.x, obj.y - offset.y))
            else:
                rect = pygame.Rect(obj.x - offset.x, obj.y - offset.y, obj.width, obj.height)
                pygame.draw.rect(surface, (255, 0, 255), rect, 2)
        else:
            rect = pygame.Rect(obj.x - offset.x, obj.y - offset.y, obj.width, obj.height)
            pygame.draw.rect(surface, (255, 0, 255), rect, 2)

def spawn_zombie(player_pos, speed_multiplier=1.0, tmx_data=None):
    """
    Spawn a zombie at a random location within the map boundaries.
    If tmx_data is provided, use the map dimensions.
    """
    if tmx_data:
        map_width = tmx_data.width * tmx_data.tilewidth
        map_height = tmx_data.height * tmx_data.tileheight
        spawn_x = random.uniform(0, map_width)
        spawn_y = random.uniform(0, map_height)
    else:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(MIN_SPAWN_DIST, MIN_SPAWN_DIST + 300)
        spawn_x = player_pos.x + math.cos(angle) * distance
        spawn_y = player_pos.y + math.sin(angle) * distance
    
    return Zombie((spawn_x, spawn_y), speed_multiplier)

def spawn_PoliceZombie(player_pos, speed_multiplier=1.0, tmx_data=None):
    """
    Spawn a zombie at a random location within the map boundaries.
    If tmx_data is provided, use the map dimensions.
    """
    if tmx_data:
        map_width = tmx_data.width * tmx_data.tilewidth
        map_height = tmx_data.height * tmx_data.tileheight
        spawn_x = random.uniform(0, map_width)
        spawn_y = random.uniform(0, map_height)
    else:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(MIN_SPAWN_DIST, MIN_SPAWN_DIST + 300)
        spawn_x = player_pos.x + math.cos(angle) * distance
        spawn_y = player_pos.y + math.sin(angle) * distance
    
    return PoliceZombie((spawn_x, spawn_y), speed_multiplier)

def spawn_special_zombie(player_pos, speed_multiplier=1.0, level=1, tmx_data=None):
    """
    Spawn a special zombie. For levels 6,9,10, use different parameters.
    If tmx_data is provided, use map boundaries.
    """
    if tmx_data:
        map_width = tmx_data.width * tmx_data.tilewidth
        map_height = tmx_data.height * tmx_data.tileheight
        spawn_x = random.uniform(0, map_width)
        spawn_y = random.uniform(0, map_height)
    else:
        spawn_x, spawn_y = player_pos.x, player_pos.y

    from SpecialZombie import SpecialZombie  # Ensure your SpecialZombie module is present
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