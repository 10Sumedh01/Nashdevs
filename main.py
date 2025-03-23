import pygame
import sys
import random
import math
from pygame.locals import *
from constants import (WIDTH, HEIGHT, FPS, SPAWN_INTERVAL, COLLISION_THRESHOLD, 
                       TEXT_COLOR, DARK_RED, PLAYER_MAX_HEALTH, PLAYER_SIZE, 
                       BULLET_RANGE, HEALTH_PACK_AMOUNT, AMMO_PACK_AMOUNT, ZOMBIE_SIZE)
from Player import Player
from Pickup import Pickup
from utilityFunctions import load_map, load_collision_rects, draw_map, draw_objects, spawn_zombie, spawn_special_zombie
from levelManager import LevelManager
from Companion import Companion
from MapManager import MapManager

DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2  # Not used in this version

def find_safe_spawn(collision_rects, tmx_data):
    """Find a safe spawn position for the player (avoiding collision rectangles)."""
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    while True:
        pos = pygame.Vector2(random.uniform(0, map_width), random.uniform(0, map_height))
        spawn_rect = pygame.Rect(pos.x - PLAYER_SIZE/2, pos.y - PLAYER_SIZE/2, PLAYER_SIZE, PLAYER_SIZE)
        if not any(spawn_rect.colliderect(rect) for rect in collision_rects):
            return pos

def find_safe_spawn_zombie(collision_rects, tmx_data):
    """Find a safe spawn position for a zombie (avoiding collision rectangles)."""
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    while True:
        pos = pygame.Vector2(random.uniform(0, map_width), random.uniform(0, map_height))
        spawn_rect = pygame.Rect(pos.x - ZOMBIE_SIZE/2, pos.y - ZOMBIE_SIZE/2, ZOMBIE_SIZE, ZOMBIE_SIZE)
        if not any(spawn_rect.colliderect(rect) for rect in collision_rects):
            return pos

def spawn_zombie_wrapper(player_pos, speed_multiplier=1.0, tmx_data=None, collision_rects=None):
    """
    Spawns a zombie using safe spawn logic if possible.
    In initial levels, spawns fewer zombies.
    """
    from Zombie import Zombie
    if tmx_data and collision_rects:
        pos = find_safe_spawn_zombie(collision_rects, tmx_data)
    else:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(500, 800)
        pos = pygame.Vector2(player_pos.x + math.cos(angle) * distance,
                             player_pos.y + math.sin(angle) * distance)
    return Zombie(pos, speed_multiplier)

