import pandas as pd
import numpy as np
import os


path = 'E:\张雨倩\PhD imperial\lab\oxgen ph sensor\oxygen\experiment\COMMERCIAL REVERSIBILITY\commercial'
files = os.listdir(path)
data = pd.read_csv(files[0], sep='\t',skiprows=230)
Arrdata=np.array(data)
Arrdata=Arrdata[:1000,:]  #to 760 nm
output=Arrdata[:,0]
for file in files:
    data = pd.read_csv(file, sep='\t',skiprows=230)
    data=np.array(data)
    output=np.vstack((output,data[:1000,1]))
output=np.transpose(output)
df=pd.DataFrame(output)
df.to_csv("organized.csv")
    
    



