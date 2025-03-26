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
                  "The virus has ravaged the world for weeks—supplies are running dry."),
        StorySlide("assets/story/level1_2.png", 
                  "We scavenge what little remains, but danger lurks in every shadow."),
        StorySlide("assets/story/level1_3.png", 
                  "With no choice left, we arm up and prepare to move out."),
        StorySlide("assets/story/level1_4.png", 
                  "The streets are eerily silent, but we know we're not alone."),
        StorySlide("assets/story/level1_5.png", 
                  "The undead wait in the darkness… and the fight for survival begins."),
        StorySlide("assets/story/level1_6.png", 
                  "Suddenly, a guttural growl breaks the silence. It’s too late to turn back."),
        StorySlide("assets/story/level1_7.png", 
                  "We brace ourselves as the first undead shuffles into view, its eyes locked onto us."),
        StorySlide("assets/story/level1_8.png", 
                  "The first shot rings out—this is just the beginning. The fight for survival has truly begun.")
    ]
    
    return play_story_sequence(screen, level1_slides)


# Level 2 storyline
def play_level2_story(screen):
    # Create slides for Level 2
    level2_slides = [
        StorySlide("assets/story/level2_1.png", 
                  "Night falls as we speed through the city, the streets eerily silent."),
        StorySlide("assets/story/level2_2.png", 
                  "The road ahead is barely visible—fog and wreckage block our path."),
        StorySlide("assets/story/level2_3.png", 
                  "Suddenly, a wrecked vehicle appears out of nowhere… there’s no time to react!"),
        StorySlide("assets/story/level2_4.png", 
                  "The car smashes into the wreckage—glass shatters, metal twists."),
        StorySlide("assets/story/level2_5.png", 
                  "Dazed, we barely process the crash… but then, we hear them."),
        StorySlide("assets/story/level2_6.png", 
                  "Shadows move in the darkness—grotesque figures closing in."),
        StorySlide("assets/story/level2_7.png", 
                  "The undead have found us. There’s no escape… we have to fight!")
    ]
    
    return play_story_sequence(screen, level2_slides)


def play_level3_story(screen):
    # Create slides for Level 3
    level3_slides = [
        StorySlide("assets/story/level3_1.png", 
                  "Night falls as we race through the city. The air feels heavy, and the streets are eerily silent. Something’s wrong… but we don't know what yet."),
        
        StorySlide("assets/story/level3_2.png", 
                  "Out of nowhere, a wrecked car emerges from the fog… We swerve, but it’s too late!"),
        
        StorySlide("assets/story/level3_3.png", 
                  "The impact is brutal—metal twists, glass shatters. We're thrown into darkness."),
        
        StorySlide("assets/story/level3_4.png", 
                  "Dazed, we barely process the crash, but then… the sounds hit us."),
        
        StorySlide("assets/story/level3_5.png", 
                  "Shadows move in the darkness—grotesque figures closing in, their eyes glowing with hunger."),
        
        StorySlide("assets/story/level3_6.png", 
                  "The thief steps forward, a grin spreading across his face. 'Time for a game,' he sneers. 'Are you ready to play?'"),
        
        StorySlide("assets/story/level3_7.png", 
                  "His companions emerge from the shadows, surrounding us. Their eyes burn with malice, and there's no way out."),
        
        StorySlide("assets/story/level3_8.png", 
                  "There's no turning back. It's time to play, or perish.")
    ]

    return play_story_sequence(screen, level3_slides)

# Level 4 storyline
def play_level4_story(screen):
    # Create slides for Level 4
    level4_slides = [
        StorySlide("assets/story/level4_1.png", 
                  "You barely escape the room, but hostile survivors spot you. They won't let you leave easily."),
        StorySlide("assets/story/level4_2.png", 
                  "You take cover inside an abandoned building. Footsteps echo as they close in."),
        StorySlide("assets/story/level4_3.png", 
                  "A broken weapons cache is in front of you. You scramble to arm yourself."),
        StorySlide("assets/story/level4_4.png", 
                  "The door slams open—armed men rush in, shouting. The fight is unavoidable."),
        StorySlide("assets/story/level4_5.png", 
                  "Gunfire erupts. Bullets pierce the silence. You must eliminate the threat to survive."),
        StorySlide("assets/story/level4_6.png", 
                  "Bodies litter the floor. You're injured, but you press on. The mission isn't over yet.")
    ]
    
    return play_story_sequence(screen, level4_slides)


