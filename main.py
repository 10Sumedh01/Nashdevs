import pygame
import random
import sys
from pygame.locals import *
from constants import *
from Player import Player
from Pickup import Pickup
from utilityFunctions import draw_grid, generate_maze_obstacles, reposition_maze_obstacles, spawn_zombie

DYNAMIC_OBSTACLE_EVENT = pygame.USEREVENT + 2

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Resident Evil 2D Survival")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    player = Player()
    zombies = []
    bullets = []
    pickups = []
    obstacles = generate_maze_obstacles(player.pos)

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
    pygame.time.set_timer(DYNAMIC_OBSTACLE_EVENT, DYNAMIC_OBSTACLE_INTERVAL)

    start_ticks = pygame.time.get_ticks()
    current_level = 1
    zombie_speed_multiplier = 1.0
    level_start_time = pygame.time.get_ticks()
    game_over = False

    while True:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_ticks
        offset = pygame.Vector2(player.pos.x - WIDTH//2, player.pos.y - HEIGHT//2)

        # Get mouse position in world coordinates
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_pos = pygame.Vector2(mouse_pos) + offset

        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and not game_over:
                bullet = player.shoot(world_mouse_pos)
                if bullet:
                    bullets.append(bullet)
            if event.type == SPAWN_EVENT and not game_over:
                zombies.append(spawn_zombie(player.pos, zombie_speed_multiplier))

        if not game_over:
            # Update player rotation and position
            player.update_rotation(world_mouse_pos)
            player.update(obstacles)
            player.update_invincibility()

            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.distance_traveled > BULLET_RANGE:
                    bullets.remove(bullet)
                    continue
                
                for zombie in zombies[:]:
                    if (bullet.pos - zombie.pos).length() < zombie.size:
                        if zombie.take_damage(50):
                            zombies.remove(zombie)
                            if random.random() < 0.3:
                                pickup_type = 'health' if random.random() < 0.5 else 'ammo'
                                pickups.append(Pickup(zombie.pos.copy(), pickup_type))
                        bullets.remove(bullet)
                        break

            # Update pickups
            for pickup in pickups[:]:
                if (player.pos - pickup.pos).length() < player.size + pickup.size:
                    if pickup.type == 'health':
                        player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                    else:
                        player.ammo += AMMO_PACK_AMOUNT
                    pickups.remove(pickup)

            # Update zombies
            for zombie in zombies:
                zombie.update(player.pos, obstacles)
                if (player.pos - zombie.pos).length() < COLLISION_THRESHOLD and not player.invincible:
                    player.take_damage(10)
                    if player.health <= 0:
                        game_over = True

            # Update obstacles
            for obs in obstacles:
                if hasattr(obs, 'update'):
                    obs.update()

            # Level progression
            if elapsed_time >= LEVEL_DURATION:
                current_level += 1
                zombie_speed_multiplier *= 1.05
                obstacles = reposition_maze_obstacles(obstacles, player.pos)
                start_ticks = current_time

        # Drawing
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
        player.draw(screen, offset)

        # UI Elements
        health_bar_width = 200
        pygame.draw.rect(screen, (255,0,0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(screen, (0,255,0), 
                        (20, 20, health_bar_width * (player.health/PLAYER_MAX_HEALTH), 20))
        
        ammo_text = font.render(f'AMMO: {player.ammo}', True, TEXT_COLOR)
        screen.blit(ammo_text, (WIDTH - 150, 20))
        
        level_text = font.render(f'LEVEL: {current_level}', True, TEXT_COLOR)
        screen.blit(level_text, (WIDTH//2 - 50, 20))

        if game_over:
            game_over_text = font.render("GAME OVER - Press R to restart", True, TEXT_COLOR)
            screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))

        pygame.display.flip()

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[K_r]:
                main()
                return

if __name__ == '__main__':
    main()