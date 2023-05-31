
import matplotlib as mp
import numpy as np
import pandas as pd
import random
from multitask.predict import predictdata

import tkinter as tk  # GUI
from tkinter import ttk
from smooth import smooth
from seabreeze.spectrometers import Spectrometer
import serial
from MVR import MVRpredict
import time

READ_from_DEVICE=False

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Brain monitoring")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        #menubar = myMenuBar(self)
        #self.config(menu=menubar)
        self.frames = {}
        self.frame = Multi_Frame(container, self)
        self.frames[Multi_Frame] = self.frame
        self.frame.grid(row=0, column=0, sticky="nsew")
        
class Multi_Frame(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #super().__init__(parent)
        self.parent = parent
        self.controller=controller

        self.con=False
        if READ_from_DEVICE:
            self.ser=serial.Serial('COM4', 115200)
        if not READ_from_DEVICE:
            self.file="spectrum.csv"
            df=pd.read_csv(self.file)
            data=np.array(df)
            self.wavelength=data[:,0]
            self.pH=data[:,1]
            self.oxygen=data[:,1]
            self.temp=data[:,1]
            self.glu=data[:,1]
            self.na=data[:,1]
            self.ca=data[:,1]
        #parent.title("Brain monitoring")
        #self.winfo_toplevel().configure(menu=myMenuBar(self).menubar)
        # define test parameters
        #self.plotstyle.set('seaborn-colorblind')
        #self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        self.build_window()
    def build_window(self):
        """Make all the tkinter widgets"""
        # build the main frame
        self.tstfrm = tk.Frame(self.parent)
        self.phfrm = tk.LabelFrame(self.tstfrm, text="pH")
        # this spacing is to avoid using multiple labels
        self.o2frm = tk.LabelFrame(self.tstfrm, text="Oxygen")
        self.glufrm = tk.LabelFrame(self.tstfrm, text="Glucose")
        self.temfrm = tk.LabelFrame(self.tstfrm, text="Temperature")
        self.nafrm = tk.LabelFrame(self.tstfrm, text="Sodium")
        self.cafrm = tk.LabelFrame(self.tstfrm, text="Calcium")
        self.controlfrm=tk.LabelFrame(self.tstfrm, text="control panel")
 
        self.conbut3 = ttk.Button(
            master=self.controlfrm,
            text="Start",
            command=lambda:self.run_test()
            ).grid(row=0, column=0)
        self.conbutstop = ttk.Button(
            master=self.controlfrm,
            text="Stop",
            command=lambda:self.end_test()
            ).grid(row=0, column=1)
        
        # grid entries into self.entfrm
        #self.fig, self.ax = plt.subplots(figsize=(5, 2), dpi=100)
        #plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        # TODO: explicitly clarify some of these args
        #self.figpH, self.axpH=plt.subplot(figsize=(4, 2), dpi=100)

        self.phLabel=ttk.Label(self.phfrm,text='pH')
        self.phLabel.grid(row=0, sticky=tk.E, padx=2)
        self.o2Label=ttk.Label(self.o2frm,text='pH')
        self.o2Label.grid(row=0, sticky=tk.E, padx=2)
        self.gluLabel=ttk.Label(self.glufrm,text='pH')
        self.gluLabel.grid(row=0, sticky=tk.E, padx=2)
        self.temLabel=ttk.Label(self.temfrm,text='pH')
        self.temLabel.grid(row=0, sticky=tk.E, padx=2)
        self.naLabel=ttk.Label(self.nafrm,text='pH')
        self.naLabel.grid(row=0, sticky=tk.E, padx=2)
        self.caLabel=ttk.Label(self.cafrm,text='pH')
        self.caLabel.grid(row=0, sticky=tk.E, padx=2)
        
        
        self.phfrm.grid(row=0, column=0, rowspan=2, sticky=tk.W, pady=2)
        self.o2frm.grid(row=4, column=0, rowspan=2, sticky=tk.W, padx=2)
        self.glufrm.grid(row=0, column=1, rowspan=2, padx=2)
        self.temfrm.grid(row=4, column=1, rowspan=2, padx=2)
        self.nafrm.grid(row=0, column=2, rowspan=2, sticky=tk.W, padx=2)
        self.cafrm.grid(row=4, column=2, rowspan=2, sticky=tk.W, padx=2)
        self.controlfrm.grid(row=6, column=1, sticky=tk.W, rowspan=2, padx=2)
        self.tstfrm.grid(padx=4)
        
        self.after(1000,self.plot_all)


    def plot_all(self):
        if (self.con == True):
            if (not READ_from_DEVICE):	            
                curpH=7+random.random()
                curdo=4+2*random.random()
                curtem=38+3*random.random()
                curna=150+30*random.random()
                curca=1+random.random()
                curglu=3+2*random.random()
            else:                
                self.ser.write(b'L4E')
                time.sleep(3)
                self.getSpectra()
                spec405=self.spectrum
                curpH,curdo,curglu=MVRpredict(spec405,405)
                self.ser.write(b'L4D')
                self.ser.write(b'L3E')
                time.sleep(3)
                self.getSpectra()
                spec450=self.spectrum
                curtem,curna=MVRpredict(spec450,450)
                self.ser.write(b'L3D')
                self.ser.write(b'L2E')
                time.sleep(3)
                self.getSpectra()
                spec540=self.spectrum
                curca=MVRpredict(spec540,540)
                self.ser.write(b'L2D')
                
                '''#for dl model prediction of all together
                size=(14,53)
                data=(np.array(spec405).reshape(size),np.array(spec450).reshape(size),np.array(spec540).reshape(size))
                prediction_sign=predictdata("cpu",data,"CNN")
                curpH=prediction_sign[0][0]  #MVRpredict(spec405,405)[0]
                curdo=prediction_sign[0][1]   #MVRpredict(spec405,405)[1]
                curtem=prediction_sign[0][3]  #MVRpredict(spec450,450)[0]
                curna=prediction_sign[0][4]   #MVRpredict(spec450,450)[1]
                curca=prediction_sign[0][2]   #MVRpredict(spec540,540)[0]
                curglu=prediction_sign[0][5]  #MVRpredict(spec405,405)[2]
                '''
            self.phLabel["text"] = str(curpH)
            self.o2Label["text"] = str(curdo)  
            self.temLabel["text"] = str(curtem)  
            self.naLabel["text"] = str(curna)  
            self.caLabel["text"] = str(curca)  
            self.gluLabel["text"] = str(curglu)  
                  
        self.after(1000,self.plot_all)
        
    def run_test(self):
        self.con=True 
        print ("run test")
    def end_test(self):
        self.con=False
        print ("end test")     
    def getSpectra(self):
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(10000)  # 0.1 seconds
        wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.spectrum=smooth(intensities,21)
        self.wavelength=wavelengths
        
        
def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    #root = tk.Tk()
    my_gui =App()
    my_gui.mainloop()

if __name__ == "__main__":
    main()
