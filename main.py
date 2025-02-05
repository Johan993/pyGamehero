import pygame
import math
import heapq
import random
import sys
import os
import json


from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 1920, 1080
TILE_SIZE = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Шаг за шагом")

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (173, 216, 230)
PATH_COLOR = (255, 215, 0)
MOUNTAIN = (100, 100, 100)
HIGHLIGHT_COLOR = (200, 200, 0, 128)
BLACK_COLOR = (0, 0, 0, 128)

all_units = []

font = pygame.font.SysFont("Arial", 16)
big_font = pygame.font.SysFont("Arial", 48)


def load_map(filename):
    with open(filename, 'r') as f:
        map_data = json.load(f)
    return map_data


def create_game_from_map(map_data):
    rows, cols = map_data["rows"], map_data["cols"]
    hex_map = HexMap(rows, cols, TILE_SIZE, obstacle_chance=0)

    for obstacle in map_data["obstacles"]:
        hex_map.obstacles.add(tuple(obstacle))

    heroes = []
    for hero_data in map_data["heroes"]:
        hero_color = pygame.Color(hero_data["color"])
        hero = Hero(hero_data["x"], hero_data["y"], color=hero_color)
        heroes.append(hero)

    enemies = []
    for enemy_data in map_data["enemies"]:
        enemy = Enemy(enemy_data["x"], enemy_data["y"])
        enemies.append(enemy)

    all_units = heroes + enemies
    return hex_map, heroes, enemies, all_units


