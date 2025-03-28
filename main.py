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
from MapManager import MapManager, line_of_sight_clear
from minimap import draw_minimap
from checkpoint import load_checkpoints, draw_checkpoints
from spawn import spawn_enemy, find_player_spawn
from storyline import play_level_story
from doctor_minigame import minigame
from human import Human
from rps import rock_paper_scissors_minigame
from antidoteg import run_antidote_hunt
from arsenal import draw_arsenal
from BossZombie import BossZombie
from sound import Sound
from pause import pause

bg_music = Sound('game_bg.mp3')
pickup_sound = Sound('pickup.mp3')

# Define game states.
STATE_MENU = "menu"
STATE_STORYLINE = "storyline"
STATE_RUNNING = "running"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"

KILL_THRESHOLD = 5  # When objective_kills reaches this value, checkpoint is activated.

def load_specific_map(current_level):
    """
    Returns the appropriate TMX map based on current level.
    Adjust file names as needed:
      - Level 1: "deadvillage3.tmx"
      - Level 2: "deadcity.tmx"
      - Level 3: (Placeholder for doctor minigame; using "theroom.tmx")
      - Level 4: "theroom.tmx"
      - Level 5: (Placeholder for doctor minigame; using "heaq1.tmx")
      - Level 6: "heaq1.tmx"
      - Level 7: "heaq2.tmx"
      - Level 8: (Placeholder for RPS minigame; using "heaq2.tmx")
      - Else: default map.
    """
    if current_level == 1:
        return load_map("deadvillage3.tmx")
    elif current_level == 2:
        return load_map("newcity.tmx")
    elif current_level == 3:
        return load_map("theroom.tmx")
    elif current_level == 4:
        return load_map("theroom.tmx")
    elif current_level == 5:
        return load_map("heaq1.tmx")
    elif current_level == 6:
        return load_map("heaq1.tmx")
    elif current_level == 7:
        return load_map("heaq2.tmx")
    elif current_level == 8:
        return load_map("heaq2.tmx")
    else:
        return load_map("deadvillage3.tmx")

def handle_menu_events(event, checkpoints):
    """
    Processes events when in the menu state.
    Returns new state (if any change), reset variables for level start, and chosen checkpoint.
    """
    new_state = STATE_MENU
    reset_vars = {"objective_kills": 0, "spawn_zombies": True, "zombies": []}
    active_checkpoint = None
    # if event.type == KEYDOWN:
    #     if event.key == K_s:
    #         new_state = STATE_STORYLINE
    #         # Reset level-specific states when starting.
    #         if checkpoints and len(checkpoints) > 0:
    #             active_checkpoint = checkpoints[0]
    #     elif event.key == K_q:
    #         pygame.quit()
    #         sys.exit()
    new_state = STATE_STORYLINE
    # Reset level-specific states when starting.
    if checkpoints and len(checkpoints) > 0:
        active_checkpoint = checkpoints[0]
    return new_state, reset_vars, active_checkpoint

def process_storyline(screen, current_level, storyline_shown):
    """
    If the storyline for the current level has not been shown, play it.
    Returns the new state and the updated storyline_shown flag.
    """
    if not storyline_shown:
        if play_level_story(screen, current_level):
            return STATE_RUNNING, True
        else:
            return STATE_MENU, True
    return STATE_RUNNING, True

def handle_running_events(event, player, zombies, world_mouse_pos, objective_kills,dead_zombies,total_kill_count):
    """
    Handles key and mouse events during gameplay.
    Returns any additional bullets (if shot) and updated objective_kills.
    """
    additional_bullets = []
    if event.type == KEYDOWN:
        if event.key == K_e:
            player.toggle_knife()
        if event.key == K_o:
            player.switch_gun()
        if event.key == K_c:
            # Toggle companion visibility (handled globally)
            global show_companion
            show_companion = not show_companion
    elif event.type == MOUSEBUTTONDOWN:
        if event.button == 1:  # Left-click to shoot
            result = player.shoot(world_mouse_pos)
            if result:
                if isinstance(result, list):
                    additional_bullets.extend(result)
                else:
                    additional_bullets.append(result)
        elif event.button == 3 and player.has_knife:
            player.use_knife()
            attacked = player.knife_attack(zombies)
            for z in attacked:
                if z in zombies:
                    if z.take_damage(999, None):  # Instant kill via knife
                        zombies.remove(z)
                        dead_zombies.append((z.pos.copy(), pygame.time.get_ticks()))
                        total_kill_count += 1
                        # Increase objective kill count if below threshold.
                        if objective_kills < KILL_THRESHOLD:
                            objective_kills += 1
    return additional_bullets, objective_kills, total_kill_count

