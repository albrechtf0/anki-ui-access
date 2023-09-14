import anki
from anki.utility.lanes import _Lane
import asyncio
try:
    from .UiMain import Ui
except ImportError:
    from UiMain import Ui
    import pygame


async def main():
    print("Start")
    pygame.init()
    async with anki.Controller() as control:
        autos = await control.connectMany(1)
        await control.scan()
        
        with Ui(autos,control.map,(1,0),False,True) as Uiob:
            while True:
                await asyncio.sleep(5)

def fakeMap():
    map = [
        anki.TrackPiece(0,anki.TrackPieceTypes.START,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.STRAIGHT,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.STRAIGHT,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.STRAIGHT,False),
        anki.TrackPiece(0,anki.TrackPieceTypes.FINISH,False)]
    return map

if __name__ == "__main__":
    asyncio.run(main())