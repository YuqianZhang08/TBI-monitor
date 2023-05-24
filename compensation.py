import numpy as np
import pandas as pd
import matplotlib as mp
import math
from scipy import optimize

class Oxygen:
    def __init__(self):
        self.Ksv=0
        self.Tc=25
        self.I0=0

    def setI0(self, I0):
        self.I0=I0

    def func(self,Real_O2,Ksv,I0):
        return I0/(Ksv*Real_O2+1)

    def Ksv_determine(self,expReal_O2, expInten):
        popt,pcov=optimize.curve_fit(self.func,expReal_O2,expInten)
        self.Ksv=popt[0]
        self.I0=popt[1]
        return self.Ksv

    def fun2(I,f,Kt,T,Tc,self):
        return (self.I0/(I-f)-1)/(self.Ksv+Kt*(T-Tc))

    def temperature_compensation(self,I,Tc,T,pO2):
        Kt=self.Ksv
        f=0
        pO2_cal=(self.I0/(I-f)-1)/(self.Ksv+Kt*(T-Tc))
        opt=optimize.least_squares(self.fun2,pO2)
        popt,pcov=optimize.curve_fit(self.func2,I,pO2)
        return (Kt, self.Ksv,pO2_cal)