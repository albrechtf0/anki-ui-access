import os
import math
import Design

import anki, asyncio, pygame
from anki import TrackPieceTypes
import threading
from VehicleControlWindow import vehicleControler
from anki.utility.lanes import _Lane

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
    def __init__(self, vehicles: list[anki.Vehicle], 
                 map,orientation :tuple[int,int],flipMap: bool =False,
                 showUi:bool = True,showControler:bool = False, fps: int = 60,
                 customLanes:list[_Lane]=[]) -> None:
        #Loading vehicles and Lanes
        self._vehicles = vehicles
        self._customLanes = customLanes
        #setting up map
        self._map = map
        self._visMap, self._lookup = generate(self._map, orientation)
        if flipMap:
            self._visMap, self._lookup = flip_h(self._visMap,self._lookup)
            #loading aditional information
        self.showUi = showUi
        self.fps = fps
        self._carInfoOffset = 0
        
        #starting pygame
        pygame.init()
        self._font = pygame.font.SysFont("Arial",20)
        #generating event list
        self._eventList: list[pygame.Surface] = []
        #Ui surfaces
        self.UiSurf: pygame.Surface = None
        self._visMapSurf: pygame.Surface = None
        #starting ui
        self._thread =  threading.Thread(target=self._UiThread,daemon=True)
        self._run = True
        self._thread.start()
        #getting eventloop and starting ControlWindow
        self._eventLoop = asyncio.get_running_loop()
        self._controlThread = None
        if showControler:
            self.startControler()
    #generating vismap
    def rotateSurf(self, surf: pygame.surface, orientation: tuple[int,int],addition:int=0) -> pygame.Surface:
        return pygame.transform.rotate(surf,math.degrees(math.atan2(orientation[1],orientation[0]))+addition)
    def genGrid(self,visMap,mapsurf)-> pygame.Surface:
        for x in range(len(visMap)):
            pygame.draw.line(mapsurf,Design.Lines,(x*100,0),(x*100,len(visMap[x])*100))
        for y in range(len(visMap[x])):
            pygame.draw.line(mapsurf,Design.Lines,(0,y*100),(len(visMap)*100,y*100))
        pygame.draw.rect(mapsurf,Design.Lines,(0,0,len(visMap)*100, len(visMap[0])*100),1)
        return mapsurf
    def gen_MapSurface(self, visMap: Vismap) -> pygame.Surface:
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
                            Gerade.set_alpha((1.5**-i)*255)
                            mapSurf.blit( self.rotateSurf(Gerade,current.orientation,90),(x*100,y*100))
                            # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                        case TrackPieceTypes.CURVE:
                            Kurve.set_alpha((1.5**-i)*255)
                            mapSurf.blit(pygame.transform.rotate(Kurve,current.rotation),(x*100,y*100))
                            #mapSurf.blit(self._font.render(
                            #    f"{current.rotation} {current.orientation} {int(current.flipped) if current.flipped is not None else '/'}",
                            #    True,
                            #    (100,100,100)
                            #),(x*100,y*100))
                        case TrackPieceTypes.INTERSECTION:
                            Kreuzung.set_alpha((1.5**-i)*255)
                            mapSurf.blit(Kreuzung, (x*100,y*100))
                        case TrackPieceTypes.START:
                            Start.set_alpha((1.5**-i)*255)
                            mapSurf.blit(self.rotateSurf(Start,current.orientation,90),(x*100,y*100))
                            # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                        case TrackPieceTypes.FINISH:
                            pass
        self._visMapSurf = mapSurf
        if Design.ShowGrid:
            self._visMapSurf = self.genGrid(visMap,mapSurf)
    #infos for cars 
    def carInfo(self, fahrzeug: anki.Vehicle, number:int) -> pygame.Surface:
        surf = pygame.surface.Surface((500,100))
        surf.fill(Design.CarInfoFill)
        try:
            surf.blit(self._font.render(f"Vehicle ID: {fahrzeug.id}",True,Design.Text),(10,10))
            surf.blit(self._font.render(f"Number: {number}",True,Design.Text),(400,10))
            surf.blit(self._font.render(f"Position: {fahrzeug.map_position}",True,Design.Text),(10,30))
            surf.blit(self._font.render(f"Lane: {fahrzeug.getLane(anki.Lane4)}",True,Design.Text),(10,50))
            surf.blit(self._font.render(f"Current Trackpiece: {fahrzeug.current_track_piece.type.name}",True,Design.Text),(10,70))
        except Exception as e:
            surf.blit(self._font.render(f"Invalid information:\n{e}",True,Design.Text),(10,10))
        pygame.draw.rect(surf,Design.Lines,(0,0,500,100),1)
        return surf
    def carOnMap(self) ->pygame.Surface:
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
                        surf.blit(self._font.render(f"{maping[x][y][i]}",True,Design.CarPosText),(x*100+100-10*(i+1),y*100+80))
                        #pygame.draw.rect(surf,(0,0,0),(x*100+100-10*(i+1),y*100+90,10,10),1)
        return surf
    
    #methods for user interaction
    def kill(self):
        self._run = False
    def addEvent(self, text:str, color:tuple[int,int,int] = Design.Text):
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
        EventSurf.fill(Design.EventFill)
        for i in range(len(self._eventList)):
            EventSurf.blit(self._eventList[i],(10,i*20))
        pygame.draw.rect(EventSurf,Design.Lines,(0,0,EventSurf.get_size()[0],EventSurf.get_size()[1]),1)
        return EventSurf
    
    #The Code that showes the Ui
    def _UiThread(self):
        self.addEvent("Started Ui",Design.Text)
        self.gen_MapSurface(self._visMap)
        if self.showUi:
            Logo = pygame.image.load(relative_to_file("Logo.png"))
            pygame.display.set_icon(Logo)
            pygame.display.set_caption(relative_to_file("Anki Ui Access"))
            BtnText = self._font.render("Controler",True,Design.Text)
            Button = pygame.surface.Surface(BtnText.get_size(),pygame.SRCALPHA)
            Button.fill(Design.ButtonFill)
            BtnRect = pygame.rect.Rect((0,0,*BtnText.get_size()))
            pygame.draw.rect(Button,Design.Lines,BtnRect,1)
            Button.blit(BtnText,(0,0)) 
            UpArrow = self._font.render("▲",True,Design.Text)
            DownArrow = self._font.render("▼", True,Design.Text)
            UpRect = pygame.rect.Rect(
                (self._visMapSurf.get_width()-UpArrow.get_width(),0,*UpArrow.get_size()))
            DownRect = pygame.rect.Rect(
                    self._visMapSurf.get_width()-DownArrow.get_width(),
                    UpArrow.get_height(),
                    *DownArrow.get_size()
                )
            ScrollSurf = pygame.surface.Surface(
                (UpArrow.get_width(),UpArrow.get_height()+DownArrow.get_height()))
            ScrollSurf.fill(Design.ButtonFill)
            ScrollSurf.blit(UpArrow,(0,0))
            ScrollSurf.blit(DownArrow,(0,UpArrow.get_height()))
            Ui = pygame.display.set_mode(
                (self._visMapSurf.get_width() + self.getCarSurfs()[0].get_width(),
                    self._visMapSurf.get_height() + Design.ConsoleHeight),pygame.SCALED)
        self.UiSurf = pygame.surface.Surface(
            (self._visMapSurf.get_width() + self.getCarSurfs()[0].get_width(),
                self._visMapSurf.get_height() + Design.ConsoleHeight))
        clock = pygame.time.Clock()
        
        while(self._run):
            self.UiSurf.fill(Design.Background)
            self.UiSurf.blit(self._visMapSurf,(0,0))
            
            self.UiSurf.blit(self.getEventSurf(),(0,self._visMapSurf.get_size()[1]))
            
            carInfoSurfs = self.getCarSurfs()
            carInfoSurfs = carInfoSurfs[self._carInfoOffset:]
            for i, carInfoSurf in enumerate(carInfoSurfs):
                self.UiSurf.blit(carInfoSurf,(self._visMapSurf.get_size()[0],100*i))
            self.UiSurf.blit(self.carOnMap(),(0,0))
            if self.showUi:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._run = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if BtnRect.collidepoint(pygame.mouse.get_pos()):
                            self.startControler()
                        if UpRect.collidepoint(pygame.mouse.get_pos()):
                            self._carInfoOffset = min(max(self._carInfoOffset+1,0),len(self._vehicles)-1)
                        if DownRect.collidepoint(pygame.mouse.get_pos()):
                            self._carInfoOffset = min(max(self._carInfoOffset-1,0),len(self._vehicles)-1)
                    if event.type == pygame.MOUSEWHEEL:
                        self._carInfoOffset = min(max(self._carInfoOffset+ event.y,0),len(self._vehicles)-1)
                Ui.blit(self.UiSurf,(0,0))
                Ui.blit(Button,(0,0))
                Ui.blit(ScrollSurf,(self._visMapSurf.get_width()-ScrollSurf.get_width(),0))
                
                pygame.display.update()
            clock.tick(self.fps)
    
    def addVehicle(self, Vehicle:anki.Vehicle):
        self._vehicles.append(Vehicle)
    
    def startControler(self): #modify starting condition
        if self._controlThread == None or self._controlThread.is_alive() == False: 
            self._controlThread = threading.Thread(target=vehicleControler,args=[self._vehicles,self._eventLoop,self._customLanes] ,daemon=True)
            self._controlThread.start()
    
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