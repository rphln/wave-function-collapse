import sys
from copy import deepcopy
from dataclasses import dataclass, field
from random import choices, shuffle
from typing import Callable, Dict, Generic, List, Sequence, Set, Type, TypeVar

from waves.terminal import clear, color, cursor, reset
from waves.util import pop, union

sys.setrecursionlimit(10_000)

T = TypeVar("T")
P = TypeVar("P")

Rules: Type = Dict[T, Set[T]]


@dataclass
class Grid(Generic[T]):
    """
    A flattened wrap-around 2D grid of `T`.
    """

    contents: List[T] = field(init=False)

    width: int
    height: int

    initialize: Callable[[int, int], T]

    def __post_init__(self):
        self.contents = [
            self.initialize(x, y) for x in range(self.width) for y in range(self.height)
        ]

    def neighbors_of(self, at: int) -> Sequence[int]:
        """
        Returns an iterable over the neighbors of the specified tile (node).

        Wraps on edges.
        """

        x, y = self.unmangle(at)

        for dx in range(-1, +2):
            for dy in range(-1, +2):
                if dx == 0 and dy == 0:
                    continue

                if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                    yield self.mangle(x + dx, y + dy)

    def mangle(self, x: int, y: int) -> int:
        """
        Converts a pair of XY coordinates to an offset.
        """

        return (x % self.width) + (y % self.height) * self.width

    def unmangle(self, at: int) -> (int, int):
        """
        Converts an offset to a pair of XY coordinates.
        """

        return (at % self.width), (at // self.width)

    def __getitem__(self, at: int) -> T:
        """
        Returns a reference to the contents of the specified node.
        """

        return self.contents[at]

    def __setitem__(self, at: int, value: T):
        """
        Overwrites the contents of the specified node.
        """

        self.contents[at] = value

    def __iter__(self) -> Sequence[T]:
        """
        Returns an iterator over the contents of the grid.
        """

        yield from self.contents


def collapse(cell: Set[T]):
    """
    Collapse this cell into a definite state.
    """

    return set(choices(list(cell)))


def propagate(grid: Grid, root: P, rules: Rules):
    """
    Propagates the consequences of collapsing the `root` cell.
    """

    stack = [root]

    while (at := pop(stack)) is not None:
        domain = union(rules[candidate] for candidate in grid[at])

        for neighbor in grid.neighbors_of(at):
            # Visit the neighbor iff it has any values outside of the domain.
            # This prevents the visits from cascading through the whole graph.
            if not grid[neighbor] - domain:
                continue

            grid[neighbor] &= domain
            stack.append(neighbor)

            if not grid[neighbor]:
                return False

    return True


def has_contradictions(grid: Grid) -> bool:
    """
    Returns whether the `grid` contains any contradictions (i.e., cells with no
    possible values).
    """

    return any(not cell for cell in grid)


def is_fully_collapsed(grid: Grid) -> bool:
    """
    Returns whether the `grid` is fully collapsed.
    """

    return not any(len(cell) > 1 for cell in grid)


def solve(grid: Grid, rules: Rules, pending: List[T], callback: Callable):
    """
    Solves the “Wave Function Collapse” for a given `grid` and `rules`.

    Returns the collapsed grid if it succeeds, or `None` otherwise.
    """

    # The “Minimum Remaining Values” heriustic.
    pending.sort(key=lambda at: len(grid[at]))

    try:
        # We can't `pop` here, as it'd also mutate the variable in the caller.
        at, *pending = pending
    except ValueError:  # We're done.
        return grid

    candidates = list(grid[at])
    shuffle(candidates)

    for chosen in candidates:
        partial = deepcopy(grid)
        partial[at] = {chosen}

        if not propagate(partial, at, rules):
            continue

        callback(partial)

        if solved := solve(partial, rules, pending, callback):
            return solved

    # Everything in `candidates` led to a contradiction.
    return None


def main():
    PRINT_CELL_WIDTH = 3

    width = 128
    height = 128

    A = color(92)
    B = color(91)
    C = color(93)
    D = color(94)

    empty = color(90)
    error = color(95)

    rules = {
        A: {B, C, D},
        B: {A, C, D},
        C: {A, B, D},
        D: {A, B, C},
    }

    grid = Grid(width, height, initialize=lambda x, y: set(rules.keys()))
    grid_ = deepcopy(grid)

    def draw(grid):
        nonlocal grid_
        for at, (cell, cell_) in enumerate(zip(grid, grid_)):
            if cell == cell_:
                continue

            x, y = grid.unmangle(at)

            match len(cell):
                case 0:
                    continue
                case 1:
                    color = next(iter(cell))
                case _:
                    color = empty

            print(
                cursor(x * PRINT_CELL_WIDTH, y),
                color,
                " " * PRINT_CELL_WIDTH,
                reset(),
                end="",
                sep="",
                flush=True,
            )

        grid_ = deepcopy(grid)

    print(clear())
    if grid := solve(grid, rules, list(range(len(grid.contents))), draw):
        draw(grid)
        print()
        message = "Done!"
    else:
        message = "Error!"

    print(cursor(0, grid_.height + 1), message)


def setup_exit_signal():
    from atexit import register
    from os import system

    register(lambda: system("reset"))


if __name__ == "__main__":
    # setup_exit_signal()
    main()
