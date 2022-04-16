import random
import numpy as np
from typing import List, Optional, Tuple

from uttt import BaseAgent, UTTTGame


class Agent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.LOCAL_POS_REWARD = np.array([
            1, 0, 1,
            0, 2, 0,
            1, 0, 1
        ])
        self.TWO_ROW_REWARD = 3
        self.THREE_ROW_REWARD = 10

    def make_move(
        self,
        boards: List[List[Optional[str]]],
        board_winners: List[Optional[str]],
        playable_boards: List[int],
    ) -> Tuple[int, int]:
        """Makes a move.

        Args:
            boards (List[List[Optional[str]]]): A list of local boards, which together form the global board.
                                                Each local board is a list of nine tiles (indexed 0 to 8),
                                                represented as either 'R' if marked by the red player,
                                                'B' if marked by the blue player, or None if the tile is empty.

            board_winners (List[Optional[str]]): The winners of each local board. While this totally random
                                                 agent does not take local board winners into account, you will
                                                 probably want to in order to implement a better strategy!

            playable_boards (List[int]): The local boards that may be played in.

        Returns:
            Tuple[int, int]: The local board and tile position to mark for your agent.
        """
        """
        move = None
        high_score = -np.inf
        for board in playable_boards:
            for tile in range(9):
                if boards[board][tile] is None:
                    current_score = self.LOCAL_POS_REWARD[tile]
                    
                    if current_score > high_score:
                        high_score = current_score
                        move = (board, tile)

        return move
        """
        possible_moves = [
            (board, tile)
            for board in playable_boards
            for tile in range(0, 9)
            if boards[board][tile] is None
        ]

        # Pick a valid move at random
        move = random.choice(possible_moves)

        ################################################################################

        return move


def main():
    # Instantiate the agent
    agent = Agent()

    # Start playing the game
    game = UTTTGame(agent)
    game.play()


# This is a common Python idiom, which signals
# to other Python programmers that this is a script.
if __name__ == "__main__":
    main()
