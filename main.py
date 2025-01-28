import pygame
import math
from pygame.locals import *


pygame.init()


WIDTH, HEIGHT = 800, 600
TILE_SIZE = 25



WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (173, 216, 230)



class HexMap:
    def __init__(self, rows, cols, tile_size):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.map_data = self.generate_map()

    def generate_map(self):
        map_data = []
        for row in range(self.rows):
            map_row = []
            for col in range(self.cols):
                offset_x = self.tile_size * 1.5 * col + 100
                offset_y = self.tile_size * math.sqrt(3) * (row + (0.5 if col % 2 else 0)) + 50
                map_row.append((offset_x, offset_y))
            map_data.append(map_row)
        return map_data

    def draw(self, screen, highlight_cells):
        for row in range(self.rows):
            for col in range(self.cols):
                if highlight_cells and (col, row) in highlight_cells:
                    color = HIGHLIGHT
                else:
                    color = WHITE if (row + col) % 2 == 0 else WHITE
                center_x, center_y = self.map_data[row][col]
                points = self.hexagon_points(center_x, center_y)
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
        self.move_range = 130
        self.comand = 0
        self.attack = 2
    def draw(self, screen, map_data):

        hero_x, hero_y = map_data[self.y][self.x]
        pygame.draw.circle(screen, self.color, (int(hero_x), int(hero_y)), TILE_SIZE // 3)

    def get_accessible_cells(self, map_data):

        accessible_cells = []
        hero_x, hero_y = map_data[self.y][self.x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                cell_x, cell_y = map_data[row][col]
                distance = math.sqrt((cell_x - hero_x) ** 2 + (cell_y - hero_y) ** 2)
                if distance <= self.move_range:
                    accessible_cells.append((col, row))
        return accessible_cells

    def move_to(self, x, y, map_data):

        accessible_cells = self.get_accessible_cells(map_data)
        if (x, y) in accessible_cells:
            self.x = x
            self.y = y


    def get_comand(self):
        return self.comand

    def attack(self):
        ...


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Поле с гексагональной сеткой")
rows, cols = 10, 10
hex_map = HexMap(rows, cols, TILE_SIZE)
hero = Hero(0, 0)


running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                closest_hex = hex_map.find_closest_hex(mouse_x, mouse_y)
                if closest_hex:
                    hero.move_to(closest_hex[0], closest_hex[1], hex_map.map_data)

    screen.fill(WHITE)
    accessible_cells = hero.get_accessible_cells(hex_map.map_data)
    hex_map.draw(screen, highlight_cells=accessible_cells)
    hero.draw(screen, hex_map.map_data)

    pygame.display.flip()

pygame.quit()