def draw_minimap(surface, tmx_data, collision_rects, player, zombies, companion):
    """
    Draws a minimap at the top-right corner of the screen.
    It scales the full map dimensions from the Tiled map and draws:
      - Obstacles as gray rectangles,
      - The player as a green circle,
      - Zombies as red circles,
      - The companion (if available) as a blue circle.
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Dead Village")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    tmx_data = load_map()
    collision_rects = load_collision_rects(tmx_data)
    print("Collision Rects:", collision_rects)
    
    safe_pos = find_safe_spawn(collision_rects, tmx_data)
    player = Player()
    player.pos = safe_pos

    companion = Companion(player.pos + pygame.Vector2(60, 0), "gun")
    show_companion = False

    level_manager = LevelManager()
    current_level = level_manager.current_level
    obstacles = collision_rects
    map_manager = MapManager(obstacles, player.pos)

    zombies = []
    bullets = []
    pickups = []
    kill_count = 0

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)

    game_over = False
    while True:
        dt = clock.tick(FPS) / 1000.0
        offset = pygame.Vector2(player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_pos = pygame.Vector2(mouse_pos) + offset

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_e:
                    player.toggle_knife()
                if event.key == K_c:
                    show_companion = not show_companion
            if event.type == MOUSEBUTTONDOWN and not game_over:
                if event.button == 1 and not player.has_knife:
                    bullet = player.shoot(world_mouse_pos)
                    if bullet:
                        bullets.append(bullet)
                elif event.button == 3 and player.has_knife:
                    player.use_knife()
                    attacked_zombies = player.knife_attack(zombies)
                    for z in attacked_zombies:
                        if z in zombies:
                            if z.take_damage(50, None):  # Each knife blow does 50 damage
                                zombies.remove(z)
                                kill_count += 1
                                if random.random() < 0.3:
                                    pickups.append(Pickup(z.pos.copy(), random.choice(["health", "ammo"])))
            if event.type == SPAWN_EVENT and not game_over:
                # In initial level(s), spawn fewer zombies
                if current_level <= 1:
                    if len(zombies) < 5:
                        zombies.append(spawn_zombie_wrapper(player.pos, 1.0, tmx_data, collision_rects))
                else:
                    zombies.append(spawn_zombie_wrapper(player.pos, 1.0, tmx_data, collision_rects))
                    zombies.append(spawn_zombie_wrapper(player.pos, 1.0, tmx_data, collision_rects))

        if not game_over:
            player.update_rotation(world_mouse_pos)
            player.update(collision_rects)
            player.update_invincibility()

            for bullet in bullets[:]:
                bullet.update()
                if bullet.distance_traveled > BULLET_RANGE:
                    bullets.remove(bullet)
                    continue
                for zombie in zombies[:]:
                    if (bullet.pos - zombie.pos).length() < zombie.size:
                        if zombie.take_damage(50, None):
                            zombies.remove(zombie)
                            kill_count += 1
                            if random.random() < 0.3:
                                pickups.append(Pickup(zombie.pos.copy(), random.choice(["health", "ammo"])))
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break

            if show_companion:
                companion.update(player, zombies, obstacles)
                for bullet in companion.bullets[:]:
                    bullet.update()
                    if bullet.distance_traveled > bullet.max_distance:
                        companion.bullets.remove(bullet)
                        continue
                    for zombie in zombies[:]:
                        if (bullet.pos - zombie.pos).length() < zombie.size:
                            if zombie.take_damage(50, None):
                                zombies.remove(zombie)
                                kill_count += 1
                                if random.random() < 0.3:
                                    pickups.append(Pickup(zombie.pos.copy(), random.choice(["health", "ammo"])))
                            if bullet in companion.bullets:
                                companion.bullets.remove(bullet)
                            break

            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == "health":
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)

            for zombie in zombies[:]:
                zombie.update(player.pos, obstacles, map_manager)
                if player.get_rect().colliderect(zombie.get_rect()):
                    player.take_damage(10)
            if player.health <= 0:
                game_over = True
            if level_manager.update_level():
                current_level = level_manager.current_level

        screen.fill(DARK_RED)
        draw_map(screen, tmx_data, offset)
        draw_objects(screen, tmx_data, "props", offset)
        for bullet in bullets:
            bullet.draw(screen, offset)
        for pickup in pickups:
            pickup.draw(screen, offset)
        for zombie in zombies:
            zombie.draw(screen, offset)
        if show_companion:
            companion.draw(screen, offset)
        player.draw(screen, offset, current_level)

        health_bar_width = 200
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, health_bar_width * (player.health / PLAYER_MAX_HEALTH), 20))
        ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
        screen.blit(ammo_text, (20, 45))
        level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
        screen.blit(level_text, (WIDTH // 2 - 50, 20))
        kill_text = font.render(f'KILLS: {kill_count}', True, TEXT_COLOR)
        screen.blit(kill_text, (20, 70))
        level_manager.draw_level_intro(screen, large_font)
        draw_minimap(screen, tmx_data, collision_rects, player, zombies, companion if show_companion else None)
        pygame.display.flip()

        if game_over:
            game_over_text = large_font.render("GAME OVER - Press R to Restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                keys = pygame.key.get_pressed()
                if keys[K_r]:
                    main()
                    return
                clock.tick(FPS)

if __name__ == "__main__":
    main()
