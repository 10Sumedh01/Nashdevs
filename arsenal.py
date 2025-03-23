# arsenal.py
import pygame
from constants import PISTOL_IMAGE_PATH, SHOTGUN_IMAGE_PATH, AKM_IMAGE_PATH

def draw_arsenal(surface, player):
    # Define the rectangle dimensions and position for the arsenal display.
    arsenal_rect = pygame.Rect(20, 100, 100, 100)
    pygame.draw.rect(surface, (50, 50, 50), arsenal_rect)
    
    # Determine which weapon image to load based on player's current gun mode.
    if player.gun_mode == 'pistol':
        img = pygame.image.load(PISTOL_IMAGE_PATH).convert_alpha()
    elif player.gun_mode == 'shotgun':
        img = pygame.image.load(SHOTGUN_IMAGE_PATH).convert_alpha()
    elif player.gun_mode == 'akm':
        img = pygame.image.load(AKM_IMAGE_PATH).convert_alpha()
    else:
        img = pygame.image.load(PISTOL_IMAGE_PATH).convert_alpha()
    
    # Scale the image to fit inside the arsenal rectangle.
    img = pygame.transform.scale(img, (arsenal_rect.width, arsenal_rect.height))
    surface.blit(img, (arsenal_rect.x, arsenal_rect.y))
