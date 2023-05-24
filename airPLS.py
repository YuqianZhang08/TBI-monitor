#!/usr/bin/python
'''
airPLS.py Copyright 2014 Renato Lombardo - renato.lombardo@unipa.it
Baseline correction using adaptive iteratively reweighted penalized least squares

This program is a translation in python of the R source code of airPLS version 2.0
by Yizeng Liang and Zhang Zhimin - https://code.google.com/p/airpls
Reference:
Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive iteratively reweighted penalized least squares. Analyst 135 (5), 1138-1146 (2010).

Description from the original documentation:

Baseline drift always blurs or even swamps signals and deteriorates analytical results, particularly in multivariate analysis.  It is necessary to correct baseline drift to perform further data analysis. Simple or modified polynomial fitting has been found to be effective in some extent. However, this method requires user intervention and prone to variability especially in low signal-to-noise ratio environments. The proposed adaptive iteratively reweighted Penalized Least Squares (airPLS) algorithm doesn't require any user intervention and prior information, such as detected peaks. It iteratively changes weights of sum squares errors (SSE) between the fitted baseline and original signals, and the weights of SSE are obtained adaptively using between previously fitted baseline and original signals. This baseline estimator is general, fast and flexible in fitting baseline.
'''

import numpy as np
import pandas as pd
from scipy.sparse import csc_matrix, eye, diags, linalg
from scipy.sparse.linalg import spsolve, norm
import matplotlib.pyplot as pl
from scipy import sparse

def WhittakerSmooth(x,w,lambda_,differences=1):
    '''
    Penalized least squares algorithm for background fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        w: binary masks (value of the mask is zero if a point belongs to peaks and one otherwise)
        lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background
        differences: integer indicating the order of the difference of penalties
    
    output
        the fitted background vector
    '''
    X=np.matrix(x)
    m=X.size
    i=np.arange(0,m)
    E=eye(m,format='csc')
    D=E[1:]-E[:-1] # numpy.diff() does not work with sparse matrix. This is a workaround.
    W=diags(w,0,shape=(m,m))
    A=csc_matrix(W+(lambda_*D.T*D))
    B=csc_matrix(W*X.T)
    background=spsolve(A,B)
    return np.array(background)

def airPLS(x, lambda_=100, porder=1, itermax=15):
    '''
    Adaptive iteratively reweighted penalized least squares for baseline fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background, z
        porder: adaptive iteratively reweighted penalized least squares for baseline fitting
    
    output
        the fitted background vector
    '''
    x=np.transpose(x)
    #m=x.shape[1]
    m=x.shape
    w=np.ones(m)
    for i in range(1,itermax+1):
        z=WhittakerSmooth(x,w,lambda_, porder)
        d=x-z
        d=d[0]
        dssn=np.abs(d[d<0].sum())
        if(dssn<0.001*(abs(x)).sum() or i==itermax):
            if(i==itermax): print ('WARING max iteration reached!')
            break
        w[d>=0]=0 # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d<0]=np.exp(i*np.abs(d[d<0])/dssn)
        w[0]=np.exp(i*(d[d<0]).max()/dssn) 
        w[-1]=w[0]
    return x-z
 

def baseline_arPLS(y, ratio=1e-6, lam=10000000, niter=40, full_output=False): 

    L = len(y) 
    diag = np.ones(L - 2) 
    D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2) 
    H = lam * D.dot(D.T)  # The transposes are flipped w.r.t the Algorithm on pg. 252 
    w = np.ones(L) 
    W = sparse.spdiags(w, 0, L, L) 
    crit = 1 
    count = 0 
    while crit > ratio: 
        z = linalg.spsolve(W + H, W * y) 
        d = y - z 
        dn = d[d < 0] 
        m = np.mean(dn) 
        s = np.std(dn) 
        w_new = 1 / (1 + np.exp(2 * (d - (2*s - m))/s)) 
        crit = np.linalg.norm(w_new - w) / np.linalg.norm(w) 
        w = w_new 
        W.setdiag(w)  # Do not create a new matrix, just update diagonal values 
        count += 1 
        if count > niter: 
            print('Maximum number of iterations exceeded') 
            break 

    if full_output: 
        info = {'num_iter': count, 'stop_criterion': crit} 
        return z, d, info 
    else: 
        return y-z 
    
    
if __name__=='__main__':
    '''
    Example usage and testing
    '''
    path="E:\张雨倩\PhD imperial\lab\\algorithm\smoothed.xlsx"
    output_path="baseline.xlsx"
    df=pd.read_excel(path)
    data=np.array(df)
    num_column=len(data[0])
    output=data[:,0]
    for i in range (1,num_column):
        output=np.vstack(airPLS(data[:,i]))
    
    output=np.transpose(output)
    df=pd.DataFrame(output)
    df.to_csv(output_path)

    '''
    print ('Testing...')
    from scipy.stats import norm
    import matplotlib.pyplot as pl
    x=np.arange(0,1000,1)
    g1=norm(loc = 100, scale = 1.0) # generate three gaussian as a signal
    g2=norm(loc = 300, scale = 3.0)
    g3=norm(loc = 750, scale = 5.0)
    signal=g1.pdf(x)+g2.pdf(x)+g3.pdf(x)
    baseline1=5e-4*x+0.2 # linear baseline
    baseline2=0.2*np.sin(np.pi*x/x.max()) # sinusoidal baseline
    noise=np.random.random(x.shape[0])/500
    print ('Generating simulated experiment')
    y1=signal+baseline1+noise
    y2=signal+baseline2+noise
    print ('Removing baselines')
    c1=y1-airPLS(y1) # corrected values
    c2=y2-airPLS(y2) # with baseline removed
    print ('Plotting results')
    fig,ax=pl.subplots(nrows=2,ncols=1)
    ax[0].plot(x,y1,'-k')
    ax[0].plot(x,c1,'-r')
    ax[0].set_title('Linear baseline')
    ax[1].plot(x,y2,'-k')
    ax[1].plot(x,c2,'-r')
    ax[1].set_title('Sinusoidal baseline')
    pl.show()
    print ('Done!')

    '''