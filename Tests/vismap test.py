from VisMapGenerator import generate, flip_h
from examplemap import map
from anki import TrackPieceTypes

lookup = {
    TrackPieceTypes.FINISH : "F",
    TrackPieceTypes.START : "F",
    TrackPieceTypes.CURVE : "C",
    TrackPieceTypes.STRAIGHT : "S",
    TrackPieceTypes.INTERSECTION : "I"
}

vismap, posMap = generate(map,(1,0))
vismap, posMap = flip_h(vismap,posMap)
for row in zip(*vismap):
    print(
        *[
            str.center("".join([lookup[e.piece.type] for e in cell]),3) 
            for cell in row
        ]
    )

for row in zip(*vismap):
    print(
        *[
            str.center("".join([str(e.orientation) for e in cell]),3) 
            for cell in row
        ]
    )
from UiMain import Ui

Ui([],map,(1,0)).waitForFinish()
