"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if terminal(board):
        return None
    b = [
        board[i][j] for i in range(3) for j in range(3) if board[i][j] != EMPTY
    ]  # this lset was created to optimise search
    if len(b) == 0 or b.count(X) == b.count(
        O
    ):  # if the board is all empty or there is as much Os as Xs then it's X's turn
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):  # return an empty list if the boards is terminal
        return []

    acts = set()  # set to store actions
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                acts.add((i, j))  # actions are a tuple of coordinates if empty spots

    return acts


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # filter out negative moves and out of bound moves by raising an exception
    if (action[0] < 0 or action[0] >= 3) or (action[1] < 0 or action[1] >= 3):
        raise Exception

    # if the spot is already taaken an exception is raised
    if board[action[0]][action[1]] != EMPTY:
        raise Exception

    cpy = copy.deepcopy(
        board
    )  # deepcopying the board in irder not to modify the original one
    play = player(board)
    cpy[action[0]][action[1]] = play  # placing the player into the spot

    return cpy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # this function works by checking all possible cases
    # cheching rows
    for row in board:
        if row[0] != EMPTY and row[0] == row[1] == row[2]:
            return row[0]
    # columns
    for j in range(3):
        if board[0][j] != EMPTY and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    # diagonals
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    if board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    b = [
        board[i][j] for i in range(3) for j in range(3) if board[i][j] != EMPTY
    ]  # this list is created to only look at its length without having to do linear search
    if len(b) == 9:  # then everything is full
        return True
    if winner(
        board
    ):  # if one of the states of the winner function is verified then no need to continue playing
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # accepts only terminal boards and follows instructions based on the winner function's result
    if not terminal(board):
        return None

    if winner(board) is None:
        return 0
    elif winner(board) == X:
        return 1
    else:
        return -1


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # the minimax algorithm using alpha beta rendering for optimisation
    if terminal(board):
        return None
    # we get the current player and if the board is terminal then there is no need to think of a move
    current_player = player(board)

    # this function returns the max value of a board and compares it to beta if it's smaller than beta then there are better options and no need to further explore
    def max_v(board, alpha, beta):
        if terminal(board):
            return utility(board)

        v = -math.inf
        for action in actions(board):
            v = max(v, min_v(result(board, action), alpha, beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)

        return v

    # same logic as the function before but we r looking for the smallest value
    def min_v(board, alpha, beta):
        if terminal(board):
            return utility(board)

        v = math.inf
        for action in actions(board):
            v = min(v, max_v(result(board, action), alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    best_a = None
    alpha = -math.inf
    beta = math.inf

    if current_player == X:  # X is the maximizer player
        best_v = -math.inf
        # the best move is the one that gives the other player the smallest value using the min_v function
        for action in actions(board):
            v = min_v(result(board, action), alpha, beta)
            if v > best_v:
                best_v = v
                best_a = action
            alpha = max(alpha, best_v)
    else:  # same logic for the min player but inverted
        best_v = math.inf
        for action in actions(board):
            v = max_v(result(board, action), alpha, beta)
            if v < best_v:
                best_v = v
                best_a = action
            beta = min(beta, best_v)

    return best_a  # we return the best move
