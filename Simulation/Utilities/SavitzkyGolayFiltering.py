'''
script taken from http://dsp.stackexchange.com/questions/9498/have-position-want-to-calculate-velocity-and-acceleration
@author: datageist
'''
import math
import scipy as sp
import scipy.linalg as linalg

def sg_filter(x, m, k=0):
    """
    x = Vector of sample times
    m = Order of the smoothing polynomial
    k = Which derivative
    """
    mid = len(x) / 2        
    a = x - x[mid]
    expa = lambda x: map(lambda i: i**x, a)    
    A = sp.r_[map(expa, range(0,m+1))].transpose()
    Ai = linalg.pinv(A)

    return Ai[k]

def smooth(x, y, size=5, order=2, deriv=0):
    '''
    time, position, size, order, derivative
    '''
    
    if deriv > order:
        raise Exception, "deriv must be <= order"

    m = size

    result = sp.zeros(len(x)+2*m)

    pad=sp.zeros(m)

    x=sp.concatenate((pad,x,pad))
    
    y=sp.concatenate((pad,y,pad))

    n = len(x)
    
    for i in xrange(m, n-m):
        start, end = i - m, i + m + 1
        f = sg_filter(x[start:end], order, deriv)
        result[i] = sp.dot(f, y[start:end])
    
    x=x[m:-m]
    y=y[m:-m]
    result=result[m:-m]
    
    if deriv > 1:
        result *= math.factorial(deriv)

    return result


if __name__=='__main__':
    from Simulation.Utilities.DatasetHandler import createNormalsDataset
    from Simulation.Utilities.Plotter import plot2d
    from Simulation.Utilities.Dec import deDec

    l=100

    time=sp.arange(l)
    position=deDec(createNormalsDataset(loc=10, scale=0.0001, size=l, cumsum=True))
    print('position array:')
    print(position)
    vel=smooth(time,position.as_matrix(),size=2,order=2,deriv=1)
    print('velocity array:')
    print(vel)
    
    print('simple computation:')
    print([deDec(position.as_matrix()[i])/time[i] for i in range(len(position))])
    
    
    plot2d(time, position.as_matrix(),title='position', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/pos',showFlag=False)
    plot2d(time, vel,title='velocity', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/vel',showFlag=False)
    plot2d(time, [deDec(position.as_matrix()[i])/time[i] for i in range(len(position))],title='velocity naive', saveFlag=True, filename='/home/ak/git/GM_Experiment/test/vel_n',showFlag=False)