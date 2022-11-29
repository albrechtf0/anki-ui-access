from VisMapGenerator import generate
from examplemap import map
from anki import TrackPieceTypes

lookup = {
    TrackPieceTypes.FINISH : "F",
    TrackPieceTypes.START : "F",
    TrackPieceTypes.CURVE : "C",
    TrackPieceTypes.STRAIGHT : "S",
    TrackPieceTypes.INTERSECTION : "I"
}

vismap, _ = generate(map,(1,0))

for row in zip(*vismap):
    print(
        *[
            str.center("".join([lookup[e.piece.type] for e in cell]),3) 
            for cell in row
        ]
    )