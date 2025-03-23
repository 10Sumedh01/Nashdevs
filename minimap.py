# minimap.py
import pygame
from constants import WIDTH, HEIGHT

def draw_minimap(surface, tmx_data, collision_rects, player, zombies, companion):
    """
    Draws a minimap at the top-right corner of the screen.
    It scales the full map dimensions from the Tiled map and draws:
      - Obstacles (from collision_rects) as gray rectangles,
      - The player as a green circle,
      - Zombies as red circles,
      - The companion as a blue circle if available,
      - Checkpoints as yellow rectangles.
    """
    minimap_width = 200
    minimap_height = 200
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((50, 50, 50))
    
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale_x = minimap_width / map_width
    scale_y = minimap_height / map_height

    for rect in collision_rects:
        mini_rect = pygame.Rect(rect.x * scale_x, rect.y * scale_y, rect.width * scale_x, rect.height * scale_y)
        pygame.draw.rect(minimap_surface, (100, 100, 100), mini_rect)
    
    mini_player = (int(player.pos.x * scale_x), int(player.pos.y * scale_y))
    pygame.draw.circle(minimap_surface, (0, 255, 0), mini_player, 5)
    
    for zombie in zombies:
        mini_zombie = (int(zombie.pos.x * scale_x), int(zombie.pos.y * scale_y))
        pygame.draw.circle(minimap_surface, (255, 0, 0), mini_zombie, 5)
    
    if companion is not None:
        mini_comp = (int(companion.pos.x * scale_x), int(companion.pos.y * scale_y))
        pygame.draw.circle(minimap_surface, (0, 0, 255), mini_comp, 5)

    surface.blit(minimap_surface, (WIDTH - minimap_width - 10, 10))