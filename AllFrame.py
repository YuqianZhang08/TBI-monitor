from tkinter.constants import FALSE
import matplotlib as mp
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
from multitask.predict import predictdata
from ringbuffer import RingBuffer
import tkinter as tk  # GUI
from tkinter import ttk
from smooth import smooth
#import seabreeze  # talking to the spectroscopy
from seabreeze.spectrometers import list_devices, Spectrometer
import serial

import time

pin405 = 33  # BOARD pin 
pin450 = 35  # BBOARD pin
pin540 = 31  # BOARD pin



READ_from_DEVICE=False
#from menubar import myMenuBar
class All_Frame(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #super().__init__(parent)
        self.parent = parent
        self.controller=controller
        self.bioquepH=RingBuffer(100)
        self.bioqueDO=RingBuffer(100)
        self.bioqueTem=RingBuffer(100)
        self.bioqueCa=RingBuffer(100)
        self.bioqueNa=RingBuffer(100)
        self.bioqueGlu=RingBuffer(100)
        self.con=False
        if READ_from_DEVICE:
            self.ser=serial.Serial('COM4', 115200)
        if not READ_from_DEVICE:
            self.file="spectrums.csv"
            df=pd.read_csv(self.file)
            data=np.array(df)
            self.wavelength=data[:,0]
            self.pH=data[:,1]
            self.oxygen=data[:,2]
            self.temp=data[:,3]
            self.glu=data[:,4]
            self.na=data[:,3]
            self.ca=data[:,4]
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
        self.Specbtn4 = ttk.Button(
            master=self.controlfrm,
            text="Save",
            command=lambda:self.save_graph()
            ).grid(row=0, column=2)
        # grid entries into self.entfrm
        #self.fig, self.ax = plt.subplots(figsize=(5, 2), dpi=100)
        #plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        # TODO: explicitly clarify some of these args
        #self.figpH, self.axpH=plt.subplot(figsize=(4, 2), dpi=100)
        self.figpH=plt.Figure(figsize=(4, 2), dpi=100)
        self.figo2=plt.Figure(figsize=(4, 2), dpi=100)
        self.figtem=plt.Figure(figsize=(4, 2), dpi=100)
        self.figglu=plt.Figure(figsize=(4, 2), dpi=100)
        self.figca=plt.Figure(figsize=(4, 2), dpi=100)
        self.figna=plt.Figure(figsize=(4, 2), dpi=100)
        self.pHplot=self.figpH.add_subplot(111)
        self.o2plot=self.figo2.add_subplot(111)
        self.templot=self.figtem.add_subplot(111)
        self.gluplot=self.figglu.add_subplot(111)
        self.caplot=self.figca.add_subplot(111)
        self.naplot=self.figna.add_subplot(111)
        self.pHtime=self.pHplot.plot([],[])[0]
        self.DOtime=self.o2plot.plot([],[])[0]
        self.temtime=self.templot.plot([],[])[0]
        self.natime=self.naplot.plot([],[])[0]
        self.catime=self.caplot.plot([],[])[0]
        self.glutime=self.gluplot.plot([],[])[0]
        self.canvaspH = FigureCanvasTkAgg(self.figpH, master=self.phfrm)
        self.canvasO2 = FigureCanvasTkAgg(self.figo2, master=self.o2frm)
        self.canvasglu = FigureCanvasTkAgg(self.figglu, master=self.glufrm)
        self.canvastem = FigureCanvasTkAgg(self.figtem, master=self.temfrm)
        self.canvasna = FigureCanvasTkAgg(self.figna, master=self.nafrm)
        self.canvasca = FigureCanvasTkAgg(self.figca, master=self.cafrm)
        #toolbar = NavigationToolbar2Tk(self.canvas, self.phfrm)
        #toolbar.update()
        self.canvaspH.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn.pack()
        #self.Specbtn.pack()
        self.canvasO2.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn2.pack()
        #self.Specbtn2.pack()
        self.canvasglu.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn3.pack()
       # self.Specbtn3.pack()
        self.canvastem.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn4.pack()
        #self.Specbtn4.pack()
        self.canvasna.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn3.pack()
       # self.Specbtn3.pack()
        self.canvasca.get_tk_widget().grid(row=0,column=0,columnspan=1)
        #self.Conbtn4.pack()
        #self.Specbtn4.pack()

        self.pHplot.set_ylabel("pH")
        self.pHplot.xaxis.set_visible(False)
        self.pHplot.set_xlim(0,100)
        self.pHplot.set_ylim(0,10)

        self.o2plot.set_ylabel("O2")
        self.o2plot.set_xlim(0,100)
        self.o2plot.set_ylim(0,10)
        
        self.templot.set_ylabel("Temperature")        
        self.templot.set_xlim(0,100)
        self.templot.set_ylim(30,50)
        
        self.naplot.set_ylabel("Na")
        self.naplot.set_xlim(0,100)
        self.naplot.set_ylim(100,200)
        
        self.caplot.set_ylabel("Ca")
        self.caplot.set_xlim(0,100)
        self.caplot.set_ylim(0,4)
        
        self.gluplot.set_ylabel("Glucose")
        self.gluplot.set_xlim(0,100)
        self.gluplot.set_ylim(0,10)
        # grid stuff into self.tstfrm
        self.phfrm.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.o2frm.grid(row=2, column=0, rowspan=2, sticky=tk.W, padx=2)
        self.glufrm.grid(row=0, column=1, sticky=tk.E, pady=2)
        self.temfrm.grid(row=2, column=1, rowspan=2,sticky=tk.E, padx=2)
        self.nafrm.grid(row=0, column=2, sticky=tk.E, pady=2)
        self.cafrm.grid(row=2, column=2, rowspan=2,sticky=tk.E, padx=2)
        self.controlfrm.grid(row=4, column=1, sticky=tk.E, rowspan=2, padx=4)
        self.tstfrm.grid(padx=4)
        
        self.after(25,self.plot_all)
   
    
        
        print ("test")
    '''   
    def spectrum(self,biomarker):
        #create a stack, buffer size, input data, display stack 
        if (biomarker=='pH'):
            self.pHplot.plot(self.wavelength,self.pH)
            self.canvaspH.draw()
        elif (biomarker=='o2'):
            self.o2plot.plot(self.wavelength,self.oxygen)
            self.canvasO2.draw()    
        elif (biomarker=='tem'):
            self.templot.plot(self.wavelength,self.temp)
            self.canvastem.draw() 
        elif (biomarker=='glu'):
            self.gluplot.plot(self.wavelength,self.glu)
            self.canvasglu.draw()
        elif (biomarker=='Na'):
            self.naplot.plot(self.wavelength,self.na)
            self.canvasna.draw() 
        elif (biomarker=='Ca'):
            self.caplot.plot(self.wavelength,self.ca)
            self.canvasca.draw()
    '''
    def run_test(self):
        self.con=True 
        print ("run test")
    def end_test(self):
        self.con=False
        print ("end test") 
    def save_graph(self):
        self.figpH.savefig('pH.png')     
        self.figo2.savefig('DO.png')   
        self.figtem.savefig('Temperature.png')   
        self.figna.savefig('Na.png')   
        self.figca.savefig('Ca.png')   
        self.figglu.savefig('Glu.png')   
                
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
                '''import RPi.GPIO as GPIO
                GPIO.setup(pin405, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(pin450, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setup(pin540, GPIO.OUT, initial=GPIO.LOW)
                GPIO.setmode(GPIO.BOARD)  # BCM pin-numbering scheme from Raspberry Pi
                size=(14,53)
                GPIO.output(pin405, GPIO.HIGH)
                time.sleep(3)
                self.getSpectra()
                spec405=self.spectrum
                GPIO.output(pin405, GPIO.LOW)
                GPIO.output(pin450, GPIO.HIGH)
                time.sleep(3)
                self.getSpectra()
                spec450=self.spectrum
                GPIO.output(pin450, GPIO.LOW)
                GPIO.output(pin540, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(pin540, GPIO.LOW)
                self.getSpectra()
                spec540=self.spectrum
                data=(np.array(spec405).reshape(size),np.array(spec450).reshape(size),np.array(spec540).reshape(size))
                prediction_sign=predictdata("cpu",data,"CNN")
                '''
                size=(14,53)
                self.ser.write(b'L4E')
                time.sleep(3)
                self.getSpectra()
                spec405=self.spectrum
                self.ser.write(b'L4D')
                self.ser.write(b'L3E')
                time.sleep(3)
                self.getSpectra()
                spec450=self.spectrum
                self.ser.write(b'L3D')
                self.ser.write(b'L2E')
                time.sleep(3)
                self.getSpectra()
                spec540=self.spectrum
                self.ser.write(b'L2D')
                data=(np.array(spec405).reshape(size),np.array(spec450).reshape(size),np.array(spec540).reshape(size))
                prediction_sign=predictdata("cpu",data,"CNN")
                curpH=prediction_sign[0][0]
                curdo=prediction_sign[0][1]
                curtem=prediction_sign[0][3]
                curna=prediction_sign[0][4]
                curca=prediction_sign[0][2]
                curglu=prediction_sign[0][5]
                
            self.bioquepH.append(curpH)
            self.bioqueDO.append(curdo)
            self.bioqueTem.append(curtem)
            self.bioqueNa.append(curna)
            self.bioqueCa.append(curca)
            self.bioqueGlu.append(curglu)
                
            self.pHtime.set_xdata(np.arange(0,len(self.bioquepH.get())))
            self.pHtime.set_ydata(self.bioquepH.get())
            self.DOtime.set_xdata(np.arange(0,len(self.bioqueDO.get())))
            self.DOtime.set_ydata(self.bioqueDO.get())
            self.temtime.set_xdata(np.arange(0,len(self.bioqueTem.get())))
            self.temtime.set_ydata(self.bioqueTem.get())
            self.natime.set_xdata(np.arange(0,len(self.bioqueNa.get())))
            self.natime.set_ydata(self.bioqueNa.get())
            self.catime.set_xdata(np.arange(0,len(self.bioqueCa.get())))
            self.catime.set_ydata(self.bioqueCa.get())
            self.glutime.set_xdata(np.arange(0,len(self.bioqueGlu.get())))
            self.glutime.set_ydata(self.bioqueGlu.get())
            self.canvaspH.draw()
            self.canvasO2.draw()
            self.canvastem.draw()
            self.canvasna.draw()
            self.canvasca.draw()
            self.canvasglu.draw()
    
        self.after(25,self.plot_all)
        
    def getSpectra(self):
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(10000)  # 0.1 seconds
        wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.spectrum=smooth(intensities,21)
        self.wavelength=wavelengths
'''
def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    #root.grid(sticky="nsew")
    my_gui =All_Frame(root)
    my_gui.mainloop()


if __name__ == "__main__":
    main()
'''