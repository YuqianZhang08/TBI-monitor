import sqlite3
import tkinter as tk  # GUI
from tkinter import Entry, Tk, ttk
import seabreeze  # talking to the spectroscopy
from seabreeze.spectrometers import list_devices, Spectrometer
import matplotlib.pyplot as plt  # plotting the data
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import pandas as pd

class calibration_db(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("calibration")
        container = tk.Frame(self)
        #container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        #self.parent=parent
        self.calibrationData=[]
        self.conn=sqlite3.connect('spectra.db')
        self.c = self.conn.cursor()

        self.plotstyle = tk.StringVar()
        self.plotstyle.set('seaborn-colorblind')

    
        #self.tstfrm = tk.Frame(container)
        self.cmdfrm = tk.LabelFrame(self, text="Command panel")
        '''
        self.pH1=tk.Label(container,width=30)
        self.pH1.grid(row=0,column=0, padx=30)
        self.pH2=tk.Label(self,width=30)
        self.pH2.grid(row=0,column=1, padx=30)
        self.Oxy1=tk.Label(self,width=30)
        self.Oxy1.grid(row=1,column=0, padx=30)
        self.Oxy2=tk.Label(self,width=30)
        self.Oxy2.grid(row=1,column=1, padx=30)
        self.Tem1=tk.Label(self,width=30)
        self.Tem1.grid(row=2,column=0, padx=30)
        self.Tem2=tk.Label(self,width=30)
        self.Tem2.grid(row=2,column=1, padx=30)
        self.Glu1=tk.Label(self,width=30)
        self.Glu1.grid(row=3,column=0, padx=30)
        self.Glu2=tk.Label(self,width=30)
        self.Glu2.grid(row=3,column=1, padx=30)
        '''
        self.whitebtn1 = ttk.Button(
            master=self.cmdfrm,
            text="reference light",
            command=self.getSpectra("reference")
            ).grid(row=0,column=0, padx=10)
        self.pHbtn1 = ttk.Button(
            master=self.cmdfrm,
            text="pH6 Calibration",
            command=self.getSpectra("pH6")
            ).grid(row=0,column=1, padx=10)
        self.pHbtn2 = ttk.Button(
            master=self.cmdfrm,
            text="pH8 Calibration",
            command=self.getSpectra("pH8")
            ).grid(row=1,column=1, padx=10)
        self.O2btn1 = ttk.Button(
            master=self.cmdfrm,
            text="0 pO2 calibration",
            command=self.getSpectra("0O2")
            ).grid(row=0,column=2, padx=10)
        self.O2btn2 = ttk.Button(
            master=self.cmdfrm,
            text="100 pO2 calibration",
            command=self.getSpectra("100O2")
            ).grid(row=1,column=2, padx=10)
        self.tempbtn1 = ttk.Button(
            master=self.cmdfrm,
            text="30 temperature calibration",
            command=self.getSpectra("30Cel")
            ).grid(row=0,column=3, padx=10)
        self.tempbtn1 = ttk.Button(
            master=self.cmdfrm,
            text="40 temperature calibration",
            command=self.getSpectra("40Cel")
            ).grid(row=1,column=3, padx=10)
        self.glubtn1 = ttk.Button(
            master=self.cmdfrm,
            text="1 Glucose",
            command=self.getSpectra("1glu")
            ).grid(row=0,column=4, padx=10)
        self.glubtn1 = ttk.Button(
            master=self.cmdfrm,
            text="5 Glucose",
            command=self.getSpectra("5glu")
            ).grid(row=1,column=4, padx=10)

        self.pltfrm = tk.LabelFrame(
            master=self,
            text=("Style: " + self.plotstyle.get())
            )

        self.fig= plt.Figure(figsize=(7.5, 4), dpi=100)
        self.subfig=self.fig.add_subplot(111)
        #self.subfig.plot(self.spectrum)
        # TODO: explicitly clarify some of these args
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.pltfrm)
        toolbar = NavigationToolbar2Tk(self.canvas, self.pltfrm)
        toolbar.update()
        self.canvas.get_tk_widget().pack()  
        
        self.cmdfrm.grid(row=0, column=0, sticky=tk.NSEW, pady=2)
        self.pltfrm.grid(row=1, column=0, rowspan=2, sticky=tk.NSEW, padx=2)

        with plt.style.context(self.plotstyle.get()):
            self.pltfrm.config(text="spectra plot")
            #self.ax.clear() 
            #self.ax.set_xlabel("Time (min)") 
            #self.ax.set_ylabel("Concentration") 


    def getSpectra(self,datalabel):
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(100000)  # 0.1 seconds
        wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        self.signal=intensities
        self.wavelength=wavelengths
        self.calibrationData.append(intensities)
        self.dataimport(datalabel)
        return 0
#create a database

    def dataimport(self,datalabel):
        # commit changes
        self.conn.commit()

#close connection
        self.conn.close()
#create a curser


def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    #root = tk.Tk()
    my_gui =calibration_db()
    my_gui.mainloop()

if __name__ == "__main__":
    main()