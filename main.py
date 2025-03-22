# main.py
import pygame
import random
import sys
from pygame.locals import *
from constants import *
from Player import Player
from Pickup import Pickup
from utilityFunctions import draw_grid, generate_maze_obstacles, reposition_maze_obstacles, spawn_zombie
from levelManager import LevelManager
from aiIntegration import AIHelper
from MapManager import MapManager, line_of_sight_clear
from Companion import Companion

DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2

def draw_minimap(surface, map_manager, player, zombies, obstacles):
    # Define minimap dimensions and position (top-right corner)
    minimap_width = 200
    minimap_height = 200
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((50, 50, 50))
    
    scale_x = minimap_width / map_manager.region_size
    scale_y = minimap_height / map_manager.region_size
    region_half = map_manager.region_size // 2
    # Draw obstacles
    for obs in obstacles:
        rel_x = (obs.pos.x - (map_manager.reference_pos.x - region_half)) * scale_x
        rel_y = (obs.pos.y - (map_manager.reference_pos.y - region_half)) * scale_y
        obs_rect = pygame.Rect(rel_x, rel_y, obs.size[0] * scale_x, obs.size[1] * scale_y)
        pygame.draw.rect(minimap_surface, (100, 100, 100), obs_rect)
    # Draw player position
    rel_x = (player.pos.x - (map_manager.reference_pos.x - region_half)) * scale_x
    rel_y = (player.pos.y - (map_manager.reference_pos.y - region_half)) * scale_y
    pygame.draw.circle(minimap_surface, (0, 255, 0), (int(rel_x), int(rel_y)), 5)
    # Draw zombies
    for zombie in zombies:
        rel_x = (zombie.pos.x - (map_manager.reference_pos.x - region_half)) * scale_x
        rel_y = (zombie.pos.y - (map_manager.reference_pos.y - region_half)) * scale_y
        pygame.draw.circle(minimap_surface, (255, 0, 0), (int(rel_x), int(rel_y)), 5)
    # Blit minimap at top-right corner
    surface.blit(minimap_surface, (WIDTH - minimap_width - 10, 10))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival - Ultimate Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    gemini_api_key = "YOUR_GEMINI_API_KEY"
    ai_helper = AIHelper(gemini_api_key)

    player = Player()
    zombies = []
    bullets = []
    pickups = []
    level_manager = LevelManager()
    obstacles = generate_maze_obstacles(player.pos, level_manager.current_level)
    map_manager = MapManager(obstacles, player.pos)

    # Create companion team (three AI survivors with unique abilities)
    companions = [
        Companion(player.pos + pygame.Vector2(60, 0), "gun"),
        Companion(player.pos + pygame.Vector2(-60, 0), "knife"),
        Companion(player.pos + pygame.Vector2(0, 60), "medic"),
        Companion(player.pos + pygame.Vector2(0, -60), "bomb")
    ]

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
    pygame.time.set_timer(DYNAMIC_OBSTACLE_EVENT, DYNAMIC_OBSTACLE_INTERVAL)

    game_over = False
    mini_game_active = False
    # Improved doctor's level mini-game variables:
    doctor_options = ["Cooperate", "Defect", "Ignore"]
    selected_option = 0
    doctor_level_active = False

    while True:
        dt = clock.tick(FPS)
        offset = pygame.Vector2(player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2)

        mouse_pos = pygame.mouse.get_pos()
        world_mouse_pos = pygame.Vector2(mouse_pos) + offset

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Toggle knife mode with E.
            if event.type == KEYDOWN:
                if event.key == K_e:
                    player.has_knife = not player.has_knife
                # In doctor's mini-game, use UP/DOWN and ENTER.
                if level_manager.current_level == 9 and doctor_level_active:
                    if event.key == K_UP:
                        selected_option = (selected_option - 1) % len(doctor_options)
                    if event.key == K_DOWN:
                        selected_option = (selected_option + 1) % len(doctor_options)
                    if event.key == K_RETURN:
                        if doctor_options[selected_option].lower() == "cooperate":
                            player.ammo += AMMO_PACK_AMOUNT
                        else:
                            player.take_damage(10)
                        doctor_level_active = False

            if not doctor_level_active:
                if not mini_game_active and event.type == MOUSEBUTTONDOWN and not game_over:
                    # Left-click: shoot if not in knife mode.
                    if event.button == 1 and not player.has_knife:
                        bullet = player.shoot(world_mouse_pos)
                        if bullet:
                            bullets.append(bullet)
                    # Right-click: if in knife mode, perform knife attack.
                    if event.button == 3 and player.has_knife:
                        attacked = player.knife_attack(zombies)
                        for z in attacked:
                            if z in zombies:
                                zombies.remove(z)
                if event.type == SPAWN_EVENT and not game_over and not mini_game_active and not doctor_level_active:
                    zombies.append(spawn_zombie(player.pos, speed_multiplier=1.0))

        if not game_over and not mini_game_active and not doctor_level_active:
            player.update_rotation(world_mouse_pos)
            player.update(obstacles)
            player.update_invincibility()

            for bullet in bullets[:]:
                bullet.update()
                bullet_rect = pygame.Rect(bullet.pos.x - bullet.size, bullet.pos.y - bullet.size, bullet.size * 2, bullet.size * 2)
                hit_obstacle = any(obs.get_rect().colliderect(bullet_rect) for obs in obstacles)
                if hit_obstacle or bullet.distance_traveled > BULLET_RANGE:
                    bullets.remove(bullet)
                    continue
                for zombie in zombies[:]:
                    if (bullet.pos - zombie.pos).length() < zombie.size:
                        if zombie.take_damage(50):
                            zombies.remove(zombie)
                            if random.random() < 0.3:
                                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                                pickups.append(Pickup(zombie.pos.copy(), pickup_type))
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break

            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    elif pickup.type == 'ammo':
                        player.ammo += AMMO_PACK_AMOUNT
                    elif pickup.type == 'antidote':
                        pickups.remove(pickup)
                        guidance = ai_helper.get_doctor_guidance("Guide the player to the helicopter")
                        print("Doctor:", guidance)
                    pickups.remove(pickup)

            for zombie in zombies:
                zombie.update(player.pos, obstacles, map_manager)
                if (player.pos - zombie.pos).length() < COLLISION_THRESHOLD and not player.invincible:
                    player.take_damage(10)
                    if player.health <= 0:
                        game_over = True

            for obs in obstacles:
                if hasattr(obs, 'update'):
                    obs.update()
                if hasattr(obs, 'is_fire'):
                    if player.get_rect().colliderect(obs.get_rect()):
                        player.take_damage(1)

            # Update companions (all AI-controlled survivors)
            for comp in companions:
                comp.update(player, zombies, obstacles)

            if level_manager.update_level():
                obstacles = reposition_maze_obstacles(obstacles, player.pos, level_manager.current_level)
                map_manager = MapManager(obstacles, player.pos)
                if level_manager.current_level == 9:
                    doctor_level_active = True
                if level_manager.current_level == 10:
                    if not any(pickup.type == 'antidote' for pickup in pickups):
                        pickups.append(Pickup(player.pos + pygame.Vector2(200, 0), 'antidote'))

        screen.fill(DARK_RED)
        draw_grid(screen, offset)
        
        for obs in obstacles:
            obs.draw(screen, offset)
        for pickup in pickups:
            pickup.draw(screen, offset)
        for zombie in zombies:
            zombie.draw(screen, offset)
        for bullet in bullets:
            bullet.draw(screen, offset)
        for comp in companions:
            comp.draw(screen, offset)
        player.draw(screen, offset, current_level=level_manager.current_level)

        # UI: Health, Ammo, Level Display
        health_bar_width = 200
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, health_bar_width * (player.health / PLAYER_MAX_HEALTH), 20))
        ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
        screen.blit(ammo_text, (WIDTH - 150, 20))
        level_text = font.render(f'LEVEL: {level_manager.current_level}', True, TEXT_COLOR)
        screen.blit(level_text, (WIDTH // 2 - 50, 20))

        # Draw minimap at top-right.
        draw_minimap(screen, map_manager, player, zombies, obstacles)

        # Draw doctor's level mini-game overlay.
        if doctor_level_active:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            prompt = large_font.render("Doctor's Dilemma: Choose an Option", True, (255, 255, 255))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 150))
            for i, option in enumerate(doctor_options):
                color = (0, 255, 0) if i == selected_option else (255, 255, 255)
                opt_text = font.render(option, True, color)
                screen.blit(opt_text, (WIDTH // 2 - opt_text.get_width() // 2, HEIGHT // 2 - 50 + i * 30))
        
        level_manager.draw_level_intro(screen, large_font)

        if game_over:
            game_over_text = large_font.render("GAME OVER - Press R to restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        
        pygame.display.flip()

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[K_r]:
                main()
                return

if __name__ == '__main__':
    main()
