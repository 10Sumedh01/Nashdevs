import pygame
import random
import sys
import os
import time

# --- Constants ---
WIDTH = 1280
HEIGHT = 720
TEXT_COLOR = (240, 240, 240)
FPS = 30

# UI Colors
BG_COLOR = (30, 30, 30)
BAR_BORDER_COLOR = (255, 255, 255)
BAR_FILL_COLOR = (50, 205, 50)
HINT_COLOR = (255, 215, 0)
SUCCESS_COLOR = (0, 255, 0)
FAIL_COLOR = (255, 69, 0)

# Game settings
INITIAL_SUCCESS_THRESHOLD = 20
ROUND_DURATION = 13000       # 13 seconds per round (for answering)
GAMBLE_DURATION = 5000       # 5 seconds to decide on the gamble
TOTAL_ROUNDS = 5           # 5 non-repetitive challenges per game
TYPE_DELAY = 16            # 16 ms delay per character for typing effect

# --- Base Challenges Pool ---
BASE_CHALLENGES = [
    {
        "challenge": "You come across an abandoned supermarket rumored to hide valuable supplies. How do you approach it?",
        "options": {"A": "Sneak in quietly", "B": "Charge in boldly", "C": "Scout the area first"},
        "correct": "C",
        "explanation": "Scouting first reduces the risk of traps or ambushes."
    },
    {
        "challenge": "A storm is approaching rapidly while you're in the open. What do you do?",
        "options": {"A": "Seek shelter under a large rock", "B": "Build a makeshift shelter immediately", "C": "Keep moving to find safety"},
        "correct": "B",
        "explanation": "Quickly constructing a shelter can protect you before the storm hits."
    },
    {
        "challenge": "While foraging, you hear rustling in the bushes. How do you respond?",
        "options": {"A": "Investigate cautiously", "B": "Hide and stay silent", "C": "Prepare your weapon"},
        "correct": "B",
        "explanation": "Hiding minimizes detection until you assess the threat."
    },
    {
        "challenge": "You find a map leading to a potential cache of supplies in a dangerous area. What is your move?",
        "options": {"A": "Follow the map immediately", "B": "Ignore it and keep moving", "C": "Plan a careful route"},
        "correct": "C",
        "explanation": "Planning a route lowers your risk of ambush or traps."
    },
    {
        "challenge": "You encounter a fork in the road in a deserted town. Which path do you choose?",
        "options": {"A": "Take the dark, narrow alley", "B": "Choose the sunlit main street", "C": "Pause and observe before deciding"},
        "correct": "C",
        "explanation": "Observing first allows you to gather critical information about potential dangers."
    },
    {
        "challenge": "You spot a suspicious van parked near a safehouse. What do you do?",
        "options": {"A": "Approach it stealthily", "B": "Call for backup", "C": "Ignore and move on"},
        "correct": "A",
        "explanation": "A stealthy approach helps avoid detection and gather intel."
    },
    {
        "challenge": "In a deserted area, you find a note hinting at hidden supplies. How will you proceed?",
        "options": {"A": "Decipher the note carefully", "B": "Follow the note immediately", "C": "Ignore it as a trap"},
        "correct": "A",
        "explanation": "Carefully deciphering the note increases your chances of safely retrieving supplies."
    }
]

# --- Utility Function: Typewriter Effect ---
def type_text(screen, font, text, pos):
    """Display text character by character with a 16 ms delay per character."""
    displayed_text = ""
    for char in text:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        displayed_text += char
        rendered = font.render(displayed_text, True, TEXT_COLOR)
        screen.fill(BG_COLOR)
        screen.blit(rendered, pos)
        pygame.display.flip()
        pygame.time.delay(TYPE_DELAY)

# --- AI & Game Theory Functions ---
def shuffle_options(challenge):
    """Shuffle options of a challenge and update the correct answer key."""
    options = list(challenge["options"].items())
    random.shuffle(options)
    shuffled_options = {key: value for key, value in options}
    for new_key, option in shuffled_options.items():
        if option == challenge["options"][challenge["correct"]]:
            challenge["correct"] = new_key
            break
    challenge["options"] = shuffled_options
    return challenge

def simulate_ai_survivor(difficulty):
    """Simulate an AI survivor's chance to answer correctly."""
    chance = max(0.3, 1.0 - 0.1 * difficulty)
    return random.random() < chance

def simulate_ai_gamble():
    """
    Simulate the AI's gamble decision.
    Returns a multiplier: 0 if gamble lost, 2 if won, or 1 if no gamble.
    """
    if random.random() < 0.5:  # AI chooses to gamble with 50% probability.
        return 2 if random.random() < 0.5 else 0
    else:
        return 1

