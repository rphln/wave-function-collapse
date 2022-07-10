from random import choices
from typing import List, Optional, Sequence, Set, TypeVar

T = TypeVar("T")


def shuffle_weighted_indices(weights: List[float]) -> Sequence[int]:
    weights = list(weights)
    indices = range(len(weights))
    for _ in indices:
        (index,) = choices(indices, weights)
        yield index
        weights[index] = 0


def shuffle_weighted(elements: List[T], weights: List[float]) -> Sequence[T]:
    for index in shuffle_weighted_indices(weights):
        yield elements[index]


def union(sets: Sequence[Set[T]]) -> Set[T]:
    """
    Returns the union of all sets in a sequence.
    """

    return set().union(*sets)


def pop(stack: List[T]) -> Optional[T]:
    """
    Pops an element from the `stack`, returning it.

    If the stack is empty, returns `None`.
    """

    try:
        return stack.pop()
    except IndexError:
        return None
