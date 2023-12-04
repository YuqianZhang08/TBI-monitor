from tkinter.constants import FALSE
import matplotlib as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
from MVR import MVRpredict
import serial
import tkinter as tk  # GUI
from tkinter import ttk
import time
#import seabreeze  # talking to the spectroscopy
from seabreeze.spectrometers import list_devices, Spectrometer
READ_from_DEVICE=False
#from menubar import myMenuBar
class calibrationFrame(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #super().__init__(parent)
        self.parent = parent
        self.controller=controller
        self.bufferselect= tk.StringVar()  
        self.bufferselect.set('buffer1')
        if not READ_from_DEVICE:
            self.file="spectrum.csv"
            df=pd.read_csv(self.file)
            data=np.array(df)
            self.specCon=False
            self.wavelength=data[:,0]
            self.spectrum=data[:,1]
        else:
            self.ser=serial.Serial('COM4', 115200)
            self.specCon=True
            self.spec = Spectrometer(list_devices()[0])
            self.spec.integration_time_micros(100000)  # 0.1 seconds
            self.getSpectra()
            #self.specCon=True
            #self.pHcon=True
            #self.DOcon=True
            #self.tempcon=True
            #self.nacon=True
            #self.cacon=True
            #self.glucon=True
            
        #self.calidata=np.zeros(len(self.wavelength),13)
        
        #self.calidata[:,0]=self.wavelength[:]
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
        self.specfrm = tk.LabelFrame(self.tstfrm, text="Spectrum reading")
        self.descriptfrm = tk.LabelFrame(self.tstfrm, text="Description")
        self.controlfrm = tk.LabelFrame(self.tstfrm, text="User Control")
        
        ttk.Label(
            master=self.descriptfrm,
            text="Please insert the sensing catheter into the following standard buffer solutions, press confirm after 5 min",wraplength=200,foreground='blue'
            ).grid(row=0, sticky=tk.W, pady=6)
        
        ttk.Label(
            master=self.descriptfrm,
            text="Buffer solution 1 (PBS):\n pH=6, DO=0, Temperature=25, Na+=150, Ca2+=0, glucose=0",wraplength=200
            ).grid(row=1, sticky=tk.NW, pady=6)
        ttk.Label(
            master=self.descriptfrm,
            text="Buffer solution 2 (PBS):\n pH=8, DO=8, temperature=40, Na+200, Ca2+=2, glucose=6",wraplength=200
            ).grid(row=2, sticky=tk.W, pady=6)
        
        ttk.Label(
            master=self.controlfrm,
            text="Please select the current buffer solution",wraplength=200,foreground='blue'
            ).grid(row=0, sticky=tk.W, pady=6)
        
        self.pHcalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="Confirm",
            command=lambda:self.savecali()
            ).grid(row=3, column=0, sticky=tk.W)
        tk.Radiobutton(
            master=self.controlfrm,
            text="Buffer Solution 1",
            variable=self.bufferselect,
            value='bf1'
            ).grid(row=1, column=0, padx=5, sticky=tk.W)
        tk.Radiobutton(
            master=self.controlfrm,
            text="Buffer solution 2",
            variable=self.bufferselect,
            value='bf2'
            ).grid(row=2, column=0, padx=5,pady=5,sticky=tk.W)
        '''
        self.pHcalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="pH 8",
            command=lambda:self.specplt('pH8')
            ).grid(row=0, column=1, sticky=tk.W)
        
        '''
        # grid entries into self.entfrm
        #self.fig, self.ax = plt.subplots(figsize=(5, 2), dpi=100)
        #plt.subplots_adjust(left=0.10, bottom=0.12, right=0.97, top=0.95)
        # TODO: explicitly clarify some of these args
        #self.figpH, self.axpH=plt.subplot(figsize=(4, 2), dpi=100)
        self.figspec=plt.Figure(figsize=(6, 4), dpi=100)
        
        self.specplot=self.figspec.add_subplot(111)
        
        self.canvassepc = FigureCanvasTkAgg(self.figspec, master=self.specfrm)
        
        #toolbar = NavigationToolbar2Tk(self.canvas, self.phfrm)
        #toolbar.update()
        self.canvassepc.get_tk_widget().grid(row=0,column=0,columnspan=2)
        
        self.specplot.set_xlabel("wavelength (nm)")
        self.specplot.set_ylabel("Intensity")
        
        self.specplot.set_ylim(0,4000)
        self.specplot.set_xlim(400,800)
        
        # grid stuff into self.tstfrm
        self.specfrm.grid(row=0, column=1, rowspan=2, sticky=tk.NSEW, padx=2)
        self.controlfrm.grid(row=1, column=0, sticky=tk.NSEW, pady=2)
        self.descriptfrm.grid(row=0, column=0, sticky=tk.NSEW, pady=1)
        
        self.tstfrm.grid(padx=3)
        
        self.calspec=self.specplot.plot(self.wavelength,self.spectrum)[0]
        
        self.after(25,self.plot_fig)
        
    def plot_fig(self):   
        
        if (self.specCon==True):
            self.getSpectra()    
            self.calspec.set_xdata(self.wavelength)
            self.calspec.set_ydata(self.spectrum)
            self.canvassepc.draw()
            
        self.after(25,self.plot_fig)    
        
    def getSpectra(self):
        wavelengths, intensities = self.spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.spectrum=intensities
        self.wavelength=wavelengths
        return 0        
    def concentration(self):
        #create a stack, buffer size, input data, display stack 
        
        print ("test")
    
    def savecali(self):
        #create a stack, buffer size, input data, display stack 
        self.ser.write(b'L4E')
        time.sleep(3)
        self.getSpectra()
        spec405=self.spectrum
        curpH,curdo,curglu=MVRpredict(spec405[1:1017],405)
        self.ser.write(b'L4D')
        self.ser.write(b'L3E')
        time.sleep(3)
        self.getSpectra()
        spec450=self.spectrum
        curtem,curna=MVRpredict(spec450[1:1017],450)
        self.ser.write(b'L3D')
        self.ser.write(b'L2E')
        time.sleep(3)
        self.getSpectra()
        spec540=self.spectrum
        curca=MVRpredict(spec540[1:1017],540)
        self.ser.write(b'L2D')       
        caliresult=[curpH, curdo, curtem, curna,curca,curglu]
         
        if self.bufferselect.get()=='bf1':
            np.savetxt('bf1.txt', caliresult, delimiter=',')  
        if self.bufferselect.get()=='bf2':
            np.savetxt('bf2.txt', caliresult, delimiter=',')  
        

def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    #root.grid(sticky="nsew")
    my_gui =calibrationFrame(root)
    my_gui.mainloop()


if __name__ == "__main__":
    main()
