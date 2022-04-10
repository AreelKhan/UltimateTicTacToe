import numpy as np

BOARD = np.array([None for _ in range(9)]).reshape(3, 3)
X: int = 1
O: int = 0
WIN_REWARD = 10
TWO_ROW_REWARD = 3
POS_REWARD = np.array([
    [1, 0, 1],
    [0, 2, 0],
    [1, 0, 1]
])


def all_same(arr):
    """
    Checks if all elements in an array are the same
    """
    return np.all(arr == arr[0])


def idx_convert(idx):
    """
    Converts from 1D to 2D arrays
    0 1 2      (0,0) (0,1) (0,2)
    3 4 5  --> (1,0) (1,1) (1,2)
    6 7 8      (2,0) (2,1) (2,2)
    """
    row = idx // 3
    col = idx % 3
    return row, col


def check_win(board):
    """
    Checks if there is a win in the board 
    """
    diag1, diag2 = [], []
    for i in range(3):
        diag1.append(board[i, i])
        diag2.append(board[2 - i, i])
        if all_same(board[i]) or all_same(board[:, i]):
            return True
    if all_same(diag1) or all_same(diag2):
        return True
    return False


def score_move(board, move, player):
    """
    board: board on which move will be made
    move: the index move where the move is played, the score for making this move is calculated
    player: the player who is playing "X" or "O"
    """
    idx = idx_convert(move)
    score = POS_REWARD[idx]
    return score
    # check three in a row


if __name__ == "__main__":
    print(score_move(BOARD, 8, X))
