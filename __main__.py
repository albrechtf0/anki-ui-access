import anki
from anki.utility.lanes import _Lane
import asyncio
try:
    from .UiCodeRedo import Ui
except ImportError:
    from UiCodeRedo import Ui

async def main():
    print("Start")
    async with anki.Controller() as control:
        auto1 = await control.connectOne()
        #auto2 = await control.connectOne()
        #auto3 = await control.connectOne()
        #await control.scan()
        
        with Ui([auto1],fakeMap(),(1,0),False,True,True) as Uiob:
            print("Constructor finished")
            #await auto1.setSpeed(200)
            #await auto2.setSpeed(300)
            #await auto3.setSpeed(400)
            # iteration = 0
            while True:
                await asyncio.sleep(10)
                #print(Uiob.getUiSurf())
            #     Uiob.addEvent(f"{iteration}",(0,0,0))
            #     iteration += 1

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
        anki.TrackPiece(0,anki.TrackPieceTypes.CURVE,True),
        anki.TrackPiece(0,anki.TrackPieceTypes.FINISH,False)]
    return map

if __name__ == "__main__":
    asyncio.run(main())