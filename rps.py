import pygame
import random
import numpy as np

def rock_paper_scissors_minigame(screen):
    # ----- Perceptron Model -----
    class Perceptron:
        def __init__(self, input_size=3, num_classes=3, learning_rate=0.1):
            self.weights = np.random.randn(num_classes, input_size) * 0.01
            self.learning_rate = learning_rate

        def predict(self, x):
            scores = np.dot(self.weights, x)
            return np.argmax(scores)

        def update(self, x, target):
            prediction = self.predict(x)
            if prediction != target:
                self.weights[target] += self.learning_rate * x
                self.weights[prediction] -= self.learning_rate * x

    # ----- Helper Functions -----
    def move_to_vector(move):
        vec = np.zeros(3)
        vec[move] = 1
        return vec

    def counter_move(predicted_move):
        return (predicted_move + 1) % 3

    def draw_buttons(surface, buttons, font):
        for btn in buttons:
            pygame.draw.rect(surface, btn['color'], btn['rect'])
            pygame.draw.rect(surface, (50, 50, 50), btn['rect'], 2)
            text_surf = font.render(btn['label'], True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=btn['rect'].center)
            surface.blit(text_surf, text_rect)

    # ----- Game Settings -----
    WIDTH, HEIGHT = 600, 500
    TOTAL_ROUNDS = 3
    BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50

    # Colors
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (220, 220, 220)
    DARK_GRAY = (50, 50, 50)
    BLUE = (70, 130, 180)
    BACKGROUND = (245, 245, 245)

    moves = ["Rock", "Paper", "Scissors"]

    # Create fonts once
    FONT_LARGE = pygame.font.SysFont("Arial", 48)
    FONT_MEDIUM = pygame.font.SysFont("Arial", 32)
    FONT_SMALL = pygame.font.SysFont("Arial", 24)

    clock = pygame.time.Clock()

    # Game Variables
    current_round = 0
    player_score = 0
    ai_score = 0
    result_text = ""
    player_move_text = ""
    ai_move_text = ""
    game_over = False
    last_player_move = None

    # Create a perceptron instance
    perceptron = Perceptron()

    # Define buttons
    rock_button = pygame.Rect(50, HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT)
    paper_button = pygame.Rect((WIDTH - BUTTON_WIDTH) // 2, HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT)
    scissors_button = pygame.Rect(WIDTH - 50 - BUTTON_WIDTH, HEIGHT - 80, BUTTON_WIDTH, BUTTON_HEIGHT)
    buttons = [
        {'rect': rock_button, 'label': "Rock", 'color': LIGHT_GRAY},
        {'rect': paper_button, 'label': "Paper", 'color': LIGHT_GRAY},
        {'rect': scissors_button, 'label': "Scissors", 'color': LIGHT_GRAY}
    ]

    def reset_game():
        nonlocal current_round, player_score, ai_score, result_text, player_move_text, ai_move_text, game_over, last_player_move, perceptron
        current_round = 0
        player_score = 0
        ai_score = 0
        result_text = ""
        player_move_text = ""
        ai_move_text = ""
        game_over = False
        last_player_move = None
        perceptron = Perceptron()

    # ----- Main Game Loop -----
    running = True
    while running:
        screen.fill(BACKGROUND)
        
        # Render header and score
        header = FONT_LARGE.render("Rock Paper Scissors", True, DARK_GRAY)
        screen.blit(header, ((WIDTH - header.get_width()) // 2, 20))
        
        score_str = f"Round: {current_round}/{TOTAL_ROUNDS}   You: {player_score}   AI: {ai_score}"
        score_text = FONT_MEDIUM.render(score_str, True, DARK_GRAY)
        screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, 90))
        
        # Display moves and result if available
        if player_move_text:
            pm_text = FONT_SMALL.render(player_move_text, True, DARK_GRAY)
            screen.blit(pm_text, (50, 150))
        if ai_move_text:
            ai_text = FONT_SMALL.render(ai_move_text, True, DARK_GRAY)
            screen.blit(ai_text, (50, 180))
        if result_text:
            res_text = FONT_MEDIUM.render(result_text, True, BLUE)
            screen.blit(res_text, ((WIDTH - res_text.get_width()) // 2, 240))
        
        # If game over, show final result and restart prompt
        if game_over:
            if player_score > ai_score:
                final_text = "You Won the Game!"
            elif ai_score > player_score:
                final_text = "AI Won the Game!"
            else:
                final_text = "The Game is a Tie!"
            final_render = FONT_MEDIUM.render(final_text, True, (200, 0, 0))
            screen.blit(final_render, ((WIDTH - final_render.get_width()) // 2, 300))
            restart_text = FONT_SMALL.render("Press 'Space' to Continue", True, DARK_GRAY)
            screen.blit(restart_text, ((WIDTH - restart_text.get_width()) // 2, 350))
        
        # Draw buttons only if game not over
        if not game_over:
            draw_buttons(screen, buttons, FONT_SMALL)
        
        # ----- Event Loop -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True  # Ensure progression even if window is closed
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                selected_move = None
                if rock_button.collidepoint(pos):
                    selected_move = 0
                elif paper_button.collidepoint(pos):
                    selected_move = 1
                elif scissors_button.collidepoint(pos):
                    selected_move = 2
                
                if selected_move is not None:
                    human_move = selected_move
                    
                    # Decide AI move
                    if last_player_move is None:
                        ai_move = random.randint(0, 2)
                    else:
                        prediction = perceptron.predict(move_to_vector(last_player_move))
                        ai_move = counter_move(prediction)
                    
                    # Determine round result
                    if human_move == ai_move:
                        round_result = "Tie!"
                    elif (human_move - ai_move) % 3 == 1:
                        round_result = "You Win this Round!"
                        player_score += 1
                    else:
                        round_result = "AI Wins this Round!"
                        ai_score += 1
                    
                    # Update the perceptron
                    if last_player_move is not None:
                        perceptron.update(move_to_vector(last_player_move), human_move)
                    
                    # Save the current move for next round prediction
                    last_player_move = human_move
                    
                    # Update texts to display
                    result_text = round_result
                    player_move_text = f"You chose: {moves[human_move]}"
                    ai_move_text = f"AI chose: {moves[ai_move]}"
                    
                    current_round += 1
                    if current_round >= TOTAL_ROUNDS:
                        game_over = True
            
            if event.type == pygame.KEYDOWN:
                # Change from 'R' to 'Space' to continue
                if event.key == pygame.K_SPACE and game_over:
                    return True  # Progression flag
        
        pygame.display.flip()
        clock.tick(30)

    return True  # Ensure progression