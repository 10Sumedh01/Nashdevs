import pygame

class ToxicPuddle:
    def __init__(self, position, duration=5000, damage=5):
        """
        Initialize the toxic puddle.
        :param position: The position of the puddle (pygame.Vector2).
        :param duration: How long the puddle lasts (in milliseconds).
        :param damage: Damage dealt to the player per second.
        """
        self.position = position
        self.duration = duration
        self.damage = damage
        self.start_time = pygame.time.get_ticks()
        self.image = pygame.image.load('assets/spit.png').convert_alpha()
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))
        self.radius = 100

    def update(self):
        """
        Check if the puddle's duration has expired.
        :return: True if the puddle should be removed, False otherwise.
        """
        current_time = pygame.time.get_ticks()
        return current_time - self.start_time > self.duration

    def draw(self, screen, offset):
        """
        Draw the puddle on the screen.
        :param screen: The game screen.
        :param offset: The camera offset.
        """
        screen.blit(self.image, self.position - offset - pygame.Vector2(60,40))