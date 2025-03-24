import pygame
import sys
from pygame.locals import *

# Define screen dimensions from constants
WIDTH = 1280
HEIGHT = 720

# Story slide class to handle each "frame" of the storyline
class StorySlide:
    def __init__(self, image_path, text):
        self.image = pygame.image.load(image_path).convert_alpha()
        # Scale image to fit screen while maintaining aspect ratio
        img_width, img_height = self.image.get_size()
        ratio = min(WIDTH / img_width, HEIGHT / img_height)
        self.image = pygame.transform.scale(self.image, 
                                           (int(img_width * ratio), int(img_height * ratio)))
        self.text = text
        
    def render(self, screen, font):
        # Center the image on screen
        img_width, img_height = self.image.get_size()
        x = (WIDTH - img_width) // 2
        y = (HEIGHT - img_height) // 2 - 50  # Offset to make room for text
        
        # Draw a semi-transparent black background for the entire screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw the image
        screen.blit(self.image, (x, y))
        
        # Render the text with word wrapping
        words = self.text.split(' ')
        lines = []
        current_line = []
        line_width = 0
        max_width = WIDTH - 100  # Margins on both sides
        
        for word in words:
            word_surface = font.render(word + ' ', True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            if line_width + word_width > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                line_width = word_width
            else:
                current_line.append(word)
                line_width += word_width
                
        if current_line:
            lines.append(' '.join(current_line))
        
        # Create a black rectangle for text background
        text_bg_height = len(lines) * 40 + 20  # Calculate height based on lines
        text_bg_surface = pygame.Surface((WIDTH - 40, text_bg_height), pygame.SRCALPHA)
        text_bg_surface.fill((0, 0, 0, 200))  # Black with some transparency
        text_bg_rect = text_bg_surface.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(text_bg_surface, text_bg_rect)
        
        # Draw each line of text
        y_text = text_bg_rect.top + 10  # Start a bit inside the black rectangle
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y_text))
            screen.blit(text_surface, text_rect)
            y_text += 40  # Line spacing
            
        # Draw "Press SPACE to continue" prompt
        prompt = font.render("Press SPACE to continue", True, (200, 200, 200))
        prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(prompt, prompt_rect)

# Function to play a sequence of story slides
def play_story_sequence(screen, slides, skip_key=K_SPACE):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28)
    
    for slide in slides:
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == skip_key:
                        waiting = False
                    elif event.key == K_ESCAPE:
                        return False  # Exit storyline completely
            
            # Render the current slide
            slide.render(screen, font)
            pygame.display.flip()
                
            clock.tick(30)
    
    return True  # Completed the storyline


# Level 1 storyline
def play_level1_story(screen):
    # Create slides for Level 1
    level1_slides = [
        StorySlide("assets/story/level1_1.png", 
                  "The virus has ravaged the world for 10-15 days—supplies are gone. "),
        StorySlide("assets/story/level1_2.png", 
                  "With no choice left, we arm up and head out."),
        StorySlide("assets/story/level1_3.png", 
                  "The two military brothers prepare for battle… the undead lurk, and it's time to fight back.")
    ]
    
    return play_story_sequence(screen, level1_slides)


# Level 2 storyline
def play_level2_story(screen):
    # Create slides for Level 2
    level2_slides = [
        StorySlide("assets/story/level1_1.png", 
                  "You've made it through the village square, but the extraction point was compromised. The infection has spread to the residential area."),
        StorySlide("assets/story/level1_1.png", 
                  "Reports indicate a military outpost has been established at the local school. That's your next destination."),
        StorySlide("assets/story/level1_1.png", 
                  "The infected are becoming more aggressive. You notice some mutations among them. Stay alert and conserve your ammunition.")
    ]
    
    return play_story_sequence(screen, level2_slides)


# Level 3 storyline
def play_level3_story(screen):
    # Create slides for Level 3
    level3_slides = [
        StorySlide("assets/story/level1_1.png", 
                  "The military outpost was abandoned. You found a radio transmitter with coordinates to a research facility on the outskirts of town."),
        StorySlide("assets/story/level1_1.png", 
                  "Scientists were working on a cure before communications went dark. Their research might be crucial for stopping this outbreak."),
        StorySlide("assets/story/level1_1.png", 
                  "You've noticed the infected are evolving. Some can now coordinate attacks. The situation is deteriorating rapidly.")
    ]
    
    return play_story_sequence(screen, level3_slides)


# Level 4 storyline
def play_level4_story(screen):
    # Create slides for Level 4
    level4_slides = [
        StorySlide("assets/story/level1_1.png", 
                  "The research facility is in chaos. You've recovered partial data about the infection's origin: a bioweapon experiment gone wrong."),
        StorySlide("assets/story/level1_1.png", 
                  "The facility's records mention a containment protocol activated in the underground lab beneath the town's hospital."),
        StorySlide("assets/story/level1_1.png", 
                  "You've gathered enough supplies for one final push. The hospital is crawling with infected, including new variants never seen before.")
    ]
    
    return play_story_sequence(screen, level4_slides)


# Level 5 storyline
def play_level5_story(screen):
    # Create slides for Level 5
    level5_slides = [
        StorySlide("assets/story/level1_1.png", 
                  "You've reached the hospital and found the entrance to the underground lab. The truth about the outbreak lies below."),
        StorySlide("assets/story/level1_1.png", 
                  "The lab's security systems are still operational. You'll need to navigate through automated defenses while fighting off the infected."),
        StorySlide("assets/story/level1_1.png", 
                  "Intelligence suggests the original strain is contained in the central chamber. Destroying it might stop the mutation process."),
        StorySlide("assets/story/level1_1.png", 
                  "This is your final mission. The fate of Arkham, and possibly the world, rests in your hands. Good luck, survivor.")
    ]
    
    return play_story_sequence(screen, level5_slides)


# Function to get storyline by level number
def play_level_story(screen, level_number):
    storyline_functions = {
        1: play_level1_story,
        2: play_level2_story,
        3: play_level3_story,
        4: play_level4_story,
        5: play_level5_story
    }
    
    # Default to level 1 if level_number is not found
    story_function = storyline_functions.get(level_number, play_level1_story)
    return story_function(screen)