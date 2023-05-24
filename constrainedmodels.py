import numpy as np
import pandas as pd
import statsmodels.api as sm
from airPLS import airPLS, baseline_arPLS
from sklearn.linear_model import LinearRegression
from sklearn.base import RegressorMixin
from sklearn.utils import check_X_y
import numpy as np
import statsmodels.api as sm

class ConstrainedLinearRegression(sm.GLM, RegressorMixin):

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


if __name__=='__main__':
    excel_path = "baselinePLS.csv"
    data = pd.read_csv(excel_path)
    dataArr=np.array(data)
    st_wavelength=0
    y=dataArr[1:,4:]
    X=dataArr[1:,0:4]
    yall=datacrop(st_wavelength,y)
    X=datacrop(st_wavelength,X)
    X = np.array(X, dtype=float)
    yall= np.array(y, dtype=float)
    num_column=len(X[0])
    
    concenlist=[]
    temp=[]
    sodium=[]

    A=np.array([[1,1,0,0],[0,0,1,1],[-1,-1,0,0],[0,0,-1,-1]])
    B=np.array([1,1,-0.99,-0.999])

    model=ConstrainedLinearRegression(A,B)
    for i in range (0, len(yall[0])):
        y=yall[:,i]
        model.fit(X,y)
        concen=model.coef_
        concenlist.append(concen)
        temp.append(36*concen[0]+41*concen[1])
        sodium.append(concen[2]*40+concen[3]*200)

    output=[temp,sodium,concenlist]
    df=pd.DataFrame(output)
    df.to_csv("outputscik.csv")