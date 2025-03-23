import pygame, math
from constants import PLAYER_SPEED, PLAYER_SIZE, PLAYER_MAX_HEALTH, HEALTH_PACK_AMOUNT, AMMO_PACK_AMOUNT, GUN_COMPANION
from CompanionBullet import CompanionBullet
from constants import PLAYER_SPEED, PLAYER_SIZE, PLAYER_MAX_HEALTH, HEALTH_PACK_AMOUNT, AMMO_PACK_AMOUNT, GUN_COMPANION
from CompanionBullet import CompanionBullet

class Companion:
    def __init__(self, pos, comp_type):
        self.pos = pygame.Vector2(pos)
        self.speed = PLAYER_SPEED * 0.5  # slower speed to create lag effect
        self.size = PLAYER_SIZE  # Set the size to be the same as the player's size
        self.speed = PLAYER_SPEED * 0.5  # slower speed to create lag effect
        self.size = PLAYER_SIZE  # Set the size to be the same as the player's size
        self.type = comp_type  # "gun", "knife", "medic", or "bomb"
        self.health = 100
        self.last_action = 0
        self.action_cooldown = 1000  # milliseconds cooldown
        # Load an image for the companion (gun companion for example)
        self.image = pygame.image.load(GUN_COMPANION).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.original_image = self.image  # Store the original image for rotation
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        self.bullets = []
        self.angle = 0  # Initial angle

    def update(self, player, zombies, obstacles):
        # Follow the main player with a small offset based on type.
        offset = {
            "gun": pygame.Vector2(60, 0),
            "knife": pygame.Vector2(-60, 0),
            "medic": pygame.Vector2(0, 60),
            "bomb": pygame.Vector2(0, -60)
        }.get(self.type, pygame.Vector2(50, 50))
        target_pos = player.pos + offset
        direction = target_pos - self.pos
        if direction.length() > 0:
            new_pos = self.pos + direction.normalize() * self.speed
            new_rect = self.rect.copy()
            new_rect.center = new_pos

            # Check for collisions with obstacles (use obs directly)
            collision = any(new_rect.colliderect(obs) for obs in obstacles)
            if not collision:
                self.pos = new_pos

        current_time = pygame.time.get_ticks()
        # Unique ability based on companion type:
        if self.type == "gun":
            # If a zombie is within 300 pixels, shoot it.
            if zombies and current_time - self.last_action > self.action_cooldown:
                closest = min(zombies, key=lambda z: (z.pos - self.pos).length())
                if (closest.pos - self.pos).length() < 300:
                    bullet_direction = closest.pos - self.pos
                    self.bullets.append(CompanionBullet(self.pos, bullet_direction))
                    bullet_direction = closest.pos - self.pos
                    self.bullets.append(CompanionBullet(self.pos, bullet_direction))
                    self.last_action = current_time
                    self.angle = math.degrees(math.atan2(bullet_direction.y, bullet_direction.x))
                    self.angle = math.degrees(math.atan2(bullet_direction.y, bullet_direction.x))
        elif self.type == "knife":
            # Perform knife attack on any zombie within 50 pixels.
            if zombies and current_time - self.last_action > self.action_cooldown:
                for z in zombies:
                    if (z.pos - self.pos).length() < 50:
                        zombies.remove(z)
                        self.last_action = current_time
                        break
        elif self.type == "medic":
            # Heal the main player if their health is below 50.
            if player.health < 50 and current_time - self.last_action > self.action_cooldown:
                player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                self.last_action = current_time
        elif self.type == "bomb":
            # If more than two zombies are within 100 pixels, deploy a bomb.
            if len(zombies) > 2 and current_time - self.last_action > self.action_cooldown:
                affected = [z for z in zombies if (z.pos - self.pos).length() < 100]
                for z in affected:
                    if z in zombies:
                        zombies.remove(z)
                self.last_action = current_time

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.distance_traveled > bullet.max_distance:
                self.bullets.remove(bullet)

        self.rect.center = (self.pos.x, self.pos.y)

        # Update companion bullets.
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.distance_traveled > bullet.max_distance:
                self.bullets.remove(bullet)

        self.rect.center = (self.pos.x, self.pos.y)

    def draw(self, surface, offset):
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, (self.pos.x - offset.x - new_rect.width // 2, self.pos.y - offset.y - new_rect.height // 2))
        for bullet in self.bullets:
            bullet.draw(surface, offset)

        rotated_image = pygame.transform.rotate(self.original_image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, (self.pos.x - offset.x - new_rect.width // 2, self.pos.y - offset.y - new_rect.height // 2))
        for bullet in self.bullets:
            bullet.draw(surface, offset)