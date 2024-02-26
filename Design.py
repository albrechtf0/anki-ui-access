from dataclasses import dataclass

@dataclass(slots=True)
class Design:
    Background:tuple[int,int,int] = (100,150,100) 
    Line:tuple[int,int,int] = (0,0,0)
    LineWidth:int = 1 #do not set smaller than 1
    Text:tuple[int,int,int] = (0,0,0)
    CarPosText:tuple[int,int,int] = (150,0,150)
    ButtonFill:tuple[int,int,int,int] = (180,180,180,100)
    EventFill:tuple[int,int,int] = (100,150,150)
    CarInfoFill:tuple[int,int,int] = (200,100,200)
    ConsoleHeight:int = 200
    ShowGrid:bool = True
    ShowOutlines:bool = True
    ShowCarOnStreet: bool = True
    Font: str = "Arial"
    FontSize: int = 20