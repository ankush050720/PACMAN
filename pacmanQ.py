import pygame
import random
from collections import defaultdict
from Board import board
from Pacman import Pacman
import matplotlib.pyplot as plt
import dill

class QLearningAgent:
    def __init__(self, alpha, epsilon, discount, get_legal_actions):
        self.get_legal_actions = get_legal_actions
        self._qvalues = defaultdict(lambda: defaultdict(lambda: 0))
        self.alpha = alpha
        self.epsilon = epsilon
        self.discount = discount

    def get_qvalue(self, state, action):
        return self._qvalues[state][action]

    def set_qvalue(self, state, action, value):
         self._qvalues[state][action] = value

    

    def save_qvalues(self, filename="qvalues.pkl"):
        with open(filename, "wb") as f:
            dill.dump(self._qvalues, f)

    def load_qvalues(self, filename="qvalues.pkl"):
        try:
            with open(filename, "rb") as f:
                return dill.load(f)
        except FileNotFoundError:
            return None

    def get_value(self, state):
        possible_actions = self.get_legal_actions(state)
        if len(possible_actions) == 0:
            return 0.0
        return max(self.get_qvalue(state, action) for action in possible_actions)

    def update(self, state, action, reward, next_state):
        gamma = self.discount
        learning_rate = self.alpha   
        value = (1 - learning_rate) * self.get_qvalue(state, action) + learning_rate * (
                reward + gamma * self.get_value(next_state))
        self.set_qvalue(state, action, value)

    def get_best_action(self, state):
        possible_actions = self.get_legal_actions(state)
        if len(possible_actions) == 0:
            return None
        best_value = self.get_value(state)
        best_actions = [action for action in possible_actions if self.get_qvalue(state, action) == best_value]
        best_action = random.choice(best_actions)
        return best_action

    def get_action(self, state):
        possible_actions = self.get_legal_actions(state)
        if len(possible_actions) == 0:
            return None
        lst = [0, 1]
        choice = random.choices(lst, weights=(1 - self.epsilon, self.epsilon))
        chosen_action = random.choice(possible_actions) if choice[0] == 1 else self.get_best_action(state)
        return chosen_action

    def turn_off_learning(self):
        self.epsilon = 0
        self.alpha = 0


def play_and_train(env, agent):
    total_reward = 0.0
    state = env.reset()
    done = False
    while not done:
        action = agent.get_action(state)
        next_state, reward, done, _ = env.step(action)
        agent.update(state, action, reward, next_state)
        state = next_state
        total_reward += reward
        if done:
            break
    return total_reward


clock = pygame.time.Clock()
pacman = Pacman(board)
pacman.reset()
agent = QLearningAgent(alpha=.5, epsilon=0.8, discount=0.99, get_legal_actions=pacman.get_possible_actions)
pacman.turn_off_display()
filename = "qvalues.pkl"
loaded_qvalues = agent.load_qvalues(filename)

if loaded_qvalues is not None:
    agent._qvalues = loaded_qvalues
    print(len(agent._qvalues))
    for state, actions in loaded_qvalues.items():
        for action, value in actions.items():
            agent.set_qvalue(state, action, value)
def gg():
    state = pacman.reset()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        state, reward, done, score = pacman.step(agent.get_best_action(state))
    return score
a = []
num_epoch = 20000
for i in range(num_epoch):
    if i % 100 == 0:
        print(f'Learning epoch: {i}')
    play_and_train(pacman, agent)
    if i%50==0:
        a.append(gg())
agent.save_qvalues(filename)
print(len(agent._qvalues), "owo")
agent.turn_off_learning()
pacman.turn_on_display()
done = False
print("Game begins...")
state = pacman.reset()
i = 0


while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    state, reward, done, score = pacman.step(agent.get_best_action(state))
    i += 1
    print(f'Score = {score}')
    clock.tick(10)

plt.plot(a)
plt.xlabel('Episodes')
plt.ylabel('Total Reward')
plt.title('Training Progress')
plt.show()