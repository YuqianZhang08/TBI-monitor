import numpy as np
import pandas as pd


path="organize.xlsx"
output_path="smoothed.xlsx"

def smooth(a,WSZ):
    # a:原始数据，NumPy 1-D array containing the data to be smoothed
    # 必须是1-D的，如果不是，请使用 np.ravel()或者np.squeeze()转化 
    # WSZ: smoothing window size needs, which must be odd number,
    # as in the original MATLAB implementation
    out0 = np.convolve(a,np.ones(WSZ,dtype=int),'valid')/WSZ
    r = np.arange(1,WSZ-1,2)
    start = np.cumsum(a[:WSZ-1])[::2]/r
    stop = (np.cumsum(a[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((  start , out0, stop  ))

# another one，边缘处理的不好

"""
def movingaverage(data, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(data, window, 'same')
"""

# another one，速度更快
# 输出结果 不与原始数据等长，假设原数据为m，平滑步长为t，则输出数据为m-t+1

"""

def movingaverage(data, window_size):
    cumsum_vec = np.cumsum(np.insert(data, 0, 0)) 
    ma_vec = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return ma_vec
"""

df=pd.read_excel(path, sheet_name=None)
writer = pd.ExcelWriter(output_path)
for k in df.keys():
    data=np.array(df[k])
    num_column=len(data[0])
    output=data[:,0]
    for i in range (1,num_column):
        output=np.vstack((output,smooth(data[:,i],11)))
    
    output=np.transpose(output)
    df2 = pd.DataFrame(output)
    df2.to_excel(writer,sheet_name=k)
writer.save()
writer.close()