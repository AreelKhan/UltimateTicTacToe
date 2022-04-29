import sys
import collections
import pygame as pg
import numpy as np
from random import randint
from itertools import product
from agent.main import Agent

pg.init()
pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN])


class UltimateTicTacToe:

    def __init__(self):
        # Screen
        self.WIDTH = 640
        self.ROWS = 3
        self.GAP = 25
        self.WIN_BORDER = 16
        self.LOCAL_WIDTH = (self.WIDTH - self.GAP * 4) // self.ROWS  # width of a local board
        self.LOCAL_DISTANCE = self.GAP + self.LOCAL_WIDTH  # distance between two consecutive local boards
        self.CELL_WIDTH = self.LOCAL_WIDTH // self.ROWS  # width of one cell

        self.FPS = 10  # limit game to 10 FPS
        self.clock = pg.time.Clock()
        self.win = pg.display.set_mode((self.WIDTH, self.WIDTH))  # pygame window
        pg.display.set_caption("Ultimate TicTacToe")

        # Colors
        self.BLACK = (0, 30, 60)
        self.LIGHT_GRAY = (210, 210, 210)
        self.BLUE = (0, 75, 150)
        self.RED = (240, 75, 25)
        self.GREEN = (0, 205, 100)
        self.YELLOW = (245, 230, 75)

        # Game Board and Logic
        self.global_board = np.array(
            [
                np.full(shape=self.ROWS ** 2, fill_value=None)
                for _ in range(self.ROWS ** 2)
            ]
        )
        self.board_winners = [None for _ in range(self.ROWS ** 2)]  # Winners of each local board
        self.playable_boards = []  # Boards on which current turn can be played
        self.turn = True  # True if user's turn, false if agent's turn
        self.winner = None

        # Agent
        self.agent = Agent()
        # DOXA uses R, B, and S for red, blue, and stalemate respectively.
        # These dictionaries help translate the DOXA lingo with the variables in this program
        self.player_turn_dict = {True: "R", False: "B"}
        self.player_color_dict = {"R": self.RED, "B": self.GREEN, "S": self.YELLOW, None: self.LIGHT_GRAY}

    def __str__(self):
        """
        Implements the string representation of the UltimateTicTacToe game object

        Returns:
            str: string representation of the game board in current state.
        """
        sep = ""
        str_board = ""
        for t in range(0, self.ROWS ** 2, self.ROWS):
            for i in range(0, self.ROWS ** 2, self.ROWS):
                row = ""
                for j in range(self.ROWS):
                    for k in range(self.ROWS):
                        row += f"{self.global_board[t + j, i + k]}".center(4)
                    if (j + 1) % self.ROWS != 0:
                        row += "| "
                str_board += row + "\n"
                sep = "_" * (len(row) - 1)
            if t != self.ROWS * (self.ROWS - 1):
                str_board += sep + "\n"
        return str_board

    def _draw_local(self, x, y, local_board):
        """
        Draws the grid lines for a local board at position x,y

        Args:
            x (float): x co-ordinate of the top left corner where the board must be drawn.
            y (float): y co-ordinate of the top left corner where the board must be drawn.
        """
        # highlight playable boards
        if local_board in self.playable_boards:
            pg.draw.rect(
                surface=self.win,
                color=self.BLUE,
                rect=pg.Rect((x, y), (self.LOCAL_WIDTH, self.LOCAL_WIDTH))
            )

        # draw local entries
        local = self.global_board[local_board]
        for i in range(self.ROWS ** 2):
            if local[i] is not None:
                cell_x = x + (i % self.ROWS) * self.CELL_WIDTH
                cell_y = y + (i // self.ROWS) * self.CELL_WIDTH
                pg.draw.rect(
                    surface=self.win,
                    color=self.player_color_dict[local[i]],
                    rect=pg.Rect((cell_x, cell_y), (self.CELL_WIDTH, self.CELL_WIDTH))
                )

        # draw local grid lines
        for i in range(self.ROWS + 1):
            pg.draw.line(
                surface=self.win,
                color=self.player_color_dict[self.board_winners[local_board]],
                start_pos=(x + self.CELL_WIDTH * i, y),
                end_pos=(x + self.CELL_WIDTH * i, y + self.LOCAL_WIDTH),
                width=3
            )
            pg.draw.line(
                surface=self.win,
                color=self.player_color_dict[self.board_winners[local_board]],
                start_pos=(x, y + self.CELL_WIDTH * i),
                end_pos=(x + self.LOCAL_WIDTH, y + self.CELL_WIDTH * i),
                width=3
            )

    def _render_board(self):
        """
        Draws and renders the full game board.

        Returns:
                None
        """
        self.win.fill(self.BLACK)

        # draw local board
        for i, j in product(range(self.ROWS), range(self.ROWS)):
            self._draw_local(
                x=self.GAP + j * self.LOCAL_DISTANCE,
                y=self.GAP + i * self.LOCAL_DISTANCE,
                local_board=self.ROWS * i + j
            )

        pg.display.update()

    def _in_range(self, corner, length, coord):
        """
        Checks if coord falls within the square with side length equal to the
        length parameter and top left corner at the corner parameter.

        Args:
            corner (Tuple[int, int]): top left corner of square.
            length (int): length of square.
            coord (Tuple[int, int]): coordinates to check.

        Returns:
            bool: True if coord in cell, False otherwise
        """
        if corner[0] <= coord[0] <= corner[0] + length:
            if corner[1] <= coord[1] <= corner[1] + length:
                return True
        return False

    def _valid_input(self, mouse_press):
        """
        Validates if the location of the player's mouse press is on a valid cell

        Args:
            mouse_press (Tuple[int, int]): (x,y) coordinates of user's mouse press

        Returns:
            bool OR Tuple[int, int]: False if invalid, (local_board, cell) if valid
        """
        for i in self.playable_boards:  # check only playable boards
            local_x = self.GAP + (i % self.ROWS) * self.LOCAL_DISTANCE
            local_y = self.GAP + (i // self.ROWS) * self.LOCAL_DISTANCE
            on_local = self._in_range(
                corner=(local_x, local_y),
                length=self.LOCAL_WIDTH,
                coord=mouse_press
            )
            if on_local:  # check all cells of the board user pressed
                for cell_num, cell_content in enumerate(self.global_board[i]):
                    if cell_content is None:
                        cell_x = (cell_num % self.ROWS) * self.CELL_WIDTH
                        cell_y = (cell_num // self.ROWS) * self.CELL_WIDTH
                        valid = self._in_range(
                            corner=(local_x + cell_x, local_y + cell_y),
                            length=self.CELL_WIDTH,
                            coord=mouse_press
                        )
                        if valid:
                            return i, cell_num  # if valid, return the local board and cell number
        return False

    def _place_move(self, move):
        """
        Enters a move in the game board and updates the game states accordingly

        Args:
            move (Tuple[int, int]): the location on the grid (local_board, cell)
        """
        # place move
        self.global_board[move] = self.player_turn_dict[self.turn]

        # update board winners if applicable
        board_state = self._check_status(self.global_board[move[0]])
        if board_state == "W":
            self.board_winners[move[0]] = self.player_turn_dict[self.turn]
        elif board_state == "S":
            self.board_winners[move[0]] = "S"

        # update playable boards
        if self.board_winners[move[1]] is None:
            self.playable_boards = [move[1]]
        elif self.board_winners[move[1]] in ("R", "B", "S"):
            open_boards = [i for i in range(self.ROWS ** 2) if self.board_winners[i] is None]
            self.playable_boards = open_boards

        # check global win
        global_status = self._check_status(np.array(self.board_winners))
        if global_status == "W":
            self.winner = self.player_turn_dict[self.turn]
        elif global_status == "S":
            self.winner = "S"

    def _play_turn(self, move):
        """
        Given a move plays one turn, for agent or user

        Args:
            move (Tuple[int, int]): the location on the grid (local_board, cell)
        """

        self._place_move(move=move)
        self._render_board()
        self.turn = not self.turn

    def _win_arr(self, arr):
        """
        Checks if arr is a three-in-a-row for either players,
        except for None or "S" for stalemate

        Args:
            arr (array[Union[str, None]]): array to check

        Returns:
            bool: True if arr is has a three in a row
        """
        if arr[0] is None or arr[0] == "S":
            return False
        return np.all(arr == arr[0])

    def _stale_arr(self, arr):
        count = collections.Counter(arr)
        if count["R"] > 0 and count["B"] > 0:
            return True
        return False

    def _check_status(self, board):
        """
        Checks if board is a win, guaranteed stalemate or undecided

        Args:
            board (array[Union[str, None]]): board to check for win

        Returns:
            str:
                'W' for win.
                'S' for guaranteed stalemate.
                'U' for undecided.
        """
        board = board.reshape(3, 3)
        stale_count = 0
        diag1, diag2 = [], []
        for i in range(self.ROWS):
            diag1.append(board[i, i])
            diag2.append(board[self.ROWS - (1 + i), i])
            if self._win_arr(board[i]) or self._win_arr(board[:, i]):
                return "W"
            stale_count += self._stale_arr(board[i])
            stale_count += self._stale_arr(board[:, i])
        diag1 = np.array(diag1)
        diag2 = np.array(diag2)
        if self._win_arr(diag1) or self._win_arr(diag2):
            return "W"
        stale_count += self._stale_arr(diag1)
        stale_count += self._stale_arr(diag2)
        if stale_count == 8:
            return "S"
        return "U"

    def _game_over(self):
        """
        Puts the game in to game over state, where no more moves can be made

        Returns:
            None
        """
        for i in range(self.ROWS - 1):
            pg.draw.line(
                surface=self.win,
                color=self.player_color_dict[self.winner],
                start_pos=(self.WIN_BORDER, self.WIN_BORDER + i * (self.WIDTH - 2 * self.WIN_BORDER)),
                end_pos=(self.WIDTH - self.WIN_BORDER, self.WIN_BORDER + i * (self.WIDTH - 2 * self.WIN_BORDER)),
                width=6
            )
            pg.draw.line(
                surface=self.win,
                color=self.player_color_dict[self.winner],
                start_pos=(self.WIN_BORDER + i * (self.WIDTH - 2 * self.WIN_BORDER), self.WIN_BORDER),
                end_pos=(self.WIN_BORDER + i * (self.WIDTH - 2 * self.WIN_BORDER), self.WIDTH - self.WIN_BORDER),
                width=6
            )
        pg.display.update()

        # wait until user quits game
        pg.event.clear()
        while True:
            event = pg.event.wait()
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

    def main(self):
        """
        Main pygame game loop

        Returns:
            None
        """
        run = True
        self.playable_boards = [randint(0, 8)]  # pick random starting local board
        self._render_board()
        while run:
            self.clock.tick(self.FPS)
            pg.event.clear()

            # user's turn
            while self.turn:
                event = pg.event.wait()
                # if user quits game
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_press = pg.mouse.get_pos()
                    user_input = self._valid_input(mouse_press=mouse_press)
                    if user_input is not False:
                        self._play_turn(move=user_input)
                        if self.winner is not None:
                            self._game_over()

            # agents turn
            if not self.turn:
                move = self.agent.make_move(
                    boards=self.global_board.copy().tolist(),
                    board_winners=self.board_winners[:],
                    playable_boards=self.playable_boards[:]
                )
                self._play_turn(move=move)
                if self.winner is not None:
                    self._game_over()


if __name__ == "__main__":
    uttt = UltimateTicTacToe()
    uttt.main()
