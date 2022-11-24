import os, sys
sys.path.append(os.getcwd())

import anki, asyncio, pygame
from anki import TrackPieceTypes
import threading

os.chdir(os.path.dirname(os.path.abspath(__file__)))

control = anki.Controller()
map = []


STOP = False #Setting this to TRUE will make your programm stop existing!!!

async def ankiMain(): 
    global auto1, auto2
    global map
    global autos

    auto1 = await control.connectOne(vehicle_id =1)
    auto2 = await control.connectOne(vehicle_id =2)
    autos = [auto1, auto2]
    await control.scan()
    map = control.map
    gen_vismap()
    #print(vismap,map,sep="\n")
    await auto1.setSpeed(200)

CarDict = {
    1 : "auto1",
    2 : "auto2"
}

def expand_map_to_size(map, width, height):
    current_width = len(map[0])
    current_height = len(map)

    for i in range(width - current_width):
        map.append([])
        pass

    for i in range(height - current_height):
        for column in map: column.append(None)
        pass
    pass

global vismap
vismap = [[]]
def gen_vismap():
    def insert_at(x_position, y_position, piece, orientation) -> tuple[int,int]:
        vis_width = len(vismap)
        vis_height = len(vismap[0])

        if x_position >= vis_width:
            vismap.append([None]*vis_height)
        elif x_position < 0:
            vismap.insert(0,[None]*vis_height)
            x_position += 1

        elif y_position >= vis_height:
            for column in vismap: column.append(None)
        elif y_position < 0:
            for column in vismap: column.insert(0,None)
            y_position += 1

        if vismap[x_position][y_position] is None:
            vismap[x_position][y_position] = (piece, orientation)
        else:
            vismap[x_position][y_position] = ((piece, vismap[x_position][y_position][0]),
            (orientation, vismap[x_position][y_position][1]))
        
        return x_position, y_position
        pass

    h_orientation = 1
    v_orientation = 0
    ORIENTATION_LOOKUP = (
        (0, 1),
        (1, 0),
        (0,-1),
        (-1,0)
    )

    x_position = 0
    y_position = 0
    

    for i, piece in enumerate(map):
        current_oindex = ORIENTATION_LOOKUP.index((h_orientation,v_orientation))
        x_position, y_position = insert_at(x_position, y_position, piece, current_oindex)

        if piece.type == TrackPieceTypes.CURVE:
            inc = 1 if piece.clockwise else -1
            current_oindex = (current_oindex + inc) % 4
            h_orientation, v_orientation = ORIENTATION_LOOKUP[current_oindex]
            pass

        x_position += h_orientation
        y_position += v_orientation
        pass




logSurface = logHistory = ...

