# checkpoint.py
import pygame

def load_checkpoints(tmx_data):
    """
    Load checkpoint objects from the "checkpoints" layer in the Tiled map.
    Each checkpoint is stored as a dict with a "rect" key and optionally an "image" key.
    """
    checkpoints = []
    try:
        layer = tmx_data.get_layer_by_name("checkpoints")
    except Exception as e:
        print("Error: 'checkpoints' layer not found in map.", e)
        return checkpoints

    for obj in layer:
        if obj.properties.get("checkpoint") in [True, "true", "True"]:
            cp = {"rect": pygame.Rect(obj.x, obj.y, obj.width, obj.height), "image": None}
            if hasattr(obj, "gid") and obj.gid:
                tile = tmx_data.get_tile_image_by_gid(obj.gid)
                if tile:
                    cp["image"] = tile
            checkpoints.append(cp)
    return checkpoints

def draw_checkpoints(surface, checkpoints, offset):
    """Draw checkpoint objects on the screen."""
    for cp in checkpoints:
        rect = cp["rect"].move(-offset.x, -offset.y)
        if cp["image"]:
            surface.blit(cp["image"], rect)
        else:
            pygame.draw.rect(surface, (255, 255, 0), rect, 2)
