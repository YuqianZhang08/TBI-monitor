#from logging import root
import numpy as np
import pandas as pd
from ringbuffer import RingBuffer
import random
#import matplotlib as mp
#import math
from smooth import smooth
#import csv  # logging the data
#from datetime import datetime  # logging the data
import matplotlib.pyplot as plt  # plotting the data
#from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
#import matplotlib.animation as animation
#from matplotlib.ticker import MultipleLocator
import os  # handling file paths
#import seabreeze  # talking to the spectroscopy
from seabreeze.spectrometers import list_devices, Spectrometer
import sys  # handling file paths
import tkinter as tk  # GUI
from tkinter import Tk, ttk
import time  # sleeping
from menubar import myMenuBar
from calibrationFrame import calibrationFrame
from AllFrame import All_Frame
import serial
import time
from airPLS import airPLS
from multitask.predict import predictdata
from MVR import MVRpredict
READ_from_DEVICE=False


pin405 = 33  # BOARD pin 
pin450 = 35  # BBOARD pin
pin540 = 31  # BOARD pin


class biomarker:  
    def __init__(self):
        self.peak=[]
        self.corrected_signal=[]
        self.concentration=0.0
        self.model=[]
        self.cal_temp=25.0
        self.device = "cpu"
        #self.spec = Spectrometer.from_first_available()
        #self.spec.integration_time_micros(100000)
        #self.wavelengths, self.intensities = self.spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        #data=np.vstack((self.wavelengths,self.intensities))
        #self.signal=np.transpose(data)
    
    def set_signal(self, signal):
        self.signal = signal
    
    def set_temperature(self, Cal_temp):
        self.cal_temp = Cal_temp

    def set_peakWavelength(self, wavelength):
        self.wavelength = wavelength

    def get_peakWavelength(self):
        return(self.wavelength)

    def baseline_correction(self):
        self.corrected_signal=airPLS(self.smoothed)

    def normalization (self):
        self.normalized=self.signal-min(self.corrected_signal)/(max(self.corrected_signal)-min(self.corrected_signal))

    def get_smoothed_signal(self):
        output=self.signal[:,0]
        output=np.vstack((output,smooth(self.signal,11)))
        self.smoothed=np.transpose(output)
        
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Brain monitoring")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        #menubar = myMenuBar(self)
        self.config(menu=myMenuBar(self).menubar)
        #self.config(menu=menubar)
        self.frames = {}
        self.frame = MainWindow(container, self)
        self.frames[MainWindow] = self.frame
        self.frame.grid(row=0, column=0, sticky="nsew")
        
       # self.show_frame(MainWindow)
      
        #self.frames = {}
       # for F in (MainWindow, All_Frame):
         #   page_name = F.__name__
          #  frame = F(container, self)
         #   self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
           # frame.grid(row=0, column=0, sticky="nsew")
        
         
        #self.show_frame("MainWindow")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.build_window()
        frame.tkraise()
    

