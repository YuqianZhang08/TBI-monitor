import numpy as np
import pandas as pd
import statsmodels.api as sm
from airPLS import airPLS, baseline_arPLS
from sklearn.linear_model import LinearRegression
from sklearn.base import RegressorMixin
from sklearn.utils import check_X_y
import numpy as np



def multivariate_fit(y,X):
    model = sm.GLM(y,X)    
    R=[[1, 1, 0, 0,0,0],[0, 0, 1, 1,0,0],[0, 0, 0,0,1,1]]
    q=[1,1,1]           
    result = model.fit_constrained((R, q))
    concen=result.params
    return(concen)

def ridgefit(X,y):
    from sklearn import linear_model
    reg = linear_model.Ridge(alpha=.5)
    reg.fit(X,y)
    concen=reg.coef_
    return (concen)

def sckl_mr(X,y):
    from sklearn.linear_model import LinearRegression
    reg = LinearRegression(positive=True).fit(X, y)
    return(reg.coef_)



class ConstrainedLinearRegression(LinearRegression, RegressorMixin):

    def __init__(self, A, B, fit_intercept=True, normalize=False, copy_X=True, tol=1e-15, lr=1.0):
        self.A = A
        self.B = B
        self.fit_intercept = fit_intercept
        self.normalize = normalize
        self.copy_X = copy_X
        self.tol = tol
        self.lr = lr

    def fit(self, X, y, initial_beta=None):
        X, y = check_X_y(
            X, y, 
            accept_sparse=['csr', 'csc', 'coo'], 
            y_numeric=True, multi_output=False
        )
        X, y, X_offset, y_offset, X_scale = self._preprocess_data(
            X, y, 
            fit_intercept=self.fit_intercept, 
            normalize=self.normalize, 
            copy=self.copy_X
        )
        if initial_beta is not None:
            # providing initial_beta may be useful, 
            # if initial solution does not respect the constraints. 
            beta = initial_beta
        else:
            beta = np.zeros(X.shape[1]).astype(float)
        prev_beta = beta + 1
        hessian = np.dot(X.transpose(), X)
        while not (np.abs(prev_beta - beta)<self.tol).all():
            prev_beta = beta.copy()
            for i in range(len(beta)):
                grad = np.dot(np.dot(X,beta) - y, X)
                max_coef = np.inf
                min_coef = -np.inf
                for a_row, b_value in zip(self.A, self.B):
                    if a_row[i] == 0:
                        continue
                    zero_out = beta.copy()
                    zero_out[i] = 0
                    bound = (b_value - np.dot(zero_out, a_row)) / a_row[i] 
                    if a_row[i] > 0:
                        max_coef = np.minimum(max_coef, bound)
                    elif a_row[i] < 0:
                        min_coef = np.maximum(min_coef, bound)
                assert min_coef <= max_coef, "the constraints are inconsistent"
                beta[i] = np.minimum(
                    max_coef, 
                    np.maximum(
                        min_coef,
                        beta[i] - (grad[i] / hessian[i,i]) * self.lr
                    )
                )
        self.coef_ = beta
        self._set_intercept(X_offset, y_offset, X_scale)
        return self  

def datacrop(wavelength,data):
    return (data[wavelength:])

def MVRpredict(signal,light):
    database_path="3overlap.xlsx"
    
    datastandard = pd.read_excel(database_path)
    datastandard=np.array(datastandard)
    signal=np.array(signal)
    baselineCrrSig=np.transpose(airPLS(signal))
    if light==405:
        concen=multivariate_fit(baselineCrrSig,datastandard[:,0:6])
        Do=0.8*concen[2]+8*concen[3]
        Glu=concen[4]*1+concen[5]*6
        pH=6*concen[0]+8*concen[1]
        return pH,Do, Glu
    elif light==450:
        '''add code to control the lasers through TTL and GPIO'''
        concen=multivariate_fit(baselineCrrSig,datastandard[:,6:10])
        temp=36*concen[2]+40*concen[3]
        sodium=concen[4]*40+concen[5]*200
        return temp, sodium
    elif light==540:
        '''add code to control the lasers through TTL and GPIO'''
        concen=multivariate_fit(baselineCrrSig,datastandard[:,10:12])
        calcium=concen[0]*0.5+concen[1]*2
        return calcium
        

if __name__=='__main__':
    excel_path = "3overlap.xlsx"
    data = pd.read_excel(excel_path)
    dataArr=np.array(data)
    st_wavelength=100
    y=dataArr[1:,6:]
    X=dataArr[1:,0:6]
    yall=datacrop(st_wavelength,y)
    X=datacrop(st_wavelength,X)
    X = np.array(X, dtype=float)
    yall= np.array(yall, dtype=float)
    num_column=len(X[0])
    
    '''
    X_basecorrected=airPLS(X[:,0])
    for i in range (1,num_column):
        X_basecorrected= np.vstack((X_basecorrected,airPLS(X[:,i])))
    X_basecorrected=np.transpose(X_basecorrected)
    y_corrected=airPLS(y)
    '''
    #concen=multivariate_fit(y_corrected,X_basecorrected)
    concenlist=[]
    temp=[]
    sodium=[]
    calcium=[]

    for i in range (0,len(yall[0])):     #len(yall[0])
       y=yall[:,i]
       concen=multivariate_fit(y,X)    #GLM fit
       #concen=ridgefit(X,y)
       #concen=sckl_mr(X,y)           #Sciklearn fit
       concenlist.append(concen)
       calcium.append(0.25*concen[0]+1.5*concen[1])
       temp.append(36*concen[2]+40*concen[3])
       sodium.append(concen[4]*40+concen[5]*200)
       print(i)
       #oxy2.append(concen[2]*0.8+7.8*concen[3])
    #concen=multivariate_fit(y,X)
    #print(concen)
    output=[temp,sodium,calcium,concenlist]
    df=pd.DataFrame(output)
    df.to_csv("outputglm78.csv")