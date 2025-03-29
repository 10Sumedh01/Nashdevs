import pygame
import sys
from pygame.locals import *

# Define screen dimensions
WIDTH = 1280
HEIGHT = 720

from sound import Sound

# Story slide class to handle each "frame" of the storyline
class StorySlide:
    def __init__(self, image_path, text, voiceover_path=None):
        self.image = pygame.image.load(image_path).convert_alpha()
        # Scale image to fit screen while maintaining aspect ratio
        img_width, img_height = self.image.get_size()
        ratio = min(WIDTH / img_width, HEIGHT / img_height)
        self.image = pygame.transform.scale(
            self.image, (int(img_width * ratio), int(img_height * ratio))
        )
        self.text = text
        self.voiceover_path = voiceover_path  # Store the voiceover file path
        
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
        text_bg_surface.fill((0, 0, 0, 200))  # Black with transparency
        text_bg_rect = text_bg_surface.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        screen.blit(text_bg_surface, text_bg_rect)
        
        # Draw each line of text
        y_text = text_bg_rect.top + 10  # Start a bit inside the rectangle
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
    
    current_voice_sound = None  # Keep track of the current slide's voiceover
    
    for slide in slides:
        waiting = True
        
        # Stop the previous slide's voiceover if it's playing
        if current_voice_sound:
            current_voice_sound.stop()
        
        # If the current slide has a voiceover, load and play it
        if slide.voiceover_path:
            current_voice_sound = Sound(slide.voiceover_path)
            current_voice_sound.play()
        else:
            current_voice_sound = None
        
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
    
    # Stop any remaining voiceover after all slides are done
    if current_voice_sound:
        current_voice_sound.pause()
        
    return True  # Completed the storyline

# --- LEVEL STORYLINES ---

def play_level1_story(screen):
    level1_slides = [
        StorySlide("assets/story/level1_1.png", 
                   "The virus has ravaged the world for weeks—supplies are running dry.",
                   "scenes/level1_6.mp3"),
        StorySlide("assets/story/level1_2.png", 
                   "We barricade the doors, rationing what little remains, hoping for a plan.",
                   "scenes/level1_7.mp3"),
        StorySlide("assets/story/level1_3.png", 
                   "Outside, the streets are filled with eerie silence, broken only by distant groans.",
                   "scenes/level1_8.mp3"),
        StorySlide("assets/story/level1_4.png", 
                   "The power is flickering. We know staying here isn't an option much longer.",
                   "scenes/level1_5.mp3"),
        StorySlide("assets/story/level1_5.png", 
                   "Arming ourselves with whatever we can find, we finally decide to leave.",
                   "scenes/level1_4.mp3"),
        StorySlide("assets/story/level1_6.png", 
                   "We cautiously step outside—the cold night air carries an unsettling stillness.",
                   "scenes/level1_3.mp3"),
        StorySlide("assets/story/level1_7.png", 
                   "A guttural growl breaks the silence. It’s too late to turn back.",
                   "scenes/level1_2.mp3"),
        StorySlide("assets/story/level1_8.png", 
                   "The first shot rings out—this is just the beginning. The fight for survival has truly begun.",
                   "scenes/level1_1.mp3"),
    ]
    return play_story_sequence(screen, level1_slides)

def play_level2_story(screen):
    level2_slides = [
        StorySlide("assets/story/level2_1.png", 
                   "Night falls as we speed through the city, the streets eerily silent.",
                   "scenes/level2_1.mp3"),
        StorySlide("assets/story/level2_2.png", 
                   "The road ahead is barely visible—fog and wreckage block our path.",
                   "scenes/level2_2.mp3"),
        StorySlide("assets/story/level2_3.png", 
                   "Suddenly, a wrecked vehicle appears out of nowhere… there’s no time to react!",
                   "scenes/level2_3.mp3"),
        StorySlide("assets/story/level2_4.png", 
                   "The car smashes into the wreckage—glass shatters, metal twists.",
                   "scenes/level2_4.mp3"),
        StorySlide("assets/story/level2_5.png", 
                   "Dazed, we barely process the crash… but then, we hear them.",
                   "scenes/level2_5.mp3"),
        StorySlide("assets/story/level2_6.png", 
                   "Shadows move in the darkness—grotesque figures closing in.",
                   "scenes/level2_6.mp3"),
        StorySlide("assets/story/level2_7.png", 
                   "The undead have found us. There’s no escape… we have to fight!",
                   "scenes/level2_7.mp3"),
    ]
    return play_story_sequence(screen, level2_slides)