def Uimain():
    global logSurface, logHistory, font
    global STOP
    pygame.init()
    Ui = pygame.display.set_mode((1000,600),pygame.SCALED)
    Logo = pygame.image.load("Logo.png")
    pygame.display.set_caption("Anki Ui Access")
    pygame.display.set_icon(Logo)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial",20)
    run = True
    Gerade = pygame.image.load("Gerade.png")
    Kurve = pygame.image.load("Kurve.png")
    Kreuzung = pygame.image.load("Kreuzung.png")
    Start = pygame.image.load("Start.png")
    Bruecke = pygame.image.load("Bruecke.png")
    font = pygame.font.SysFont("Arial",20)
    mapxSize = len(vismap)*100
    mapYSize = len(vismap[0])*100
    mapsurface = pygame.Surface((mapxSize, mapYSize)) 
    mapsurface.fill((98, 60, 73))
    carPosSurface = pygame.Surface((mapxSize, mapYSize), pygame.SRCALPHA)
    carPosMap = [None]*(mapxSize//100) #nen array mit nem array und nem array
    for i in range(len(carPosMap)):
        carPosMap[i] = [None]*(mapYSize//100)
        for o in range(len(carPosMap[i])):
            carPosMap[i][o] = []
    logSurface = pygame.Surface((100,150))
    logHistory = [None]*5
    for i in range(len(logHistory)):
        logHistory[i] = font.render("", True, (0,0,0))

    for x in range(len(vismap)):
        for y in range(len(vismap[x])):
            if vismap[x][y] is not None  :
                if not isinstance(vismap[x][y][1], tuple):
                    if vismap[x][y][0].type is TrackPieceTypes.CURVE:
                        mapsurface.blit(pygame.transform.rotate(Kurve, vismap[x][y][1]*90),(x*100, y*100))
                    elif vismap[x][y][0].type is TrackPieceTypes.STRAIGHT:
                        mapsurface.blit(pygame.transform.rotate(Gerade, vismap[x][y][1]*90),(x*100, y*100))
                    elif vismap[x][y][0].type is TrackPieceTypes.FINISH:
                        mapsurface.blit(pygame.transform.rotate(Start, vismap[x][y][1]*90),(x*100, y*100))
                else: 
                    if vismap[x][y][0][0].type is TrackPieceTypes.INTERSECTION:
                        mapsurface.blit(pygame.transform.rotate(Kreuzung, vismap[x][y][1][0]*90),(x*100, y*100))
                    elif vismap[x][y][0][0].type is TrackPieceTypes.FINISH:
                        mapsurface.blit(pygame.transform.rotate(Start, vismap[x][y][1][0]*90),(x*100, y*100))
                    else:
                        mapsurface.blit(pygame.transform.rotate(Bruecke, vismap[x][y][1][0]*90),(x*100, y*100))
    autoData = []
    for i in range(len(autos)):
        autoData.append(pygame.Surface((100,100)))
    
    
    while run and not STOP:
        Ui.fill((81, 255, 174))
        Ui.blit(pygame.transform.flip(mapsurface, True, False),(0,0))
        for x in range(len(autos)):
            work_surface = autoData[x]
            work_surface.fill((135, 237, 208))
            auto_name = font.render(f"Name: {CarDict[autos[x].id]}", True, (0,0,0))
            auto_id = font.render(f"ID: {autos[x].id}", True, (0,0,0))
            auto_pos = font.render(f"Position: {autos[x].map_position}", True, (0,0,0))
            
            auto_piece = font.render(f"Streckenteil Typ:{anki.TrackPieceTypes.as_str(autos[x].current_track_piece.type)}", True, (0,0,0))
            
            auto_lane = font.render(f"Spur: {autos[x].current_lane4}", True, (0,0,0))
            surf_height = 40 + sum([surf.get_height() for surf in (auto_name, auto_pos, auto_piece, auto_lane)])
            #surf_width = max([surf.get_width() for surf in (auto_name, auto_pos, auto_piece)])
            if surf_height != work_surface.get_height():
                autoData[x] = work_surface = pygame.Surface((400,surf_height))
            
            work_surface.blits((
                (auto_name,(0,0)),
                (auto_id, (auto_name.get_width() + 20, 0)),
                (auto_pos,(0,auto_name.get_height())),
                (auto_piece,(0, auto_name.get_height() + auto_pos.get_height())),
                (auto_lane,(0, auto_name.get_height() + auto_pos.get_height() + auto_piece.get_height()))
            ))
            pygame.draw.line(work_surface, (98, 60, 73), (0, work_surface.get_height()),(work_surface.get_width(), work_surface.get_height()), 20)
            Ui.blit(work_surface, (mapxSize, x*work_surface.get_height()))
            
        carPosSurface.fill((255,255,255, 0))
        for x in range(len(vismap)):
            for y in range(len(vismap[x])):
                if vismap[x][y] is not None:
                    if not isinstance(vismap[x][y][1], tuple):
                        for a in autos:
                            if a.current_track_piece is vismap[x][y][0]:
                                carPosMap[x][y].append(a.id)
                    else:
                        for z in range(len(vismap[x][y][0])):
                            for a in autos:
                                if a.current_track_piece is vismap[x][y][0][z]:
                                    carPosMap[x][y].append(a.id)
        for x in range(len(carPosMap)):
            for y in range(len(carPosMap[x])):
                for vehicle_num in range(len(carPosMap[x][y])):
                    carPosSurface.blit(
                        pygame.transform.flip(
                            font.render(
                                str(carPosMap[x][y][vehicle_num]), 
                            True, 
                            (245,255,84)
                            )
                            ,True, False),
                            (x*100+80-vehicle_num*20, y*100+70)
                        )
                carPosMap[x][y].clear()
        Ui.blit(pygame.transform.flip(carPosSurface,True, False),(0,0))
        Ui.blit(logSurface,(0,mapsurface.get_height()))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()
        clock.tick(10)
    STOP = True #Stopping programm 

def enterLog(logEntry, color = (0,0,0)):
    global logSurface, logHistory
    width = 0
    for i in reversed(range(len(logHistory)-1)):
        logHistory[i+1] = logHistory[i]
        if width < logHistory[i].get_width():
            width = logHistory[i].get_width()
    logHistory[0] = font.render(str(logEntry), True, color)
    if width < logHistory[0].get_width():
        width = logHistory[0].get_width()

    logSurface = pygame.Surface((width, 150))
    logSurface.fill((117,164,120))
    for i in range(len(logHistory)):
        logSurface.blit(logHistory[i], (0, i*30))
        # print(i, logHistory[i])




async def ankiside():
    await auto2.setSpeed(300)

async def setup():
    global STOP
    await asyncio.create_task(ankiMain())
    asyncio.create_task(ankiside())
    # await asyncio.sleep(40)
    frontend = threading.Thread(target = Uimain)
    frontend.start()
    await asyncio.sleep(1)
    enterLog("Setup System!", (0,255,255))
    for v in autos:
        enterLog(f"Vehicle {CarDict[v.id]} ready!")

    try:
        while not STOP:
            await asyncio.sleep(1)
            pass
    except KeyboardInterrupt: pass
    finally:
        await asyncio.gather(*[v.stop() for v in autos])
        await control.disconnectAll()
    pass


asyncio.run(setup())