# --- Main Game Class ---
class SurvivalChallengeGame:
    def __init__(self, api_key):
        self.api_key = api_key
        self.success_threshold = INITIAL_SUCCESS_THRESHOLD
        self.total_score = 0
        self.difficulty = 1
        self.lifelines = {
            "Scout": True,              # Eliminates one wrong option.
            "Ear to the Ground": True,  # Provides a hint.
            "Survivor's Instinct": True # Provides detailed AI insight.
        }
        # Preselect non-repetitive challenges.
        available = BASE_CHALLENGES.copy()
        # Ensure we have enough challenges.
        self.challenges_order = random.sample(available, min(TOTAL_ROUNDS, len(available)))
        self.challenges_played = []
        self.ai_score = 0

    def run(self, screen, font, large_font):
        for round_num in range(1, len(self.challenges_order) + 1):
            challenge = self.challenges_order[round_num - 1]
            # Shuffle options for each challenge.
            challenge = shuffle_options(challenge)
            self.challenges_played.append(challenge)
            result, round_points, player_multiplier, ai_multiplier = self.run_round(screen, font, large_font, challenge, round_num)
            self.adjust_score(result, round_points, player_multiplier, ai_multiplier)
            self.show_round_feedback(screen, large_font, round_num, challenge, result, round_points, player_multiplier, ai_multiplier)
            pygame.time.delay(1500)
            if result["correct"]:
                self.difficulty += 0.5
            else:
                self.difficulty = max(1, self.difficulty - 0.5)
            ai_correct = simulate_ai_survivor(self.difficulty)
            base_points = 10
            self.ai_score += base_points * (ai_multiplier if ai_correct else 1)
        self.show_final_feedback(screen, large_font)
        pygame.time.delay(3000)
        return self.total_score >= self.success_threshold

    def run_round(self, screen, font, large_font, challenge, round_num):
        clock = pygame.time.Clock()
        answer = None
        used_lifeline = None
        lifeline_hint = ""
        scout_options = None

        # Display challenge text with typewriter effect.
        screen.fill(BG_COLOR)
        header = f"Survival Challenge: Round {round_num}"
        header_text = large_font.render(header, True, TEXT_COLOR)
        screen.blit(header_text, (WIDTH//2 - header_text.get_width()//2, 30))
        pygame.display.flip()
        type_text(screen, font, challenge["challenge"], (50, 100))
        pygame.time.delay(500)

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < ROUND_DURATION:
            elapsed = pygame.time.get_ticks() - start_time
            remaining = max(0, ROUND_DURATION - elapsed)
            progress = remaining / ROUND_DURATION

            screen.fill(BG_COLOR)
            header_text = large_font.render(header, True, TEXT_COLOR)
            screen.blit(header_text, (WIDTH//2 - header_text.get_width()//2, 30))
            challenge_text = font.render(challenge["challenge"], True, TEXT_COLOR)
            screen.blit(challenge_text, (50, 100))

            options_to_show = scout_options if scout_options else challenge["options"]
            option_y = 200
            for key, option in options_to_show.items():
                option_line = f"{key}: {option}"
                option_text = font.render(option_line, True, TEXT_COLOR)
                screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, option_y))
                option_y += 40

            lifeline_text = "Lifelines: " + ", ".join([name for name, available in self.lifelines.items() if available])
            lifeline_surface = font.render(lifeline_text, True, HINT_COLOR)
            screen.blit(lifeline_surface, (20, HEIGHT - 60))
            timer_text = font.render(f"Time: {remaining//1000}s", True, TEXT_COLOR)
            screen.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, HEIGHT - 150))
            bar_width = 300
            bar_height = 20
            progress_width = int(bar_width * progress)
            bar_x = WIDTH//2 - bar_width//2
            bar_y = HEIGHT - 120
            pygame.draw.rect(screen, BAR_BORDER_COLOR, (bar_x, bar_y, bar_width, bar_height), 2)
            pygame.draw.rect(screen, BAR_FILL_COLOR, (bar_x, bar_y, progress_width, bar_height))
            
            if lifeline_hint:
                hint_surface = font.render(lifeline_hint, True, HINT_COLOR)
                screen.blit(hint_surface, (WIDTH//2 - hint_surface.get_width()//2, HEIGHT - 200))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        answer = "A"
                    elif event.key == pygame.K_b:
                        answer = "B"
                    elif event.key == pygame.K_c:
                        answer = "C"
                    elif event.key == pygame.K_1 and self.lifelines["Scout"]:
                        used_lifeline = "Scout"
                        self.lifelines["Scout"] = False
                        scout_options = self.apply_scout(challenge)
                    elif event.key == pygame.K_2 and self.lifelines["Ear to the Ground"]:
                        used_lifeline = "Ear to the Ground"
                        self.lifelines["Ear to the Ground"] = False
                        lifeline_hint = self.get_hint(challenge)
                    elif event.key == pygame.K_3 and self.lifelines["Survivor's Instinct"]:
                        used_lifeline = "Survivor's Instinct"
                        self.lifelines["Survivor's Instinct"] = False
                        lifeline_hint = self.get_ai_explanation(challenge)
            if answer is not None:
                break

            clock.tick(FPS)

        if answer is None:
            answer = "None"
        correct = (answer == challenge["correct"])
        base_points = 10
        player_multiplier = 1
        ai_multiplier = 1
        if correct:
            player_multiplier = self.gamble_decision(screen, font, large_font)
            ai_multiplier = simulate_ai_gamble()
        return {"choice": answer, "correct": correct, "lifeline": used_lifeline}, base_points, player_multiplier, ai_multiplier

    def gamble_decision(self, screen, font, large_font):
        start_time = pygame.time.get_ticks()
        prompt = "Gamble? Press Y to risk: 50% chance to double your points, 50% chance to lose them."
        gamble_decided = False
        player_choice = False
        while pygame.time.get_ticks() - start_time < GAMBLE_DURATION:
            screen.fill(BG_COLOR)
            prompt_text = font.render(prompt, True, HINT_COLOR)
            screen.blit(prompt_text, (WIDTH//2 - prompt_text.get_width()//2, HEIGHT//2 - 50))
            timer = GAMBLE_DURATION - (pygame.time.get_ticks() - start_time)
            timer_text = font.render(f"Time to decide: {timer//1000}s", True, TEXT_COLOR)
            screen.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        player_choice = True
                        gamble_decided = True
                        break
                    else:
                        gamble_decided = True
                        break
            if gamble_decided:
                break
        if player_choice:
            return 2 if random.random() < 0.5 else 0
        else:
            return 1

    def apply_scout(self, challenge):
        options = challenge["options"].copy()
        wrong_options = [key for key in options if key != challenge["correct"]]
        if wrong_options:
            remove = random.choice(wrong_options)
            del options[remove]
        return options

    def get_hint(self, challenge):
        return "Hint: " + challenge["explanation"].split()[0] + "..."

    def get_ai_explanation(self, challenge):
        return "Survivor Insight: " + challenge["explanation"]

    def adjust_score(self, result, base_points, player_multiplier, ai_multiplier):
        if result["correct"]:
            self.total_score += base_points * player_multiplier
        else:
            self.total_score -= 5

    def show_round_feedback(self, screen, large_font, round_num, challenge, result, base_points, player_multiplier, ai_multiplier):
        screen.fill((0, 0, 0))
        feedback = f"Round {round_num}: You chose {result['choice']}."
        feedback_text = large_font.render(feedback, True, TEXT_COLOR)
        if result["correct"]:
            outcome_str = f"Correct! (x{player_multiplier} points)"
            outcome_color = SUCCESS_COLOR
        else:
            outcome_str = f"Incorrect! Right answer was {challenge['correct']}."
            outcome_color = FAIL_COLOR
        outcome_text = large_font.render(outcome_str, True, outcome_color)
        score_text = large_font.render(f"Your Score: {self.total_score}   |   Rival Score: {self.ai_score}", True, TEXT_COLOR)
        screen.blit(feedback_text, (WIDTH//2 - feedback_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(outcome_text, (WIDTH//2 - outcome_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()

    def show_final_feedback(self, screen, large_font):
        screen.fill((0, 0, 0))
        if self.total_score >= self.success_threshold and self.total_score >= self.ai_score:
            final_msg = "Survival Success! You outsmarted the wild and the rival!"
        elif self.total_score < self.success_threshold:
            final_msg = "You faltered... The wild wins this round."
        else:
            final_msg = "Close call! But the rival survivor edged you out."
        final_text = large_font.render(final_msg, True, TEXT_COLOR)
        score_text = large_font.render(f"Final Score: You {self.total_score} | Rival {self.ai_score}", True, TEXT_COLOR)
        screen.blit(final_text, (WIDTH//2 - final_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
        pygame.display.flip()

# --- Main Loop ---
def minigame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Survival Scavenge Challenge")
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)
    api_key = os.environ.get("SURVIVAL_API_KEY", "Your_API_Key_Here")
    game = SurvivalChallengeGame(api_key)
    outcome = game.run(screen, font, large_font)
    print("Game Outcome:", "Survived!" if outcome else "Lost!")
    pygame.time.delay(3000)
    # pygame.quit()

if __name__ == "__main__":
    minigame()