def update_bullets(bullets, zombies, pickups, dead_zombies, tmx_data, current_level, total_kill_count, objective_kills):
    """
    Update bullets and check for collisions with enemies.
    Returns updated bullets, total_kill_count, and objective_kills.
    """
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
                    if objective_kills < KILL_THRESHOLD:
                        objective_kills += 1
                    # 30% chance to spawn a pickup.
                    if random.random() < 0.3:
                        pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                        pickups.append(Pickup(enemy.pos.copy(), pickup_type))
                if bullet in bullets:
                    bullets.remove(bullet)
                break
    return bullets, total_kill_count, objective_kills

def update_companion(companion, player, zombies, obstacles, total_kill_count, objective_kills, pickups, dead_zombies):
    """
    Update companion (if visible), its bullets, and process collisions.
    Returns updated total_kill_count and objective_kills.
    """
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
                    if objective_kills < KILL_THRESHOLD:
                        objective_kills += 1
                    if random.random() < 0.3:
                        pickups.append(Pickup(enemy.pos.copy(), random.choice(["health", "ammo"])))
                if bullet in companion.bullets:
                    companion.bullets.remove(bullet)
                break
    return total_kill_count, objective_kills

def update_pickups(player, pickups):
    """
    Check if player collects any pickups.
    """
    for pickup in pickups[:]:
        if (player.pos - pickup.pos).length() < player.size + pickup.size:
            pickup_sound.play()
            if pickup.type == 'health':
                player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
            else:
                player.ammo += AMMO_PACK_AMOUNT
            pickups.remove(pickup)
    return pickups

def update_zombies(zombies, player, collision_rects, map_manager, tmx_data, current_level, total_kill_count, objective_kills, dead_zombies):
    """
    Update each zombie (and special zombies) and handle collisions with the player.
    Returns updated zombies, total_kill_count, and objective_kills.
    """
    new_zombies = []
    for enemy in zombies[:]:
        if enemy.is_special:
            enemy.update(player.pos, collision_rects, map_manager)
            if (enemy.pos - player.pos).length() <= 150:
                new_enemies = [spawn_enemy(1.0, tmx_data, current_level) for _ in range(8)]
                if current_level != 4:
                    zombies.extend(new_enemies)
                dead_zombies.append((enemy.pos.copy(), pygame.time.get_ticks()))
                zombies.remove(enemy)
                total_kill_count += 1
                if objective_kills < KILL_THRESHOLD:
                    objective_kills += 1
                continue
        else:
            # Update regular zombies
            if line_of_sight_clear(enemy.pos, player.pos, collision_rects):
                # Move directly toward the player if they are visible
                enemy.update(player.pos, collision_rects, map_manager)
            else:
                # Use A* pathfinding if the player is not visible
                if not enemy.path or enemy.path_index >= len(enemy.path):
                    enemy.path = map_manager.astar(enemy.pos, player.pos)
                    enemy.path_index = 0
                if enemy.path and enemy.path_index < len(enemy.path):
                    target = enemy.path[enemy.path_index]
                    direction = target - enemy.pos
                    if direction.length() < enemy.speed:
                        enemy.pos = target
                        enemy.path_index += 1
                    else:
                        direction = direction.normalize()
                        enemy.pos += direction * enemy.speed

        # Check for collisions with the player
        if player.get_rect().colliderect(enemy.get_rect()):
            player.take_damage(10)

    zombies.extend(new_zombies)
    return zombies, total_kill_count, objective_kills

