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

    import scipy as sp
    import scipy.signal as spsig
    from Simulation.Utilities.Plotter import *
    
    wl=20
    order=4
    wr=0
    
    t=sp.arange(0,300)
    
    vel=5.0
    linear_increasing=spsig.chirp(t, 1/20.0, 100, 1/100.0) #sp.array([vel*i for i in t])
    
    
    #complete sg
    resComplete=savitzky_golay(linear_increasing, wl=wl, wr=wr, order=order, deriv=1)
    
    
    multiplePlots2d([t[15:27],t[15:27]], [linear_increasing[15:27],resComplete[15:27]], labels=['original', 'sg'],saveFlag=True,filename='/home/ak/git/GM_Experiment/sgtest',showFlag=False)
     
    #streaming sg
    resIncremental=[]
    for i in range(2,len(linear_increasing)):
        sig=linear_increasing[0:i]
        if wl>len(sig):
            wlt=len(sig) if len(sig)%2==0 else len(sig)-1
            if order+2>wlt+wr+1:
                ordert=wlt+wr+1-2
            else:
                ordert=order
        else:
            wlt=wl
        print('--left:%d right:%d order:%d'%(wlt,wr,ordert))
        out=savitzky_golay(sig, wl=wlt , wr=wr, order=ordert, deriv=1)
        resIncremental.append(out)
     
    for i in range(len(resIncremental)):
        print(i)
        print(resIncremental[i])
     
    multiplePlots2d([t[15:len(i)] for i in resIncremental[15:27]],resIncremental[15:27],saveFlag=True, filename='/home/ak/git/GM_Experiment/sgIncTest', showFlag=False)