import sys
import pygame as pg
import numpy as np
from random import randint
from agent.main import Agent

pg.init()
pg.event.set_allowed([pg.QUIT, pg.MOUSEBUTTONDOWN])


class UltimateTicTacToe:

    def __init__(self):
        """
        instantiation method
        """

        # Screen
        self.WIDTH = 640
        self.ROWS = 3
        self.GAP = 25
        self.LOCAL_WIDTH = (self.WIDTH - self.GAP * 4) // self.ROWS  # width of a local board
        self.LOCAL_DISTANCE = self.GAP + self.LOCAL_WIDTH  # distance between two consecutive local boards
        self.CELL_WIDTH = self.LOCAL_WIDTH // self.ROWS  # width of one cell
        # by default there are (3x3) cells on local board
        # and (9x9) cells on global board

        self.FPS = 20  # limit game to 20 FPS
        self.clock = pg.time.Clock()
        self.win = pg.display.set_mode((self.WIDTH, self.WIDTH))  # pygame window
        pg.display.set_caption("Ultimate TicTacToe")

        # Colors
        self.BLACK = (32, 32, 32)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 75, 153)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)

        # Game Board
        self.global_board = np.array(
            [
                np.full(shape=self.ROWS ** 2, fill_value=None)
                for _ in range(self.ROWS ** 2)
            ]
        )
        self.board_winners = [None for _ in range(self.ROWS ** 2)]  # Winners of each local board
        self.playable_boards = []  # Boards on which current turn can be played
        self.turn = True  # True if user's turn, false if agent's turn

        # Agent
        self.agent = Agent()
        # DOXA uses R and B to identify players. This script uses boolean values,
        # these dictionaries are helpful to translate between the two
        self.player_turn_dict = {True: "R", False: "B"}
        self.player_color_dict = {"R": self.RED, "B": self.GREEN}

    def __str__(self):
        """
        Implements the string representation of the UltimateTicTacToe game object

        @return: str
            string representation of the game board in current state
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
        draws the grid lines for a local board at position x,y

        @param x: float
            the x co-ordinate of the top left corner where the board must be drawn
        @param y: float
            the y co-ordinate of the top left corner where the board must be drawn

        @return: None
        """
        for i in range(self.ROWS + 1):
            pg.draw.line(
                surface=self.win,
                color=self.LIGHT_GRAY,
                start_pos=(x + self.CELL_WIDTH * i, y),
                end_pos=(x + self.CELL_WIDTH * i, y + self.LOCAL_WIDTH),
                width=3
            )
            pg.draw.line(
                surface=self.win,
                color=self.LIGHT_GRAY,
                start_pos=(y, x + self.CELL_WIDTH * i),
                end_pos=(y + self.LOCAL_WIDTH, x + self.CELL_WIDTH * i),
                width=3
            )

        local = self.global_board[local_board]
        for i in range(self.ROWS ** 2):
            if local[i] is not None:
                cell_x = x + (local_board % self.ROWS) * self.CELL_WIDTH
                cell_y = y + (local_board // self.ROWS) * self.CELL_WIDTH
                pg.draw.rect(
                    surface=self.win,
                    color=self.player_color_dict[local[i]],
                    rect=pg.Rect((cell_x + 2, cell_y), (self.CELL_WIDTH - 3, self.CELL_WIDTH))
                )

    def _render_board(self):
        """
        draws and renders the full game board

        @return: None
        """

        self.win.fill(self.BLACK)

        # TODO: Highlight playable boards
        # TODO: Color each local board according to game state (green, red, yellow, or white)
        # TODO: Implement board entries

        # draw local board
        for i in range(self.ROWS):
            for j in range(self.ROWS):
                self._draw_local(
                    x=self.GAP + j * self.LOCAL_DISTANCE,
                    y=self.GAP + i * self.LOCAL_DISTANCE,
                    local_board=self.ROWS * i + j
                )

        pg.display.update()

    def _cell_range(self, cell_corner, coord):
        """
        checks if the (x,y) coordinates of the coord parameter are within
        the range of the cell with top left corner at cell_corner

        @param cell_corner: tuple(float, float)
            top left corner of cell
        @param coord: tuple(float, float)
            coordinates to check

        @return: bool
            True if coord in cell, False otherwise
        """
        if cell_corner[0] <= coord[0] <= cell_corner[0] + self.CELL_WIDTH:
            if cell_corner[1] <= coord[1] <= cell_corner[1] + self.CELL_WIDTH:
                return True
        return False

    def _valid_input(self, mouse_press):
        """
        validates if the location of the player's mouse press is on a valid cell

        @param mouse_press: tuple(float,float)
            (x,y) coordinates of user's mouse press

        @return: bool
            True if input is valid, False otherwise
        """
        for i in self.playable_boards:
            local_x_pos = (i % self.ROWS) * self.LOCAL_WIDTH
            local_y_pos = (i // self.ROWS) * self.LOCAL_WIDTH
            for cell_num, cell_content in enumerate(self.global_board[i]):
                if cell_content is None:
                    cell_x_pos = (cell_num % self.ROWS) * self.CELL_WIDTH
                    cell_y_pos = (cell_num // self.ROWS) * self.CELL_WIDTH
                    valid = self._cell_range(
                        (local_x_pos + cell_x_pos, local_y_pos + cell_y_pos),
                        mouse_press
                    )
                    if valid:
                        print("Valid")
                        return True
        print("Invalid")
        return False

    def _place_move(self, move):
        """
        enters a move in the game board

        @param move: tuple(int,int)
            move location on the grid

        @return: None
        """
        self.global_board[move] = self.player_turn_dict[self.turn]

    def main(self):
        """
        main pygame game loop

        @return: None
        """
        run = True
        self.playable_boards = [randint(0, 8)]  # pick random starting local board
        self._render_board()
        while run:
            self.clock.tick(self.FPS)

            # user's turn
            if self.turn:
                # loop until user enters input
                while self.turn:
                    for event in pg.event.get():
                        # if user quits game
                        if event.type == pg.QUIT:
                            pg.quit()
                            sys.exit()
                        if event.type == pg.MOUSEBUTTONDOWN:
                            mouse_press = pg.mouse.get_pos()
                            if self._valid_input(mouse_press=mouse_press):
                                self._render_board()
                                self.turn = not self.turn

            # agents turn
            if not self.turn:
                move = self.agent.make_move(
                    boards=self.global_board.copy().tolist(),
                    board_winners=self.board_winners[:],
                    playable_boards=self.playable_boards[:]
                )
                self._place_move(move=move)
                self._render_board()
                self.turn = not self.turn


if __name__ == "__main__":
    uttt = UltimateTicTacToe()
    uttt.global_board[1, 0] = "B"
    uttt.global_board[1, 1] = "R"
    uttt.global_board[1, 2] = "B"
    print(uttt)
    uttt.main()
