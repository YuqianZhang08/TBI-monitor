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
READ_from_DEVICE=True
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
            self.getSpectra()
            self.specCon=True
            self.pHcon=True
            self.DOcon=True
            self.tempcon=True
            self.nacon=True
            self.cacon=True
            self.glucon=True
            
        #self.calidata=np.zeros(len(self.wavelength),13)
        self.calidata=self.wavelength
        #self.calidata[:,0]=self.wavelength[:]
        #parent.title("Brain monitoring")
        #self.winfo_toplevel().configure(menu=myMenuBar(self).menubar)
        # define test parameters
        #self.plotstyle.set('seaborn-colorblind')
        #self.outfile = f"{self.chem.get()}_{self.conc.get()}.csv"
        self.build_window()
    def getSpectra(self):
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(100000)  # 0.1 seconds
        wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.signal=intensities
        self.wavelength=wavelengths
        return 0
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
        
        
        # define the self.entfrm entries
        self.pHcalbtn1 = ttk.Button(
            master=self.phfrm,
            text="pH 6",
            command=lambda:self.spectrum('pH6')
            ).grid(row=1, column=0, sticky=tk.W)
        
        self.pHcalbtn2 = ttk.Button(
            master=self.phfrm,
            text="pH 8",
            command=lambda:self.spectrum('pH8')
            ).grid(row=1, column=1, sticky=tk.W)
        
        self.temcalbtn1 = ttk.Button(
            master=self.temfrm,
            text="Temperature 35",
            command=lambda:self.spectrum('temp35')
            ).grid(row=1, column=0, sticky=tk.W)
        self.temcalbtn2 = ttk.Button(
            master=self.temfrm,
            text="Temperature 40",
            command=lambda:self.spectrum('temp40')
            ).grid(row=1, column=1, sticky=tk.W)
        
        self.o2calbtn1 = ttk.Button(
            master=self.o2frm,
            text="DO 0",
            command=lambda:self.spectrum('DO0')
            ).grid(row=1, column=0, sticky=tk.W)
        self.o2calbtn2 = ttk.Button(
            master=self.o2frm,
            text="DO 8",
            command=lambda:self.spectrum('DO8')
            ).grid(row=1, column=1, sticky=tk.W)
        
        self.nacalbtn1 = ttk.Button(
            master=self.nafrm,
            text="Na 0",
            command=lambda:self.spectrum('na0')
            ).grid(row=1, column=0,sticky=tk.W)
        self.nacalbtn2 = ttk.Button(
            master=self.nafrm,
            text="Na 200",
            command=lambda:self.spectrum('na200')
            ).grid(row=1, column=1,sticky=tk.W)
        
        self.cacalbtn1 = ttk.Button(
            master=self.cafrm,
            text="Ca 0",
            command=lambda:self.spectrum('ca0')
            ).grid(row=1, column=0,sticky=tk.W)
        self.cacalbtn2 = ttk.Button(
            master=self.cafrm,
            text="Ca 2",
            command=lambda:self.spectrum('ca2')
            ).grid(row=1, column=1,sticky=tk.W)
        
        self.gluCalbtn1 = ttk.Button(
            master=self.glufrm,
            text="glucose 0",
            command=lambda:self.spectrum('glu0')
            ).grid(row=1, column=0,sticky=tk.W)
        self.gluCalbtn2 = ttk.Button(
            master=self.glufrm,
            text="glucose 6",
            command=lambda:self.spectrum('glu6')
            ).grid(row=1, column=1,sticky=tk.W)
        
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

        self.pHplot.set_xlabel("wavelength (nm)")
        self.pHplot.set_ylabel("Intensity")
        self.o2plot.set_xlabel("wavelength (nm)")
        self.o2plot.set_ylabel("Intensity")
        self.templot.set_xlabel("wavelength (nm)")
        self.templot.set_ylabel("Intensity")
        self.naplot.set_xlabel("wavelength (nm)")
        self.naplot.set_ylabel("Intensity")
        self.caplot.set_xlabel("wavelength (nm)")
        self.caplot.set_ylabel("Intensity")
        self.gluplot.set_xlabel("wavelength (nm)")
        self.gluplot.set_ylabel("Intensity")
        self.pHplot.set_ylim(1400,3000)
        self.pHplot.set_xlim(400,800)
        self.o2plot.set_ylim(1400,3000)
        self.o2plot.set_xlim(400,800)
        self.templot.set_ylim(1400,3000)
        self.templot.set_xlim(400,800)
        # grid stuff into self.tstfrm
        self.phfrm.grid(row=0, column=0, sticky=tk.W)
        self.o2frm.grid(row=2, column=0, sticky=tk.W)
        self.glufrm.grid(row=4, column=1, sticky=tk.E, pady=2)
        self.temfrm.grid(row=0, column=1, sticky=tk.E, padx=2)
        self.nafrm.grid(row=2, column=1, sticky=tk.E, pady=2)
        self.cafrm.grid(row=4, column=0, sticky=tk.W, padx=2)
        self.tstfrm.grid(padx=4)
        
        self.calpH=self.pHplot.plot([],[])[0]
        self.calDO=self.o2plot.plot([],[])[0]
        self.caltem=self.templot.plot([],[])[0]
        self.calna=self.naplot.plot([],[])[0]
        self.calca=self.caplot.plot([],[])[0]
        self.calglu=self.gluplot.plot([],[])[0]
        
        self.after(25,self.plot_fig)
        
    def plot_fig(self):   
        
        if (self.specCon==True):
            self.getSpectra()
            if (self.pHcon==True):
                self.calpH.set_xdata(self.wavelength)
                self.calpH.set_ydata(self.spectrum)
            if (self.DOcon==True):
                self.calDO.set_xdata(self.wavelength)
                self.calDO.set_ydata(self.spectrum)
            if (self.tempcon==True):
                self.caltem.set_xdata(self.wavelength)
                self.caltem.set_ydata(self.spectrum)
            if (self.nacon==True):
                self.calna.set_xdata(self.wavelength)
                self.calna.set_ydata(self.spectrum)
            if (self.cacon==True):
                self.calca.set_xdata(self.wavelength)
                self.calca.set_ydata(self.spectrum)
            if (self.glucon==True):
                self.calglu.set_xdata(self.wavelength)
                self.calglu.set_ydata(self.spectrum)

            self.canvaspH.draw()
            self.canvasO2.draw()
            self.canvastem.draw()
            self.canvasna.draw()
            self.canvasca.draw()
            self.canvasglu.draw()
        self.after(25,self.plot_fig)    
        
            
    def concentration(self):
        #create a stack, buffer size, input data, display stack 
        
        print ("test")
    
    def spectrum(self,biomarker):
        #create a stack, buffer size, input data, display stack 
        if (biomarker=='pH6'):
            self.pHcon=False
            time.sleep(2)
            self.pHcon=True
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