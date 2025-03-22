# Companion.py
import pygame, math
from constants import PLAYER_SPEED, PLAYER_SIZE, PLAYER_MAX_HEALTH, HEALTH_PACK_AMOUNT, AMMO_PACK_AMOUNT

class Companion:
    def __init__(self, pos, comp_type):
        self.pos = pygame.Vector2(pos)
        self.speed = PLAYER_SPEED * 0.9  # slightly slower than the main player
        self.size = PLAYER_SIZE
        self.type = comp_type  # "gun", "knife", "medic", or "bomb"
        self.health = 100
        self.last_action = 0
        self.action_cooldown = 1000  # milliseconds cooldown
        # Use different colors to represent companions (for simplicity)
        if self.type == "gun":
            self.color = (0, 0, 255)
        elif self.type == "knife":
            self.color = (255, 255, 0)
        elif self.type == "medic":
            self.color = (0, 255, 255)
        elif self.type == "bomb":
            self.color = (255, 0, 255)

    def update(self, player, zombies, obstacles):
        # Follow the main player with a small offset based on type
        offset = {
            "gun": pygame.Vector2(60, 0),
            "knife": pygame.Vector2(-60, 0),
            "medic": pygame.Vector2(0, 60),
            "bomb": pygame.Vector2(0, -60)
        }.get(self.type, pygame.Vector2(50,50))
        target_pos = player.pos + offset
        direction = target_pos - self.pos
        if direction.length() > 0:
            self.pos += direction.normalize() * self.speed

        current_time = pygame.time.get_ticks()
        # Unique ability based on companion type:
        if self.type == "gun":
            # If a zombie is within 300 pixels, shoot it
            if zombies and current_time - self.last_action > self.action_cooldown:
                closest = min(zombies, key=lambda z: (z.pos - self.pos).length())
                if (closest.pos - self.pos).length() < 300:
                    zombies.remove(closest)
                    self.last_action = current_time
        elif self.type == "knife":
            # Perform knife attack on any zombie within 50 pixels
            if zombies and current_time - self.last_action > self.action_cooldown:
                for z in zombies:
                    if (z.pos - self.pos).length() < 50:
                        zombies.remove(z)
                        self.last_action = current_time
                        break
        elif self.type == "medic":
            # Heal the main player if their health is below 50
            if player.health < 50 and current_time - self.last_action > self.action_cooldown:
                player.health = min(PLAYER_MAX_HEALTH, player.health + HEALTH_PACK_AMOUNT)
                self.last_action = current_time
        elif self.type == "bomb":
            # If more than two zombies are within 100 pixels, deploy a bomb
            if len(zombies) > 2 and current_time - self.last_action > self.action_cooldown:
                affected = [z for z in zombies if (z.pos - self.pos).length() < 100]
                for z in affected:
                    if z in zombies:
                        zombies.remove(z)
                self.last_action = current_time

    def draw(self, surface, offset):
        pygame.draw.circle(surface, self.color, (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), self.size // 2)
