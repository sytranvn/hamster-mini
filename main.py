import logging
from copy import deepcopy
from curses import (COLOR_BLACK, COLOR_GREEN, COLOR_RED, COLOR_WHITE,
                    COLOR_YELLOW, color_pair, init_pair, wrapper)
from typing import TYPE_CHECKING, Generator, List, Tuple

logging.basicConfig(filename="hamster.log", level=logging.INFO)

Coord = Tuple[int, int]
Block = Tuple[Coord, Coord]


if TYPE_CHECKING:
    from curses import _CursesWindow

board = [
    [0, 2, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 3, 3, 3, 0, 0],
    [0, 0, 0, 0, 0, 0],
]

COLOR_KEY_PAIR = 1
COLOR_ROW_PAIR = 2
COLOR_COL_PAIR = 3
COLOR_EMP_PAIR = 4


class Game:
    def __init__(self, stdscr: "_CursesWindow") -> None:
        self.stdscr = stdscr
        self.board = deepcopy(board)

    def is_over(self):
        return all(c for r in self.board for c in r if c != 1)

    def render(self):
        self.stdscr.clear()
        for start, end in self.get_blocks():
            sr, sc = start
            er, ec = end
            block = self.stdscr.subwin(
                (er-sr+1) * 3, (ec-sc+1) * 5, sr*3, sc*5)
            block.border()
            if self.board[sr][sc] == 1:
                block.bkgd(' ', color_pair(COLOR_KEY_PAIR))
            elif self.board[sr][sc] % 2:
                block.bkgd(' ', color_pair(COLOR_ROW_PAIR))
            elif self.board[sr][sc] != 0:
                block.bkgd(' ', color_pair(COLOR_COL_PAIR))
            else:
                block.bkgd(' ', color_pair(COLOR_EMP_PAIR))
        self.stdscr.refresh()

    def heuristic(self):
        key = self.get_key()
        return 6 - 1 - key[1][1]

    def get_block(self, coord: Coord) -> Block:
        r, c = coord
        if self.board[r][c] == 0:
            return (r, c), (r, c)
        if self.board[r][c] % 2:
            sc, ec = c, c

            while sc > 0:
                if self.board[r][c] == self.board[r][sc - 1]:
                    sc -= 1
                else:
                    break
            while ec < 6 - 1:
                if self.board[r][c] == self.board[r][ec + 1]:
                    ec += 1
                else:
                    break
            return (r, sc), (r, ec)

        sr, er = r, r

        while sr > 0:
            if self.board[r][c] == self.board[sr - 1][c]:
                sr -= 1
            else:
                break
        while er < 6 - 1:
            if self.board[r][c] == self.board[er + 1][c]:
                er += 1
            else:
                break
        return (sr, c), (er, c)

    def get_blocks(self) -> List[Block]:
        visited = [[False] * 6 for _ in range(6)]
        result = []
        for r in range(6):
            for c in range(6):
                if not visited[r][c]:
                    start, end = self.get_block((r, c))
                    for br in range(start[0], end[0] + 1):
                        for bc in range(start[1], end[1] + 1):
                            visited[br][bc] = True
                    result.append((start, end))
        return result

    def is_mt(self, coord: Coord):
        return self.board[coord[0]][coord[1]] == 0

    def successors(self) -> Generator[Tuple[Block, Coord], None, None]:
        """
        return: block and where to move it to
        """
        for r in range(6):
            for c in range(6):
                if self.board[r][c] == 0:
                    continue
                if self.board[r][c] % 2:
                    block = self.get_block((r, c))
                    start, end = block
                    for bc in reversed(range(0, start[1])):
                        if self.board[r][bc] == 0:
                            yield block, (0, bc - c)
                    for bc in range(end[1]+1, 6):
                        if self.board[r][bc] == 0:
                            yield block, (0, bc - c)
                else:
                    block = self.get_block((r, c))
                    start, end = block
                    for br in reversed(range(0, start[0])):
                        if self.board[br][c] == 0:
                            yield block, (br-r, 0)
                    for br in range(end[0]+1, 6):
                        if self.board[r][br] == 0:
                            yield block, (br - r, 0)

    def move(self, block: Block, move: Coord):
        """ assuming move is valid """
        start, end = block
        mr, mc = move
        cell = self.board[start[0]][start[1]]
        if mr != 0:
            if mr > 0:
                for i in range(mr):
                    self.board[start[0] + i][start[1]] = 0
                    self.board[end[0] + i + 1][end[1]] = cell
            else:
                for i in range(-mr):
                    self.board[start[0] - i - 1][start[1]] = cell
                    self.board[end[0] - i][end[1]] = 0
        else:
            if mc > 0:
                for i in range(mc):
                    self.board[start[0]][start[1] + i] = 0
                    self.board[end[0]][end[1] + i + 1] = cell
            else:
                for i in range(-mr):
                    self.board[start[0]][start[1] - i - 1] = cell
                    self.board[end[0]][end[1] - i] = 0

    def get_key(self) -> Block:
        for i in range(6):
            if self.board[2][i] == 1:
                return self.get_block((2, i))
        return ((2, 0), (2, 1))  # never reach


def main(stdscr: "_CursesWindow"):
    game = Game(stdscr)

    init_pair(COLOR_KEY_PAIR, COLOR_YELLOW, COLOR_BLACK)
    init_pair(COLOR_ROW_PAIR, COLOR_GREEN, COLOR_BLACK)
    init_pair(COLOR_COL_PAIR, COLOR_RED, COLOR_BLACK)
    init_pair(COLOR_EMP_PAIR, COLOR_WHITE, COLOR_BLACK)

    game.render()
    while game.heuristic():
        stdscr.getch()
        key = game.get_key()
        game.move(key, (0, 1))
        game.render()

    stdscr.getch()


if __name__ == "__main__":
    wrapper(main)