def play_level3_story(screen):
    level3_slides = [
        StorySlide("assets/story/level3_1.png", 
                   "The battle rages..we fight desperately dodging and striking.",
                   "scenes/level3_1.mp3"),
        StorySlide("assets/story/level3_2.png", 
                   "A car speeds in..Screeching to the halt. A door flings open.",
                   "scenes/level3_2.mp3"),
        StorySlide("assets/story/level3_3.png", 
                   "No time to think—we jump in. A sharp sting… vision fades.",
                   "scenes/level3_3.mp3"),
        StorySlide("assets/story/level3_4.png", 
                   "Darkness. Voices murmur. My wrists are bound.",
                   "scenes/level3_4.mp3"),
        StorySlide("assets/story/level3_5.png", 
                   "A dim light flickers—shadows loom over us.",
                   "scenes/level3_5.mp3"),
        StorySlide("assets/story/level3_6.png", 
                   "A scream. Someone collapses. Blood stains the floor.",
                   "scenes/level3_6.mp3"),
        StorySlide("assets/story/level3_7.png", 
                   "A smirking figure steps forward. 'You want to live?'",
                   "scenes/level3_7.mp3"),
        StorySlide("assets/story/level3_8.png", 
                   "'Win… or die.' The game begins.",
                   "scenes/level3_8.mp3"),
    ]
    return play_story_sequence(screen, level3_slides)

def play_level4_story(screen):
    level4_slides = [
        StorySlide("assets/story/level4_1.png", 
                   "You barely escape the room, but hostile survivors spot you. They won't let you leave easily.",
                   "scenes/level4_1.mp3"),
        StorySlide("assets/story/level4_2.png", 
                   "You take cover inside an abandoned building. Footsteps echo as they close in.",
                   "scenes/level4_2.mp3"),
        StorySlide("assets/story/level4_3.png", 
                   "A broken weapons cache is in front of you. You scramble to arm yourself.",
                   "scenes/level4_3.mp3"),
        StorySlide("assets/story/level4_4.png", 
                   "The door slams open—armed men rush in, shouting. The fight is unavoidable.",
                   "scenes/level4_4.mp3"),
        StorySlide("assets/story/level4_5.png", 
                   "Gunfire erupts. Bullets pierce the silence. You must eliminate the threat to survive.",
                   "scenes/level4_5.mp3"),
        StorySlide("assets/story/level4_6.png", 
                   "Bodies litter the floor. You're injured, but you press on. The mission isn't over yet.",
                   "scenes/level4_6.mp3"),
    ]
    return play_story_sequence(screen, level4_slides)

def play_level5_story(screen):
    level5_slides = [
        StorySlide("assets/story/level5_1.png", 
                   "The cold, dark prison cell creaks as you force the rusted door open. Your head still throbs.",
                   "scenes/level5_1.mp3"),
        StorySlide("assets/story/level5_2.png", 
                   "Inside, a man—weak, bruised, but alive. 'Help me…' he pleads. You cut his restraints.",
                   "scenes/level5_2.mp3"),
        StorySlide("assets/story/level5_3.png", 
                   "'I’m a scientist… there's a lab… an antidote…' he gasps, eyes wide with fear.",
                   "scenes/level5_3.mp3"),
        StorySlide("assets/story/level5_4.png", 
                   "Distant gunfire shakes the walls. You recognize that sound… your brother?",
                   "scenes/level5_4.mp3"),
        StorySlide("assets/story/level5_5.png", 
                   "You and the scientist sneak past fallen guards. The chaos outside grows louder.",
                   "scenes/level5_5.mp3"),
        StorySlide("assets/story/level5_6.png", 
                   "A burst of headlights—your brother arrives in a military jeep, rifle raised.",
                   "scenes/level5_6.mp3"),
        StorySlide("assets/story/level5_7.png", 
                   "You climb in, the scientist barely keeping up. 'We need to reach the headquarters… now!'",
                   "scenes/level5_7.mp3"),
        StorySlide("assets/story/level5_8.png", 
                   "No time to waste—the jeep speeds off, leaving the burning prison behind.",
                   "scenes/level5_8.mp3"),
    ]
    return play_story_sequence(screen, level5_slides)

