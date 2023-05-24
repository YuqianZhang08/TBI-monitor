from tkinter.constants import FALSE
import matplotlib as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
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
        if not READ_from_DEVICE:
            self.file="spectrums.csv"
            df=pd.read_csv(self.file)
            data=np.array(df)
            self.specCon=False
            self.wavelength=data[:,0]
            self.pH6=data[:,1]
            self.do0=data[:,2]
            self.temp35=data[:,3]
            self.glu0=data[:,4]
            self.na0=data[:,3]
            self.ca0=data[:,4]
            self.pH8=data[:,1]
            self.do8=data[:,2]
            self.temp40=data[:,3]
            self.glu6=data[:,4]
            self.na200=data[:,3]
            self.ca2=data[:,4]
        else:
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
        self.controlfrm = tk.LabelFrame(self.tstfrm, text="control frame")
        # define the self.entfrm entries
        self.pHcalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="pH 6",
            command=lambda:self.specplt('pH6')
            ).grid(row=0, column=0, sticky=tk.W)
        '''
        self.pHcalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="pH 8",
            command=lambda:self.specplt('pH8')
            ).grid(row=0, column=1, sticky=tk.W)
        
        self.temcalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="Temperature 35",
            command=lambda:self.specplt('temp35')
            ).grid(row=1, column=0, sticky=tk.W)
        self.temcalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="Temperature 40",
            command=lambda:self.specplt('temp40')
            ).grid(row=1, column=1, sticky=tk.W)
        
        self.o2calbtn1 = ttk.Button(
            master=self.controlfrm,
            text="DO 0",
            command=lambda:self.specplt('DO0')
            ).grid(row=2, column=0, sticky=tk.W)
        self.o2calbtn2 = ttk.Button(
            master=self.controlfrm,
            text="DO 8",
            command=lambda:self.specplt('DO8')
            ).grid(row=2, column=1, sticky=tk.W)
        
        self.nacalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="Na 0",
            command=lambda:self.specplt('na0')
            ).grid(row=3, column=0,sticky=tk.W)
        self.nacalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="Na 200",
            command=lambda:self.specplt('na200')
            ).grid(row=3, column=1,sticky=tk.W)
        
        self.cacalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="Ca 0",
            command=lambda:self.specplt('ca0')
            ).grid(row=4, column=0,sticky=tk.W)
        self.cacalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="Ca 2",
            command=lambda:self.specplt('ca2')
            ).grid(row=4, column=1,sticky=tk.W)
        
        self.gluCalbtn1 = ttk.Button(
            master=self.controlfrm,
            text="glucose 0",
            command=lambda:self.specplt('glu0')
            ).grid(row=5, column=0,sticky=tk.W)
        self.gluCalbtn2 = ttk.Button(
            master=self.controlfrm,
            text="glucose 6",
            command=lambda:self.specplt('glu6')
            ).grid(row=5, column=1,sticky=tk.W)
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
        
        self.specplot.set_ylim(1400,3000)
        self.specplot.set_xlim(400,800)
        
        # grid stuff into self.tstfrm
        self.specfrm.grid(row=0, column=0, sticky=tk.W)
        self.controlfrm.grid(row=0, column=1, sticky=tk.W)
        
        self.tstfrm.grid(padx=4,pady=1)
        
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
    
    def specplt(self,biomarker):
        #create a stack, buffer size, input data, display stack 
        if (biomarker=='pH6'):
            self.specCon=False
            time.sleep(2)
            self.specCon=True
            self.pH6=self.spectrum
        elif (biomarker=='pH8'):
            self.pHcon=False
            time.sleep(2)
            self.pH8=self.spectrum
        elif (biomarker=='DO0'):
            self.DOcon=False
            time.sleep(2)
            self.DOcon=True
            self.DO0=self.spectrum
        elif (biomarker=='DO8'):
            self.DOcon=False
            time.sleep(2)
            self.DO8=self.spectrum
        elif (biomarker=='temp35'):
            self.tempcon=False
            time.sleep(2)
            self.tempcon=True
            self.temp35=self.spectrum
        elif (biomarker=='tem40'):
            self.tempcon=False
            time.sleep(2)
            self.temp40=self.spectrum
        elif (biomarker=='glu0'):
            self.glucon=False
            time.sleep(2)
            self.glucon=True
            self.glu0=self.spectrum
        elif (biomarker=='glu6'):
            self.glucon=False
            time.sleep(2)
            self.glu6=self.spectrum
        elif (biomarker=='Na0'):
            self.nacon=False
            time.sleep(2)
            self.nacon=True
            self.na0=self.spectrum
        elif (biomarker=='Na200'):
            self.nacon=False
            time.sleep(2)
            self.na200=self.spectrum
        elif (biomarker=='Ca0'):
            self.cacon=False
            time.sleep(2)
            self.cacon=True
            self.ca0=self.spectrum
        elif (biomarker=='Ca2'):
            self.cacon=False
            time.sleep(2)
            self.ca2=self.spectrum
        


def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    #root.grid(sticky="nsew")
    my_gui =calibrationFrame(root)
    my_gui.mainloop()


if __name__ == "__main__":
    main()
