import pygame
from constants import PLAYER_MAX_HEALTH,WIDTH,HEIGHT,PLAYER_SPEED,PLAYER_SIZE,PLAYER_START_AMMO,PLAYER_COLOR
from Bullet import Bullet

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
        self.speed = PLAYER_SPEED
        self.size = PLAYER_SIZE
        self.health = PLAYER_MAX_HEALTH
        self.ammo = PLAYER_START_AMMO
        self.last_hit = 0
        self.invincible = False
        self.invincible_duration = 1000
        self.flashlight = True

    def take_damage(self, damage):
        if not self.invincible:
            self.health = max(0, self.health - damage)
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_duration:
            self.invincible = False

    def shoot(self, target_pos):
        if self.ammo > 0:
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        return None

    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: move.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move.y += self.speed

        if move.length() > 0:
            move = move.normalize() * self.speed

        old_pos = self.pos.copy()
        self.pos += move
        for obs in obstacles:
            if self.get_rect().colliderect(obs.get_rect()):
                self.pos = old_pos
                break

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                         self.pos.y - self.size//2,
                         self.size, self.size)

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)
        
        if self.flashlight:
            flashlight_radius = 250
            mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 200))
            pygame.draw.circle(mask, (0, 0, 0, 0), 
                             (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), 
                             flashlight_radius)
            surface.blit(mask, (0, 0))