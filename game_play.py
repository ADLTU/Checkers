import numpy as np
from MCT_search import *


class Checkers:

    def __init__(self, state, color=1):
        self.curr_state = state
        self.color = color
        # self.num_plays = 0

    def find_possible_plays(self, color=0):
        if not color:
            color = self.color
        if color == 1:
            curr_state = self.curr_state
        else:
            curr_state = np.rot90(self.curr_state, 2)

        # Check for normal pieces and kings moves in the right direction
        curr_pos_r, curr_pos_c = np.where((curr_state == color) | (curr_state == color * 2))
        num_pcs_left = len(curr_pos_r)
        has_jumps, possible_plays = self.find_play_from_board(curr_state, num_pcs_left, curr_pos_r, curr_pos_c, color)

        # Check for kins moves in the opposite direction
        curr_state = np.rot90(curr_state, 2)
        curr_pos_r, curr_pos_c = np.where(curr_state == color * 2)
        num_k = len(curr_pos_r)
        k_jumps, k_possible_plays = self.find_play_from_board(curr_state, num_k, curr_pos_r, curr_pos_c, color, k=True)

        if has_jumps or k_jumps:  # if jumps are possible force them
            possible_plays = [pp for pp in possible_plays if pp[2]]
            k_possible_plays = [pp for pp in k_possible_plays if pp[2]]

        if possible_plays and k_possible_plays:
            return np.concatenate((possible_plays, k_possible_plays))
        elif possible_plays:
            return possible_plays
        elif k_possible_plays:
            return k_possible_plays
        else:
            return []

    def find_play_from_board(self, curr_state, num_pcs_left, curr_pos_r, curr_pos_c, color, k=False):
        has_jumps = False
        jumped = False
        possible_plays = []
        enemy = [-color, -color*2]
        for i in range(num_pcs_left):
            c_jump_l = True
            c_jump_r = True
            if curr_pos_r[i] == 6 or curr_pos_c[i] == 1:
                c_jump_r = False
            if curr_pos_r[i] == 6 or curr_pos_c[i] == 6:
                c_jump_l = False
            if curr_pos_r[i] != 7:
                old_pos = [curr_pos_r[i], curr_pos_c[i]]
                new_pos = []
                if self.xor(color == -1, k):
                    old_pos = 7 - np.array(old_pos)
                if curr_pos_c[i] != 7:  # piece is not on right edge of board
                    if curr_state[curr_pos_r[i] + 1][curr_pos_c[i] + 1] in enemy and c_jump_l:  # enemy piece on right?
                        if curr_state[curr_pos_r[i] + 2][curr_pos_c[i] + 2] == 0:  # can kill enemy?
                            jumped = True
                            has_jumps = True
                            new_pos = [curr_pos_r[i] + 2, curr_pos_c[i] + 2]
                    elif curr_state[curr_pos_r[i] + 1][curr_pos_c[i] + 1] == 0:
                        new_pos = [curr_pos_r[i] + 1, curr_pos_c[i] + 1]
                    if len(new_pos):
                        if self.xor(color == -1, k):
                            new_pos = 7 - np.array(new_pos)
                        possible_plays.append([old_pos, new_pos, has_jumps])
                        has_jumps = False
                new_pos = []
                if curr_pos_c[i] != 0:  # piece is on right edge of board
                    if curr_state[curr_pos_r[i] + 1][curr_pos_c[i] - 1] in enemy and c_jump_r:  # enemy piece on left?
                        if curr_state[curr_pos_r[i] + 2][curr_pos_c[i] - 2] == 0:  # can kill enemy?
                            jumped = True
                            has_jumps = True
                            new_pos = [curr_pos_r[i] + 2, curr_pos_c[i] - 2]
                    elif curr_state[curr_pos_r[i] + 1][curr_pos_c[i] - 1] == 0:
                        new_pos = [curr_pos_r[i] + 1, curr_pos_c[i] - 1]
                    if len(new_pos):
                        if self.xor(color == -1, k):
                            new_pos = 7 - np.array(new_pos)
                        possible_plays.append([old_pos, new_pos, has_jumps])
                        has_jumps = False
        return jumped, possible_plays

    # def evaluate(self, curr_state):
    #     color = self.color
    #     curr_pos_r,  curr_pos_c = np.where(curr_state == self.color) #get position of friendly pieces in the current state
    #     num_pcs = len(curr_pos_r) #get number of pieces of friendly side
    #     col_calc = curr_pos_c[np.where(curr_pos_c > 3)] - 4 #account fo column, closer to edge the better
    #     col_calc_2 = 3 - curr_pos_c[np.where(curr_pos_c < 4)] #account fo column, closer to edge the better
    #
    #
    #     oppo_curr_pos_r,  oppo_curr_pos_c = np.where(curr_state == - self.color) #get position of enemy pieces in the current state
    #     oppo_curr_pos_r = 7 - oppo_curr_pos_r
    #     oppo_num_pcs = len(oppo_curr_pos_r)#get number of pieces of enemy side
    #     oppo_col_calc = oppo_curr_pos_c[np.where(oppo_curr_pos_c > 3)] - 4#account fo column, closer to edge the better
    #     oppo_col_calc_2 = 3 - oppo_curr_pos_c[np.where(oppo_curr_pos_c < 4)]#account fo column, closer to edge the better
    #
    #     #calculating the differance according to the following rule:
    #     # 1 piece = 4 pts
    #     # the closer to enemy edge the better +1 for each row
    #     # the closer the board edge the better +1 for each column away from center
    #
    #     points = (4 * num_pcs) + sum(curr_pos_r) + sum(col_calc) + sum(col_calc_2)
    #     oppo_points = (4 * oppo_num_pcs) + sum(oppo_curr_pos_r) + sum(oppo_col_calc) + sum(oppo_col_calc_2)
    #
    #     final = points - oppo_points
    #
    #     return final

    def update_state(self, move):
        new_state = np.copy(self.curr_state)

        # move the piece
        new_state[move[0][0]][move[0][1]], new_state[move[1][0]][move[1][1]] = new_state[move[1][0]][
                                                                                   move[1][1]], \
                                                                               new_state[move[0][0]][move[0][1]]

        if self.color == 1 and move[1][0] == 7 and new_state[move[1][0]][move[1][1]] == 1:  # make a white king
            new_state[move[1][0]][move[1][1]] += 1
        if self.color == -1 and move[1][0] == 0 and new_state[move[1][0]][move[1][1]] == -1:  # Make a black king
            new_state[move[1][0]][move[1][1]] -= 1

        if move[2]: # if a jump was made remove a piece
            if move[0][0] > move[1][0]:
                x = move[0][0] - 1
            else:
                x = move[0][0] + 1

            if move[0][1] > move[1][1]:
                y = move[0][1] - 1
            else:
                y = move[0][1] + 1
            new_state[x][y] = 0

        return Checkers(new_state, -self.color)

    def game_over(self):

        if self.check_winner() is None:
            return False #game not over
        else:
            return True #game over

    def check_winner(self):
        curr_w_r, curr_w_c = np.where((self.curr_state == 1) | (self.curr_state == 2))
        num_w_pcs = len(curr_w_r) #get number of white pieces

        curr_b_r, curr_b_c = np.where((self.curr_state == - 1) | (self.curr_state == -2))
        num_b_pcs = len(curr_b_r) #get number of black pieces

        if num_w_pcs == 0:
            return 1
        elif num_b_pcs == 0:
            return -1
        elif len(self.find_possible_plays(1)) == 0:
            return -1
        elif len(self.find_possible_plays(-1)) == 0:
            return 1
        else:
            return None #game not over

    def xor(self, a, b):
        if a != b:
            return 1
        else:
            return 0