def draw_game_scene(screen, tmx_data, offset, player, bullets, pickups, zombies, companion, checkpoints, dead_zombies, dead_sprite, total_kill_count, objective_kills, current_level, level_manager, collision_rects, map_manager, active_checkpoint, font, large_font, puddles):
    """
    Draw the game scene in the running state, including the map, objects, UI, blood effects, and minimap.
    """
    screen.fill(DARK_RED)
    draw_map(screen, tmx_data, offset)
    draw_objects(screen, tmx_data, "props", offset)

    # Draw blood effect: show dead zombie sprite (blood splatter) for 5 seconds.
    current_time = pygame.time.get_ticks()
    for item in dead_zombies[:]:
        pos, death_time = item
        if current_time - death_time < 5000:
            screen.blit(dead_sprite, pos - offset - pygame.Vector2(50, 20))
        else:
            dead_zombies.remove(item)
    
    for puddle in puddles:
        puddle.draw(screen, offset)
        print("YOLO")
        distance_to_puddle = (player.pos - puddle.position).length()
        if distance_to_puddle <= puddle.radius:  # Check if the player is within the puddle's radius
            print("Player is in the puddle!")  # Debug print
            player.take_damage(puddle.damage)

    for zombie in zombies[:]:
        if isinstance(zombie, BossZombie):
            zombie.draw(screen, offset, player)  # Update BossZombie behavior
        else:
            zombie.draw(screen, offset)

    if checkpoints:
        draw_checkpoints(screen, checkpoints, offset)
    for bullet in bullets:
        bullet.draw(screen, offset)
    for pickup in pickups:
        pickup.draw(screen, offset)

    if show_companion:
        companion.draw(screen, offset)
    player.draw(screen, offset, current_level)

    # Draw health bar.
    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 20))
    pygame.draw.rect(screen, (0, 255, 0), (20, 20, 200 * (player.health / PLAYER_MAX_HEALTH), 20))
    ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
    screen.blit(ammo_text, (20, 45))
    level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
    screen.blit(level_text, (WIDTH // 2 - 50, 20))

    # Draw objective texts.
    objective_title = font.render('OBJECTIVE:', True, TEXT_COLOR)
    objective_progress = font.render(f'{min(objective_kills, KILL_THRESHOLD)}/{KILL_THRESHOLD}', True, TEXT_COLOR)
    total_kill_text = font.render(f'TOTAL KILLS: {total_kill_count}', True, TEXT_COLOR)
    objective_y = HEIGHT // 2 - 50
    progress_y = objective_y + 30
    total_kill_y = progress_y + 30
    screen.blit(objective_title, (20, objective_y))
    screen.blit(objective_progress, (50, progress_y))
    screen.blit(total_kill_text, (20, total_kill_y))

    # Display proper status text.
    if objective_kills < KILL_THRESHOLD:
        status_text = font.render(f"Objective: Eliminate {KILL_THRESHOLD} zombies", True, TEXT_COLOR)
    else:
        status_text = font.render("Objective: Find and reach the checkpoint!", True, TEXT_COLOR)
        if active_checkpoint:
            cp_rect = active_checkpoint["rect"]
            checkpoint_x = cp_rect.x - offset.x
            checkpoint_y = cp_rect.y - offset.y
            # If on-screen, draw a pulsing outline.
            if 0 <= checkpoint_x <= WIDTH and 0 <= checkpoint_y <= HEIGHT:
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 2 + 1
                pygame.draw.rect(screen, (255, 255, 0),
                                 (checkpoint_x - pulse, checkpoint_y - pulse,
                                  cp_rect.width + pulse * 2, cp_rect.height + pulse * 2), 3)
            # Off-screen arrow indicator.
            if checkpoint_x < 0 or checkpoint_x > WIDTH or checkpoint_y < 0 or checkpoint_y > HEIGHT:
                direction = pygame.Vector2(active_checkpoint["rect"].centerx - player.pos.x,
                                           active_checkpoint["rect"].centery - player.pos.y).normalize()
                arrow_length = 30
                arrow_center = (WIDTH - 50, 50)
                pygame.draw.line(screen, (255, 255, 0),
                                 arrow_center,
                                 (arrow_center[0] + direction.x * arrow_length,
                                  arrow_center[1] + direction.y * arrow_length), 3)
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
        cp_obj_text = font.render("Find and reach the checkpoint!", True, TEXT_COLOR)
        screen.blit(cp_obj_text, (20, total_kill_y + 30))
    screen.blit(status_text, (WIDTH - status_text.get_width() - 25, 230))
    level_manager.draw_level_intro(screen, large_font)
    draw_minimap(screen, tmx_data, collision_rects, player, zombies, companion if show_companion else None, active_checkpoint)
    draw_arsenal(screen, player)
    pygame.display.flip()

def draw_menu(screen, large_font, font, current_level, total_kill_count, player):
    """
    Draw the main menu screen.
    """
    return 
    screen.fill(DARK_RED)
    title_text = large_font.render("RESIDENT EVIL 2D SURVIVAL", True, TEXT_COLOR)
    level_text = large_font.render(f"LEVEL {current_level}", True, TEXT_COLOR)
    start_text = font.render("Press S to Start", True, TEXT_COLOR)
    quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
    kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
    ammo_text = font.render(f"Ammo: {player.ammo}", True, TEXT_COLOR)
    
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 100))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 150))
    screen.blit(kills_text, (WIDTH // 2 - kills_text.get_width() // 2, HEIGHT // 2 + 50))
    screen.blit(ammo_text, (WIDTH // 2 - ammo_text.get_width() // 2, HEIGHT // 2 + 75))
    pygame.display.flip()

def draw_overlay(screen, text, large_font):
    """
    Draw a semi-transparent overlay with centered text.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    text_surface = large_font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 3))
    pygame.display.flip()

def draw_level_complete(screen, large_font, font, total_kill_count, player):
    """
    Draw the level complete overlay.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    complete_text = large_font.render("LEVEL COMPLETE", True, TEXT_COLOR)
    screen.blit(complete_text, (WIDTH // 2 - complete_text.get_width() // 2, HEIGHT // 3))
    
    vertical_spacing = 35
    stats_start_y = HEIGHT // 2 - 50
    kills_text = font.render(f"Level Kills: {KILL_THRESHOLD}/{KILL_THRESHOLD}", True, TEXT_COLOR)
    total_kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
    ammo_text = font.render(f"Ammo: {player.ammo}", True, TEXT_COLOR)
    screen.blit(kills_text, (WIDTH // 2 - kills_text.get_width() // 2, stats_start_y))
    screen.blit(total_kills_text, (WIDTH // 2 - total_kills_text.get_width() // 2, stats_start_y + vertical_spacing))
    screen.blit(ammo_text, (WIDTH // 2 - ammo_text.get_width() // 2, stats_start_y + vertical_spacing * 2))
    
    options_start_y = stats_start_y + vertical_spacing * 3 + 20
    next_text = font.render("Press N for Next Level", True, TEXT_COLOR)
    quit_text = font.render("Press Q to Quit", True, TEXT_COLOR)
    screen.blit(next_text, (WIDTH // 2 - next_text.get_width() // 2, options_start_y))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, options_start_y + vertical_spacing))
    pygame.display.flip()

def draw_game_over(screen, large_font, font, total_kill_count):
    """
    Draw the game over overlay.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    game_over_text = large_font.render("GAME OVER", True, TEXT_COLOR)
    restart_text = font.render("Press R to Restart", True, TEXT_COLOR)
    final_kills_text = font.render(f"Total Kills: {total_kill_count}", True, TEXT_COLOR)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    screen.blit(final_kills_text, (WIDTH // 2 - final_kills_text.get_width() // 2, HEIGHT // 2 - 100))
    pygame.display.flip()

def main():
    bg_music.play_loop()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Dead Village")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    # Initialize level, map, and collision data.
    current_level = 1
    tmx_data = load_specific_map(current_level)
    collision_rects = load_collision_rects(tmx_data)
    checkpoints = load_checkpoints(tmx_data)
    print("Collision Rects:", collision_rects)

    safe_pos = find_player_spawn(tmx_data)
    player = Player(safe_pos)
    # Load the blood effect (dead zombie) sprite.
    dead_sprite = pygame.image.load('assets/Dead_img.png').convert_alpha()

    companion = Companion(player.pos + pygame.Vector2(60, 0), "gun")
    global show_companion
    show_companion = False

    level_manager = LevelManager()
    # current_level might be updated by the level manager.
    current_level = level_manager.current_level
    obstacles = collision_rects
    map_manager = MapManager(obstacles, player.pos)

    # Game object lists and counters.
    zombies = []
    bullets = []
    pickups = []
    dead_zombies = []
    puddles = []
    total_kill_count = 0
    objective_kills = 0

    checkpoint_active = False
    active_checkpoint = None

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
    spawn_zombies = True
    storyline_shown = False

    state = STATE_MENU

    while True:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks()

        # Global event processing.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Press 'P' to pause
                    pause(screen)
                    
            # Process events per state.
            if state == STATE_MENU:
                state, resets, active_checkpoint = handle_menu_events(event, checkpoints)
                if state == STATE_STORYLINE:
                    objective_kills = resets["objective_kills"]
                    spawn_zombies = resets["spawn_zombies"]
                    zombies = resets["zombies"]
            elif state == STATE_STORYLINE:
                # Storyline state events are handled internally.
                pass
            elif state == STATE_RUNNING:
                offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
                mouse_pos = pygame.mouse.get_pos()
                world_mouse_pos = pygame.Vector2(mouse_pos) + offset
                add_bullets, objective_kills, total_kill_count = handle_running_events(event, player, zombies, world_mouse_pos, objective_kills,dead_zombies,total_kill_count)
                if add_bullets:
                    bullets.extend(add_bullets)
                if event.type == SPAWN_EVENT:
                    if spawn_zombies and objective_kills < KILL_THRESHOLD:
                        new_enemies = [spawn_enemy(1.0, tmx_data, current_level) for _ in range(2)]
                        zombies.extend(new_enemies)
                for puddle in puddles:
                    puddle.draw(screen, offset)
                    distance_to_puddle = (player.pos - (puddle.position - offset - pygame.Vector2(60,40))).length()

                    if distance_to_puddle <= puddle.radius:  # Check if the player is within the puddle's radius
                        print("Player is in the puddle!")  # Debug print
                        player.take_damage(puddle.damage)
            elif state == STATE_LEVEL_COMPLETE:
                if event.type == KEYDOWN:
                    if event.key == K_n:
                        current_level += 1
                        tmx_data = load_specific_map(current_level)
                        collision_rects = load_collision_rects(tmx_data)
                        checkpoints = load_checkpoints(tmx_data)
                        safe_pos = find_player_spawn(tmx_data)
                        player = Player(safe_pos)

                        # Play slides before minigames for specific levels
                        if current_level == 3:
                            if not storyline_shown:
                                if play_level_story(screen, current_level):
                                    storyline_shown = True
                            elif rock_paper_scissors_minigame(screen):
                                current_level += 1

                        if current_level == 5:
                            if not storyline_shown:
                                if play_level_story(screen, current_level):
                                    storyline_shown = True
                            elif minigame():
                                current_level += 1

                        if current_level == 8:
                            if not storyline_shown:
                                if play_level_story(screen, current_level):
                                    storyline_shown = True
                            elif run_antidote_hunt():
                                current_level += 1

                        objective_kills = 0
                        checkpoint_active = False
                        active_checkpoint = None
                        state = STATE_MENU
                        storyline_shown = False
                    if event.key == K_q:
                        pygame.quit()
                        sys.exit()
            elif state == STATE_GAME_OVER:
                if event.type == KEYDOWN and event.key == K_r:
                    main()
                    return

        # State-specific updates and drawing.
        if state == STATE_MENU:
            draw_menu(screen, large_font, font, current_level, total_kill_count, player)
        elif state == STATE_STORYLINE:
            state, storyline_shown = process_storyline(screen, current_level, storyline_shown)
        elif state == STATE_RUNNING:
            offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = pygame.Vector2(mouse_pos) + offset
            player.update_rotation(world_mouse_pos)
            player.update(collision_rects)
            player.update_invincibility()

            bullets, total_kill_count, objective_kills = update_bullets(bullets, zombies, pickups, dead_zombies, tmx_data, current_level, total_kill_count, objective_kills)

            if show_companion:
                total_kill_count, objective_kills = update_companion(companion, player, zombies, obstacles, total_kill_count, objective_kills, pickups, dead_zombies)

            pickups = update_pickups(player, pickups)
            zombies, total_kill_count, objective_kills = update_zombies(zombies, player, collision_rects, map_manager, tmx_data, current_level, total_kill_count, objective_kills, dead_zombies)

            if player.health <= 0:
                state = STATE_GAME_OVER

            if objective_kills >= KILL_THRESHOLD:
                spawn_zombies = False
                if not checkpoint_active and active_checkpoint:
                    checkpoint_active = True

            if checkpoint_active and active_checkpoint:
                if player.get_rect().colliderect(active_checkpoint["rect"]):
                    state = STATE_LEVEL_COMPLETE

            draw_game_scene(screen, tmx_data, offset, player, bullets, pickups, zombies,
                            companion, checkpoints, dead_zombies, dead_sprite,
                            total_kill_count, objective_kills, current_level, level_manager,
                            collision_rects, map_manager, active_checkpoint, font, large_font, puddles)
        elif state == STATE_LEVEL_COMPLETE:
            draw_level_complete(screen, large_font, font, total_kill_count, player)
        elif state == STATE_GAME_OVER:
            draw_game_over(screen, large_font, font, total_kill_count)

if __name__ == "__main__":
    main()
