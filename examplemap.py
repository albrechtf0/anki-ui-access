from anki import TrackPiece, TrackPieceTypes
from anki.utility.const import RawTrackPieces

def g(type_: TrackPieceTypes, clockwise: bool = False):
    return TrackPiece(0,type_,clockwise)
    pass

START = TrackPieceTypes.START
FINISH = TrackPieceTypes.FINISH
CURVE = TrackPieceTypes.CURVE
STRAIGHT = TrackPieceTypes.STRAIGHT
INTERSECTION = TrackPieceTypes.INTERSECTION

map = (
    g(START),
    g(CURVE,False),
    g(CURVE,False),
    g(STRAIGHT),
    g(INTERSECTION),
    g(INTERSECTION),
    g(CURVE,True),
    g(CURVE,True),
    g(STRAIGHT),
    g(INTERSECTION),
    g(CURVE,True),
    g(STRAIGHT),
    g(CURVE,True),
    g(STRAIGHT),
    g(CURVE,True),
    g(INTERSECTION),
    g(STRAIGHT),
    g(CURVE,True),
    g(CURVE,True),
    g(INTERSECTION),
    g(INTERSECTION),
    g(CURVE,False),
    g(FINISH)
)