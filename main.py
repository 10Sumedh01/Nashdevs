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
from spawn import find_safe_spawn, find_safe_spawn_zombie, spawn_zombie
from minimap import draw_minimap
from checkpoint import load_checkpoints, draw_checkpoints

DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2  # Not used in this version

# -----------------------------
# Main game loop
# -----------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Dead Village")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    # Load the Tiled map, collision objects, and checkpoints.
    tmx_data = load_map()
    collision_rects = load_collision_rects(tmx_data)
    checkpoints = load_checkpoints(tmx_data)
    print("Collision Rects:", collision_rects)  # Debug output

    # Spawn the player safely.
    safe_pos = find_safe_spawn(collision_rects, tmx_data)
    player = Player()
    player.pos = safe_pos

    companion = Companion(player.pos + pygame.Vector2(60, 0), "gun")
    show_companion = False

    # Initialize level and map managers.
    level_manager = LevelManager()
    current_level = level_manager.current_level
    # Obstacles are taken from the Tiled map (collision objects).
    obstacles = collision_rects
    map_manager = MapManager(obstacles, player.pos)

    zombies = []
    bullets = []
    pickups = []
    kill_count = 0

    # Checkpoint logic variables.
    checkpoint_active = False
    active_checkpoint = None
    KILL_THRESHOLD = 30  # When kill count reaches 30, activate checkpoint.

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)

    game_over = False
    level_complete = False  # Flag for level completion overlay.

    while True:
        dt = clock.tick(FPS) / 1000.0  # Delta time (seconds)
        current_time = pygame.time.get_ticks()

        # Camera offset: center on the player.
        offset = pygame.Vector2(player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_pos = pygame.Vector2(mouse_pos) + offset

        # Process events.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_e:
                    player.toggle_knife()
                if event.key == K_c:
                    show_companion = not show_companion
                # When level complete overlay is active, choose next level or quit.
                if level_complete:
                    if event.key == K_n:
                        level_manager.current_level += 1
                        current_level = level_manager.current_level
                        kill_count = 0
                        checkpoint_active = False
                        active_checkpoint = None
                        level_complete = False
                    if event.key == K_q:
                        pygame.quit()
                        sys.exit()
            if not level_complete and not game_over:
                if event.type == MOUSEBUTTONDOWN:
                    # Left-click: shoot if not in knife mode.
                    if event.button == 1 and not player.has_knife:
                        bullet = player.shoot(world_mouse_pos)
                        if bullet:
                            bullets.append(bullet)
                    # Right-click: if in knife mode, perform knife attack.
                    elif event.button == 3 and player.has_knife:
                        player.use_knife()  # Trigger knife attack animation.
                        attacked_zombies = player.knife_attack(zombies)
                        for z in attacked_zombies:
                            if z in zombies:
                                # Each knife hit does 50 damage; two blows kill a zombie.
                                if z.take_damage(50, None):
                                    zombies.remove(z)
                                    kill_count += 1
                if event.type == SPAWN_EVENT and not game_over and not level_complete:
                    # Only spawn zombies if checkpoint is not active.
                    if not checkpoint_active:
                        zombies.append(spawn_zombie(player.pos, 1.0, tmx_data, collision_rects))
                        zombies.append(spawn_zombie(player.pos, 1.0, tmx_data, collision_rects))

        if not game_over and not level_complete:
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
                                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                                pickups.append(Pickup(zombie.pos.copy(), pickup_type))
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
            new_zombies = []
            for zombie in zombies[:]:
                if zombie.is_special:
                    zombie.update(player.pos, collision_rects, None)
                    if (zombie.pos - player.pos).length() <= 150:
                        num_explode = 8
                        offset_distance = 30
                        for i in range(num_explode):
                            angle = math.radians(i * (360 / num_explode))
                            spawn_offset = pygame.Vector2(math.cos(angle) * offset_distance,
                                                          math.sin(angle) * offset_distance)
                            new_zombies.append(spawn_zombie(player.pos, 1.0, tmx_data, collision_rects))
                            kill_count += 1
                        zombies.remove(zombie)
                        continue
                else:
                    zombie.update(player.pos, collision_rects, None)
                if player.get_rect().colliderect(zombie.get_rect()):
                    player.take_damage(10)
            zombies.extend(new_zombies)

            if player.health <= 0:
                game_over = True

            # Activate checkpoint when kill count reaches threshold.
            if kill_count >= 30 and not checkpoint_active and len(checkpoints) > 0:
                checkpoint_active = True
                active_checkpoint = checkpoints[0]

            # When checkpoint is active, if player collides with it, show level complete overlay.
            if checkpoint_active and active_checkpoint:
                if player.get_rect().colliderect(active_checkpoint["rect"]):
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    screen.blit(overlay, (0, 0))
                    complete_text = large_font.render("LEVEL COMPLETE", True, TEXT_COLOR)
                    screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 100))
                    next_text = font.render("Press N for Next Level", True, TEXT_COLOR)
                    quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
                    screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2))
                    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 30))
                    pygame.display.flip()
                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == QUIT:
                                pygame.quit()
                                sys.exit()
                        keys = pygame.key.get_pressed()
                        if keys[K_n]:
                            level_manager.current_level += 1
                            current_level = level_manager.current_level
                            kill_count = 0
                            checkpoint_active = False
                            active_checkpoint = None
                            waiting = False
                        if keys[K_q]:
                            pygame.quit()
                            sys.exit()

        screen.fill(DARK_RED)
        draw_map(screen, tmx_data, offset)
        draw_objects(screen, tmx_data, "props", offset)
        if checkpoint_active and active_checkpoint:
            if active_checkpoint["image"]:
                cp_rect = active_checkpoint["rect"].move(-offset.x, -offset.y)
                screen.blit(active_checkpoint["image"], cp_rect)
            else:
                pygame.draw.rect(screen, (255, 255, 0), active_checkpoint["rect"].move(-offset.x, -offset.y), 2)

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
        pygame.draw.rect(screen, (0, 255, 0),
                         (20, 20, health_bar_width * (player.health / PLAYER_MAX_HEALTH), 20))
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
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
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
