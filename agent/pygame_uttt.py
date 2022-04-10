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
        self.CELL_WIDTH = self.LOCAL_WIDTH // self.ROWS  # width of a one cell
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
        self.player_dict = {True: "R", False: "B"}

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

    def _draw_local_grid(self, x, y):
        """
        draws the grid lines for a local board at position x,y

        @param x: float
            the x co-ordinate of the top left corner where the board must be drawn
        @param y: float
            the y co-ordinate of the top left corner where the board must be drawn

        @return: None
        """
        for i in range(1, self.ROWS):
            pg.draw.line(
                surface=self.win,
                color=self.LIGHT_GRAY,
                start_pos=(x, y + self.CELL_WIDTH * i),
                end_pos=(x + self.CELL_WIDTH * self.ROWS, y + self.CELL_WIDTH * i),
                width=2
            )
            pg.draw.line(
                surface=self.win,
                color=self.LIGHT_GRAY,
                start_pos=(x + self.CELL_WIDTH * i, y),
                end_pos=(x + self.CELL_WIDTH * i, y + self.CELL_WIDTH * self.ROWS),
                width=2
            )

    def _draw_global_grid(self):
        """
        draws the global grid lines

        @return: None
        """
        for i in range(0, self.ROWS):
            pg.draw.line(
                surface=self.win,
                color=self.BLUE,
                start_pos=(self.LOCAL_WIDTH * i, 0),
                end_pos=(self.LOCAL_WIDTH * i, self.WIDTH),
                width=5
            )
            pg.draw.line(
                surface=self.win,
                color=self.BLUE,
                start_pos=(0, self.LOCAL_WIDTH * i,),
                end_pos=(self.WIDTH, self.LOCAL_WIDTH * i),
                width=5
            )

    def _draw_cell(self, local_board, local_cell, player):
        pass

    def _draw_board(self):
        """
        draws the full game board

        @return: None
        """
        # highlight playable boards

        # draw local grid lines
        for i in range(1 + self.ROWS):
            for j in range(1 + self.ROWS):
                self._draw_local_grid(
                    x=i * self.LOCAL_WIDTH,
                    y=j * self.LOCAL_WIDTH,
                )

        # draw global grid lines
        self._draw_global_grid()

        # draw board entries
        for i in range(len(self.global_board)):
            for j in range(len(self.global_board)):
                if self.global_board[i, j] is not None:
                    self._draw_cell(
                        local_board=i,
                        local_cell=j,
                        player=self.global_board[i, j]
                    )

    def _render(self):
        """
        renders the game graphics on pygame screen

        @return: None
        """
        self.win.fill(self.BLACK)
        self._draw_board()
        pg.draw.rect(self.win, (100, 100, 100),
                     pg.Rect((210, 210), (self.CELL_WIDTH, self.CELL_WIDTH)))
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
        self.global_board[move] = self.player_dict[self.turn]

    def main(self):
        """
        main pygame game loop

        @return: None
        """
        run = True
        self.playable_boards = [randint(0, 8)]  # pick random starting local board
        self._render()
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
                                self._render()
                                self.turn = not self.turn

            # agents turn
            if not self.turn:
                move = self.agent.make_move(
                    boards=self.global_board.copy().tolist(),
                    board_winners=self.board_winners[:],
                    playable_boards=self.playable_boards[:]
                )
                self._place_move(move=move)
                self._render()
                self.turn = not self.turn


if __name__ == "__main__":
    uttt = UltimateTicTacToe()
    uttt.main()