def show_map_choice_screen():
    font = pygame.font.Font(None, 48)
    choice_text = ["Выберите карту:", "1 - Ущелье", "2 - Гора", "3 - Случайная"]
    y_offset = 100
    for line in choice_text:
        rendered_text = font.render(line, True, (0, 0, 0))
        screen.blit(rendered_text, (WIDTH // 2 - rendered_text.get_width() // 2, y_offset))
        y_offset += 50

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_1:
                    return load_map('map1.json')
                elif event.key == K_2:
                    return load_map('map2.json')
                elif event.key == K_3:
                    return load_map('map3.json')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def show_intro_screen():
    intro_text = ["Здравствуйте"]
    a = ['Clouds 1.png', 'Clouds 2.png', 'Clouds 4.png', 'Clouds 5.png', 'Clouds 6.png', 'Clouds 7.png', 'Clouds 8.png']
    random_fon = random.choice(a)
    fon = pygame.transform.scale(load_image(random_fon), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_input = False


class HexMap:
    def __init__(self, rows, cols, tile_size, obstacle_chance=0.1):
        global map_data
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.mountain_image = pygame.transform.scale(load_image('Picsart_25-02-05_00-43-30-497.png'), (90, 90))
        map_data = self.generate_map()
        self.obstacles = set()
        for row in range(self.rows):
            for col in range(self.cols):
                if random.random() < obstacle_chance:
                    self.obstacles.add((col, row))

    def generate_map(self):
        map_data = []
        for row in range(self.rows):
            map_row = []
            for col in range(self.cols):
                offset_x = self.tile_size * 1.5 * col + 100
                offset_y = self.tile_size * math.sqrt(3) * (row + (0.5 if col % 2 else 0)) + 300
                map_row.append((offset_x, offset_y))
            map_data.append(map_row)
        return map_data

    def draw(self, screen, highlight_cells=None, path=None):
        fon = pygame.transform.scale(load_image('original-7e5a6cf41f2b42e44df523eb95835688.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        highlight_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for row in range(self.rows):
            for col in range(self.cols):
                center_x, center_y = map_data[row][col]
                points = self.hexagon_points(center_x, center_y)
                if (col, row) in self.obstacles:
                    mountain_rect = self.mountain_image.get_rect(center=(center_x, center_y))
                    screen.blit(self.mountain_image, mountain_rect)
                elif path and (col, row) in path:
                    color = PATH_COLOR
                    pygame.draw.polygon(screen, color, points)
                elif highlight_cells and (col, row) in highlight_cells:
                    color = HIGHLIGHT
                else:
                    pass

                if highlight_cells and (col, row) in highlight_cells:
                    pygame.draw.polygon(highlight_surface, HIGHLIGHT_COLOR, points)
                pygame.draw.polygon(highlight_surface, BLACK_COLOR, points, 2)
        screen.blit(highlight_surface, (0, 0))

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
        for row_idx, row in enumerate(map_data):
            for col_idx, (hex_x, hex_y) in enumerate(row):
                distance = math.hypot(mouse_x - hex_x, mouse_y - hex_y)
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
        self.move_range = 260
        self.move_cell = 3
        self.atack_range = 90
        self.hp = 10
        self.damage = 2
        center_x, center_y = map_data[self.y][self.x]
        self.pixel_x = center_x
        self.pixel_y = center_y
        self.target_pixel_x = center_x
        self.target_pixel_y = center_y
        self.speed = 8
        self.moving = False
        self.image = load_image('Idle (1).png')

    def draw(self, screen, map_data):
        screen.blit(self.image, (self.pixel_x - self.image.get_width() // 2, self.pixel_y - self.image.get_height() // 2))
        hp_text = font.render(str(self.hp), True, BLACK)
        screen.blit(hp_text, (self.pixel_x - hp_text.get_width() // 2, self.pixel_y - TILE_SIZE))

    def is_cell_occupied(self, col, row):
        if (col, row) in hex_map.obstacles:
            return True
        for unit in all_units:
            if unit != self and unit.x == col and unit.y == row:
                return True
        return False

    def get_neighbors(self, x, y):
        neighbors = []
        current_x, current_y = map_data[y][x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                if (col, row) == (x, y):
                    continue
                if self.is_cell_occupied(col, row):
                    continue
                neighbor_x, neighbor_y = map_data[row][col]
                distance = math.hypot(neighbor_x - current_x, neighbor_y - current_y)
                if distance <= TILE_SIZE * 2:
                    neighbors.append((col, row))
        return neighbors

    def get_accessible_cells(self):
        accessible_cells = []
        accessible_cells1 = []
        hero_x, hero_y = map_data[self.y][self.x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                if self.is_cell_occupied(col, row):
                    continue
                cell_x, cell_y = map_data[row][col]
                distance = math.hypot(cell_x - hero_x, cell_y - hero_y)
                if distance <= self.move_range:
                    accessible_cells.append((col, row))
        for i in accessible_cells:
            if self.move_cell  >= len(self.a_star_search((self.x, self.y), (i[0], i[1]))):
                accessible_cells1.append(i)
        return accessible_cells1

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
                return path

            for neighbor in self.get_neighbors(*current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

    def set_target_pixel(self, cell):
        col, row = cell
        self.target_pixel_x, self.target_pixel_y = map_data[row][col]

    def move_to(self, target):
        self.path = self.a_star_search((self.x, self.y), target)
        if self.path:
            self.moving = True
            next_cell = self.path.pop(0)
            self.set_target_pixel(next_cell)

    def update_position(self):
        if not self.moving:
            return

        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.pixel_x = self.target_pixel_x
            self.pixel_y = self.target_pixel_y
            for row in range(len(map_data)):
                for col in range(len(map_data[row])):
                    center_x, center_y = map_data[row][col]
                    if center_x == self.target_pixel_x and center_y == self.target_pixel_y:
                        self.x, self.y = col, row
                        break
            if self.path:
                next_cell = self.path.pop(0)
                self.set_target_pixel(next_cell)
            else:
                self.moving = False
        else:
            dx_norm = dx / distance
            dy_norm = dy / distance
            self.pixel_x += dx_norm * self.speed
            self.pixel_y += dy_norm * self.speed

    def can_attack(self):
        attack_cells = []
        hero_x, hero_y = map_data[self.y][self.x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                cell_x, cell_y = map_data[row][col]
                distance = math.hypot(cell_x - hero_x, cell_y - hero_y)
                if distance <= self.atack_range:
                    attack_cells.append((col, row))
        return attack_cells

    def attack(self, target):
        target.hp -= self.damage


class Enemy(Hero):
    def __init__(self, x, y, color=(255, 0, 0)):
        super().__init__(x, y, color)
        self.image = load_image('Idle (2).png')

    def draw(self, screen, map_data):
        screen.blit(self.image,
                    (self.pixel_x - self.image.get_width() // 2, self.pixel_y - self.image.get_height() // 2))
        hp_text = font.render(str(self.hp), True, BLACK)
        screen.blit(hp_text, (self.pixel_x - hp_text.get_width() // 2, self.pixel_y - TILE_SIZE))

    def is_cell_occupied(self, col, row, ignore_heroes=False):
        if (col, row) in hex_map.obstacles:
            return True
        for unit in all_units:
            if unit is self:
                continue
            if ignore_heroes:
                if isinstance(unit, Enemy) and unit.x == col and unit.y == row:
                    return True
            else:
                if unit.x == col and unit.y == row:
                    return True
        return False

    def get_neighbors(self, x, y):
        neighbors = []
        current_x, current_y = map_data[y][x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                if (col, row) == (x, y):
                    continue
                if self.is_cell_occupied(col, row, ignore_heroes=True):
                    continue
                neighbor_x, neighbor_y = map_data[row][col]
                distance = math.hypot(neighbor_x - current_x, neighbor_y - current_y)
                if distance <= TILE_SIZE * 2:
                    neighbors.append((col, row))
        return neighbors

    def get_accessible_cells(self):
        accessible_cells = []
        hero_x, hero_y = map_data[self.y][self.x]
        for row in range(len(map_data)):
            for col in range(len(map_data[row])):
                if self.is_cell_occupied(col, row, ignore_heroes=False):
                    continue
                cell_x, cell_y = map_data[row][col]
                distance = math.hypot(cell_x - hero_x, cell_y - hero_y)
                if distance <= self.move_range:
                    accessible_cells.append((col, row))
        return accessible_cells

    def update_position(self):
        if not self.moving:
            return

        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.pixel_x = self.target_pixel_x
            self.pixel_y = self.target_pixel_y
            for row in range(len(map_data)):
                for col in range(len(map_data[row])):
                    center_x, center_y = map_data[row][col]
                    if center_x == self.target_pixel_x and center_y == self.target_pixel_y:
                        self.x, self.y = col, row
                        break
            if self.path:
                next_cell = self.path.pop(0)
                if not self.is_cell_occupied(next_cell[0], next_cell[1], ignore_heroes=False):
                    self.x, self.y = next_cell
            else:
                self.moving = False
        else:
            dx_norm = dx / distance
            dy_norm = dy / distance
            self.pixel_x += dx_norm * self.speed
            self.pixel_y += dy_norm * self.speed


show_intro_screen()

map_data = show_map_choice_screen()
hex_map, heroes, enemies, all_units = create_game_from_map(map_data)

turn_order = all_units[:]
current_unit_index = 0
can_move = False
clock = pygame.time.Clock()
running = True
current_unit = turn_order[current_unit_index]
while running:
    if current_unit.moving is False and can_move is True:
        current_unit = turn_order[current_unit_index]
    highlight_cells = current_unit.get_accessible_cells()
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if current_unit in heroes and current_unit.moving is False:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                target_cell = hex_map.find_closest_hex(mouse_x, mouse_y)
                if target_cell is None:
                    print("Клик вне карты")
                    continue

                enemy_clicked = None
                for enemy in enemies:
                    if (enemy.x, enemy.y) == target_cell:
                        enemy_clicked = enemy
                        break

                if enemy_clicked:
                    if target_cell in current_unit.can_attack():
                        print(f"Герой атакует врага в ячейке {target_cell}")
                        current_unit.attack(enemy_clicked)
                        current_unit_index = (current_unit_index + 1) % len(turn_order)
                        highlight_cells = []
                        continue
                    else:
                        print("Враг вне зоны атаки.")
                        continue

                if target_cell in highlight_cells:
                    print(f"Герой выбирает ячейку {target_cell}")
                    current_unit.move_to(target_cell)
                    current_unit_index = (current_unit_index + 1) % len(turn_order)
                    highlight_cells = []
                else:
                    print(f"Ячейка {target_cell} недоступна для перемещения.")

    if current_unit in enemies and current_unit.moving is False:
        target = random.choice(heroes)
        highlight_cells = current_unit.get_accessible_cells()
        path = []
        print(current_unit.a_star_search((current_unit.x, current_unit.y), (target.x, target.y)))
        for i in current_unit.a_star_search((current_unit.x, current_unit.y), (target.x, target.y)):
            path.append(i)
        for step in path:
            attack_zone = current_unit.can_attack()
            if step in highlight_cells:
                current_unit.move_to(step)
                current_unit.update_position()
            if step in attack_zone and step == (target.x, target.y):
                current_unit.attack(target)
                print(f"У героя осталось hp: {target.hp}")
        current_unit_index = (current_unit_index + 1) % len(turn_order)
        highlight_cells = []

    for unit in turn_order:
        unit.update_position()
        can_move = True


    heroes = [hero for hero in heroes if hero.hp > 0]
    enemies = [enemy for enemy in enemies if enemy.hp > 0]
    all_units = heroes + enemies
    turn_order = [unit for unit in turn_order if unit.hp > 0]

    if not heroes or not enemies:
        a = ['Clouds 1.png', 'Clouds 2.png', 'Clouds 4.png', 'Clouds 5.png', 'Clouds 6.png', 'Clouds 7.png',
             'Clouds 8.png']
        random_fon = random.choice(a)
        fon = pygame.transform.scale(load_image(random_fon), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        if not heroes:
            game_over_text = big_font.render("Враги победили!", True, BLACK)
        else:
            game_over_text = big_font.render("Герои победили!", True, BLACK)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False
    else:
        current_unit_index %= len(turn_order)

    screen.fill(WHITE)
    hex_map.draw(screen, highlight_cells=highlight_cells)
    for hero in heroes:
        hero.draw(screen, map_data)
    for enemy in enemies:
        enemy.draw(screen, map_data)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()