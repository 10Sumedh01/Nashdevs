import pygame
import math
from constants import PLAYER_IMAGE_PATH, EXKNIFE_IMAGE, PLAYER_SIZE, PLAYER_MAX_HEALTH, PLAYER_START_AMMO, BULLET_RANGE
from Bullet import Bullet

class Player:
    def __init__(self, pos=(0,0)):
        self.pos = pygame.Vector2(pos)
        self.speed = 5
        self.size = PLAYER_SIZE
        self.health = PLAYER_MAX_HEALTH
        self.ammo = PLAYER_START_AMMO
        self.angle = 0
        self.invincible = False
        self.invincible_duration = 1000  # milliseconds
        self.last_hit = 0

        # Load images:
        # Gun mode image
        self.gun_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
        self.gun_image = pygame.transform.scale(self.gun_image, (PLAYER_SIZE, PLAYER_SIZE))
        # Normal knife-holding image (when knife mode is active but not attacking)
        self.knife_normal_image = pygame.image.load("assets/knifeplayer.png").convert_alpha()
        self.knife_normal_image = pygame.transform.scale(self.knife_normal_image, (PLAYER_SIZE, PLAYER_SIZE))
        # Knife attack image (for the brief attack animation)
        self.knife_attack_image = pygame.image.load(EXKNIFE_IMAGE).convert_alpha()
        self.knife_attack_image = pygame.transform.scale(self.knife_attack_image, (PLAYER_SIZE, PLAYER_SIZE))
        
        # Start in gun mode
        self.has_knife = False  
        self.current_image = self.gun_image
        self.rect = self.current_image.get_rect(center=self.pos)
        
        # Knife attack animation parameters
        self.knife_attack_active = False
        self.knife_attack_duration = 200  # milliseconds
        self.knife_attack_start = 0

    def toggle_knife(self):
        """Toggle between gun mode and knife mode.
           When toggled to knife mode, display the normal knife-holding image."""
        self.has_knife = not self.has_knife
        self.current_image = self.knife_normal_image if self.has_knife else self.gun_image

    def use_knife(self):
        """Activate the knife attack animation if in knife mode.
           Temporarily set the sprite to the knife attack image."""
        if self.has_knife:
            self.knife_attack_active = True
            self.knife_attack_start = pygame.time.get_ticks()
            self.current_image = self.knife_attack_image

    def knife_attack(self, zombies):
        """Return a list of zombies within 80 pixels.
           Iterates over a copy of the zombie list to avoid crashes."""
        attack_range = 80
        attacked = []
        for z in list(zombies):
            if (self.pos - z.pos).length() < attack_range:
                attacked.append(z)
        return attacked

    def shoot(self, target_pos):
        """Example shooting method (not used in knife mode)."""
        if self.ammo > 0:
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        return None

    def take_damage(self, damage):
        """Reduces player health if not invincible, and triggers invincibility."""
        if not self.invincible:
            self.health = max(0, self.health - damage)
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_duration:
            self.invincible = False

    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y += self.speed
        if move.length() > 0:
            move = move.normalize() * self.speed

        old_pos = self.pos.copy()
        self.pos += move

        # Check collisions with obstacles
        for obs in obstacles:
            if self.get_rect().colliderect(obs):
                self.pos = old_pos
                break

        # Revert knife attack image after duration
        if self.knife_attack_active and pygame.time.get_ticks() - self.knife_attack_start >= self.knife_attack_duration:
            self.current_image = self.knife_normal_image if self.has_knife else self.gun_image
            self.knife_attack_active = False

        self.rect = self.current_image.get_rect(center=self.pos)

    def update_rotation(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0:
            self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                           self.pos.y - self.size//2,
                           self.size, self.size)

    def draw(self, surface, offset, current_level=None):
        rotated_image = pygame.transform.rotate(self.current_image, self.angle)
        rect = rotated_image.get_rect(center=self.pos - offset)
        surface.blit(rotated_image, rect.topleft)