# Level 5 storyline
def play_level5_story(screen):
    # Create slides for Level 5
    level5_slides = [
        StorySlide("assets/story/level5_1.png", 
                  "The cold, dark prison cell creaks as you force the rusted door open. Your head still throbs from being knocked out."),
        StorySlide("assets/story/level5_2.png", 
                  "Inside, a man—weak, bruised, but alive. 'Help me…' he pleads. You cut his restraints."),
        StorySlide("assets/story/level5_3.png", 
                  "He gasps, catching his breath. 'I’m a scientist… there’s a lab, a headquarters… inside, the antidote…'"),
        StorySlide("assets/story/level5_4.png", 
                  "Suddenly, distant gunfire! The walls tremble. You recognize that sound… your brother?"),
        StorySlide("assets/story/level5_5.png", 
                  "You and the scientist push forward, sneaking past fallen guards. The chaos outside grows louder."),
        StorySlide("assets/story/level5_6.png", 
                  "A burst of headlights cuts through the darkness—your brother pulls up in a military jeep, rifle raised."),
        StorySlide("assets/story/level5_7.png", 
                  "You climb in, the scientist barely keeping up. 'We need to get to the headquarters… Now!'"),
        StorySlide("assets/story/level5_8.png", 
                  "Without a second thought, the jeep speeds off, leaving the burning prison behind. The real fight is ahead."),
    ]
    
    return play_story_sequence(screen, level5_slides)


def play_level6_story(screen):
    # Create slides for Level 6
    level6_slides = [
        StorySlide("assets/story/level6_1.png", 
                  "You and Doc reach the headquarters. The eerie silence is suffocating, the air thick with tension."),

        StorySlide("assets/story/level6_2.png", 
                  "Your brother stays back to hold off the zombies. 'Go!' he shouts. You and Doc push forward."),

        StorySlide("assets/story/level6_3.png", 
                  "Inside, an overwhelming sense of dread settles in. Doc mutters, 'Something isn't right here…'"),

        
    ]

    return play_story_sequence(screen, level6_slides)

def play_level7_story(screen):
    # Create slides for Level 7
    level7_slides = [

         StorySlide("assets/story/level6_4.png", 
                  "At the control center, Doc points to a console. 'This will unlock the lab.' You hesitate, then press the button."),

        StorySlide("assets/story/level6_5.png", 
                  "The lab doors slide open. On the CCTV screen, a monstrous figure moves in the shadows. It’s massive… and it's coming."),
       
    ]

    return play_story_sequence(screen, level7_slides)

def play_level8_story(screen):
    # Create slides for Level 8
    level8_slides = [
        StorySlide("assets/story/level7_1.png", 
                  "You step into the abandoned lab. The air is stale, and the dim lights flicker ominously."),

        StorySlide("assets/story/level7_2.png", 
                  "Metallic crates are scattered everywhere. Doc mutters, 'The antidote has to be in one of these.'"),

        StorySlide("assets/story/level7_3.png", 
                  "You search frantically, but there’s no sign of it. Suddenly, a distant growl sends a chill down your spine."),

        StorySlide("assets/story/level7_4.png", 
                  "The emergency lights flicker red. A console in the corner displays: 'Security Override Required.'"),

        StorySlide("assets/story/level7_5.png", 
                  "To unlock the vault containing the antidote, you must bypass the lab’s security system… fast.")
    ]

    return play_story_sequence(screen, level8_slides)

def play_level9_story(screen):
    level9_slides = [
        StorySlide("assets/story/level8_1.png", 
                  "Reunited at last, you, your brother, and the doctor make it to the rooftop. The city burns below."),

        StorySlide("assets/story/level8_2.png", 
                  "Doc looks up at the helicopter. 'I used to fly one of these in the army,' he says. You exchange glances—it's your only way out."),

        StorySlide("assets/story/level8_3.png", 
                  "The rotors begin to spin as Doc takes the pilot’s seat. You and your brother jump inside, securing the doors."),

        StorySlide("assets/story/level8_4.png", 
                  "As the helicopter lifts off, zombies flood onto the rooftop, screeching and clawing. Just in time, you ascend into the night sky."),

        StorySlide("assets/story/level8_5.png", 
                  "The city stretches beneath you—fires rage, streets overrun. You finally breathe. 'We made it…' your brother mutters."),

        StorySlide("assets/story/level8_6.png", 
                  "As dawn breaks, the helicopter flies toward the horizon. The antidote is safe. A new hope begins. The nightmare is finally over.")
    ]

    return play_story_sequence(screen, level9_slides)
# Function to get storyline by level number
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
    
    # Default to level 1 if level_number is not found
    story_function = storyline_functions.get(level_number, play_level1_story)
    return story_function(screen)