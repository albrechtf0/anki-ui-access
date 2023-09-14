class Design:
    def __init__(self,
                 Background:tuple[int,int,int] = (100,150,100), 
                 Line:tuple[int,int,int] = (0,0,0), 
                 LineWidt:int = 1, 
                 Text:tuple[int,int,int] = (0,0,0),
                 CarPosText:tuple[int,int,int] = (150,0,150),
                 ButtonFill:tuple[int,int,int,int] = (180,180,180,100),
                 EventFill:tuple[int,int,int] = (100,150,150),
                 CarInfoFill:tuple[int,int,int] = (200,100,200),
                 ConsoleHeight:int = 200,
                 ShowGrid:bool = True,
                 ShowOutlines:bool = True
                 ):
        self._Background: tuple[int,int,int] = Background
        self._Line: tuple[int,int,int] = Line
        self._LineWidth: int = LineWidt 
        self._Text: tuple[int,int,int] = Text
        self._CarPosText: tuple[int,int,int] = CarPosText
        self._ButtonFill: tuple[int,int,int] = ButtonFill
        self._EventFill: tuple[int,int,int] = EventFill
        self._CarInfoFill: tuple[int,int,int] = CarInfoFill
        self._ConsoleHeight: int = ConsoleHeight
        self._ShowGrid: bool = ShowGrid
        self._ShowOutlines:bool = ShowOutlines
    
    @property
    def Background(self) -> tuple[int,int,int]:
        return self._Background
    @property
    def Line(self) -> tuple[int,int,int]:
        return self._Line
    @property
    def LineWidth(self) -> tuple[int,int,int]:
        return self._LineWidth
    @property
    def Text(self) -> tuple[int,int,int]:
        return self._Text
    @property
    def CarPosText(self) -> tuple[int,int,int]:
        return self._CarPosText
    @property
    def ButtonFill(self) -> tuple[int,int,int]:
        return self._ButtonFill
    @property
    def EventFill(self) -> tuple[int,int,int]:
        return self._EventFill
    @property
    def CarInfoFill(self) -> tuple[int,int,int]:
        return self._CarInfoFill
    @property
    def ConsoleHeight(self) -> tuple[int,int,int]:
        return self._ConsoleHeight
    @property
    def ShowGrid(self) -> tuple[int,int,int]:
        return self._ShowGrid
    @property
    def ShowOutlines(self) -> tuple[int,int,int]:
        return self._ShowOutlines
    
    def setBackground(self, Background: tuple[int,int,int]):
        self._Background = Background
    def setLine(self, Line: tuple[int,int,int]):
        self._Line = Line
    def setLineWidth(self, LineWidth: int):
        self._LineWidth = LineWidth
    def setText(self, Text: tuple[int,int,int]):
        self._Text = Text
    def setCarPosText(self, CarPosText: tuple[int,int,int]):
        self._CarPosText = CarPosText
    def setButtonFill(self, ButtonFill: tuple[int,int,int]):
        self._ButtonFill = ButtonFill
    def setEventFill(self, EventFill: tuple[int,int,int]):
        self._EventFill = EventFill
    def setCarInfoFill(self, CarInfoFill: tuple[int,int,int]):
        self._CarInfoFill = CarInfoFill
    def setConsoleHeight(self, ConsoleHeight: int):
        self._ConsoleHeight = ConsoleHeight
    def setShowGrid(self, ShowGrid: bool):
        self._ShowGrid = ShowGrid
    def setShowOutlines(self, ShowOutlines: bool):
        self._ShowOutlines = ShowOutlines