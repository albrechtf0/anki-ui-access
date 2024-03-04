import anki
import asyncio
import random
import pygame
import random
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
        with Ui(list(autos),control.map,(1,0),False,fps=10,
                vehicleColors=[(255,0,0)]) as Uiob:
            Uiob.addEvent("test")
            while True:
                await asyncio.sleep(10)
                #des = randDes()
                #Uiob.setDesign(des)
                #print(des)


if __name__ == "__main__":
    asyncio.run(main())