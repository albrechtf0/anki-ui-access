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
        with Ui.fromController(control, orientation=(0, -1), flip=(False, True)) as Uiob:
            await Uiob.waitForSetupAsync() # Ensure addEvent is called only after successful setup.
            Uiob.addEvent("test")
            while True:
                await asyncio.sleep(10)
                #des = randDes()
                #Uiob.setDesign(des)
                #print(des)


if __name__ == "__main__":
    asyncio.run(main())