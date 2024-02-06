import os
import math
import warnings
import threading
import asyncio
import pygame 

import anki
from anki import TrackPieceType
from anki.misc.lanes import BaseLane

import Design
from VehicleControlWindow import vehicleControler
from helpers import *

try:
    from .VisMapGenerator import generate, flip_h, Vismap, Element
except ImportError:
    from VisMapGenerator import generate, flip_h, Vismap


class Ui:    
    def __init__(self, vehicles: list[anki.Vehicle], 
                 map,orientation :tuple[int,int],flipMap: bool =False,
                 showUi:bool = True,showControler:bool = False, fps: int = 60,
                 customLanes:list[BaseLane]=[], Design = Design.Design()) -> None:
        #Loading vehicles and Lanes
        self._vehicles = vehicles
        self._customLanes = customLanes + anki.Lane3.getAll() + anki.Lane4.getAll()
        self._laneSystem = BaseLane("CustomLanes",{lane.name:lane.value for lane in self._customLanes})
        #setting up map
        self._map = map
        self._visMap, self._lookup = generate(self._map, orientation)
        if flipMap:
            self._visMap, self._lookup = flip_h(self._visMap,self._lookup)
            #loading aditional information
        self.showUi = showUi
        self.fps = fps
        self._carInfoOffset = 0
        self._Design = Design
        
        #starting pygame
        pygame.init()
        self._font = pygame.font.SysFont("Arial",20)
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
        #getting eventloop and starting ControlWindow
        self._eventLoop = asyncio.get_running_loop()
        self._controlThread = None
        if showControler:
            self.startControler()
        
        self._carIMG = load_image(relative_to_file("Fahrzeug.png"))
    
    #generating vismap
    def genGrid(self,visMap,mapsurf)-> pygame.Surface:
        drawGridLine = lambda start, end: pygame.draw.line(
            mapsurf,
            self._Design.Line,
            start,
            end,
            self._Design.LineWidth
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
        for x, column in enumerate(visMap):
            for y, layers in enumerate(column):
                for i, current in enumerate(layers):
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
        if self._Design.ShowGrid:
            self._visMapSurf = self.genGrid(visMap,mapSurf)
        if self._Design.ShowOutlines:
            pygame.draw.rect(self._visMapSurf,self._Design.Line,(0,0,len(visMap)*100, len(visMap[0])*100),self._Design.LineWidth)
    
    #infos for cars
    def _blitCarInfoOnSurface(self, surf: pygame.Surface, text: str, dest: tuple[int, int]):
        surf.blit(
            self._font.render(text, True, self._Design.Text),
            dest
        )
    def carInfo(self, fahrzeug: anki.Vehicle, number:int) -> pygame.Surface:
        surf = pygame.surface.Surface((500,100))
        surf.fill(self._Design.CarInfoFill)
        try:
            self._blitCarInfoOnSurface(surf, f"Vehicle ID: {fahrzeug.id}",(10,10))
            self._blitCarInfoOnSurface(surf, f"Number: {number}",(400,10))
            self._blitCarInfoOnSurface(surf, f"Position: {fahrzeug.map_position}",(10,30))
            self._blitCarInfoOnSurface(surf, f"Lane: {fahrzeug.get_lane(self._laneSystem)}",(10,50))
            self._blitCarInfoOnSurface(surf, f"Current Trackpiece: {fahrzeug.current_track_piece.type.name}",(10,70))
            self._blitCarInfoOnSurface(surf, f"Offset: {round(fahrzeug.road_offset,2)}",(350,30))
        except Exception as e:
            surf.fill(self._Design.CarInfoFill)
            self._blitCarInfoOnSurface(surf, f"Invalid information:\n{e}", (10,10))
            warnings.warn(e)
        if self._Design.ShowOutlines:
            pygame.draw.rect(surf,self._Design.Line,(0,0,500,100),self._Design.LineWidth)
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
                if (layers != []):
                    for i, current in enumerate(layers):
                        surf.blit(
                            self._font.render(
                                f"{current}",
                                True,
                                self._Design.CarPosText
                            ),
                            (x*100+100-10*(i+1),y*100+80)
                        )
                        #pygame.draw.rect(surf,(0,0,0),(x*100+100-10*(i+1),y*100+90,10,10),1)
        return surf
    def carOnStreet(self) -> pygame.Surface:
        rotationToDirection:dict[int,tuple[int,int]]= {
            0: (1,-1),
            90: (-1,-1),
            180: (-1,1),
            270: (1,1)
        }
        
        surf = pygame.surface.Surface(self._visMapSurf.get_size(),pygame.SRCALPHA)
        for car in self._vehicles:
            x, y, i = self._lookup[car.map_position]
            offset = (car.road_offset / 50)*15
            orientation = self._visMap[x][y][i].orientation
            #print(offset, orientation)
            if car.current_track_piece.type is not TrackPieceType.CURVE:
                surf.blit(
                    rotateSurf(self._carIMG,orientation,-90),
                    (x*100+40+offset*orientation[1],y*100+40+offset*orientation[0]))
            else:
                piece: Element = self._visMap[x][y][i]
                print(piece.rotation)
                carImage = pygame.transform.rotate(
                    self._carIMG,
                    piece.rotation - 135 + (180 if piece.piece.clockwise else 0)
                )
                direction = rotationToDirection[piece.rotation]
                surf.blit(
                    carImage,
                    (
                        x*100 + 50-carImage.get_width()/2 + (offset + 25) * direction[0],
                        y*100+50-carImage.get_height()/2 + (offset + 25) * direction[1]
                    )
                )
                # TODO: Remove this when no longer required (added for testing purposes)
                pygame.draw.circle(surf,(0,0,255),
                                   (x*100+50 + (offset + 25) * rotationToDirection[piece.rotation][0],
                                    y*100+50 + (offset + 25) * rotationToDirection[piece.rotation][1]),1)
        return surf
    
    def gen_Buttons(self):
        # NOTE: Pygame sucks. You can't render fonts with translucent background.
        # You _can_ render fonts with transparent background though, 
        # so this blitting nonsense works while a background colour doesn't.
        BtnText = self._font.render("Controller",True,self._Design.Text)
        Button = pygame.surface.Surface(BtnText.get_size(),pygame.SRCALPHA)
        Button.fill(self._Design.ButtonFill)
        BtnRect = BtnText.get_rect()
        if self._Design.ShowOutlines:
            pygame.draw.rect(
                Button,
                self._Design.Line,
                BtnRect,
                self._Design.LineWidth
            )
        Button.blit(BtnText,(0,0))
        UpArrow = self._font.render("\u25b2",True,self._Design.Text)
        DownArrow = self._font.render("\u25bc", True,self._Design.Text)
        UpRect = UpArrow.get_rect()
        UpRect.topright = (self._visMapSurf.get_width(), 0)
        DownRect = DownArrow.get_rect()
        DownRect.topright = (self._visMapSurf.get_width(), UpArrow.get_height())
        ScrollSurf = pygame.surface.Surface(
            (UpArrow.get_width(),UpArrow.get_height()+DownArrow.get_height()),
            pygame.SRCALPHA
        )
        ScrollSurf.fill(self._Design.ButtonFill)
        ScrollSurf.blit(UpArrow,(0,0))
        ScrollSurf.blit(DownArrow,(0,UpArrow.get_height()))
        self._rects = (BtnRect,UpRect,DownRect)
        return (Button,ScrollSurf)
    
    
    def updateUi(self):
        self.UiSurf.fill(self._Design.Background)
        self.UiSurf.blit(self._visMapSurf,(0,0))
        
        self.UiSurf.blit(self._eventSurf,(0,self._visMapSurf.get_height()))
        if self._Design.ShowOutlines:
            pygame.draw.rect(
                self._eventSurf,
                self._Design.Line,
                self._eventSurf.get_rect(),
                self._Design.LineWidth
            )
        
        carInfoSurfs = self.getCarSurfs()
        carInfoSurfs = carInfoSurfs[self._carInfoOffset:]
        for i, carInfoSurf in enumerate(carInfoSurfs):
            self.UiSurf.blit(carInfoSurf,(self._visMapSurf.get_width(),100*i))
        self.UiSurf.blit(self.carOnMap(),(0,0))
        self.UiSurf.blit(self.carOnStreet(),(0,0))
    
    #The Code that showeth the Ui (:D)
    def _UiThread(self):
        self.gen_MapSurface(self._visMap)
        self._eventSurf = pygame.Surface((
            self._visMapSurf.get_width(),
            self._Design.ConsoleHeight
        ))
        self._eventSurf.fill(self._Design.EventFill)
        self.addEvent("Started Ui",self._Design.Text)
        uiSize = (
            self._visMapSurf.get_width() + self.getCarSurfs()[0].get_width(),
            self._visMapSurf.get_height() + self._Design.ConsoleHeight
        )
        if self.showUi:
            Logo = load_image("Logo.png")
            pygame.display.set_icon(Logo)
            pygame.display.set_caption("Anki Ui Access")
            self._ControlButtonSurf, self._ScrollSurf = self.gen_Buttons()
            Ui = pygame.display.set_mode(uiSize, pygame.SCALED)
        self.UiSurf = pygame.surface.Surface(uiSize)
        
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
            self._Design.EventFill
        )
        #The lines between messages when using outlines apear due to using scroll 
        # this is seen as a feature
        self._eventSurf.scroll(dy=event.get_height())
        pygame.draw.rect(self._eventSurf,self._Design.EventFill,
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
                self._visMapSurf.get_height() + self._Design.ConsoleHeight))
        if(self.showUi):
            self._ControlButtonSurf, self._ScrollSurf = self.gen_Buttons()
        
        old_eventSurf = self._eventSurf
        # TODO: Fix code duplication with _UiThread
        self._eventSurf = pygame.Surface((
            self._visMapSurf.get_width(),
            self._Design.ConsoleHeight
        ))
        self._eventSurf.blit(old_eventSurf, (0, 0))
    def setDesign(self,Design: Design.Design):
        self._Design = Design
        self.updateDesign()
    
    def addVehicle(self, Vehicle:anki.Vehicle):
        self._vehicles.append(Vehicle)
    
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
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, traceback,_) -> None:
        self.kill()
    pass