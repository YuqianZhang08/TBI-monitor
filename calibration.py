import numpy as np
import pandas as pd
import matplotlib as mp
import math

path_oxy="oxygen_0.xlsx"
path_glu="glucose5.xlsx"
output_path="smoothed.xlsx"
df_oxygen0=pd.read_excel(path_oxy, sheet_name="oxy0")
df_oxygen100=pd.read_excel(path_oxy, sheet_name="oxy100")
df_glu=pd.read_excel(path_glu, sheet_name="5mM")

ArrOxy0=np.array(df_oxygen0)
ArrOxy100=np.array(df_oxygen100)
ArrGlu=np.array(df_glu)

#alfa=

