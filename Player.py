import pygame
import math
import random
from constants import (
    PLAYER_MAX_HEALTH, PLAYER_START_AMMO, BULLET_RANGE, PLAYER_SIZE,
    PLAYER_PISTOL_IMAGE_PATH, PLAYER_SHOTGUN_IMAGE_PATH, PLAYER_AKM_IMAGE_PATH,
    PISTOL_IMAGE_PATH, SHOTGUN_IMAGE_PATH, AKM_IMAGE_PATH, EXKNIFE_IMAGE
)
from Bullet import Bullet
from sound import Sound

shotgun_sound = Sound('shotgun.mp3')
shotgun_sound.set_volume(0.5)
pistol_sound = Sound('pistol.mp3')
akm_sound = Sound('akm.mp3')
gun_switch_sound = Sound('gun_switch.mp3')
knife_sound = Sound('knife_stab.mp3')
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

        # Gun modes: pistol, shotgun, akm.
        self.gun_modes = ['pistol', 'shotgun', 'akm']
        self.current_gun_index = 0
        self.gun_mode = self.gun_modes[self.current_gun_index]
        
        # Load images for player sprite.
        self.pistol_image = pygame.image.load(PLAYER_PISTOL_IMAGE_PATH).convert_alpha()
        self.pistol_image = pygame.transform.scale(self.pistol_image, (PLAYER_SIZE, PLAYER_SIZE))
        
        self.shotgun_image = pygame.image.load(PLAYER_SHOTGUN_IMAGE_PATH).convert_alpha()
        self.shotgun_image = pygame.transform.scale(self.shotgun_image, (PLAYER_SIZE, PLAYER_SIZE))
        
        self.akm_image = pygame.image.load(PLAYER_AKM_IMAGE_PATH).convert_alpha()
        self.akm_image = pygame.transform.scale(self.akm_image, (PLAYER_SIZE, PLAYER_SIZE))
        
        # Load arsenal images (for display in the arsenal rectangle).
        self.pistol_arsenal = pygame.image.load(PISTOL_IMAGE_PATH).convert_alpha()
        self.pistol_arsenal = pygame.transform.scale(self.pistol_arsenal, (50, 50))
        
        self.shotgun_arsenal = pygame.image.load(SHOTGUN_IMAGE_PATH).convert_alpha()
        self.shotgun_arsenal = pygame.transform.scale(self.shotgun_arsenal, (50, 50))
        
        self.akm_arsenal = pygame.image.load(AKM_IMAGE_PATH).convert_alpha()
        self.akm_arsenal = pygame.transform.scale(self.akm_arsenal, (50, 50))
        
        # Set initial images.
        self.current_image = self.pistol_image
        self.arsenal_img = self.pistol_arsenal
        
        # For collision/position.
        self.rect = self.current_image.get_rect(center=self.pos)
        
        # Knife attributes.
        self.has_knife = False
        self.knife_normal_image = pygame.image.load("assets/knifeplayer.png").convert_alpha()
        self.knife_normal_image = pygame.transform.scale(self.knife_normal_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.knife_attack_image = pygame.image.load(EXKNIFE_IMAGE).convert_alpha()
        self.knife_attack_image = pygame.transform.scale(self.knife_attack_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.knife_attack_active = False
        self.knife_attack_duration = 200  # milliseconds
        self.knife_attack_start = 0

    def toggle_knife(self):
        self.has_knife = not self.has_knife
        if not self.has_knife:
            self.current_image = self.get_gun_image()
        else:
            self.current_image = self.knife_normal_image

    def switch_gun(self):
        """Cycle to the next gun mode: pistol -> shotgun -> akm -> pistol."""
        gun_switch_sound.play()
        self.current_gun_index = (self.current_gun_index + 1) % len(self.gun_modes)
        self.gun_mode = self.gun_modes[self.current_gun_index]
        if not self.has_knife:
            self.current_image = self.get_gun_image()
        self.arsenal_img = self.get_arsenal_image()

    def get_gun_image(self):
        if self.gun_mode == 'pistol':
            return self.pistol_image
        elif self.gun_mode == 'shotgun':
            return self.shotgun_image
        elif self.gun_mode == 'akm':
            return self.akm_image
        else:
            return self.pistol_image

    def get_arsenal_image(self):
        if self.gun_mode == 'pistol':
            return self.pistol_arsenal
        elif self.gun_mode == 'shotgun':
            return self.shotgun_arsenal
        elif self.gun_mode == 'akm':
            return self.akm_arsenal
        else:
            return self.pistol_arsenal

    def shoot(self, target_pos):
        """Fire bullets based on the current gun mode.
           If knife is active, do not shoot bullets."""
        if self.has_knife:
            return None
        if self.ammo <= 0:
            return None
        if self.gun_mode == 'pistol':
            pistol_sound.play()
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        elif self.gun_mode == 'shotgun':
            shotgun_sound.set_volume(0.5)
            shotgun_sound.play()
            self.ammo -= 1
            bullets = []
            base_direction = (target_pos - self.pos).normalize()
            for angle_offset in [-15, 0, 15]:
                rotated = base_direction.rotate(angle_offset)
                bullets.append(Bullet(self.pos.copy(), rotated))
            return bullets
        elif self.gun_mode == 'akm':
            akm_sound.play()
            self.ammo -= 1
            bullets = []
            base_direction = (target_pos - self.pos).normalize()
            for _ in range(5):
                deviation = random.uniform(-2, 2)
                rotated = base_direction.rotate(deviation)
                bullets.append(Bullet(self.pos.copy(), rotated))
            return bullets
        else:
            return None

    def use_knife(self):
        """Trigger knife attack animation."""
        if self.has_knife:
            self.knife_attack_active = True
            self.knife_attack_start = pygame.time.get_ticks()
            knife_sound.play()
            self.current_image = self.knife_attack_image

    def knife_attack(self, zombies):
        """Return a list of zombies within 80 pixels for knife attack."""
        attack_range = 80
        attacked = []
        for z in list(zombies):
            if (self.pos - z.pos).length() < attack_range:
                attacked.append(z)
        return attacked

    def take_damage(self, damage):
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
        for obs in obstacles:
            if self.get_rect().colliderect(obs):
                self.pos = old_pos
                break
        if self.knife_attack_active and pygame.time.get_ticks() - self.knife_attack_start >= self.knife_attack_duration:
            self.current_image = self.knife_normal_image if self.has_knife else self.get_gun_image()
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
        rotated = pygame.transform.rotate(self.current_image, self.angle)
        rect = rotated.get_rect(center=self.pos - offset)
        surface.blit(rotated, rect.topleft)
