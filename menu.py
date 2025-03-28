import pygame
import sys
from button import Button
from main import main
from sound import Sound
from Endless import endless_mode

menu_sound = Sound('menu_bg.mp3')
btn_click_sound = Sound('btn_click.mp3')

pygame.init()
SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Menu")
BG = pygame.image.load("assets/Background.png")

def get_font(size): 
    return pygame.font.Font("assets/font.ttf", size)

def play():
    # Directly start the main game
    main()

def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()
        SCREEN.fill("white")

        # Render the controls text
        OPTIONS_TEXT = get_font(45).render("CONTROLS", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        # List of controls
        controls = [
            "W/A/S/D: Move the player",
            "Mouse: Aim and shoot",
            "Left Click: Shoot",
            "Right Click: Use knife (if equipped)",
            "P: Pause the game",
            "C: Toggle companion visibility",
            "O: Switch weapons",
            "E: Toggle knife"
        ]

        # Render each control line
        for i, control in enumerate(controls):
            control_text = get_font(30).render(control, True, "Black")
            control_rect = control_text.get_rect(center=(640, 160 + i * 40))
            SCREEN.blit(control_text, control_rect)

        # Back button
        OPTIONS_BACK = Button(image=None, pos=(640, 600),
                            text_input="BACK", font=get_font(50), base_color="Black", hovering_color="Green")
        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    menu_sound.play_loop()
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # Render the main menu title
        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        # Adjust the vertical positions of the buttons
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 250),
                            text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        ENDLESS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 370),
                                text_input="ENDLESS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        CONTROLS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(640, 490),
                                text_input="CONTROLS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 610),
                            text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        # Draw the menu title and buttons
        SCREEN.blit(MENU_TEXT, MENU_RECT)
        for button in [PLAY_BUTTON, ENDLESS_BUTTON, CONTROLS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn_click_sound.play()
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    menu_sound.pause()
                    play()  # This will now directly start the game
                if ENDLESS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    menu_sound.pause()
                    endless_mode()
                if CONTROLS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    menu_sound.pause()
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

if __name__ == "__main__":
    main_menu()