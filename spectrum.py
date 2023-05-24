import seabreeze
import numpy as np
import pandas as pd

from threading import Timer

seabreeze.use('cseabreeze')
from seabreeze.spectrometers import list_devices, Spectrometer

devices = list_devices()
#print(devices)

def getSpectra(integraT):
        spec = Spectrometer.from_first_available()
        spec.integration_time_micros(integraT)  # 0.1 seconds
        wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
        return wavelengths, intensities

def readspec(data):
    spec.integration_time_micros(100000)  # 0.1 seconds
    wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
    data=np.vstack((data,intensities))

def prep_Spectrum(size=(14,53)):
    _,data405=spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
    t = Timer(30.0, getSpectra(100000))
    t.start()
    _,data450=spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
    _,data540=spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
    data=(np.array(data405).reshape(size),np.array(data450).reshape(size),np.array(data540).reshape(size))
    return data

class RepeatingTimer(Timer): 
    def run(self):
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)
         
#spec = Spectrometer(devices[0])
#print (spec)
spec = Spectrometer.from_first_available()
spec.integration_time_micros(100000)  # 0.1 seconds
wavelengths, intensities = spec.spectrum(correct_dark_counts=False, correct_nonlinearity=True)
data=np.vstack((wavelengths,intensities))
data=np.transpose(data)
#df = pd.DataFrame(data)
#df.to_csv('white.csv')   
t = RepeatingTimer(10.0,readspec)
t.start()
t.cancel()
data=np.transpose(data)
df = pd.DataFrame(data)
df.to_csv('white.csv')