import pygame
import random
import copy
from State import State
from collections import deque

LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3
NO_MOVE = 4
actions = [LEFT, DOWN, RIGHT, UP, NO_MOVE]

class Pacman:
    def __init__(self, board):
        self.player_image = pygame.transform.scale(pygame.image.load("assets/pacman.png"), (30, 30))
        self.ghost_image = pygame.transform.scale(pygame.image.load("assets/red_ghost.png"), (30, 30))
        self.display_mode_on = True
        self.board = board
        self.cell_size = 60
        pygame.init()
        self.screen = pygame.display.set_mode((len(board[0]) * self.cell_size, (len(board) * self.cell_size)))
        self.player_pos = dict()
        self.ghosts = []
        self.foods = []
        self.score = 0

        self.__init_game_elements()
        self.states = self.__init_states()
        self.current_state = self.__get_state()
        self.__draw_board()

    def __init_game_elements(self):
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                if self.board[y][x] == 'p':
                    self.player_pos['x'] = x
                    self.player_pos['y'] = y
                    self.init_player_pos = self.player_pos.copy()
                elif self.board[y][x] == 'g':
                    ghost = dict()
                    ghost['x'] = x
                    ghost['y'] = y
                    ghost['direction'] = random.choice([LEFT, DOWN])
                    self.ghosts.append(ghost)
                elif self.board[y][x] == '*':
                    food = dict()
                    food['x'] = x
                    food['y'] = y
                    self.foods.append(food)

        self.init_foods = copy.deepcopy(self.foods)
        self.init_ghosts = copy.deepcopy(self.ghosts)

    def reset(self):
        self.foods = copy.deepcopy(self.init_foods)
        self.ghosts = copy.deepcopy(self.init_ghosts)
        self.player_pos = self.init_player_pos.copy()
        self.score = 0
        return self.__get_state()

    def __init_states(self) -> list:
        states = []
        possible_player_pos = []
        possible_ghost_pos = []
        possible_food_pos = [[{'x': 0, 'y': 0}, {'x': 2, 'y': 2}, {'x': 6, 'y': 2}],
                             [{'x': 0, 'y': 0}, {'x': 2, 'y': 2}],
                             [{'x': 0, 'y': 0}, {'x': 6, 'y': 2}],
                             [{'x': 0, 'y': 0}],
                             [{'x': 2, 'y': 2}],
                             [{'x': 2, 'y': 2}, {'x': 6, 'y': 2}],
                             [{'x': 6, 'y': 2}], []]

        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                if self.board[y][x] != 'w':
                    possible_player_pos.append({'x': x, 'y': y})
                    possible_ghost_pos.append({'x': x, 'y': y})

        for player_pos in possible_player_pos:
            for ghost_pos in possible_ghost_pos:
                for food_pos in possible_food_pos:
                    states.append(State(player_pos=player_pos, ghost_pos=ghost_pos, food_pos=food_pos))

        for idx, state in enumerate(states):
            state.possible_actions = self.get_possible_actions(state)
            state.name = str(idx)

        return states

    def get_all_states(self):
        return self.states

    def is_terminal(self, state) -> bool:
        if (state.player_pos == state.ghost_pos) or state.food_pos == False:
            return True
        return False

    def get_possible_actions(self, state: object) -> tuple:
        possible_actions = []
        player_x = state.player_pos['x']
        player_y = state.player_pos['y']
        directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]

        for idx, (x, y) in enumerate(directions):
            try:
                next_y = player_y + y
                next_x = player_x + x
                next_pos = self.board[next_y][next_x]
            except IndexError:
                continue
            else:
                if next_y != -1 and next_x != -1 and next_pos != 'w':
                    possible_actions.append(idx)

        return tuple(possible_actions)

    def get_next_states(self, state, action):
        next_states = []
        for s in self.states:
            if s.player_pos == state.simulate_player_action(action) and s.food_pos == state.food_pos:
                for i in range(4):
                    if s.ghost_pos == state.simulate_ghost_action(i):
                        next_states.append(s)

        probability = 1 / len(next_states)
        return dict(zip(next_states, [probability] * len(next_states)))

    def get_reward(self, state, action, next_state):
        reward = 0
        for food_pos in state.food_pos:
            if state.simulate_player_action(action) == food_pos:
                reward += 10
        if next_state.food_pos == False:
            reward += 500
        if state.simulate_player_action(action) == next_state.ghost_pos:
            reward -= 500
        reward -= 1
        return reward

    def step(self, action):
        width = len(self.board[0])
        height = len(self.board)

        if action == LEFT and self.player_pos['x'] > 0:
            if self.board[self.player_pos['y']][self.player_pos['x'] - 1] != 'w':
                self.player_pos['x'] -= 1
        if action == RIGHT and self.player_pos['x'] + 1 < width:
            if self.board[self.player_pos['y']][self.player_pos['x'] + 1] != 'w':
                self.player_pos['x'] += 1
        if action == UP and self.player_pos['y'] > 0:
            if self.board[self.player_pos['y'] - 1][self.player_pos['x']] != 'w':
                self.player_pos['y'] -= 1
        if action == DOWN and self.player_pos['y'] + 1 < height:
            if self.board[self.player_pos['y'] + 1][self.player_pos['x']] != 'w':
                self.player_pos['y'] += 1

        for ghost in self.ghosts:
            if ghost['x'] == self.player_pos['x'] and ghost['y'] == self.player_pos['y']:
                self.score -= 500
                reward = -500
                self.__draw_board()
                return self.__get_state(), reward, True, self.score

        for food in self.foods:
            if food['x'] == self.player_pos['x'] and food['y'] == self.player_pos['y']:
                self.score += 10
                reward = 10
                self.foods.remove(food)
                break
        else:
            self.score -= 1
            reward = -1

        for ghost in self.ghosts:
            path_to_pacman = self.bfs((ghost['x'], ghost['y']), (self.player_pos['x'], self.player_pos['y']))

            if path_to_pacman:
                next_pos = path_to_pacman[0]
                ghost['x'], ghost['y'] = next_pos

        for ghost in self.ghosts:
            if ghost['x'] == self.player_pos['x'] and ghost['y'] == self.player_pos['y']:
                self.score -= 500
                reward = -500
                self.__draw_board()
                return self.__get_state(), reward, True, self.score

        self.__draw_board()

        if len(self.foods) == 0:
            reward = 500
            self.score += 500

        return self.__get_state(), reward, len(self.foods) == 0, self.score

    def bfs(self, start, target):
        queue = deque([(start, [])])
        visited = set()

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            if current in visited:
                continue

            visited.add(current)

            x, y = current
            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

            for neighbor in neighbors:
                if 0 <= neighbor[0] < len(self.board[0]) and 0 <= neighbor[1] < len(self.board) and \
                        self.board[neighbor[1]][neighbor[0]] != 'w':
                    queue.append((neighbor, path + [neighbor]))

        return []

    def __draw_board(self):
        if self.display_mode_on:
            self.screen.fill((0, 0, 0))

            y = 0

            for line in self.board:
                x = 0
                for obj in line:
                    if obj == 'w':
                        color = (0, 255, 255)
                        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, 60, 60))
                    x += 60
                y += 60

            color = (255, 255, 0)
            self.screen.blit(self.player_image, (self.player_pos['x'] * self.cell_size + 15,
                                                 self.player_pos['y'] * self.cell_size + 15))

            color = (255, 0, 0)
            for ghost in self.ghosts:
                self.screen.blit(self.ghost_image, (ghost['x'] * self.cell_size + 15, ghost['y'] * self.cell_size + 15))

            color = (255, 255, 255)

            for food in self.foods:
                pygame.draw.ellipse(self.screen, color,
                                    pygame.Rect(food['x'] * self.cell_size + 25, food['y'] * self.cell_size + 25, 10, 10))

            pygame.display.flip()

    def __get_state(self):
        for state in self.states:
            if state.player_pos == self.player_pos and state.ghost_pos['x'] == self.ghosts[0]['x'] and \
                    state.ghost_pos['y'] == self.ghosts[0]['y'] and state.food_pos == self.foods:
                return state

    def turn_off_display(self):
        self.display_mode_on = False

    def turn_on_display(self):
        self.display_mode_on = True

    def get_state_size(self):
        return len(self.board) * len(self.board[0]) * 4