def from_idx_to_pos(f_idx, t_idx):  # this is to convert from matrix indexes to alphanumerical positions
    change = {
        0: 'A',
        1: 'B',
        2: 'C',
        3: 'D',
        4: 'E',
        5: 'F',
        6: 'G',
        7: 'H'
    }

    f_pos = change[f_idx[1]] + str(7 - f_idx[0])
    t_pos = change[t_idx[1]] + str(7 - t_idx[0])

    return [f_pos, t_pos]


def robot_make_play(board_state, play_as=1, search_time=1):
    game = Checkers(board_state, color=play_as)
    if game.game_over():
        return board_state
    tree_root = MCT_Node(game)
    tree = MonteCarloTree(tree_root, sim_time=search_time)
    best_next_state = tree.search_best_action()
    return best_next_state.state.curr_state


def get_user_play(board_state, play_as=-1):
    game = Checkers(board_state, color=play_as)
    if game.game_over():
        return board_state
    available_plays = game.find_possible_plays()
    print("Your turn, Pick on of The available plays:")
    for v, p in enumerate(available_plays):
        print(v+1, ":", from_idx_to_pos(p[0], p[1]))
    chosen_play = input()
    ### for testing
    # ran = random.choice(available_plays)
    player_choice_state = game.update_state(available_plays[int(chosen_play)-1])
    return player_choice_state.curr_state


def main(board):
    current_board = board
    side = int(input("Want to play as Black (-1) or White (1)?"))
    if side == 1:
        print("You have Chosen White, now please select game difficulty")
    elif side == -1:
        print("You have Chosen Black, now please select game difficulty")
    diff = int(input("1: Easy\n2: Difficult"))
    if diff == 1:
        diff = 0.01
    elif diff == 2:
        diff = 1
    while True:
        if side == -1:
            current_board = get_user_play(current_board, play_as=-1)
            current_board = robot_make_play(current_board, play_as=1, search_time=diff)
        else:
            current_board = robot_make_play(current_board, play_as=-1, search_time=diff)
            current_board = get_user_play(current_board, play_as=1)
        if Checkers(current_board).game_over():
            print("got Here")
            if Checkers(current_board).check_winner() == -1:
                print("Black wins!")
            elif Checkers(current_board).check_winner() == 1:
                print("White wins!")
            else:
                print("Tie!")
            break


initial_board = np.array([
            [+0, +1, +0, +1, +0, +1, +0, +1],
            [+1, +0, +1, +0, +1, +0, +1, +0],
            [+0, +1, +0, +1, +0, +1, +0, +1],

            [+0, +0, +0, +0, +0, +0, +0, +0],
            [+0, +0, +0, +0, +0, +0, +0, +0],

            [-1, +0, -1, +0, -1, +0, -1, +0],
            [+0, -1, +0, -1, +0, -1, +0, -1],
            [-1, +0, -1, +0, -1, +0, -1, +0],
        ])

main(initial_board)
