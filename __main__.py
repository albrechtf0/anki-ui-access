import anki
from anki.utility.lanes import _Lane
import asyncio
import random
try:
    from .UiMain import Ui
    from .Design import Design
except ImportError:
    from UiMain import Ui
    import pygame
    from Design import Design


async def main():
    print("Start")
    pygame.init()
    async with anki.Controller() as control:
        autos = await control.connectMany(1)
        #await control.scan()
        autos[0]._position = 0
        with Ui(autos,fakeMap(),(1,0),False) as Uiob:
            Uiob.addEvent("test")
            while True:
                await asyncio.sleep(10)
                des = Design(Background=(45, 167, 184), Line=(169, 77, 95), LineWidth=0, Text=(99, 121, 67), CarPosText=(61, 88, 241), ButtonFill=(40, 237, 105, 236), EventFill=(225, 109, 137), CarInfoFill=(144, 12, 47), ConsoleHeight=303, ShowGrid=False, ShowOutlines=True)
                Uiob.setDesign(des)
                #print(des)

def randColor():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
def randColorA():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
def randDes():
    return Design(randColor(),
                             randColor(),
                             random.randint(0,5),
                             randColor(),
                             randColor(),
                             randColorA(),
                             randColor(),
                             randColor(),
                             random.randint(100,400),
                             random.randint(0,1)==1,
                             random.randint(0,1)==1)
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