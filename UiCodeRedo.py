import os
import math

import anki, asyncio, pygame
from anki import TrackPieceTypes
import threading
try:
    from .VisMapGenerator import generate, flip_h, Vismap
except ImportError:
    from VisMapGenerator import generate, flip_h, Vismap

def relative_to_file(relpath: str) -> str:
    return os.path.join(os.path.dirname(
        os.path.abspath(__file__)),
        relpath
    )
    pass

class Ui:    
    def __init__(self, vehicles: list[anki.Vehicle], map,orientation :tuple[int,int],flipMap: bool =False,showUi:bool = True, fps: int = 60) -> None:
        self._vehicles = vehicles
        self._map = map
        self._visMap, self._lookup = generate(self._map, orientation)
        if flipMap:
            self._visMap, self._lookup = flip_h(self._visMap,self._lookup)
        self.showUi = showUi
        self.fps = fps
        self.UiSurf = None
        
        pygame.init()
        self._font = pygame.font.SysFont("Arial",20)
        
        self._eventList: list[pygame.Surface] = []
        self._visMapSurf: pygame.Surface = None
        self._run = True
        self._thread =  threading.Thread(target=self._UiThread,daemon=True)
        self._thread.start()
    
    def kill(self):
        self._run = False
    
    def rotateSurf(self, surf: pygame.surface, orientation: tuple[int,int],addition:int=0):
        return pygame.transform.rotate(surf,math.degrees(math.atan2(orientation[1],orientation[0]))+addition)
    def genGrid(self,visMap,mapsurf):
        for x in range(len(visMap)):
            pygame.draw.line(mapsurf,(0,0,0),(x*100,0),(x*100,len(visMap[x])*100))
        for y in range(len(visMap[x])):
            pygame.draw.line(mapsurf,(0,0,0),(0,y*100),(len(visMap)*100,y*100))
        pygame.draw.rect(mapsurf,(0,0,0),(0,0,len(visMap)*100, len(visMap[0])*100),1)
        return mapsurf
    def gen_MapSurface(self, visMap: Vismap):
        Gerade = pygame.image.load(relative_to_file("Gerade.png"))
        Kurve = pygame.image.load(relative_to_file("Kurve.png"))
        Kreuzung = pygame.image.load(relative_to_file("Kreuzung.png"))
        Start = pygame.image.load(relative_to_file("Start.png"))
        mapSurf = pygame.surface.Surface((len(visMap)*100, len(visMap[0])*100),pygame.SRCALPHA)
        for x in range(len(visMap)):
            for y in range(len(visMap[x])):
                for i in range(len(visMap[x][y])):
                    current = visMap[x][y][i]
                    match current.piece.type:
                        case TrackPieceTypes.STRAIGHT:
                            mapSurf.blit(self.rotateSurf(Gerade,current.orientation,90),(x*100,y*100))
                            # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                        case TrackPieceTypes.CURVE:
                            mapSurf.blit(pygame.transform.rotate(Kurve,current.rotation),(x*100,y*100))
                            #mapSurf.blit(self._font.render(
                            #    f"{current.rotation} {current.orientation} {int(current.flipped) if current.flipped is not None else '/'}",
                            #    True,
                            #    (100,100,100)
                            #),(x*100,y*100))
                        case TrackPieceTypes.INTERSECTION:
                            mapSurf.blit(Kreuzung ,(x*100,y*100))
                        case TrackPieceTypes.START:
                            mapSurf.blit(self.rotateSurf(Start,current.orientation,90),(x*100,y*100))
                            # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                        case TrackPieceTypes.FINISH:
                            pass
        self._visMapSurf = self.genGrid(visMap,mapSurf)
    
    def carInfo(self, fahrzeug: anki.Vehicle, number:int):
        surf = pygame.surface.Surface((500,100))
        surf.fill((200,100,200))
        try:
            surf.blit(self._font.render(f"Vehicle ID: {fahrzeug.id}",True,(0,0,0)),(10,10))
            surf.blit(self._font.render(f"Number: {number}",True,(0,0,0)),(400,10))
            surf.blit(self._font.render(f"Position: {fahrzeug.map_position}",True,(0,0,0)),(10,30))
            surf.blit(self._font.render(f"Lane: {fahrzeug.getLane(anki.Lane4)}",True,(0,0,0)),(10,50))
            surf.blit(self._font.render(f"Current Trackpiece: {fahrzeug.current_track_piece.type.name}",True,(0,0,0)),(10,70))
        except Exception as e:
            surf.blit(self._font.render(f"Invalid information: {e}",True,(0,0,0)),(10,10))
        return surf
    
    def carOnMap(self):
        maping = []
        for x in range(len(self._visMap)):
            maping.append([])
            for y in range(len(self._visMap[x])):
                maping[x].append([])
        surf = pygame.surface.Surface(self._visMapSurf.get_size(),pygame.SRCALPHA)
        for i in range(len(self._vehicles)):
            x, y, _ = self._lookup[self._vehicles[i].map_position]
            maping[x][y].append(i)
        for x in range(len(maping)):
            for y in range(len(maping[x])):
                if (maping[x][y] != []):
                    for i in range(len(maping[x][y])):
                        surf.blit(self._font.render(f"{maping[x][y][i]}",True,(150,0,150)),(x*100+100-10*(i+1),y*100+80))
                        #pygame.draw.rect(surf,(0,0,0),(x*100+100-10*(i+1),y*100+90,10,10),1)
        return surf
    
    #methods for user interaction
    def addEvent(self, text:str, color:tuple[int,int,int]):
        self._eventList.insert(0,self._font.render(text,True,color))
        if(len(self._eventList) > 5):
            self._eventList.pop(len(self._eventList)-1)
    def getUiSurf(self) -> pygame.Surface: 
        return self.UiSurf
    def getCarSurfs(self) -> list[pygame.Surface]:
        return [self.carInfo(self._vehicles[i],i) for i in range(len(self._vehicles)) ]
    def getMapsurf(self) -> pygame.surface:
        return self._visMapSurf
    def getCarsOnMap(self) -> pygame.surface:
        return self.carOnMap()
    def getEventSurf(self) -> pygame.surface:
        EventSurf = pygame.surface.Surface((self._visMapSurf.get_size()[0],200))
        EventSurf.fill((100,150,150))
        for i in range(len(self._eventList)):
            EventSurf.blit(self._eventList[i],(10,i*20))
        pygame.draw.rect(EventSurf,(0,0,0),(0,0,EventSurf.get_size()[0],EventSurf.get_size()[1]),1)
        return EventSurf
    
    #The Code that showes the Ui
    def _UiThread(self):
        self.addEvent("Started Ui",(0,0,0))
        self.gen_MapSurface(self._visMap)
        if self.showUi:
            Ui = pygame.display.set_mode((1000,600),pygame.SCALED)
            Logo = pygame.image.load(relative_to_file("Logo.png"))
            pygame.display.set_icon(Logo)
            pygame.display.set_caption(relative_to_file("Anki Ui Access"))
        self.UiSurf = pygame.surface.Surface((1000,600))
        clock = pygame.time.Clock()
        EventSurf = pygame.surface.Surface((self._visMapSurf.get_size()[0],200))
        while(self._run):
            self.UiSurf.fill((100,150,100))
            self.UiSurf.blit(self._visMapSurf,(0,0))
            
            self.UiSurf.blit(self.getEventSurf(),(0,self._visMapSurf.get_size()[1]))
            
            for i in range(len(self._vehicles)):
                self.UiSurf.blit(self.carInfo(self._vehicles[i],i),(self._visMapSurf.get_size()[0],100*i))
            self.UiSurf.blit(self.carOnMap(),(0,0))
            if self.showUi:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._run = False
                Ui.blit(self.UiSurf,(0,0))
                pygame.display.update()
            clock.tick(self.fps)
    
    def addVehicle(self, Vehicle:anki.Vehicle):
        self._vehicles.append(Vehicle)
    
    def waitForFinish(self, timeout: float|None=None) -> bool:
        self._thread.join(timeout)
        return self._thread.is_alive()
    
    async def waitForFinishAsync(self, timeout: float|None=None) -> bool:
        return await asyncio.get_running_loop().run_in_executor(None,self.waitForFinish,timeout)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, traceback,_) -> None:
        self.kill()
    pass