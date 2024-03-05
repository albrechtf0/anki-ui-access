from warnings import warn
from anki import TrackPiece, TrackPieceType
from dataclasses import dataclass
from typing import Literal

__all__ = ("generate",)


Vismap = list[list[list["Element"]]]
PositionTracker = list[tuple[int,int,int]]
Orientation = tuple[Literal[-1,0,1],Literal[-1,0,1]]

@dataclass(repr=False,frozen=True,slots=True)
class Element:
    piece: TrackPiece
    orientation: Orientation
    rotation: int

    def __repr__(self):
        return f"{type(self).__qualname__}({self.piece.type.name},{self.orientation}[{self.rotation}])"
        pass
    def __str__(self):
        return repr(self)
    pass

_ORIENTATIONS: tuple[Orientation,...] = ((1,0),(0,-1),(-1,0),(0,1))
def _next_orientation(orientation: Orientation, is_clockwise: bool) -> Orientation:
    new_index = _ORIENTATIONS.index(orientation) + (1 if not is_clockwise else -1)
    return _ORIENTATIONS[new_index%len(_ORIENTATIONS)]

def _invert_orientation(o: Orientation) -> Orientation:
    # Inverts the orientation. 
    # This just changes the sign of the components
    return (-o[0],-o[1])
    pass

def _expand_right(vismap: Vismap):
    vismap.append(
        [[] for _ in range(len(vismap[0]))]
        # len(vismap[0]) is the column length (i.e. row count)
    )
    pass

def _expand_left(vismap: Vismap, position_tracker: PositionTracker):
    vismap.insert(
        0,
        [[] for _ in range(len(vismap[0]))]
        # len(vismap[0]) is the column length (i.e. row count)
    )

    prev_tracker = position_tracker.copy()
    position_tracker.clear()
    for x,y,z in prev_tracker:
        position_tracker.append((x+1,y,z))
        pass
    pass

def _expand_up(vismap: Vismap, position_tracker: PositionTracker):
    for column in vismap:
        column.insert(0,[])
        pass
    
    prev_tracker = position_tracker.copy()
    position_tracker.clear()
    for x,y,z in prev_tracker:
        position_tracker.append((x,y+1,z))
    pass

def _expand_down(vismap: Vismap):
    for column in vismap:
        column.append([])
        pass
    pass

_CURVE_ROTATIONS_LOOKUP: dict[tuple[Orientation, Orientation],int] = {
    ((1,0),(0,-1)) : 0,
    ((-1,0),(0,-1)) : 90,
    ((-1,0),(0,1)) : 180,
    ((1,0),(0,1)) : 270
}
"""
This is a from-to lookup table. It is NOT directly using the previous
piece orientation. The previous piece orientation has to be inverted.
"""

def orientation_to_rotation(
    type: TrackPieceType,
    orientation: Orientation, 
    previous_orientation: Orientation
) -> int:
    if type == TrackPieceType.CURVE:
        try:
            rotation = _CURVE_ROTATIONS_LOOKUP[
                (orientation,_invert_orientation(previous_orientation))
            ]
        except KeyError:
            # Any version with reversed conditions 
            # has the same rotation
            rotation = _CURVE_ROTATIONS_LOOKUP[
                (_invert_orientation(previous_orientation),orientation)
            ]
        return rotation
        pass
    elif type in (
        TrackPieceType.STRAIGHT,
        TrackPieceType.START,
        TrackPieceType.FINISH
    ):
        return _ORIENTATIONS.index(orientation)*90
    elif type == TrackPieceType.INTERSECTION:
        return 0
    else:
        raise RuntimeError
    pass

def generate(
    track_map: list[TrackPiece],
    orientation: tuple[int,int] = (1,0)
) -> tuple[Vismap,PositionTracker]:
    """Creates a 3d map of the track from the 1d version passed as an argument"""
    if orientation not in _ORIENTATIONS:
        raise ValueError(f"Passed orientation is not valid. Must be one of {_ORIENTATIONS}")

    vismap: Vismap = [[[]]]
    position_tracker = []

    head = [0,0]
    previous_orientation = orientation
    for piece in track_map:
        head[0] += orientation[0]
        head[1] += orientation[1]

        # Adjust vismap when needed
        if head[0] > len(vismap)-1: 
            # If not enough columns to the right
            _expand_right(vismap)
            pass
        elif head[0] < 0: 
            # If not enough columns to the left
            _expand_left(vismap,position_tracker)
            head[0]+=1
            pass
        if head[1] > len(vismap[0])-1:
            # If not enough rows down
            _expand_down(vismap)
            pass
        elif head[1] < 0:
            # If not enough rows up
            _expand_up(vismap,position_tracker)
            head[1]+=1
            # Incrementing head, because the vismap has now shifted
            pass
        
        # Set new orientation
        if piece.type == TrackPieceType.CURVE:
            orientation = _next_orientation(orientation, piece.clockwise)
            pass
        
        # Adding vismap entry if doing so will not cause two intersections to overlay
        # This is done so that the vismap doesn't always have two intersections for every intersection that exists
        working_cell = vismap[head[0]][head[1]]
        position_tracker.append((head[0],head[1],len(working_cell)))
        if not(piece.type == TrackPieceType.INTERSECTION 
        and len(working_cell) > 0
        and all([
            check.piece.type == TrackPieceType.INTERSECTION 
            for check in working_cell
        ])):
            working_cell.append(Element(
                piece,
                orientation,
                orientation_to_rotation(
                    piece.type,
                    orientation,
                    previous_orientation
                )
            ))
            pass
        else:
            warn(
                "Ignoring an intersection piece. If you have stacked two intersection pieces, this will cause bugs. If not, you can ignore this warning.",
                stacklevel=2
            )
            working_cell.append(Element(
                piece,
                orientation,
                orientation_to_rotation(
                    piece.type,
                    orientation,
                    previous_orientation
                )
            ))
        previous_orientation = orientation
        pass

    return vismap, position_tracker
    pass

ROTATION_FLIP_MAP = {
    0: 90,
    90: 0,
    180: 270,
    270: 180
}
def h_rotation_flip(r: int) -> int: 
    return ROTATION_FLIP_MAP[r]

def flip_h(
    vismap: Vismap, 
    position_map: list[tuple[int,int,int]]
) -> tuple[Vismap,PositionTracker]:
    flipped_vismap = [
        [
            [
                Element(
                    e.piece,
                    (-e.orientation[0],e.orientation[1]),
                    h_rotation_flip(e.rotation)
                )
                for e in position
            ]
            for position in column
        ] 
        for column in reversed(vismap)
    ]
    
    column_count = len(vismap)
    flipped_positions = [
        (column_count-1-x,y,z) 
        for x,y,z in position_map
    ]
    
    return flipped_vismap, flipped_positions
    pass