def play_level6_story(screen):
    level6_slides = [
        StorySlide("assets/story/level6_1.png", 
                   "You and Doc reach the headquarters. The eerie silence is suffocating, the air thick with tension.",
                   "scenes/level6_1.mp3"),
        StorySlide("assets/story/level6_2.png", 
                   "Your brother stays back to hold off the zombies. 'Go!' he shouts. You and Doc push forward.",
                   "scenes/level6_2.mp3"),
        StorySlide("assets/story/level6_3.png", 
                   "Inside, an overwhelming dread settles in. Doc mutters, 'Something isn't right…'",
                   "scenes/level6_3.mp3"),
    ]
    return play_story_sequence(screen, level6_slides)

def play_level7_story(screen):
    level7_slides = [
        StorySlide("assets/story/level6_4.png", 
                   "At the control center, Doc points to a console. 'This will unlock the lab.' You hesitate, then press the button.",
                   "scenes/level6_4.mp3"),
        StorySlide("assets/story/level6_5.png", 
                   "The lab doors slide open. On the CCTV, a massive figure lurks in the shadows… and it's coming.",
                   "scenes/level6_5.mp3"),
    ]
    return play_story_sequence(screen, level7_slides)

def play_level8_story(screen):
    level8_slides = [
        StorySlide("assets/story/level7_1.png", 
                   "You step into the abandoned lab. The air is stale, and the dim lights flicker ominously.",
                   "scenes/level7_1.mp3"),
        StorySlide("assets/story/level7_2.png", 
                   "Metallic crates are scattered everywhere. Doc mutters, 'The antidote must be in one of these.'",
                   "scenes/level7_2.mp3"),
        StorySlide("assets/story_7_3.png", 
                   "You search frantically, but there's no sign of it. A distant growl sends a chill down your spine.",
                   "scenes/level7_3.mp3"),
        StorySlide("assets/story_7_4.png", 
                   "The emergency lights flicker red. A console displays: 'Security Override Required.'",
                   "scenes/level7_4.mp3"),
        StorySlide("assets/story_7_5.png", 
                   "To unlock the vault with the antidote, you must bypass the security system… fast.",
                   "scenes/level7_5.mp3"),
    ]
    return play_story_sequence(screen, level8_slides)

def play_level9_story(screen):
    level9_slides = [
        StorySlide("assets/story/level8_1.png", 
                   "Reunited, you, your brother, and Doc make it to the rooftop. The city burns below.",
                   "scenes/level8_1.mp3"),
        StorySlide("assets/story/level8_2.png", 
                   "Doc glances at the helicopter. 'I used to fly these...' he murmurs. It's our escape.",
                   "scenes/level8_2.mp3"),
        StorySlide("assets/story/level8_3.png", 
                   "The rotors spin as Doc takes the pilot’s seat. You and your brother secure the doors.",
                   "scenes/level8_3.mp3"),
        StorySlide("assets/story/level8_4.png", 
                   "As the chopper lifts off, zombies flood the rooftop. You ascend into the night.",
                   "scenes/level8_4.mp3"),
        StorySlide("assets/story/level8_5.png", 
                   "Fires rage below, the city overrun. Your brother sighs, 'We made it…'",
                   "scenes/level8_5.mp3"),
        StorySlide("assets/story/level8_6.png", 
                   "Dawn breaks as the helicopter soars. The antidote is safe. Hope returns—the nightmare ends… for now.",
                   "scenes/level8_6.mp3"),
    ]
    return play_story_sequence(screen, level9_slides)

def play_level_story(screen, level_number):
    storyline_functions = {
        1: play_level1_story,
        2: play_level2_story,
        3: play_level3_story,
        4: play_level4_story,
        5: play_level5_story,
        6: play_level6_story,
        7: play_level7_story,
        8: play_level8_story,
        9: play_level9_story
    }
    story_function = storyline_functions.get(level_number, play_level1_story)
    return story_function(screen)