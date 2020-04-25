import time
import random
from collections import defaultdict
import numpy as np


class MonteCarloTree:

    def __init__(self, root, sim_time=5):
        self.sim_time = sim_time  # Simulation time
        self.root = root  # Game state tree

    def search_best_action(self):

        sim_count = 0
        start_time = time.time()

        while time.time() - start_time < self.sim_time:
            picked_child = self.pick_child()
            simulation_out = picked_child.simulate()
            picked_child.backpropagate(simulation_out)
        return self.root.find_best_child(ev=0)

    def pick_child(self):
        curr_node = self.root
        while curr_node.is_leaf() is False:
            if not curr_node.is_fully_expanded():
                return curr_node.expand()
            else:
                curr_node = curr_node.find_best_child()
        return curr_node


class MCT_Node:

    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []

        self.number_of_visits = 0
        self.results = defaultdict(int)
        self.untried_plays = None

    def get_untried_plays(self):  # Get a list of all unexplored nodes
        if self.untried_plays is None:
            self.untried_plays = self.state.find_possible_plays()
        return self.untried_plays

    def gt_num_wins(self):  # How many times has following this node lead to a win?
        wins = self.results[self.state.color]
        loses = self.results[-self.state.color]
        return wins - loses

    def gt_num_visits(self):  # How many times has a node been visited
        return self.number_of_visits

    def expand(self):  # Pick one of the children of a node
        untried_plays = list(self.untried_plays)
        play = untried_plays.pop()
        next_state = self.state.update_state(play)
        child = MCT_Node(next_state, self)
        self.children.append(child)
        return child

    def is_leaf(self):  # is the node representing a terminal state
        return self.state.game_over()

    def find_best_child(self, ev=1):  # Calculate the Upper Confidence Bound (UCB) of a node
        vis = self.number_of_visits
        child_weights = [
            (c.gt_num_wins() / c.gt_num_visits()) + ev * np.sqrt((2 * np.log(vis) / c.gt_num_visits()))
            for c in self.children
        ]
        return self.children[np.argmax(child_weights)]

    def simulate(self):  # We simulate a game through making random moves
        current_sim_state = self.state
        while not current_sim_state.game_over():
            possible_plays = current_sim_state.find_possible_plays()
            play = random.choice(possible_plays)
            current_sim_state = current_sim_state.update_state(play)

        return current_sim_state.check_winner()

    def backpropagate(self, sim_outcome):  # We reached a leaf and now we update the values of all nodes before it
        self.number_of_visits += 1
        self.results[sim_outcome] += 1
        if self.parent:
            self.parent.backpropagate(sim_outcome)

    def is_fully_expanded(self):  # Do we have all children of a certain node
        return len(self.get_untried_plays()) == 0


