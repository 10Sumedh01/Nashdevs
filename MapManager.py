import pygame
import math
from constants import MAZE_CELL_SIZE, MAZE_REGION_SIZE

class Node:
    def __init__(self, x, y, walkable=True, row=0, col=0):
        self.x = x
        self.y = y
        self.walkable = walkable
        self.row = row
        self.col = col
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

def line_of_sight_clear(start, end, obstacles):
    steps = int(start.distance_to(end) // 5)
    if steps == 0:
        steps = 1
    for i in range(steps + 1):
        pos = start.lerp(end, i / steps)
        point = pygame.Rect(pos.x, pos.y, 1, 1)
        for obs in obstacles:
            # Use obs directly because it is a pygame.Rect.
            if obs.colliderect(point):
                return False
    return True

class MapManager:
    def __init__(self, obstacles, reference_pos):
        self.obstacles = obstacles
        self.cell_size = MAZE_CELL_SIZE
        self.region_size = MAZE_REGION_SIZE
        self.reference_pos = reference_pos
        self.grid = self.build_grid()

    def build_grid(self):
        grid = []
        region_half = self.region_size // 2
        start_x = int(self.reference_pos.x - region_half)
        start_y = int(self.reference_pos.y - region_half)
        cols = self.region_size // self.cell_size
        rows = self.region_size // self.cell_size
        for row in range(rows):
            grid_row = []
            for col in range(cols):
                cell_x = start_x + col * self.cell_size
                cell_y = start_y + row * self.cell_size
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)
                walkable = True
                for obs in self.obstacles:
                    if cell_rect.colliderect(obs):
                        walkable = False
                        break
                node = Node(cell_x + self.cell_size / 2, cell_y + self.cell_size / 2, walkable, row, col)
                grid_row.append(node)
            grid.append(grid_row)
        self.rows = rows
        self.cols = cols
        return grid

    def get_node_from_position(self, pos):
        region_half = self.region_size // 2
        start_x = self.reference_pos.x - region_half
        start_y = self.reference_pos.y - region_half
        col = int((pos.x - start_x) // self.cell_size)
        row = int((pos.y - start_y) // self.cell_size)
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return None
        return self.grid[row][col]

    def get_neighbors(self, node):
        neighbors = []
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = node.row + d_row
            new_col = node.col + d_col
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                neighbor = self.grid[new_row][new_col]
                if neighbor.walkable:
                    neighbors.append(neighbor)
        return neighbors

    def heuristic(self, node, goal):
        return math.hypot(node.x - goal.x, node.y - goal.y)

    def astar(self, start_pos, goal_pos):
        start_node = self.get_node_from_position(start_pos)
        goal_node = self.get_node_from_position(goal_pos)
        if not start_node or not goal_node:
            return []

        # Reset all nodes
        for row in self.grid:
            for node in row:
                node.g = float('inf')
                node.f = float('inf')
                node.parent = None

        open_set = [start_node]
        start_node.g = 0
        start_node.h = self.heuristic(start_node, goal_node)
        start_node.f = start_node.h

        while open_set:
            current = min(open_set, key=lambda n: n.f)
            if current == goal_node:
                path = []
                while current:
                    path.append(pygame.Vector2(current.x, current.y))
                    current = current.parent
                path.reverse()
                return path

            open_set.remove(current)
            for neighbor in self.get_neighbors(current):
                tentative_g = current.g + self.heuristic(current, neighbor)
                if tentative_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic(neighbor, goal_node)
                    neighbor.f = neighbor.g + neighbor.h
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        return []  # No path found
