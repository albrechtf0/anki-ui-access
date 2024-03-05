import os
import pygame
import math
from typing import Iterable, Sequence, TypeVar, Generator, Any

T = TypeVar('T')
NestedIterable = Iterable["T|NestedIterable[T]"]
NestedSequence = Sequence["T|NestedSequence[T]"]

def relative_to_file(relpath: str) -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        relpath
    )

def load_image(relpath: str):
    return pygame.image.load(relative_to_file(relpath))

def rotateSurf(surf: pygame.Surface, orientation: tuple[int,int],addition:int=0) -> pygame.Surface:
    return pygame.transform.rotate(
        surf,
        math.degrees(math.atan2(-orientation[1],orientation[0]))+addition
    )

def flatten(iterable: NestedIterable|T) -> Iterable[T]:
    """
    Flattens a nested iterable with depth n 
    and potentially non-uniform shape into a
    depth-first iterable of each element.

    e. g. `( (1, 2), (3, 4) )`
    is flattened to `(1, 2, 3, 4)`
    (as an iterator)
    """
    if isinstance(iterable, Iterable):
        for v in iterable:
            yield from flatten(v)
    else:
        yield iterable

def enumerated_flatten(iterable: NestedIterable|T) -> Iterable[tuple[list[int], Any]]:
    """
    Similar to flatten, except each entry also sends its location in the iterable.

    A location value is a list of integer indexes assembled depth-first.
    This value can be used to identify the position in the nested iterable.
    The size of this list varies with the depth of the specific value.
    """
    if isinstance(iterable, Iterable):
        for i, internal in enumerate(iterable):
            for pos, v in enumerated_flatten(internal):
                pos.append(i)
                yield pos.copy(), v
    else:
        yield [], iterable

def nested_index(sequence: NestedSequence|T, pos: list[int]) -> T|NestedSequence:
    """
    Looks up the element in a nested sequence by its location.
    
    The location list is defined the same as in nested_enumerate.
    """
    if len(pos) == 0:
        return sequence
    if not isinstance(sequence, Sequence):
        raise IndexError("Maximum depth exceeded")
    return nested_index(sequence[pos[-1]], pos[:-1])