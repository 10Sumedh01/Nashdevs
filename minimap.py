import pygame
from constants import WIDTH, HEIGHT

def draw_minimap(surface, tmx_data, collision_rects, player, zombies, companion, checkpoint=None):
    """
    Draws a minimap at the top-right corner of the screen.
    It scales the full map dimensions from the Tiled map and draws:
      - Obstacles (from collision_rects) as gray rectangles,
      - The player as a green circle,
      - Zombies as red circles,
      - The companion as a blue circle if available,
      - If a checkpoint is active, draws it as a yellow rectangle.
    """
    minimap_width = 200
    minimap_height = 200
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((50, 50, 50))
    
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    scale_x = minimap_width / map_width
    scale_y = minimap_height / map_height

    # Draw obstacles.
    for rect in collision_rects:
        mini_rect = pygame.Rect(rect.x * scale_x, rect.y * scale_y, rect.width * scale_x, rect.height * scale_y)
        pygame.draw.rect(minimap_surface, (100, 100, 100), mini_rect)
    
    # Draw player.
    mini_player = (int(player.pos.x * scale_x), int(player.pos.y * scale_y))
    pygame.draw.circle(minimap_surface, (0, 255, 0), mini_player, 5)
    
    # Draw zombies.
    for zombie in zombies:
        mini_zombie = (int(zombie.pos.x * scale_x), int(zombie.pos.y * scale_y))
        pygame.draw.circle(minimap_surface, (255, 0, 0), mini_zombie, 5)
    
    # Draw companion.
    if companion is not None:
        mini_comp = (int(companion.pos.x * scale_x), int(companion.pos.y * scale_y))
        pygame.draw.circle(minimap_surface, (0, 0, 255), mini_comp, 5)
    
    # Draw checkpoint if active.
    if checkpoint is not None:
        cp_rect = checkpoint["rect"]
        mini_cp = pygame.Rect(cp_rect.x * scale_x, cp_rect.y * scale_y, cp_rect.width * scale_x, cp_rect.height * scale_y)
        pygame.draw.rect(minimap_surface, (255, 255, 0), mini_cp, 2)
    
    surface.blit(minimap_surface, (WIDTH - minimap_width - 10, 10))