class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller=controller
        #root.title("monitoring")
       # parent.title("Brain monitoring")

        #self.winfo_toplevel().configure(menu=myMenuBar(self).menubar)
        self.device = tk.StringVar()  
        self.integTime = tk.DoubleVar()
        self.smoothinx=tk.DoubleVar()
        self.sampleinx=tk.DoubleVar()
        self.bioselect = tk.StringVar()  
        self.plotstyle = tk.StringVar()

        # set initial
        self.paused = False
        self.device.set('0')
        self.integTime.set(100000.0)
        self.smoothinx.set(1)
        self.sampleinx.set(10)
    
        self.bioqueue=RingBuffer(100)
        #self.savepath.set(os.getcwd())
        self.bioselect.set('pH')
        self.con=False
        self.specCon=False
        self.plotstyle.set('seaborn-colorblind')
        self.specfig= plt.Figure(figsize=(4.5, 2.5), dpi=100)
        self.specsub=self.specfig.add_subplot(111)
        self.biofig= plt.Figure(figsize=(7.5, 4), dpi=100)
        #plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        self.subbio=self.biofig.add_subplot(111)
        #self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        if not READ_from_DEVICE:
            self.file="spectrums.csv"
            df=pd.read_csv(self.file)
            data=np.array(df)
            self.spectrum=data[:,5]
        else:
            self.ser = serial.Serial('COM4', 115200)
            devices=list_devices()
            self.spec = Spectrometer(devices[0])
            self.spec.integration_time_micros(self.integTime.get())  # 0.1 seconds
            self.getSpectra()
        self.build_window()
        

    def build_window(self):
        """Make all the tkinter widgets"""
        #self.menu = MenuBar(self.parent)
        # build the main frame
        self.tstfrm = tk.Frame(self.parent)
        self.entfrm = tk.LabelFrame(self.tstfrm, text="Default Settings")
        # this spacing is to avoid using multiple labels
        self.outfrm = tk.LabelFrame(self.tstfrm,
            text="Current spectrum")
        self.cmdfrm = tk.LabelFrame(self.tstfrm, text="Plot Controls")

        # define the self.entfrm entries
        self.p1 = ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.device,
            justify=tk.CENTER
            )
        self.p2 = ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.integTime,
            justify=tk.CENTER
            )
        self.smoothdegree= ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.smoothinx,
            justify=tk.CENTER
            )
        self.sampleFreq= ttk.Entry(
            master=self.entfrm,
            width=14,
            textvariable=self.sampleinx,
            justify=tk.CENTER
            )
        self.strtbtn = ttk.Button(
            master=self.entfrm,
            text="Start",
            command=lambda: self.spec_run()
            )
        self.stopbtn = ttk.Button(
            master=self.entfrm,
            text="Stop",
            command=lambda: self.spec_stop()
            )
        self.calibrationbtn = ttk.Button(
            master=self.entfrm,
            text="Calibration",
            command=lambda:self.calibration_test()
            )

        # grid entry labels into self.entfrm
        ttk.Label(
            master=self.entfrm,
            text="Device:"
            ).grid(row=0, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Integration time (s):"
            ).grid(row=1, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Smooth correction:"
            ).grid(row=2, sticky=tk.E)
        ttk.Label(
            master=self.entfrm,
            text="Sample frequency:"
            ).grid(row=3, sticky=tk.E)

        # grid entries into self.entfrm
        self.p1.grid(row=0, column=1, sticky=tk.E, padx=1)
        self.p2.grid(row=1, column=1, sticky=tk.E, pady=1)
        self.smoothdegree.grid(row=2, column=1, sticky=tk.E, pady=1)
        self.sampleFreq.grid(row=3, column=1, sticky=tk.E, pady=1)
        self.strtbtn.grid(row=5, column=2, columnspan=1, pady=1)
        self.stopbtn.grid(row=5, column=3, columnspan=1, pady=1)
        self.calibrationbtn.grid(row=5, column=1, sticky=tk.W, pady=1)
        cols = self.entfrm.grid_size()
        for col in range(cols[0]):
            self.entfrm.grid_columnconfigure(col, weight=1)

        # build self.outfrm PACK
        self.plotspec=self.specsub.plot([],[])[0]
        
        # TODO: explicitly clarify some of these args
        self.canvasspec = FigureCanvasTkAgg(self.specfig, master=self.outfrm)
        toolbar = NavigationToolbar2Tk(self.canvasspec, self.outfrm)
        toolbar.update()
        self.canvasspec.get_tk_widget().pack()
        #self.canvasspec.draw()
        self.after(25,self.plot_fig)
        # build self.cmdfrm 4x3 GRID
        self.runbtn = ttk.Button(
            master=self.cmdfrm,
            text="Run",
            command=lambda: self.run_test(),
            width=15
            )
        self.endbtn = ttk.Button(
            master=self.cmdfrm,
            text="End",
            command=lambda: self.end_test(),
            width=15
            )
        self.runbtn.grid(row=0, column=2, padx=5, pady=2, sticky=tk.E)
        self.endbtn.grid(row=0, column=3, padx=5, pady=2, sticky=tk.E)
        tk.Label(
            master=self.cmdfrm,
            text="Select data to plot:"
            ).grid(row=0, column=0, padx=5)
        
        tk.Radiobutton(
            master=self.cmdfrm,
            text="pH",
            variable=self.bioselect,
            value='pH'
            ).grid(row=1, column=0, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="Dissolved Oxygen",
            variable=self.bioselect,
            value='DO'
            ).grid(row=1, column=1, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="Temperature",
            variable=self.bioselect,
            value='Temp'
            ).grid(row=1, column=2, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="Sodium ion",
            variable=self.bioselect,
            value='Na'
            ).grid(row=2, column=0, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="Calcium ion",
            variable=self.bioselect,
            value='Ca'
            ).grid(row=2, column=1, padx=5)
        tk.Radiobutton(
            master=self.cmdfrm,
            text="Glucose",
            variable=self.bioselect,
            value='Glu'
            ).grid(row=2, column=2, padx=5)
        

        # disable the controls to prevent starting test w/o parameters
        if self.paused:
            for child in self.cmdfrm.winfo_children():
                child.configure(state="disabled")

        # set up the plot area
        self.pltfrm = tk.LabelFrame(
            master=self.tstfrm,
            text=("Style: " + self.plotstyle.get())
            )
        
        self.plottime=self.subbio.plot([],[])[0]
        # TODO: explicitly clarify some of these args
        self.canvasbio = FigureCanvasTkAgg(self.biofig, master=self.pltfrm)
        toolbar = NavigationToolbar2Tk(self.canvasbio, self.pltfrm)
        toolbar.update()
        self.canvasbio.get_tk_widget().pack()
        #self.canvasbio.show()
        with plt.style.context(self.plotstyle.get()):
            self.pltfrm.config(text=("Biomarker concentration"))
            self.outfrm.config(text=("Spectrum"))
            self.subbio.set_ylabel("Concentration") 
            self.subbio.set_xlabel("Time")
            self.subbio.set_xlim(0,100)
            self.subbio.set_ylim(0,10)
            self.subbio.xaxis.set_visible(False)
            self.specsub.set_ylabel("Intensity") 
            self.specsub.set_xlabel("wavelength (nm)")
            self.specsub.set_ylim(1400,3000)
            self.specsub.set_xlim(400,800)
        
        # grid stuff into self.tstfrm
        self.entfrm.grid(row=0, column=0, sticky=tk.NSEW, pady=2)
        self.pltfrm.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=2)
        self.outfrm.grid(row=1, column=0, sticky=tk.NSEW, pady=1) 
        self.cmdfrm.grid(row=2, column=0, sticky=tk.NSEW, pady=2)
        self.tstfrm.grid(padx=3)

    def getSpectra(self):
        
        wavelengths, intensities = self.spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.spectrum=smooth(intensities,21)
        self.wavelength=wavelengths
        
    def plot_fig(self):   
        
        if (self.specCon==True):
            self.getSpectra()
            self.plotspec.set_xdata(self.wavelength)
            self.plotspec.set_ydata(self.spectrum)
            self.canvasspec.draw()
        if (self.specCon==False):
            self.plotspec.set_ydata(self.spectrum)
            self.plotspec.set_xdata(np.arange(0,len((self.spectrum))))
            self.canvasspec.draw()
           
        if (self.con == True):	
            if ( READ_from_DEVICE):
                curpH=random.random()
                curdo=random.random()
                curtem=random.random()
                curna=random.random()
                curca=random.random()
                curglu=random.random()
                if (self.bioselect.get()=="pH"):
                    self.bioqueue.append(curpH)
                elif (self.bioselect.get()=="DO"):
                    self.bioqueue.append(curdo)
                elif (self.bioselect.get()=="Temp"):
                    self.bioqueue.append(curtem)
                elif (self.bioselect.get()=="Na"):
                    self.bioqueue.append(curna)
                elif (self.bioselect.get()=="Ca"):
                    self.bioqueue.append(curca)
                elif (self.bioselect.get()=="Glu"):
                    self.bioqueue.append(curglu)
            if (not READ_from_DEVICE):
                
                '''
                prediction_sign=predictdata(self.device,self.spectrum,"CNN")
                if (self.bioselect.get()=="pH"):
                    self.bioqueue.append(prediction_sign[0][0])
                elif (self.bioselect.get()=="DO"):
                    self.bioqueue.append(prediction_sign[0][1])
                elif (self.bioselect.get()=="Temp"):
                    self.bioqueue.append(prediction_sign[0][3])
                elif (self.bioselect.get()=="Na"):
                    self.bioqueue.append(prediction_sign[0][4])
                elif (self.bioselect.get()=="Ca"):
                    self.bioqueue.append(prediction_sign[0][2])
                elif (self.bioselect.get()=="Glu"):
                    self.bioqueue.append(prediction_sign[0][5])
                '''
                
                if (self.bioselect.get()=="pH"):
                    '''add code to control the lasers through TTL and GPIO'''
                    self.ser.write(b'L4E')
                    self.ser.write(b'L3D')
                    self.ser.write(b'L2D')
                    self.bioqueue.append(MVRpredict(self.spectrum,405)[0])
                elif (self.bioselect.get()=="DO"):
                    self.ser.write(b'L4E')
                    self.ser.write(b'L3D')
                    self.ser.write(b'L2D')                   
                    self.bioqueue.append(MVRpredict(self.spectrum,405)[1])
                elif (self.bioselect.get()=="Temp"):
                    self.ser.write(b'L4D')
                    self.ser.write(b'L3E')
                    self.ser.write(b'L2D')
                    self.bioqueue.append(MVRpredict(self.spectrum,450)[0])
                elif (self.bioselect.get()=="Na"):
                    self.ser.write(b'L4D')
                    self.ser.write(b'L3E')
                    self.ser.write(b'L2D')
                    self.bioqueue.append(MVRpredict(self.spectrum,450)[1])
                elif (self.bioselect.get()=="Ca"):
                    self.ser.write(b'L4D')
                    self.ser.write(b'L3D')
                    self.ser.write(b'L2E')
                    self.bioqueue.append(MVRpredict(self.spectrum,540)[0])
                elif (self.bioselect.get()=="Glu"):
                    self.ser.write(b'L4E')
                    self.ser.write(b'L3D')
                    self.ser.write(b'L2D')                    
                    self.bioqueue.append(MVRpredict(self.spectrum,405)[2])
            self.plottime.set_xdata(np.arange(0,len(self.bioqueue.get())))
            self.plottime.set_ydata(self.bioqueue.get())
            self.canvasbio.draw()
    
        self.after(25,self.plot_fig)
    

    def spec_run(self):
        self.specCon=True
        print ("spec run")
    def spec_stop(self):
        self.specCon=False
        print ("spec stop")      
    def run_test(self):
        self.con=True
        print ("run test")
    def end_test(self):
        self.con=False
        print ("endtest")        
    def calibration_test(self):
        self.spec.close()
        self.ser.close()
        self.newWindow=tk.Toplevel()
        self.newWindow.title("calibration")
        self.newWindow.frames = {}
        #self.parent.frame.destroy()
        container = tk.Frame(self.newWindow)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        frame = calibrationFrame(container, self.newWindow)
        #self.parent.frames[calibrationFrame] = frame
        frame.grid(row=0, column=0, sticky="nsew")
    
        print ("all")

def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    #root = tk.Tk()
    my_gui =App()
    my_gui.mainloop()

if __name__ == "__main__":
    main()


