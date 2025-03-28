import pygame
import sys
import numpy as np
import random
import time

def neural_siege_main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Neural Siege: The Last Escape with Collectibles")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)
    big_font = pygame.font.SysFont("Arial", 36)

    # Constants
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    PLAYER_RADIUS = 15
    PLAYER_COLOR = (0, 255, 0)
    BG_COLOR = (20, 20, 20)
    TRAP_COLOR = (200, 0, 0)
    ITEM_COLOR = (255, 255, 0)  # Yellow collectibles
    PLAYER_MAX_HEALTH = 100
    HISTORY_SIZE = 5
    INPUT_DIM = HISTORY_SIZE * 2
    OUTPUT_DIM = 2
    INITIAL_SPAWN_INTERVAL = 2000
    MIN_SPAWN_INTERVAL = 500
    SPAWN_ACCELERATION = 0.95
    TRAP_SPEED = 3.0
    DAMAGE_PER_HIT = 25
    SURVIVAL_TIME = 60000
    TARGET_ITEMS = 12

    # Simple Perceptron Class
    class Perceptron:
        def __init__(self, input_dim, output_dim, learning_rate=0.01):
            self.weights = np.random.randn(output_dim, input_dim) * 0.1
            self.bias = np.random.randn(output_dim, 1) * 0.1
            self.lr = learning_rate

        def predict(self, x):
            return self.weights @ x + self.bias

        def train(self, x, target):
            pred = self.predict(x)
            error = target - pred
            self.weights += self.lr * error @ x.T
            self.bias += self.lr * error
            return error

    # Player Class
    class Player:
        def __init__(self):
            self.pos = np.array([SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], dtype=float)
            self.health = PLAYER_MAX_HEALTH
            self.history = []

        def update(self, new_pos):
            new_pos = np.array(new_pos, dtype=float)
            delta = new_pos - self.pos
            if np.linalg.norm(delta) > 0.5:
                self.history.append(delta)
            if len(self.history) > HISTORY_SIZE:
                self.history.pop(0)
            self.pos = new_pos.copy()

        def draw(self, surface):
            pygame.draw.circle(surface, PLAYER_COLOR, self.pos.astype(int), PLAYER_RADIUS)

    # Trap Class
    class Trap:
        def __init__(self, spawn_point, target_point):
            self.pos = np.array(spawn_point, dtype=float)
            self.target = np.array(target_point, dtype=float)
            self.radius = 10

        def update(self, player_pos):
            direction = self.target - self.pos
            dist = np.linalg.norm(direction)
            if dist != 0:
                direction /= dist
            self.pos += direction * TRAP_SPEED

        def draw(self, surface):
            pygame.draw.circle(surface, TRAP_COLOR, self.pos.astype(int), self.radius)

        def collides_with(self, player):
            return np.linalg.norm(self.pos - player.pos) < (self.radius + PLAYER_RADIUS)

    # Collectible Class
    class Collectible:
        def __init__(self, pos):
            self.pos = np.array(pos, dtype=float)
            self.radius = 10

        def draw(self, surface):
            pygame.draw.circle(surface, ITEM_COLOR, self.pos.astype(int), self.radius)

        def collides_with(self, player):
            return np.linalg.norm(self.pos - player.pos) < (self.radius + PLAYER_RADIUS)

    # Utility Functions
    def get_input_vector(history):
        vec = []
        missing = HISTORY_SIZE - len(history)
        if missing > 0:
            vec.extend([0] * 2 * missing)
        for delta in history:
            vec.extend(delta.tolist())
        return np.array(vec).reshape(-1, 1)

    def draw_text(text, font, color, surface, x, y):
        txt = font.render(text, True, color)
        rect = txt.get_rect(center=(x, y))
        surface.blit(txt, rect)

    # Main Game Logic
    player = Player()
    ensemble = Perceptron(INPUT_DIM, OUTPUT_DIM, learning_rate=0.01)
    traps = []
    collectibles = []
    collected_items = 0

    spawn_interval = INITIAL_SPAWN_INTERVAL
    last_trap_spawn = pygame.time.get_ticks()
    last_item_spawn = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return True

        # Player movement (arrow keys)
        keys = pygame.key.get_pressed()
        new_pos = player.pos.copy()
        speed = 5
        if keys[pygame.K_LEFT]:
            new_pos[0] -= speed
        if keys[pygame.K_RIGHT]:
            new_pos[0] += speed
        if keys[pygame.K_UP]:
            new_pos[1] -= speed
        if keys[pygame.K_DOWN]:
            new_pos[1] += speed

        new_pos[0] = np.clip(new_pos[0], 0, SCREEN_WIDTH)
        new_pos[1] = np.clip(new_pos[1], 0, SCREEN_HEIGHT)
        player.update(new_pos)

        # Trap spawning
        if current_time - last_trap_spawn >= spawn_interval:
            input_vec = get_input_vector(player.history)
            if input_vec.shape[0] < INPUT_DIM:
                predicted_delta = np.random.uniform(-10, 10, (OUTPUT_DIM, 1))
            else:
                predicted_delta = ensemble.predict(input_vec)
            scaling = 10
            predicted_future = player.pos.reshape(2, 1) + scaling * predicted_delta
            predicted_future = predicted_future.flatten()
            predicted_future[0] = np.clip(predicted_future[0], 0, SCREEN_WIDTH)
            predicted_future[1] = np.clip(predicted_future[1], 0, SCREEN_HEIGHT)

            # Spawn trap at edge based on predicted future
            if predicted_future[0] < SCREEN_WIDTH / 2:
                spawn_x = 0
            else:
                spawn_x = SCREEN_WIDTH
            if predicted_future[1] < SCREEN_HEIGHT / 2:
                spawn_y = 0
            else:
                spawn_y = SCREEN_HEIGHT
            spawn_point = (spawn_x, spawn_y)
            traps.append(Trap(spawn_point, predicted_future))
            last_trap_spawn = current_time

            if len(player.history) >= HISTORY_SIZE:
                target = np.array(player.history[-1]).reshape(-1, 1)
                ensemble.train(input_vec, target)

            spawn_interval = max(int(spawn_interval * SPAWN_ACCELERATION), MIN_SPAWN_INTERVAL)

        # Collectible item spawning
        if current_time - last_item_spawn >= 3000:
            item_x = random.randint(20, SCREEN_WIDTH - 20)
            item_y = random.randint(20, SCREEN_HEIGHT - 20)
            collectibles.append(Collectible((item_x, item_y)))
            last_item_spawn = current_time

        # Update traps
        for trap in traps:
            trap.update(player.pos)

        # Check collisions: trap hits player
        for trap in traps[:]:
            if trap.collides_with(player):
                player.health -= DAMAGE_PER_HIT
                traps.remove(trap)

        # Check collisions: player collects item
        for item in collectibles[:]:
            if item.collides_with(player):
                collected_items += 1
                collectibles.remove(item)

        # Win if 12 collectibles are gathered
        if collected_items >= TARGET_ITEMS:
            screen.fill(BG_COLOR)
            draw_text("You Win! You collected all the items!", big_font, (0, 255, 0), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            pygame.display.update()
            pygame.time.delay(2000)
            running = False
            return True

        # Lose condition: health <= 0
        if player.health <= 0:
            screen.fill(BG_COLOR)
            draw_text("You Lose! The captor's predictions caught you.", big_font, (255, 0, 0), screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
            pygame.display.update()
            pygame.time.delay(2000)
            running = False
            return False

        screen.fill(BG_COLOR)
        player.draw(screen)
        for trap in traps:
            trap.draw(screen)
        for item in collectibles:
            item.draw(screen)
        draw_text(f"Health: {player.health}", font, (255, 255, 255), screen, 70, 20)
        draw_text(f"Items: {collected_items}/{TARGET_ITEMS}", font, (255, 255, 255), screen, SCREEN_WIDTH - 100, 20)
        time_left = max(0, (SURVIVAL_TIME - elapsed_time) // 1000)
        draw_text(f"Time Left: {time_left}s", font, (255, 255, 255), screen, SCREEN_WIDTH - 100, 40)
        pygame.display.update()

    pygame.quit()
    return False

# This allows the game to be run directly if needed
if __name__ == "__main__":
    neural_siege_main()