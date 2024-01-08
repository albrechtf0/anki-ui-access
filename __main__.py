import anki
import asyncio
import random
import pygame
try:
    from .UiMain import Ui
    from .Design import Design
except ImportError:
    from UiMain import Ui
    from Design import Design


async def main():
    print("Start")
    pygame.init()
    async with anki.Controller() as control:
        autos = await control.connect_many(1)
        #autos[0]._position = 0
        await control.scan() # type: ignore
        with Ui(list(autos),control.map,(1,0),False) as Uiob:
            Uiob.addEvent("test")
            while True:
                await asyncio.sleep(10)
                #des = randDes()
                #Uiob.setDesign(des)
                #print(des)

def randColor():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255))
def randColorA():
    return (random.randint(0,255),random.randint(0,255),random.randint(0,255),random.randint(0,255))
def randDes():
    return Design(randColor(),
                             randColor(),
                             random.randint(1,5),
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
        anki.TrackPiece(0,anki.TrackPieceType.START,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.STRAIGHT,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceType.STRAIGHT,True),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.CURVE,False),
        anki.TrackPiece(0,anki.TrackPieceType.STRAIGHT,False),
        anki.TrackPiece(0,anki.TrackPieceType.FINISH,False)]
    return map

if __name__ == "__main__":
    asyncio.run(main())