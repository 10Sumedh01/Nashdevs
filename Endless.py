import pygame
import sys
import random
import math
from pygame.locals import *
from constants import (WIDTH, HEIGHT, FPS, SPAWN_INTERVAL, COLLISION_THRESHOLD,
                       TEXT_COLOR, DARK_RED, PLAYER_MAX_HEALTH, PLAYER_SIZE,
                       BULLET_RANGE, HEALTH_PACK_AMOUNT, AMMO_PACK_AMOUNT, ZOMBIE_SIZE,
                       BASE_ZOMBIE_SPEED, BASE_ZOMBIE_SIZE)
from Player import Player
from Pickup import Pickup
from utilityFunctions import load_map, load_collision_rects, draw_map, draw_objects, spawn_special_zombie
from Companion import Companion
from MapManager import MapManager
from minimap import draw_minimap
from spawn import spawn_all_enemies_equally, find_player_spawn
from arsenal import draw_arsenal
from BossZombie import BossZombie
from sound import Sound
from pause import pause

# Sound effects
bg_music = Sound('game_bg.mp3')
pickup_sound = Sound('pickup.mp3')

def endless_mode():
    """
    Endless mode where player fights increasingly difficult waves of zombies
    until they die. Difficulty increases over time with more and faster zombies.
    """
    # Initialize pygame and display
    bg_music.play_loop()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Endless Mode")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    # Load map and initialize game objects
    tmx_data = load_map("deadvillage3.tmx")  # Using the first map for endless mode
    collision_rects = load_collision_rects(tmx_data)
    
    # Initialize player
    safe_pos = find_player_spawn(tmx_data)
    player = Player(safe_pos)
    player.ammo = 50  # Starting with more ammo in endless mode
    
    # Load blood splatter effect
    dead_sprite = pygame.image.load('assets/Dead_img.png').convert_alpha()
    
    # Initialize companion
    companion = Companion(player.pos + pygame.Vector2(60, 0), "gun")
    global show_companion
    show_companion = False
    
    # Initialize map manager
    obstacles = collision_rects
    map_manager = MapManager(obstacles, player.pos)
    
    # Game object lists and counters
    zombies = []
    bullets = []
    pickups = []
    dead_zombies = []
    puddles = []
    total_kill_count = 0
    
    # Game difficulty variables
    spawn_rate = SPAWN_INTERVAL  # Starting spawn rate
    zombie_speed_multiplier = 1.0  # Starting speed multiplier
    zombie_spawn_count = 2  # Starting number of zombies per spawn
    wave_number = 1  # Starting wave
    wave_kill_threshold = 10  # Kills needed to advance to next wave
    wave_kills = 0  # Current wave kill counter
    
    # Create timer events
    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, spawn_rate)
    
    DIFFICULTY_INCREASE_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(DIFFICULTY_INCREASE_EVENT, 30000)  # Increase difficulty every 30 seconds
    
    running = True
    game_over = False
    spawn_zombies = True
    start_time = pygame.time.get_ticks()
    
    # Main game loop
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks()
        survival_time = (current_time - start_time) // 1000  # Time in seconds
        
        # Process events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause game
                    pause(screen)
                if event.key == pygame.K_q and game_over:  # Quit when game over
                    return
                if event.key == pygame.K_r and game_over:  # Restart when game over
                    endless_mode()
                    return
                if event.key == K_e:  # Toggle knife
                    player.toggle_knife()
                if event.key == K_o:  # Switch gun
                    player.switch_gun()
                if event.key == K_c:  # Toggle companion
                    show_companion = not show_companion
            
            # Combat events
            if not game_over:
                offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = pygame.Vector2(mouse_pos) + offset
                
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left-click to shoot
                        result = player.shoot(world_mouse_pos)
                        if result:
                            if isinstance(result, list):
                                bullets.extend(result)
                            else:
                                bullets.append(result)
                    elif event.button == 3 and player.has_knife:  # Right-click knife attack
                        player.use_knife()
                        attacked = player.knife_attack(zombies)
                        for z in attacked:
                            if z in zombies:
                                if z.take_damage(999, None):  # Instant kill via knife
                                    zombies.remove(z)
                                    dead_zombies.append((z.pos.copy(), pygame.time.get_ticks()))
                                    total_kill_count += 1
                                    wave_kills += 1
                
                # Enemy spawning
                if event.type == SPAWN_EVENT and spawn_zombies:
                    new_enemies = [spawn_all_enemies_equally(zombie_speed_multiplier, tmx_data) 
                                for _ in range(zombie_spawn_count)]
                    zombies.extend(new_enemies)
                
                # Increase difficulty over time
                if event.type == DIFFICULTY_INCREASE_EVENT:
                    zombie_speed_multiplier += 0.1
                    spawn_rate = max(500, spawn_rate - 200)  # Speed up spawn rate
                    pygame.time.set_timer(SPAWN_EVENT, spawn_rate)
        
        # Check if wave is complete
        if wave_kills >= wave_kill_threshold:
            wave_number += 1
            wave_kills = 0
            wave_kill_threshold = int(wave_kill_threshold * 1.5)  # Increase kills needed for next wave
            zombie_spawn_count = min(10, zombie_spawn_count + 1)  # Increase zombies per spawn
            
            # Drop some pickups when completing a wave
            for _ in range(3):
                pickup_pos = pygame.Vector2(
                    player.pos.x + random.randint(-200, 200),
                    player.pos.y + random.randint(-200, 200)
                )
                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                pickups.append(Pickup(pickup_pos, pickup_type))
        
        if not game_over:
            # Update player
            offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = pygame.Vector2(mouse_pos) + offset
            player.update_rotation(world_mouse_pos)
            player.update(collision_rects)
            player.update_invincibility()
            
            # Update bullets and check for collisions
            for bullet in bullets[:]:
                bullet.update()
                if bullet.distance_traveled > BULLET_RANGE:
                    bullets.remove(bullet)
                    continue
                for enemy in zombies[:]:
                    if (bullet.pos - enemy.pos).length() < enemy.size:
                        if enemy.take_damage(50, None):
                            dead_zombies.append((enemy.pos.copy(), pygame.time.get_ticks()))
                            zombies.remove(enemy)
                            total_kill_count += 1
                            wave_kills += 1
                            # 30% chance to spawn a pickup
                            if random.random() < 0.3:
                                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                                pickups.append(Pickup(enemy.pos.copy(), pickup_type))
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
            
            # Update companion if visible
            if show_companion:
                companion.update(player, zombies, obstacles)
                for bullet in companion.bullets[:]:
                    bullet.update()
                    if bullet.distance_traveled > bullet.max_distance:
                        companion.bullets.remove(bullet)
                        continue
                    for enemy in zombies[:]:
                        if (bullet.pos - enemy.pos).length() < enemy.size:
                            if enemy.take_damage(50, None):
                                dead_zombies.append((enemy.pos.copy(), pygame.time.get_ticks()))
                                zombies.remove(enemy)
                                total_kill_count += 1
                                wave_kills += 1
                                if random.random() < 0.3:
                                    pickups.append(Pickup(enemy.pos.copy(), random.choice(["health", "ammo"])))
                            if bullet in companion.bullets:
                                companion.bullets.remove(bullet)
                            break
            
            # Update pickups
            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    pickup_sound.play()
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)
            
            # Update zombies and check player collision
            for enemy in zombies[:]:
                if isinstance(enemy, BossZombie):
                    enemy.update(player.pos, collision_rects, map_manager)
                else:
                    enemy.update(player.pos, collision_rects, map_manager)
                if player.get_rect().colliderect(enemy.get_rect()):
                    damage = 20 if isinstance(enemy, BossZombie) else 10
                    player.take_damage(damage)
            
            # Check if player is dead
            if player.health <= 0:
                game_over = True
        
        # Draw game elements
        screen.fill(DARK_RED)
        draw_map(screen, tmx_data, offset)
        draw_objects(screen, tmx_data, "props", offset)
        
        # Draw blood effects
        current_time = pygame.time.get_ticks()
        for item in dead_zombies[:]:
            pos, death_time = item
            if current_time - death_time < 5000:
                screen.blit(dead_sprite, pos - offset - pygame.Vector2(50, 20))
            else:
                dead_zombies.remove(item)
        
        # Draw all game objects
        for zombie in zombies[:]:
            if isinstance(zombie, BossZombie):
                zombie.draw(screen, offset, player)
            else:
                zombie.draw(screen, offset)
        
        for bullet in bullets:
            bullet.draw(screen, offset)
        
        for pickup in pickups:
            pickup.draw(screen, offset)
        
        if show_companion:
            companion.draw(screen, offset)
        
        player.draw(screen, offset)
        
        # Draw HUD elements
        # Health bar
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, 200 * (player.health / PLAYER_MAX_HEALTH), 20))
        
        # Ammo and stats text
        ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
        wave_text = font.render(f'WAVE: {wave_number}', True, TEXT_COLOR)
        kills_text = font.render(f'KILLS: {total_kill_count}', True, TEXT_COLOR)
        time_text = font.render(f'SURVIVAL TIME: {survival_time}s', True, TEXT_COLOR)
        wave_progress_text = font.render(f'WAVE PROGRESS: {wave_kills}/{wave_kill_threshold}', True, TEXT_COLOR)
        
        screen.blit(ammo_text, (20, 45))
        screen.blit(wave_text, (WIDTH // 2 - 50, 20))
        screen.blit(kills_text, (20, 70))
        screen.blit(time_text, (WIDTH - 240, 20))
        screen.blit(wave_progress_text, (WIDTH - 240, 50))
        
        # Draw minimap
        draw_minimap(screen, tmx_data, collision_rects, player, zombies, 
                     companion if show_companion else None, None)
        
        # Draw arsenal
        draw_arsenal(screen, player)
        
        # Game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = large_font.render("GAME OVER", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
            quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
            
            final_wave_text = font.render(f"Final Wave: {wave_number}", True, TEXT_COLOR)
            final_kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
            final_time_text = font.render(f"Survival Time: {survival_time} seconds", True, TEXT_COLOR)
            
            vertical_spacing = 40
            center_y = HEIGHT // 2 - 50
            
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, center_y - 100))
            screen.blit(final_wave_text, (WIDTH // 2 - final_wave_text.get_width() // 2, center_y))
            screen.blit(final_kills_text, (WIDTH // 2 - final_kills_text.get_width() // 2, center_y + vertical_spacing))
            screen.blit(final_time_text, (WIDTH // 2 - final_time_text.get_width() // 2, center_y + vertical_spacing * 2))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, center_y + vertical_spacing * 4))
            screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, center_y + vertical_spacing * 5))
        
        pygame.display.flip()

if __name__ == "__main__":
    endless_mode()
