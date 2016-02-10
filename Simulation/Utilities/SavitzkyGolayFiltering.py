'''
script taken from http://pythonmining.com/posts/smoothing-noisy-data-with-polynomials.html
'''
import math
from math import factorial
import scipy as sp
import numpy as np
import scipy.linalg as linalg


def savitzky_golay(y, wl, wr, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    wl : int
        the length of the left half-window. Must be wl+wr=even integer.
    wr : int
        the length of the right half-window. Must be wl+wr=even integer.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, wl=15,wr=15, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """

    try:
        window_size = np.abs(np.int(wl+wr+1))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)

    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-wl, wr+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:wl+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-wr-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

if __name__=='__main__':
    from Simulation.Utilities.DatasetHandler import createNormalsDataset
    from Simulation.Utilities.Plotter import *
    from Simulation.Utilities.Dec import deDec
    '''
    l=100

    time=sp.arange(l)
    position=deDec(createNormalsDataset(loc=10, scale=0.0001, size=l, cumsum=True))
    print('position array:')
    print(position)
    vel=smooth_causal(time,position.as_matrix(),size=2,order=2,deriv=1)
    print('velocity array:')
    print(vel)
    
    print('simple computation:')
    print([deDec(position.as_matrix()[i])/time[i] for i in range(len(position))])
    
    
    plot2d(time, position.as_matrix(),title='position', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/pos',showFlag=False)
    plot2d(time, vel,title='velocity', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/vel',showFlag=False)
    plot2d(time, [deDec(position.as_matrix()[i])/time[i] for i in range(len(position))],title='velocity naive', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/vel_n',showFlag=False)
    '''
    
    
    import pandas as pd
    from Simulation.Utilities.DatasetHandler import *
    
    monfunc1D=lambda x:x[0]
    monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
    
    node='n1'
    
    
    ds=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/singleH_heuristic_distOptPair_random_1D2N/singleH_heuristic_distOptPair_random_1D2N_0/dataset_train.p')
    
    ds=ds.loc[:,:,:]
    
    dsTrain,dsTest=splitTrainTestDataset(ds,percentage=0.8)
    
    print(dsTrain)
    print(len(dsTrain.major_axis))

    
    print(dsTest)
    print(len(dsTest.major_axis))
        
    timeTrain=sp.arange(len(dsTrain.major_axis))
    timeTest=sp.arange(len(dsTest.major_axis))
    
    fTrain=sp.array([monfunc1D(i) for i in dsTrain.loc[node,:,:].values])
    fTest=sp.array([monfunc1D(i) for i in dsTest.loc[node,:,:].values])
    
    velTrain=savitzky_golay(deDec(fTrain),wl=10,wr=0,order=3,deriv=1)
    velTrain2=savitzky_golay(deDec(fTrain),wl=200,wr=0,order=3,deriv=1)
    
    #print(velTrain[-50:-1])
    print(sp.mean(velTrain2))
    #print(velTrain[-50:-1]-velTrain2[-50:-1])

    # sp.absolute(velTrain[100:500]-velTrain2), ,timeTrain[100:500]
    #multiplePlots2d([timeTrain[100:500],timeTrain[100:500]], [velTrain[100:500],velTrain2] ,title='velocity',labels=['full','partial','diff'], saveFlag=True, filename='/home/ak/git/GM_Experiment/test/velTrainCompareN',showFlag=False)
    multiplePlots2d([timeTrain[-50:-1], timeTrain[-50:-1]], [fTrain[-50:-1], velTrain2[-50:-1]], ['val','vel'],saveFlag=True, filename='/home/ak/git/GM_Experiment/test/posveltrain', showFlag=False)
    
    velTest=savitzky_golay(deDec(fTest),wl=200,wr=0,order=3,deriv=1)
    
    plot2d(timeTrain, deDec(fTrain) ,title='position', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/posTrainN',showFlag=False)
    plot2d(timeTrain, velTrain ,title='velocity', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/velTrainN',showFlag=False)
    
    plot2d(timeTest, deDec(fTest) ,title='position', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/posTestN',showFlag=False)
    plot2d(timeTest, velTest ,title='velocity', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/velTestN',showFlag=False)
    