import pygame
import math
import heapq
from pygame.locals import *

pygame.init()


WIDTH, HEIGHT = 800, 600
TILE_SIZE = 25
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гексагональная карта с A*")


WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (173, 216, 230)
PATH_COLOR = (255, 215, 0)



class HexMap:
    def __init__(self, rows, cols, tile_size):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.map_data = self.generate_map()

    def generate_map(self):
        global map_data
        map_data = []
        for row in range(self.rows):
            map_row = []
            for col in range(self.cols):
                offset_x = self.tile_size * 1.5 * col + 100
                offset_y = self.tile_size * math.sqrt(3) * (row + (0.5 if col % 2 else 0)) + 50
                map_row.append((offset_x, offset_y))
            map_data.append(map_row)

        return map_data

    def draw(self, screen, highlight_cells=None, path=None):

        for row in range(self.rows):
            for col in range(self.cols):
                center_x, center_y = self.map_data[row][col]
                points = self.hexagon_points(center_x, center_y)

                if path and (col, row) in path:
                    color = PATH_COLOR
                elif highlight_cells and (col, row) in highlight_cells:
                    color = HIGHLIGHT
                else:
                    color = WHITE

                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, BLACK, points, 2)

    def hexagon_points(self, center_x, center_y):

        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            x = center_x + self.tile_size * math.cos(angle)
            y = center_y + self.tile_size * math.sin(angle)
            points.append((x, y))
        return points

    def find_closest_hex(self, mouse_x, mouse_y):

        closest_hex = None
        min_distance = float("inf")
        for row_idx, row in enumerate(self.map_data):
            for col_idx, (hex_x, hex_y) in enumerate(row):
                distance = math.sqrt((mouse_x - hex_x) ** 2 + (mouse_y - hex_y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_hex = (col_idx, row_idx)
        return closest_hex


class Hero:
    def __init__(self, x, y, color=BLUE):
        self.x = x
        self.y = y
        self.color = color
        self.path = []
        self.move_range = 130

    def draw(self, screen, map_data):
        hero_x, hero_y = map_data[self.y][self.x]
        pygame.draw.circle(screen, self.color, (int(hero_x), int(hero_y)), TILE_SIZE // 3)

    def get_neighbors(self, x, y):
        neighbors = []
        current_x, current_y = map_data[y][x]

        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                if col == x and row == y:
                    continue
                neighbor_x, neighbor_y = map_data[row][col]
                distance = math.sqrt((neighbor_x - current_x) ** 2 + (neighbor_y - current_y) ** 2)
                if distance <= TILE_SIZE * 2:
                    neighbors.append((col, row))

        return neighbors

    def get_accessible_cells(self):
        accessible_cells = []
        hero_x, hero_y = map_data[self.y][self.x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                cell_x, cell_y = map_data[row][col]
                distance = math.sqrt((cell_x - hero_x) ** 2 + (cell_y - hero_y) ** 2)
                if distance <= self.move_range:
                    accessible_cells.append((col, row))
        return accessible_cells

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star_search(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                print(path)
                print(start,goal)
                return path

            for neighbor in self.get_neighbors(*current):
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def move_to(self, x, y):
        self.path = self.a_star_search((self.x, self.y), (x, y))

    def update_position(self):
        if self.path:
            self.x, self.y = self.path.pop(0)


rows, cols = 10, 24
hex_map = HexMap(rows, cols, TILE_SIZE)
hero = Hero(0, 0)
print(hero.get_neighbors(1, 1))
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                closest_hex = hex_map.find_closest_hex(mouse_x, mouse_y)
                if closest_hex:
                    hero.move_to(closest_hex[0], closest_hex[1])

    hero.update_position()

    screen.fill(WHITE)
    accessible_cells = hero.get_accessible_cells()
    hex_map.draw(screen, highlight_cells=accessible_cells, path=hero.path)
    hero.draw(screen, hex_map.map_data)

    pygame.display.flip()
    clock.tick(5)
pygame.quit()