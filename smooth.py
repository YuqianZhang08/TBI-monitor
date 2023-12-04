import numpy as np
import pandas as pd

def smooth(a,WSZ):
    out0 = np.convolve(a,np.ones(WSZ,dtype=int),'valid')/WSZ
    r = np.arange(1,WSZ-1,2)
    start = np.cumsum(a[:WSZ-1])[::2]/r
    stop = (np.cumsum(a[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((  start , out0, stop  ))

if __name__=='__main__':
    path="D:\\research article 2\\transmission.csv"
    output_path="smoothed.xlsx"
    df=pd.read_csv(path, encoding= 'unicode_escape')
    writer = pd.ExcelWriter(output_path)
    for k in df.keys():
        data=np.array(df[k])
        df=pd.DataFrame(data,columns=['wavelength','intensity'])
        df=df[df["wave"]>420]
        df=df[df["wave"]<760]
        data=np.array(df)
        num_column=len(data[0])
        output=data[:,0]
        for i in range (0,num_column):
            output=np.vstack((output,smooth(data[:,i],21)))
    
        output=np.transpose(output)
        df2 = pd.DataFrame(output)
        df2.to_excel(writer,sheet_name=k)
    writer.save()
    writer.close()
