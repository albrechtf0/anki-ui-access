import itertools
import math
from typing import Iterable
import warnings
import threading
import concurrent.futures
import asyncio
import pygame 

import anki
from anki import TrackPieceType
from anki.misc.lanes import BaseLane

from Design import Design
from VehicleControlWindow import vehicleControler
from helpers import *

try:
    from .VisMapGenerator import generate, flip_h, Vismap, Element
except ImportError:
    from VisMapGenerator import generate, flip_h, Vismap

CAR_INFO_WIDTH = 500

class Ui:    
    def __init__(self,
            vehicles: list[anki.Vehicle], 
            map,
            orientation: tuple[int,int] = (1,0),
            flip: tuple[bool, bool] = (False, False),
            showUi: bool = True,
            showControler: bool = False,
            fps: int = 10,
            customLanes: list[BaseLane] = [], 
            design: Design = Design(),
            vehicleColors: Iterable[tuple[int,int,int]] = []
        ) -> None:
        self._vehicleColorIterator = itertools.chain(
            iter(vehicleColors), 
            itertools.repeat((255,255,255))
        )
        #Loading vehicles and Lanes
        self._vehicles = vehicles
        self._accumulatedVehicleColors = [
            next(self._vehicleColorIterator)
            for _ in range(len(vehicles))
        ]
        self._customLanes = customLanes + anki.Lane3.getAll() + anki.Lane4.getAll()
        self._laneSystem = BaseLane("CustomLanes",{lane.name:lane.value for lane in self._customLanes})
        #setting up map
        flip_horizontal = flip[0]
        if flip[1]:
            # Vertical flipping is 180° rotation with horizontal flipping
            flip_horizontal = not flip_horizontal
            orientation = (-orientation[0], -orientation[1])

        self._map = map
        self._visMap, self._lookup = generate(self._map, orientation)
        
        if flip_horizontal:
            self._visMap, self._lookup = flip_h(self._visMap, self._lookup)

        
        #loading aditional information
        self.showUi = showUi
        self.fps = fps
        self._carInfoOffset = 0
        self._design = design
        
        #starting pygame
        pygame.init()
        self._font = pygame.font.SysFont(design.Font, design.FontSize)
        # integrated event logging
        self._eventSurf: pygame.Surface|None = None
        #Ui surfaces
        self.UiSurf: pygame.Surface|None = None
        self._visMapSurf: pygame.Surface|None = None
        self._ControlButtonSurf: pygame.Surface|None = None
        self._ScrollSurf: pygame.Surface|None = None
        self._rects: tuple[pygame.rect.Rect|None,pygame.rect.Rect|None,pygame.rect.Rect|None] = (
            None, None, None
        )
        #starting ui
        self._thread = threading.Thread(target=self._UiThread,daemon=True)
        self._run = True
        self._thread.start()
        # concurrent.futures doesn not see the potential of manually created futures
        # too bad!
        self._uiSetupComplete = concurrent.futures.Future()
        #getting eventloop and starting ControlWindow
        self._eventLoop = asyncio.get_running_loop()
        self._controlThread = None
        if showControler:
            self.startControler()
        
        self._carIMG = load_image(relative_to_file("Fahrzeug.png"))
    
    @classmethod
    def fromController(cls,
        controller: anki.Controller,
        **kwargs
    ):
        return cls(list(controller.vehicles), controller.map, **kwargs)
    
    #generating vismap
    def genGrid(self,visMap,mapsurf)-> pygame.Surface:
        drawGridLine = lambda start, end: pygame.draw.line(
            mapsurf,
            self._design.Line,
            start,
            end,
            self._design.LineWidth
        )
        for x in range(1,len(visMap)):
            drawGridLine((x*100,0), (x*100,len(visMap[x])*100))
        for y in range(1,len(visMap[0])):
            drawGridLine((0,y*100), (len(visMap)*100,y*100))
        return mapsurf
    def gen_MapSurface(self, visMap: Vismap):
        Gerade = load_image(relpath="Gerade.png")
        Kurve = load_image("Kurve.png")
        Kreuzung = load_image("Kreuzung.png")
        Start = load_image("Start.png")
        mapSurf = pygame.surface.Surface((len(visMap)*100, len(visMap[0])*100),pygame.SRCALPHA)
        for (i, y, x), current in enumerated_flatten(visMap):
            current: Element
            match current.piece.type:
                case TrackPieceType.STRAIGHT:
                    Gerade.set_alpha(int((1.5**-i)*255))
                    mapSurf.blit(
                        rotateSurf(Gerade,current.orientation,90),
                        (x*100,y*100)
                    )
                    # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                case TrackPieceType.CURVE:
                    Kurve.set_alpha(int((1.5**-i)*255))
                    mapSurf.blit(pygame.transform.rotate(Kurve,float(current.rotation)),(x*100,y*100)) # type: ignore
                    #mapSurf.blit(self._font.render(
                    #    f"{current.rotation} {current.orientation} {int(current.flipped) if current.flipped is not None else '/'}",
                    #    True,
                    #    (100,100,100)
                    #),(x*100,y*100))
                case TrackPieceType.INTERSECTION:
                    if current.orientation[0] != 0:
                        Kreuzung.set_alpha(int((1.5**-i)*255))
                        mapSurf.blit(Kreuzung, (x*100,y*100))
                case TrackPieceType.START:
                    Start.set_alpha(int((1.5**-i)*255))
                    mapSurf.blit(rotateSurf(Start,current.orientation,90),(x*100,y*100))
                    # mapSurf.blit(self._font.render(f"{current.orientation}",True,(100,100,100)),(x*100,y*100))
                case TrackPieceType.FINISH:
                    pass
        self._visMapSurf = mapSurf
        if self._design.ShowGrid:
            self._visMapSurf = self.genGrid(visMap,mapSurf)
        if self._design.ShowOutlines:
            pygame.draw.rect(self._visMapSurf,self._design.Line,(0,0,len(visMap)*100, len(visMap[0])*100),self._design.LineWidth)
    
    #infos for cars
    def _blitCarInfoOnSurface(self, surf: pygame.Surface, text: str, dest: tuple[int, int]):
        surf.blit(
            self._font.render(text, True, self._design.Text),
            (10+dest[0]*300,
            10+self._design.FontSize*dest[1])
        )
    def carInfo(self, vehicle: anki.Vehicle, number:int) -> pygame.Surface:
        surf = pygame.surface.Surface((CAR_INFO_WIDTH,20+self._design.FontSize*4))
        surf.fill(self._design.CarInfoFill)
        try:
            self._blitCarInfoOnSurface(surf, f"Vehicle ID: {vehicle.id}",(0,0))
            self._blitCarInfoOnSurface(surf, f"Number: {number}",(1,0))
            self._blitCarInfoOnSurface(surf, f"Position: {vehicle.map_position}",(0,1))
            self._blitCarInfoOnSurface(surf, f"Offset: {round(vehicle.road_offset,2)}",(1,1))
            self._blitCarInfoOnSurface(surf, f"Lane: {vehicle.get_lane(self._laneSystem)}",(0,2))
            self._blitCarInfoOnSurface(surf, f"Speed: {round(vehicle.speed,2)}", (1,2))
            self._blitCarInfoOnSurface(surf, f"Trackpiece: {vehicle.current_track_piece.type.name}",(0,3))
            pygame.draw.circle(surf,self._accumulatedVehicleColors[number],
                               (CAR_INFO_WIDTH-10-self._design.FontSize/2,10+self._design.FontSize*3.5),
                               self._design.FontSize/2)
        except (AttributeError, TypeError) as e:
            surf.fill(self._design.CarInfoFill)
            self._blitCarInfoOnSurface(surf, f"Invalid information:", (0,0))
            self._blitCarInfoOnSurface(surf, f"{e}", (0,1))
            warnings.warn(e)
        if self._design.ShowOutlines:
            pygame.draw.rect(surf,self._design.Line,surf.get_rect(),self._design.LineWidth)
        return surf
    def carOnMap(self) ->pygame.Surface:
        maping = []
        for x in range(len(self._visMap)):
            maping.append([])
            for y in range(len(self._visMap[x])):
                maping[x].append([])
        
        surf = pygame.surface.Surface(self._visMapSurf.get_size(),pygame.SRCALPHA)
        for i in range(len(self._vehicles)):
            x, y, _ = self._lookup[self._vehicles[i].map_position] # type: ignore
            maping[x][y].append(i)
        
        for x, column in enumerate(maping):
            for y, layers in enumerate(column):
                width = 0
                for i, current in enumerate(layers):
                    text = self._font.render(
                        f"{current}",
                        True,
                        self._design.CarPosText
                    )
                    width += text.get_width()
                    surf.blit(
                        text,
                        (x*100+100-width,y*100+100-text.get_height())
                    )
                    #pygame.draw.rect(surf,(0,0,0),(x*100+100-10*(i+1),y*100+90,10,10),1)
        return surf
    def carOnStreet(self) -> pygame.Surface:
        rotationToDirection:dict[int,tuple[int,int]]= {
            0: (1,0),
            90: (0,0),
            180: (0,1),
            270: (1,1)
        }
        
        surf = pygame.surface.Surface(self._visMapSurf.get_size(),pygame.SRCALPHA)
        for carNum, car in enumerate(self._vehicles):
            x, y, i = self._lookup[car.map_position]
            laneOffset = (car.road_offset / 60)*(20-5)
            piece: Element = self._visMap[x][y][i]
            orientation = piece.orientation

            carImage = self._carIMG.copy()
            carImage.fill(self._accumulatedVehicleColors[carNum],None,pygame.BLEND_RGB_MULT)
            if car.current_track_piece.type is not TrackPieceType.CURVE:
                surf.blit(
                    rotateSurf(carImage,orientation,-90),
                    (x*100+40+laneOffset*-orientation[1],
                     y*100+40+laneOffset*orientation[0]))
            else:
                laneOffset *= -1 if piece.piece.clockwise else 1
                laneOffset += 50
                direction = rotationToDirection[piece.rotation]
                rotation = math.radians(piece.rotation)
                curveOffset = (-math.cos(math.pi/4+rotation),math.sin(math.pi/4+rotation))
                carImage = pygame.transform.rotate(
                    carImage,
                    piece.rotation - 135 + (180 if piece.piece.clockwise else 0)
                )
                surf.blit(
                    carImage,
                    (
                        x*100 -carImage.get_width()/2  + 100* direction[0] + curveOffset[0]*laneOffset,
                        y*100 -carImage.get_height()/2 + 100* direction[1] + curveOffset[1]*laneOffset
                    )
                )
                # TODO: Remove this when no longer required (added for testing purposes)
                # pygame.draw.circle(surf,(255,255,255),
                #                 (x*100+50,
                #                  y*100+50),1)
                # pygame.draw.circle(surf,(0,255,255),
                #                 (x*100 + 100* direction[0],
                #                  y*100 + 100* direction[1]),50,1)
                # pygame.draw.circle(surf,(255,0,0),
                #                 (x*100 + 100* direction[0] + curveOffset[0]*50,
                #                  y*100 + 100* direction[1] + curveOffset[1]*50),1)
                # pygame.draw.circle(surf,(255,0,255),
                #                 (x*100 + 100* direction[0] + curveOffset[0]*laneOffset,
                #                  y*100 + 100* direction[1] + curveOffset[1]*laneOffset),2)
        return surf

    def gen_Buttons(self):
        # NOTE: Pygame sucks. You can't render fonts with translucent background.
        # You _can_ render fonts with transparent background though, 
        # so this blitting nonsense works while a background colour doesn't.
        BtnText = self._font.render("Controller",True,self._design.Text)
        Button = pygame.surface.Surface(BtnText.get_size(),pygame.SRCALPHA)
        Button.fill(self._design.ButtonFill)
        BtnRect = BtnText.get_rect()
        if self._design.ShowOutlines:
            pygame.draw.rect(
                Button,
                self._design.Line,
                BtnRect,
                self._design.LineWidth
            )
        Button.blit(BtnText,(0,0))
        
        UpArrow = self._font.render("\u25b2",True,self._design.Text)
        DownArrow = self._font.render("\u25bc", True,self._design.Text)
        
        UpRect = UpArrow.get_rect()
        UpRect.topright = (self._visMapSurf.get_width(), 0)
        
        DownRect = DownArrow.get_rect()
        DownRect.topright = (self._visMapSurf.get_width(), UpArrow.get_height())
        
        ScrollSurf = pygame.surface.Surface(
            (UpArrow.get_width(),UpArrow.get_height()+DownArrow.get_height()),
            pygame.SRCALPHA
        )
        ScrollSurf.fill(self._design.ButtonFill)
        ScrollSurf.blit(UpArrow,(0,0))
        ScrollSurf.blit(DownArrow,(0,UpArrow.get_height()))
        
        self._rects = (BtnRect,UpRect,DownRect)
        return (Button,ScrollSurf)
    
    
    def updateUi(self):
        self.UiSurf.fill(self._design.Background)
        self.UiSurf.blit(self._visMapSurf,(0,0))
        
        self.UiSurf.blit(self._eventSurf,(0,self._visMapSurf.get_height()))
        if self._design.ShowOutlines:
            pygame.draw.rect(
                self._eventSurf,
                self._design.Line,
                self._eventSurf.get_rect(),
                self._design.LineWidth
            )
        
        carInfoSurfs = self.getCarSurfs()
        carInfoSurfs = carInfoSurfs[self._carInfoOffset:]
        for i, carInfoSurf in enumerate(carInfoSurfs):
            self.UiSurf.blit(carInfoSurf,(self._visMapSurf.get_width(),carInfoSurf.get_height()*i))
        
        if(self._design.ShowCarNumOnMap):
            self.UiSurf.blit(self.carOnMap(),(0,0))
        if(self._design.ShowCarOnStreet):
            self.UiSurf.blit(self.carOnStreet(),(0,0))
    
    #The Code that showeth the Ui (:D)
    def _UiThread(self):
        self.gen_MapSurface(self._visMap)
        self._eventSurf = pygame.Surface((
            self._visMapSurf.get_width(),
            self._design.ConsoleHeight
        ))
        self._eventSurf.fill(self._design.EventFill)
        self.addEvent("Started Ui",self._design.Text)
        uiSize = (
            self._visMapSurf.get_width() + CAR_INFO_WIDTH,
            self._visMapSurf.get_height() + self._design.ConsoleHeight
        )
        if self.showUi:
            Logo = load_image("Logo.png")
            pygame.display.set_icon(Logo)
            pygame.display.set_caption("Anki Ui Access")
            self._ControlButtonSurf, self._ScrollSurf = self.gen_Buttons()
            Ui = pygame.display.set_mode(uiSize, pygame.SCALED)
        self.UiSurf = pygame.surface.Surface(uiSize)
        
        self._uiSetupComplete.set_result(True)
        clock = pygame.time.Clock()
        while(self._run and self.showUi):
            self.updateUi()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self._rects[0].collidepoint(pygame.mouse.get_pos()):
                        self.startControler()
                    if self._rects[1].collidepoint(pygame.mouse.get_pos()):
                        self._carInfoOffset = min(max(self._carInfoOffset+1,0),len(self._vehicles)-1)
                    if self._rects[2].collidepoint(pygame.mouse.get_pos()):
                        self._carInfoOffset = min(max(self._carInfoOffset-1,0),len(self._vehicles)-1)
                if event.type == pygame.MOUSEWHEEL:
                    self._carInfoOffset = min(
                        max(self._carInfoOffset + event.y, 0),
                        len(self._vehicles)-1
                    )
            
            if(Ui.get_size() != self.UiSurf.get_size()):# type: ignore
                Ui = pygame.display.set_mode(self.UiSurf.get_size(),pygame.SCALED)
            Ui.blit(self.UiSurf,(0,0))# type: ignore
            Ui.blit(self._ControlButtonSurf,(0,0))# type: ignore
            Ui.blit(self._ScrollSurf,(self._visMapSurf.get_width()-self._ScrollSurf.get_width(),0))# type: ignore
            
            pygame.display.update()
            clock.tick(self.fps)
    
    
    
    #methods for user interaction
    def kill(self):
        self._run = False
    def addEvent(self, text:str, color:tuple[int,int,int]|None=None):
        if self._eventSurf is None:
            warnings.warn("Ui.addEvent called before Ui was initialized", RuntimeWarning)
            return
        event = self._font.render(
            text,
            True,
            color if color != None else (0,0,0),
            self._design.EventFill
        )
        #The lines between messages when using outlines apear due to using scroll 
        # this is seen as a feature
        self._eventSurf.scroll(dy=event.get_height())
        pygame.draw.rect(self._eventSurf,self._design.EventFill,
                         (0,0,self._eventSurf.get_width(),event.get_height()))
        self._eventSurf.blit(event, (10, 0))
    def getUiSurf(self) -> pygame.Surface: 
        self.updateUi()
        return self.UiSurf
    def getCarSurfs(self) -> list[pygame.Surface]:
        return [self.carInfo(self._vehicles[i],i) for i in range(len(self._vehicles)) ]
    def getMapsurf(self) -> pygame.Surface:
        return self._visMapSurf
    def getCarsOnMap(self) -> pygame.Surface:
        return self.carOnMap()
    def getEventSurf(self) -> pygame.Surface:
        return self._eventSurf
    def updateDesign(self):
        self.gen_MapSurface(self._visMap)
        self.UiSurf = pygame.surface.Surface(
            (self._visMapSurf.get_width() + self.getCarSurfs()[0].get_width(),
                self._visMapSurf.get_height() + self._design.ConsoleHeight))
        if(self.showUi):
            self._ControlButtonSurf, self._ScrollSurf = self.gen_Buttons()
        
        old_eventSurf = self._eventSurf
        # TODO: Fix code duplication with _UiThread
        self._eventSurf = pygame.Surface((
            self._visMapSurf.get_width(),
            self._design.ConsoleHeight
        ))
        self._eventSurf.blit(old_eventSurf, (0, 0))
    def setDesign(self, design: Design):
        self._design = design
        self.updateDesign()
    
    def addVehicle(
            self,
            Vehicle:anki.Vehicle,
            VehicleColor: tuple[int,int,int]|None=None
        ):
        self._vehicles.append(Vehicle)
        if VehicleColor is None:
            self._accumulatedVehicleColors.append(next(self._vehicleColorIterator))
        else:
            self._accumulatedVehicleColors.append(VehicleColor)
    
    def removeVehicle(self,index: int):
        self._vehicles.pop(index)
        self._accumulatedVehicleColors.pop(index)
    
    def startControler(self): #modify starting condition
        if self._controlThread is None or not self._controlThread.is_alive():
            self._controlThread = threading.Thread(
                target=vehicleControler,
                args=(self._vehicles,self._eventLoop,self._customLanes),
                daemon=True
            )
            self._controlThread.start()
    
    def waitForFinish(self, timeout: float|None=None) -> bool:
        self._thread.join(timeout)
        return self._thread.is_alive()
    
    async def waitForFinishAsync(self, timeout: float|None=None) -> bool:
        return await asyncio.get_running_loop().run_in_executor(None,self.waitForFinish,timeout)
    
    def waitForSetup(self, timeout: float|None=None) -> bool:
        return self._uiSetupComplete.result(timeout)
    
    async def waitForSetupAsync(self) -> bool:
        return await asyncio.wrap_future(self._uiSetupComplete)
    
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, traceback,_) -> None:
        self.kill()
    pass