# Import the storyline module at the top of main.py
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
from utilityFunctions import load_map, load_collision_rects, draw_map, draw_objects, spawn_special_zombie
from levelManager import LevelManager
from Companion import Companion
from MapManager import MapManager
from minimap import draw_minimap
from checkpoint import load_checkpoints, draw_checkpoints
from spawn import spawn_zombie,find_player_spawn
from storyline import play_level_story  # Add this import
from doctor_minigame import minigame

# Game states - add a new STORYLINE state
STATE_MENU = "menu"
STATE_STORYLINE = "storyline"  # New state for storyline
STATE_RUNNING = "running"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Dead Village")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)
    current_level = 1
    def load_specific_map(current_level):
        if current_level <= 2:
            return load_map()  # Original map (deadvillage.tmx)
        elif current_level >= 3:
            return load_map('deadcity.tmx')  # Specifically load deadcity map for level 3
        else:
            return load_map()  # Default map for other levels
    # Load the Tiled map, collision objects, and checkpoints.

    tmx_data = load_specific_map(current_level)
    collision_rects = load_collision_rects(tmx_data)
    checkpoints = load_checkpoints(tmx_data)
    print("Collision Rects:", collision_rects)

    # Spawn the player safely.
    safe_pos = find_player_spawn(tmx_data)
    player = Player(safe_pos)

    dead_sprite = pygame.image.load('assets/Dead_img.png').convert_alpha()

    # Create a single companion.
    companion = Companion(player.pos + pygame.Vector2(60, 0), "gun")
    show_companion = False

    # Initialize level and map managers.
    level_manager = LevelManager()
    current_level = level_manager.current_level
    obstacles = collision_rects  # Obstacles come from the Tiled map.
    map_manager = MapManager(obstacles, player.pos)

    zombies = []
    bullets = []
    pickups = []
    dead_zombies = []
    
    # Track high score separately from objective kills
    total_kill_count = 0  # This is the high score/total kills
    objective_kills = 0   # This is for the current level objective
    
    # Checkpoint logic.
    checkpoint_active = False
    active_checkpoint = None
    KILL_THRESHOLD = 30  # Activate checkpoint when kill count reaches 30

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)

    # Start with the menu state
    state = STATE_MENU
    
    # Flag to track if zombie spawning is active
    spawn_zombies = True
    
    # Flag to track if storyline has been shown for the current level
    storyline_shown = False

    while True:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        current_time = pygame.time.get_ticks()

        # Process events.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if state == STATE_MENU:
                if event.type == KEYDOWN:
                    if event.key == K_s:  # Start game with 'S' key
                        # Show storyline first
                        state = STATE_STORYLINE
                        storyline_shown = False
                        # Reset objective kills and zombie spawning when starting a new level
                        objective_kills = 0
                        spawn_zombies = True
                        # Reset checkpoint state
                        checkpoint_active = False
                        active_checkpoint = None
                        # Clear existing zombies list
                        zombies = []
                        
                        # If checkpoints exist, choose the first one as the active one
                        if checkpoints and len(checkpoints) > 0:
                            active_checkpoint = checkpoints[0]
                    if event.key == K_q:  # Quit game with 'Q' key
                        pygame.quit()
                        sys.exit()
            
            elif state == STATE_STORYLINE:
                # Event handling will be managed within the play_level_story function
                pass
                        
            elif state == STATE_RUNNING:
                # Camera offset: center on the player.
                offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = pygame.Vector2(mouse_pos) + offset
                
                if event.type == KEYDOWN:
                    # Toggle knife mode with E.
                    if event.key == K_e:
                        player.toggle_knife()
                    # Switch gun mode with O.
                    if event.key == K_o:
                        player.switch_gun()
                    # Toggle companion visibility with C.
                    if event.key == K_c:
                        show_companion = not show_companion
                if event.type == MOUSEBUTTONDOWN:
                    # Left-click: shoot.
                    if event.button == 1:
                        result = player.shoot(world_mouse_pos)
                        if result:
                            if isinstance(result, list):
                                bullets.extend(result)
                            else:
                                bullets.append(result)
                    # Right-click: if in knife mode, perform knife attack.
                    elif event.button == 3 and player.has_knife:
                        player.use_knife()
                        attacked = player.knife_attack(zombies)
                        for z in attacked:
                            if z in zombies:
                                if z.take_damage(999, None):  # Instant kill via knife.
                                    dead_zombies.append((z.pos.copy(), pygame.time.get_ticks()))
                                    zombies.remove(z)
                                    total_kill_count += 1
                                    # Only count if we haven't reached the threshold
                                    if objective_kills < KILL_THRESHOLD:
                                        objective_kills += 1
                if event.type == SPAWN_EVENT:
                    # Only spawn zombies if spawning is active and we haven't reached the kill threshold
                    if spawn_zombies and objective_kills < KILL_THRESHOLD:
                        zombies.append(spawn_zombie(1.0, tmx_data,current_level))
                        zombies.append(spawn_zombie(1.0, tmx_data,current_level))
                        # Optionally, spawn special zombies if desired:
                        # if current_level >= 5:
                        #     zombies.append(spawn_special_zombie(player.pos, 1.0, current_level, tmx_data))
                        
            elif state == STATE_LEVEL_COMPLETE:
                if event.type == KEYDOWN:
                    if event.key == K_n:
                        # Increment level by 1 (not continuous)
                        current_level += 1
                        # Load new map based on new level
                        tmx_data = load_specific_map(current_level)
                        collision_rects = load_collision_rects(tmx_data)
                        checkpoints = load_checkpoints(tmx_data)
                        
                        # Respawn player at new map's spawn point
                        safe_pos = find_player_spawn(tmx_data)
                        player = Player(safe_pos)

                        # Check if the next level is the minigame level
                        if current_level == 3:
                            minigame()
                            current_level += 1
                        
                        # Don't reset total kill count (high score)
                        # Reset objective kills for the new level
                        objective_kills = 0
                        checkpoint_active = False
                        active_checkpoint = None
                        # Return to menu screen instead of running state
                        state = STATE_MENU
                        # Reset storyline flag for the new level
                        storyline_shown = False
                    if event.key == K_q:
                        pygame.quit()
                        sys.exit()
                        
            elif state == STATE_GAME_OVER:
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        main()
                        return

        # Menu screen
        if state == STATE_MENU:
            screen.fill(DARK_RED)
            title_text = large_font.render("RESIDENT EVIL 2D SURVIVAL", True, TEXT_COLOR)
            level_text = large_font.render(f"LEVEL {current_level}", True, TEXT_COLOR)
            start_text = font.render("Press S to Start", True, TEXT_COLOR)
            quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
            
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 100))
            screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 150))
            
            # Display total kills and ammo on menu screen
            kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
            ammo_text = font.render(f"Ammo: {player.ammo}", True, TEXT_COLOR)
            screen.blit(kills_text, (WIDTH // 2 - kills_text.get_width() // 2, HEIGHT // 2 + 50))
            screen.blit(ammo_text, (WIDTH // 2 - ammo_text.get_width() // 2, HEIGHT // 2 + 75))
            
            pygame.display.flip()
            
        # Storyline state - show the story slides for the current level
        elif state == STATE_STORYLINE:
            if not storyline_shown:
                # Play the storyline for the current level
                storyline_shown = True
                if play_level_story(screen, current_level):
                    # If storyline completes successfully, transition to the game
                    state = STATE_RUNNING
                else:
                    # If storyline is skipped with Escape, go back to menu
                    state = STATE_MENU
            else:
                # If storyline has already been shown, go directly to the game
                state = STATE_RUNNING

        elif state == STATE_RUNNING:
            # Camera offset: center on the player.
            offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = pygame.Vector2(mouse_pos) + offset
            
            # Update game objects.
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
                            dead_zombies.append((zombie.pos.copy(), pygame.time.get_ticks()))
                            zombies.remove(zombie)
                            total_kill_count += 1
                            # Only increment objective_kills if we haven't reached the threshold
                            if objective_kills < KILL_THRESHOLD:
                                objective_kills += 1
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
                                dead_zombies.append((zombie.pos.copy(), pygame.time.get_ticks()))
                                zombies.remove(zombie)
                                total_kill_count += 1
                                # Only increment objective_kills if we haven't reached the threshold
                                if objective_kills < KILL_THRESHOLD:
                                    objective_kills += 1
                                if random.random() < 0.3:
                                    pickups.append(Pickup(zombie.pos.copy(), random.choice(["health", "ammo"])))
                            if bullet in companion.bullets:
                                companion.bullets.remove(bullet)
                            break

            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)

            new_zombies = []
            for zombie in zombies[:]:
                if zombie.is_special:
                    zombie.update(player.pos, collision_rects, map_manager)
                    if (zombie.pos - player.pos).length() <= 150:
                        num_explode = 8
                        offset_distance = 30
                        for i in range(num_explode):
                            angle = math.radians(i * (360 / num_explode))
                            new_zombies.append(spawn_zombie(1.0, tmx_data,current_level))
                            # Don't increment kill count for these spawned zombies
                        dead_zombies.append(zombie.pos.copy())
                        zombies.remove(zombie)
                        total_kill_count += 1
                        # Only increment objective_kills if we haven't reached the threshold
                        if objective_kills < KILL_THRESHOLD:
                            objective_kills += 1
                        continue
                else:
                    zombie.update(player.pos, collision_rects, map_manager)
                if player.get_rect().colliderect(zombie.get_rect()):
                    player.take_damage(10)
            zombies.extend(new_zombies)

            if player.health <= 0:
                state = STATE_GAME_OVER

            # Check if objective kill count has reached the threshold
            if objective_kills >= KILL_THRESHOLD:
                # Stop spawning zombies
                spawn_zombies = False
                
                # Activate checkpoint when kill count threshold is reached
                if not checkpoint_active and active_checkpoint:
                    checkpoint_active = True

            # If checkpoint is active and the player touches it, transition to level complete
            if checkpoint_active and active_checkpoint:
                checkpoint_rect = active_checkpoint["rect"]
                player_rect = player.get_rect()
                
                # Improve collision detection with checkpoint
                if player_rect.colliderect(checkpoint_rect):
                    state = STATE_LEVEL_COMPLETE

            # Draw game scene.
            screen.fill(DARK_RED)
            draw_map(screen, tmx_data, offset)
            draw_objects(screen, tmx_data, "props", offset)
            if checkpoints:
                draw_checkpoints(screen, checkpoints, offset)
            for bullet in bullets:
                bullet.draw(screen, offset)
            for pickup in pickups:
                pickup.draw(screen, offset)
            for zombie in zombies:
                zombie.draw(screen, offset)
            if show_companion:
                companion.draw(screen, offset)
            player.draw(screen, offset, current_level)
            current_time = pygame.time.get_ticks()
            for pos, death_time in dead_zombies[:]:
                if current_time - death_time < 5000:  # 5 seconds
                    screen.blit(dead_sprite, pos - offset - pygame.Vector2(50, 20))
                else:
                    dead_zombies.remove((pos, death_time))

            # Draw UI elements.
            pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (20, 20, 200 * (player.health / PLAYER_MAX_HEALTH), 20))
            ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
            screen.blit(ammo_text, (20, 45))
            level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
            screen.blit(level_text, (WIDTH // 2 - 50, 20))
            
            # Move objective messages to middle left of screen with better spacing
            objective_title = font.render('OBJECTIVE:', True, TEXT_COLOR)
            objective_progress = font.render(f'{min(objective_kills, KILL_THRESHOLD)}/{KILL_THRESHOLD}', True, TEXT_COLOR)
            total_kill_text = font.render(f'TOTAL KILLS: {total_kill_count}', True, TEXT_COLOR)
            
            # Position in middle left with proper spacing
            objective_y = HEIGHT // 2 - 50
            progress_y = objective_y + 30
            total_kill_y = progress_y + 30
            
            screen.blit(objective_title, (20, objective_y))
            screen.blit(objective_progress, (50, progress_y))
            screen.blit(total_kill_text, (20, total_kill_y))
            
            # Display proper objective text based on game state
            if objective_kills < KILL_THRESHOLD:
                status_text = font.render(f"Objective: Eliminate {KILL_THRESHOLD} zombies", True, TEXT_COLOR)
            else:
                if active_checkpoint:
                    checkpoint_x = active_checkpoint["rect"].x - offset.x
                    checkpoint_y = active_checkpoint["rect"].y - offset.y
                    
                    # Draw a visual indicator for the checkpoint
                    if checkpoint_active:
                        # Draw a larger, more noticeable marker
                        if (checkpoint_x >= 0 and checkpoint_x <= WIDTH and 
                            checkpoint_y >= 0 and checkpoint_y <= HEIGHT):
                            # Checkpoint is on screen - draw a pulsing outline
                            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 2 + 1
                            pygame.draw.rect(screen, (255, 255, 0), 
                                            (checkpoint_x - pulse, checkpoint_y - pulse, 
                                            active_checkpoint["rect"].width + pulse*2, 
                                            active_checkpoint["rect"].height + pulse*2), 
                                            3)
                    
                    # Draw an indicator arrow pointing to checkpoint if it's off-screen
                    if (checkpoint_x < 0 or checkpoint_x > WIDTH or 
                        checkpoint_y < 0 or checkpoint_y > HEIGHT):
                        direction = pygame.Vector2(active_checkpoint["rect"].centerx - player.pos.x,
                                                  active_checkpoint["rect"].centery - player.pos.y).normalize()
                        arrow_length = 30
                        arrow_center = (WIDTH - 50, 50)
                        # Draw arrow body
                        pygame.draw.line(screen, (255, 255, 0), 
                                        arrow_center,
                                        (arrow_center[0] + direction.x * arrow_length, 
                                        arrow_center[1] + direction.y * arrow_length), 3)
                        # Draw arrow head
                        head_length = 10
                        pygame.draw.line(screen, (255, 255, 0),
                                        (arrow_center[0] + direction.x * arrow_length,
                                        arrow_center[1] + direction.y * arrow_length),
                                        (arrow_center[0] + direction.x * arrow_length - head_length * direction.y,
                                        arrow_center[1] + direction.y * arrow_length + head_length * direction.x), 3)
                        pygame.draw.line(screen, (255, 255, 0),
                                        (arrow_center[0] + direction.x * arrow_length,
                                        arrow_center[1] + direction.y * arrow_length),
                                        (arrow_center[0] + direction.x * arrow_length + head_length * direction.y,
                                        arrow_center[1] + direction.y * arrow_length - head_length * direction.x), 3)
                        
                    # Add checkpoint objective text to the left middle area
                    checkpoint_objective = font.render("Find and reach the checkpoint!", True, TEXT_COLOR)
                    screen.blit(checkpoint_objective, (20, total_kill_y + 30))
                else:
                    status_text = font.render("Error: No checkpoint found!", True, (255, 0, 0))
                    
            # Position status text in top right (keep this as a summary)
            if objective_kills < KILL_THRESHOLD:
                status_text = font.render(f"Objective: Eliminate {KILL_THRESHOLD} zombies", True, TEXT_COLOR)
            else:
                status_text = font.render("Objective: Find and reach the checkpoint!", True, TEXT_COLOR)
            screen.blit(status_text, (WIDTH - status_text.get_width() - 25, 230))

            level_manager.draw_level_intro(screen, large_font)
            draw_minimap(screen, tmx_data, collision_rects, player, zombies, companion if show_companion else None, active_checkpoint)
            from arsenal import draw_arsenal
            draw_arsenal(screen, player)
            pygame.display.flip()

        # Level complete overlay with better spacing
        if state == STATE_LEVEL_COMPLETE:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Main title with proper positioning
            complete_text = large_font.render("LEVEL COMPLETE", True, TEXT_COLOR)
            screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 3))
            
            # Stats section with increased spacing
            vertical_spacing = 35  # Increased spacing between elements
            stats_start_y = HEIGHT // 2 - 50
            
            # Display current stats with better spacing
            kills_text = font.render(f"Level Kills: {KILL_THRESHOLD}/{KILL_THRESHOLD}", True, TEXT_COLOR)
            total_kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
            ammo_text = font.render(f"Ammo: {player.ammo}", True, TEXT_COLOR)
            
            screen.blit(kills_text, (WIDTH // 2 - kills_text.get_width() // 2, stats_start_y))
            screen.blit(total_kills_text, (WIDTH // 2 - total_kills_text.get_width() // 2, stats_start_y + vertical_spacing))
            screen.blit(ammo_text, (WIDTH // 2 - ammo_text.get_width() // 2, stats_start_y + vertical_spacing * 2))
            
            # Navigation options with better spacing
            options_start_y = stats_start_y + vertical_spacing * 3 + 20  # Extra gap before options
            
            next_text = font.render("Press N for Next Level", True, TEXT_COLOR)
            quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
            
            screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, options_start_y))
            screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, options_start_y + vertical_spacing))
            
            pygame.display.flip()

        # Game over overlay.
        if state == STATE_GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            game_over_text = large_font.render("GAME OVER", True, TEXT_COLOR)
            restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
            
            # Display final stats
            final_kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
            screen.blit(final_kills_text, (WIDTH // 2 - final_kills_text.get_width() // 2, HEIGHT // 2 - 100))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            keys = pygame.key.get_pressed()
            if keys[K_r]:
                main()
                return

if __name__ == "__main__":
    main()