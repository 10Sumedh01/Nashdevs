# levelManager.py
import pygame
from constants import WIDTH, HEIGHT, FPS

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.level_start_time = pygame.time.get_ticks()
        self.level_intro_duration = 3000  # Show level intro for 3 seconds
        self.level_texts = {
            1: "Level 1: Home",
            2: "Level 2: Nearby Area",
            3: "Nightmare Level",
            4: "City Area - Level 4",
            5: "City Area - Level 5",
            6: "Human Interaction Level",
            7: "Armed and Ready - Level 7",
            8: "Armed and Ready - Level 8",
            9: "Doctor's Puzzle - Level 9",
            10: "Final Army Base - Level 10"
        }
        self.level_duration = 30000  # For demonstration, 30 seconds per level

    def update_level(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time >= self.level_duration:
            self.current_level += 1
            self.level_start_time = current_time
            return True  # Level changed
        return False

    def draw_level_intro(self, screen, font):
        current_time = pygame.time.get_ticks()
        if current_time - self.level_start_time < self.level_intro_duration:
            text = self.level_texts.get(self.current_level, f"Level {self.current_level}")
            intro_text = font.render(text, True, (255, 255, 255))
            rect = intro_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(intro_text, rect)
