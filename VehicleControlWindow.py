import anki
from anki.misc.lanes import BaseLane
import asyncio
from tkinter import *
from tkinter import ttk as ttk
class vehicleControler:
    
    def startVehicle(self,speed:IntVar,vehicleSelection:list[IntVar]):
        from time import perf_counter
        async def setSpeedTask(i):
            await self.vehicles[i].setSpeed(speed.get())
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                asyncio.run_coroutine_threadsafe(setSpeedTask(i),self.eventLoop)
    def stopVehicle(self,vehicleSelection:list[IntVar]):
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                asyncio.run_coroutine_threadsafe(self.vehicles[i].stop(),self.eventLoop)
    def changeLane(self,vehicleSelection: list[IntVar],lane:StringVar,laneSpeed: IntVar):
        ln = next(filter(lambda x: x.lane_name == lane.get(),self.lanes))
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                asyncio.run_coroutine_threadsafe(self.vehicles[i].change_lane(ln,laneSpeed.get()),
                                                 self.eventLoop)
    def alignVehicle(self, vehicleSelection:list[IntVar]):
        for i in range(len(vehicleSelection)):
            if(vehicleSelection[i].get() == 1):
                asyncio.run_coroutine_threadsafe(self.vehicles[i].align(),self.eventLoop)
    
    def __init__(
        self,
        vehicles:list[anki.Vehicle], 
        eventLoop:asyncio.AbstractEventLoop,
        lanes:list[BaseLane]=[]
    ) -> None:
        self.vehicles = vehicles
        self.eventLoop:asyncio.AbstractEventLoop = eventLoop
        self.lanes = lanes
        root = Tk()
        root.title("Vehicle Control")
        
        frm = ttk.Frame(root, padding=10)
        frm.grid()
        speedValue = IntVar(frm)
        laneSpeed = IntVar(frm)
        #Controls
        btnFrm = ttk.Frame(frm,padding=10,borderwidth=5,relief="groove",)
        btnFrm.grid(column=0,row=0)
        #ttk.Button(btnFrm, text="Exit",command=self.stop).grid(column=0, row=0)
        ttk.Button(btnFrm, text="Set Speed",command=lambda: self.startVehicle(speedValue,vSStates),).grid(column=0, row=0)
        ttk.Button(btnFrm, text="Stop",command=lambda: self.stopVehicle(vSStates)).grid(column=0, row=1)
        ttk.Button(btnFrm, text="Align",command=lambda: self.alignVehicle(vSStates)).grid(column=0, row=2)
        #speed selector
        spFrm = ttk.Frame(frm,padding=10,borderwidth=5,relief="groove")
        spFrm.grid(column=1,row=0,rowspan=2)
        ttk.Label(spFrm,text="Speed:").grid(column=0,row=0)
        Scale(spFrm,from_=1000,to=100,variable=speedValue,orient="vertical",tickinterval=10).grid(column=0,row=1,rowspan=4)
        #Vehicle selection
        vSfrm = ttk.Frame(frm,padding=10,borderwidth=5,relief="groove")
        vSfrm.grid(column=2,row=0,rowspan=3)
        vSStates = []
        ttk.Label(vSfrm,text="Vehicles: ").grid(column=0,row=0)
        for i in range(len(vehicles)):
            vSStates.append(IntVar())
            btn = ttk.Checkbutton(vSfrm,text=f"Vehicle {i}",variable=vSStates[i],state="0").grid(column=0,row=i+1)
        lsLane = StringVar(frm)
        #lane changes
        lcFrm = ttk.Frame(frm,padding=10,borderwidth=5,relief="groove")
        lcFrm.grid(column=0,row=1,)
        ttk.OptionMenu(lcFrm,lsLane,str(self.lanes[0]),*(str(lane) for lane in self.lanes)).grid(column=0,row=0)
        ttk.Button(lcFrm,text="Change Lane",command=lambda:self.changeLane(vSStates,lsLane,laneSpeed)).grid(column=0, row=1 )
        ttk.Label(lcFrm,text="Vehicles do not\nchange lanes when\nslower than 300 speed").grid(column=0,row=2)
        #lane change speed
        lcsFrm = ttk.Frame(frm,padding=10,borderwidth=5,relief="groove")
        lcsFrm.grid(column=0,row=2,columnspan=2)
        ttk.Label(lcsFrm,text="Lane change Speed:").grid(column=0,row=0)
        Scale(lcsFrm,from_=100,to=400,variable= laneSpeed,orient="horizontal").grid(column=1,row=0,columnspan=2)
        
        root.mainloop()