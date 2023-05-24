
from re import X
from scipy import optimize
import numpy as np

x_values=[0.99,0.9,2.2,2.91,3.1,3.9,4.02,5.37,5.78,6.1,6.8]
y_values=[3.208370058,3.215722797,3.095872298,2.999482728,2.98419954,2.960944815,2.87840786,2.866216585,2.857364661,2.730207108,2.754580078]

def func(realO2,Ksv,I0):
    return I0/(Ksv*realO2+1)

popt, _ = optimize.curve_fit(func, x_values, y_values)
x_values=np.array(x_values)
fitted_value=popt[1]/(popt[0]*x_values+1)

#calculate rsquare
sstot=sum(np.square((y_values-np.mean(y_values))))
ssres=sum(np.square((y_values-fitted_value)))
Rsquare=1-ssres/sstot

print(Rsquare)
print(popt[0])
print(popt[1])
