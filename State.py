import numpy as np

class State:

    def __init__(self, player_pos: dict, ghost_pos: dict, food_pos: list, possible_actions: tuple = None):
        self.player_pos = player_pos
        self.ghost_pos = ghost_pos
        self.food_pos = food_pos
        self.possible_actions = possible_actions
        self.probability = None
        self.name = None

    def transform_to_vector(self):
        vector = []
        vector.append([self.player_pos['x'], self.player_pos['y']])
        vector.append([self.ghost_pos['x'], self.ghost_pos['y']])
        for food in self.food_pos:
            vector.append([food['x'], food['y']])

        if len(self.food_pos) == 0:
            vector.append([-1, -1])
            vector.append([-1, -1])
        if len(self.food_pos) == 1:
            vector.append([-1, -1])

        return np.array(vector).flatten()

    def simulate_player_action(self, action: int) -> dict:
        pos = dict()
        if action == 0:
            pos['x'] = self.player_pos['x'] - 1
            pos['y'] = self.player_pos['y']
        if action == 1:
            pos['x'] = self.player_pos['x']
            pos['y'] = self.player_pos['y'] + 1
        if action == 2:
            pos['x'] = self.player_pos['x'] + 1
            pos['y'] = self.player_pos['y']
        if action == 3:
            pos['x'] = self.player_pos['x']
            pos['y'] = self.player_pos['y'] - 1
        if action == 4:
            pos['x'] = self.player_pos['x']
            pos['y'] = self.player_pos['y']
        return pos

    def simulate_ghost_action(self, action: int) -> dict:
        pos = dict()
        if action == 0:
            pos['x'] = self.ghost_pos['x'] - 1
            pos['y'] = self.ghost_pos['y']
        if action == 1:
            pos['x'] = self.ghost_pos['x']
            pos['y'] = self.ghost_pos['y'] + 1
        if action == 2:
            pos['x'] = self.ghost_pos['x'] + 1
            pos['y'] = self.ghost_pos['y']
        if action == 3:
            pos['x'] = self.ghost_pos['x']
            pos['y'] = self.ghost_pos['y'] - 1
        return pos
