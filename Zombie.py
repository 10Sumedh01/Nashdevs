import pygame
import math
import random
from constants import ZOMBIE_COLOR, ZOMBIE_SIZE, ZOMBIE_SPEED, COLLISION_THRESHOLD
from MapManager import line_of_sight_clear

# --- A* Pathfinding Algorithm ---
def astar_path(start, goal, obstacles, cell_size=50):
    """
    Compute a path from start to goal using a grid-based A* algorithm.
    start, goal: pygame.Vector2 positions.
    obstacles: list of pygame.Rect obstacles.
    cell_size: grid cell size.
    Returns a list of pygame.Vector2 positions (centers of cells).
    """
    grid_width = pygame.display.get_surface().get_width()
    grid_height = pygame.display.get_surface().get_height()
    cols = math.ceil(grid_width / cell_size)
    rows = math.ceil(grid_height / cell_size)
    
    def node_from_pos(pos):
        return (int(pos.x // cell_size), int(pos.y // cell_size))
    
    def pos_from_node(node):
        return pygame.Vector2(node[0] * cell_size + cell_size / 2,
                              node[1] * cell_size + cell_size / 2)
    
    def heuristic(a, b):
        # Euclidean distance
        return math.hypot(b[0] - a[0], b[1] - a[1])
    
    def is_walkable(node):
        x, y = node
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        node_rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
        for obs in obstacles:
            if node_rect.colliderect(obs):
                return False
        return True

    start_node = node_from_pos(start)
    goal_node = node_from_pos(goal)
    
    open_set = {start_node}
    came_from = {}
    g_score = {start_node: 0}
    f_score = {start_node: heuristic(start_node, goal_node)}
    
    while open_set:
        current = min(open_set, key=lambda n: f_score.get(n, float('inf')))
        if current == goal_node:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(pos_from_node(current))
                current = came_from[current]
            path.append(pos_from_node(start_node))
            path.reverse()
            return path
        
        open_set.remove(current)
        cx, cy = current
        # Check all 8 neighbors
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor = (cx + dx, cy + dy)
                if not is_walkable(neighbor):
                    continue
                tentative_g = g_score.get(current, float('inf')) + (math.hypot(dx, dy))
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal_node)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
    # No path found
    return []

# --- Zombie Class ---
class Zombie:
    def __init__(self, spawn_pos, speed_multiplier=1.0):
        self.pos = pygame.Vector2(spawn_pos)
        self.speed = ZOMBIE_SPEED * speed_multiplier
        self.size = ZOMBIE_SIZE
        self.is_special = False
        self.max_health = 100 + 100 * 25 / 100
        self.health = self.max_health
        self.angle = 0
        self.path = []
        self.path_index = 0
        self.last_path_update = pygame.time.get_ticks()
        ZOMBIE_IMAGE_PATH = "assets/zombie.png"
        self.original_image = pygame.image.load(ZOMBIE_IMAGE_PATH).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.image = self.original_image

    def take_damage(self, damage, game=None):
        self.health -= damage
        return self.health <= 0

    def update(self, player_pos, obstacles, map_manager):
        current_time = pygame.time.get_ticks()
        # Try direct approach if line-of-sight is clear.
        if line_of_sight_clear(self.pos, player_pos, obstacles):
            direction = player_pos - self.pos
            if direction.length() > 0:
                self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
                direction = direction.normalize()
                candidate_pos = self.pos + direction * self.speed
                candidate_rect = pygame.Rect(candidate_pos.x - self.size // 2,
                                             candidate_pos.y - self.size // 2,
                                             self.size, self.size)
                collision = any(candidate_rect.colliderect(obs) for obs in obstacles)
                if not collision:
                    self.pos = candidate_pos
                    self.path = []
                    self.path_index = 0
                    self.last_path_update = current_time
                else:
                    if current_time - self.last_path_update > 500:
                        if map_manager:
                            self.path = map_manager.astar(self.pos, player_pos)
                        else:
                            self.path = astar_path(self.pos, player_pos, obstacles, cell_size=50)
                        self.path_index = 0
                        self.last_path_update = current_time
        else:
            if (not self.path or self.path_index >= len(self.path)) and (current_time - self.last_path_update > 500):
                if map_manager:
                    self.path = map_manager.astar(self.pos, player_pos)
                else:
                    self.path = astar_path(self.pos, player_pos, obstacles, cell_size=50)
                self.path_index = 0
                self.last_path_update = current_time
            if self.path and self.path_index < len(self.path):
                target = self.path[self.path_index]
                direction = target - self.pos
                if direction.length() < self.speed:
                    self.pos = target
                    self.path_index += 1
                else:
                    direction = direction.normalize()
                    candidate_pos = self.pos + direction * self.speed
                    candidate_rect = pygame.Rect(candidate_pos.x - self.size // 2,
                                                 candidate_pos.y - self.size // 2,
                                                 self.size, self.size)
                    collision = any(candidate_rect.colliderect(obs) for obs in obstacles)
                    if not collision:
                        self.pos = candidate_pos
                    else:
                        if current_time - self.last_path_update > 500:
                            if map_manager:
                                self.path = map_manager.astar(self.pos, player_pos)
                            else:
                                self.path = astar_path(self.pos, player_pos, obstacles, cell_size=50)
                            self.path_index = 0
                            self.last_path_update = current_time
                self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size // 2,
                           self.pos.y - self.size // 2,
                           self.size, self.size)

    def draw(self, surface, offset):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        img_rect = rotated_image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(rotated_image, img_rect)
        self.draw_health_bar(surface, offset)

    def draw_health_bar(self, surface, offset):
        """
        Draw the health bar above the zombie.
        :param surface: The game screen.
        :param offset: The camera offset.
        """
        bar_width = self.size  # Width of the health bar (same as zombie size)
        bar_height = 5  # Height of the health bar
        health_ratio = self.health / self.max_health  # Health percentage

        # Calculate the position of the health bar
        bar_x = self.pos.x - offset.x - bar_width // 2
        bar_y = self.pos.y - offset.y - self.size // 2 - 10  # Above the zombie

        # Draw the background (red) and foreground (green) of the health bar
        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))  # Green foreground
