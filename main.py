from copy import deepcopy
from curses import newpad, wrapper, color_pair, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, init_pair, COLOR_WHITE, COLOR_BLACK
from typing import TYPE_CHECKING, Tuple, List

Coord = Tuple[int, int]
if TYPE_CHECKING:
    from curses import _CursesWindow

board = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
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
        for c in range(6):
            if self.board[2][c] == 1:
                start, _ = self.get_block((2, c))
                return 6 - start[1]
        else:
            return 0

    def get_block(self, coord: Coord) -> Tuple[Coord, Coord]:
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

    def get_blocks(self) -> List[Tuple[Coord, Coord]]:
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


def main(stdscr: "_CursesWindow"):
    game = Game(stdscr)

    init_pair(COLOR_KEY_PAIR, COLOR_YELLOW, COLOR_BLACK)
    init_pair(COLOR_ROW_PAIR, COLOR_GREEN, COLOR_BLACK)
    init_pair(COLOR_COL_PAIR, COLOR_RED, COLOR_BLACK)
    init_pair(COLOR_EMP_PAIR, COLOR_WHITE, COLOR_BLACK)

    game.render()
    stdscr.getch()


if __name__ == "__main__":
    wrapper(main)
