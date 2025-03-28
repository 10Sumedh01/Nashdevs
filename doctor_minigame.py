import os
import pygame
import sys
import random
import time
from groq import Groq  # Ensure you have installed the groq package

# --- Constants ---
WIDTH, HEIGHT = 1280, 720
FPS = 30
BG_COLOR = (20, 20, 40)
TEXT_COLOR = (240, 240, 240)
BUTTON_COLOR = (50, 50, 100)
BUTTON_HOVER_COLOR = (70, 70, 150)
TIMER_COLOR = (255, 0, 0)

ROUND_DURATION = 15000  # 15 seconds per round
TOTAL_ROUNDS = 5

# --- Groq API Prompt Template (Edited) ---
# We specifically request shorter, concise questions (1-2 lines).
CHAIN_PROMPT = """
You are a seasoned doctor in a zombie apocalypse, deciding which of two survivors to take on a mission. 
Generate 5 SHORT, concise multiple-choice questions (each ~1-2 lines of text) about zombie survival, 
with 4 options (A-D). Each question is separated by a line containing only '###'.

Format each question exactly as:
Question: <short question text>
Options: A. <option A>  B. <option B>  C. <option C>  D. <option D>
Correct Answer: <A, B, C, or D>
"""

# --- Helper function to wrap text ---
def draw_wrapped_text(surface, text, font, color, rect, line_spacing=5):
    """
    Draws the given text within the provided rectangle by wrapping the text.
    Returns the total height used in drawing.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    if current_line:
        lines.append(current_line)
    
    y_offset = 0
    for line in lines:
        line_surf = font.render(line.strip(), True, color)
        surface.blit(line_surf, (rect.x, rect.y + y_offset))
        y_offset += font.get_linesize() + line_spacing
    return y_offset

# --- Function to fetch a chain of questions using Groq ---
def get_questions(api_key):
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": CHAIN_PROMPT}],
            model="llama-3.3-70b-versatile",
        )
        generated = chat_completion.choices[0].message.content
        if not generated:
            raise ValueError("No generated text returned.")
        # Split by delimiter "###"
        raw_questions = generated.split("###")
        questions = []
        for raw in raw_questions:
            raw = raw.strip()
            if not raw:
                continue
            lines = raw.split("\n")
            q_text = ""
            options_line = ""
            correct_line = ""
            for line in lines:
                line = line.strip()
                if line.startswith("Question:"):
                    q_text = line.replace("Question:", "").strip()
                elif line.startswith("Options:"):
                    options_line = line.replace("Options:", "").strip()
                elif line.startswith("Correct Answer:"):
                    correct_line = line.replace("Correct Answer:", "").strip().upper()
            if q_text and options_line and correct_line:
                # Parse options_line expecting: A. text  B. text  C. text  D. text
                options_parts = options_line.split("  ")
                options = {}
                for part in options_parts:
                    part = part.strip()
                    if len(part) >= 3 and part[1] == ".":
                        key = part[0].upper()
                        option_text = part[2:].strip()
                        options[key] = option_text
                if all(k in options for k in ["A", "B", "C", "D"]):
                    questions.append({"question": q_text, "options": options, "correct": correct_line})
        if len(questions) < TOTAL_ROUNDS:
            raise ValueError("Not enough questions generated.")
        return questions[:TOTAL_ROUNDS]
    except Exception as e:
        print("Groq API call failed or parsing error:", e)
        fallback = [
            {
                "question": "Zombies approach your safehouse. Quick plan?",
                "options": {
                    "A": "Seal doors/windows",
                    "B": "Run for it",
                    "C": "Set traps",
                    "D": "Try to negotiate"
                },
                "correct": "A"
            },
            {
                "question": "You find a car with minimal fuel. Next step?",
                "options": {
                    "A": "Drive away fast",
                    "B": "Look for more fuel",
                    "C": "Stay and fortify",
                    "D": "Torch the car"
                },
                "correct": "B"
            },
            {
                "question": "Strange noises in the basement. What do you do?",
                "options": {
                    "A": "Investigate carefully",
                    "B": "Shout a warning",
                    "C": "Ignore them",
                    "D": "Hide quietly"
                },
                "correct": "A"
            },
            {
                "question": "Radio broadcast offers help but might be a trap?",
                "options": {
                    "A": "Follow instructions",
                    "B": "Stay hidden",
                    "C": "Check source carefully",
                    "D": "Broadcast location"
                },
                "correct": "C"
            },
            {
                "question": "Map leads to rumored safe zone. Action?",
                "options": {
                    "A": "Follow it blindly",
                    "B": "Plan route carefully",
                    "C": "Discard the map",
                    "D": "Sell it for supplies"
                },
                "correct": "B"
            }
        ]
        return fallback

# --- Button Class for Options ---
class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font

    def draw(self, surface, mouse_pos):
        color = BUTTON_HOVER_COLOR if self.rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        rendered = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = rendered.get_rect(center=self.rect.center)
        surface.blit(rendered, text_rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]

# --- Game Class ---
class ZombieQuizChainGame:
    def __init__(self, api_key):
        self.api_key = api_key
        self.questions = get_questions(api_key)  # Chain call: list of questions
        self.current_index = 0
        self.user_score = 0
        self.ai_score = 0
        self.selected_answer = None
        self.feedback = ""
        self.round_timer = ROUND_DURATION
        self.last_tick = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 28)
        self.large_font = pygame.font.SysFont("Arial", 36)
        self.option_font = pygame.font.SysFont("Arial", 26)
        self.buttons = {}
        self.setup_buttons()

    def setup_buttons(self):
        btn_width = 700
        btn_height = 60
        gap = 20
        start_y = 350
        # We'll store button rects in a dictionary keyed by A, B, C, D
        for key in ["A", "B", "C", "D"]:
            rect = (WIDTH//2 - btn_width//2, start_y, btn_width, btn_height)
            self.buttons[key] = Button(rect, "", self.option_font)
            start_y += btn_height + gap

    def load_current_question(self):
        qdata = self.questions[self.current_index]
        for key in ["A", "B", "C", "D"]:
            # For the button text, we'll keep it short
            # But if it's long, we still rely on the button rect for bounding
            # The user can see the wrapped text if needed
            self.buttons[key].text = f"{key}: {qdata['options'][key]}"
        self.selected_answer = None
        self.feedback = ""
        self.round_timer = ROUND_DURATION
        self.last_tick = pygame.time.get_ticks()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        qdata = self.questions[self.current_index]
        
        # Draw question in a wrapped manner
        question_rect = pygame.Rect(50, 50, WIDTH - 100, 100)  
        draw_wrapped_text(screen, qdata["question"], self.large_font, TEXT_COLOR, question_rect, line_spacing=3)

        # Draw options as buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.draw(screen, mouse_pos)

        # Timer
        timer_surf = self.font.render(f"Time Left: {self.round_timer//1000}s", True, TIMER_COLOR)
        screen.blit(timer_surf, (WIDTH - 250, 20))
        
        # Scores
        score_surf = self.font.render(f"Your Score: {self.user_score}   AI Score: {self.ai_score}", True, TEXT_COLOR)
        screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 20))

        # Round info
        round_surf = self.font.render(f"Round {self.current_index+1}/{TOTAL_ROUNDS}", True, TEXT_COLOR)
        screen.blit(round_surf, (50, 20))

        # Feedback
        if self.feedback:
            fb_surf = self.large_font.render(self.feedback, True, TEXT_COLOR)
            fb_rect = fb_surf.get_rect(center=(WIDTH//2, HEIGHT - 60))
            screen.blit(fb_surf, fb_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode.upper() in ["A", "B", "C", "D"]:
                self.selected_answer = event.unicode.upper()

    def update(self):
        now = pygame.time.get_ticks()
        dt = now - self.last_tick
        self.last_tick = now
        if self.round_timer > 0:
            self.round_timer -= dt
            if self.round_timer <= 0:
                self.round_timer = 0
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if self.round_timer > 0 and self.selected_answer is None:
            for key, btn in self.buttons.items():
                if btn.is_clicked(mouse_pos, mouse_pressed):
                    self.selected_answer = key

    def check_round(self):
        qdata = self.questions[self.current_index]
        correct = qdata["correct"].upper()
        if self.selected_answer is None:
            self.feedback = f"Time's up! Correct answer was {correct}."
            self.ai_score += 1
        elif self.selected_answer == correct:
            self.feedback = "Correct!"
            self.user_score += 1
        else:
            self.feedback = f"Incorrect! Correct answer was {correct}."
            self.ai_score += 1

    def round_over(self):
        return self.round_timer <= 0 or self.selected_answer is not None

    def next_round(self):
        self.current_index += 1
        if self.current_index < TOTAL_ROUNDS:
            self.load_current_question()

    def game_over(self):
        return self.current_index >= TOTAL_ROUNDS

    def final_result(self, screen):
        screen.fill(BG_COLOR)
        if self.user_score > self.ai_score:
            result_text = "Congratulations! You outsmarted the AI survivor!"
        elif self.user_score < self.ai_score:
            result_text = "The AI survivor outwitted you in the apocalypse."
        else:
            result_text = "It's a tie! Every win counts in the zombie apocalypse."
        result_surf = self.large_font.render(result_text, True, TEXT_COLOR)
        result_rect = result_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(result_surf, result_rect)
        score_surf = self.large_font.render(f"Final Score - You: {self.user_score}  AI: {self.ai_score}", True, TEXT_COLOR)
        score_rect = score_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        screen.blit(score_surf, score_rect)
        pygame.display.flip()
        pygame.time.delay(4000)

# --- Main Game Loop ---
def doc_main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombie Apocalypse Quiz Challenge")
    clock = pygame.time.Clock()

    # Use environment variable or fallback to a known key
    api_key = os.environ.get("GROQ_API_KEY", "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")
    game = ZombieQuizChainGame(api_key)
    game.load_current_question()

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False  # Explicitly return False if game is quit
            game.handle_event(event)
        game.update()
        if game.game_over():
            break
        game.draw(screen)
        pygame.display.flip()
        if game.round_over():
            game.check_round()
            pygame.time.delay(1500)
            if game.game_over():
                break
            else:
                game.next_round()
    game.final_result(screen)
    return True  # Successful completion of the minigame