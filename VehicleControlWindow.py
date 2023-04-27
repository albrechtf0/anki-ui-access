import anki
from anki.utility.lanes import _Lane
import asyncio
from tkinter import *
from tkinter import ttk as ttk
class vehicleControler:
    
    def stop(self):
        exit(0)
    def startVehicle(self,speed:IntVar,vehicleSelection:list[IntVar]):
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                self.eventLoop.create_task(self.vehicles[i].setSpeed(speed.get()))
    def stopVehicle(self,vehicleSelection:list[IntVar]):
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                self.eventLoop.create_task(self.vehicles[i].stop())
    def changeLane(self,vehicleSelection: list[IntVar],lane:StringVar,laneSpeed: IntVar):
        ln = next(filter(lambda x: x.lane_name == lane.get(),self.lanes))
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                task = self.eventLoop.create_task(self.vehicles[i].changeLane(ln,laneSpeed.get()))
    
    def __init__(self,vehicles:list[anki.Vehicle], eventLoop:asyncio.AbstractEventLoop,customLanes:list[_Lane]=[]) -> None:
        self.vehicles = vehicles
        self.eventLoop:asyncio.AbstractEventLoop = eventLoop
        self.lanes = anki.Lane3.getAll()+anki.Lane4.getAll()+customLanes
        root = Tk()
        root.title("Vehicle Control")
        
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        ttk.Entry(frm,)
        speedValue = IntVar(frm)
        laneSpeed = IntVar(frm)
        
        ttk.Button(frm, text="Exit",command=self.stop).grid(column=0, row=0)
        ttk.Button(frm, text="Set Speed",command=lambda: self.startVehicle(speedValue,vSStates),).grid(column=0, row=1)
        ttk.Button(frm, text="Stop",command=lambda: self.stopVehicle(vSStates),).grid(column=0, row=2)
        Scale(frm,from_=1000,to=100,variable=speedValue,orient="vertical",tickinterval=10).grid(column=1,row=1,rowspan=4)
        Scale(frm,from_=100,to=400,variable= laneSpeed,orient="horizontal").grid(column=0,row=5,columnspan=2)
        
        vSfrm = ttk.Frame(frm,padding=10,border=1)
        vSfrm.grid(column=2,row=0,rowspan=len(vehicles))
        vSfrm.grid()
        vSStates = []
        for i in range(len(vehicles)):
            vSStates.append(IntVar())
            btn = ttk.Checkbutton(vSfrm,text=f"Vehicle {i}",variable=vSStates[i],state=0).grid(column=0,row=i)
        lsLane = StringVar(frm)
        ttk.OptionMenu(frm,lsLane,None,*self.lanes).grid(column=0,row=3)
        ttk.Button(frm,text="Change Lane",command=lambda:self.changeLane(vSStates,lsLane,laneSpeed)).grid(column=0, row=4 )
        root.mainloop()