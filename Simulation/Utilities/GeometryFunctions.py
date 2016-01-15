'''
@author: ak
'''
import pickle
import time
import math
from pyOpt import Optimization
from pyOpt import SOLVOPT
import scipy as sp
from scipy import linalg
from Simulation.Utilities.Dec import *
from decimal import Decimal

def computeBallFromDiametralPoints(p1,p2):
    '''
    computes a ball given two diametric points
    args:
        @param p1: point vector
        @param p2: point vector
    @return (center point vector,radius)
    '''
    print(p1)
    print(p2)
    
    d=(p1-p2)/(dec(2.0) if (all(isinstance(i,Decimal) for i in p1) and all(isinstance(i,Decimal) for i in p2)) else 2.0)
    center=p2+d
    radius=linalg.norm(d)
    
    return (center,radius)


def __objfunc(x,**kwargs):
    
    c,r=kwargs['ball']
    fu=kwargs['func']
    
    f=fu(x)
    
    g=[0.0]
    g[0]=sum((x-c)**2)-r**2

    fail=0
    
    return f,g,fail

def computeExtremesFuncValuesInBall(func,ball,type='max',tolerance=1e-7):
    '''
    compute the extremes (min, max) of f(ball)
    args:
        @param func: the function
        @param ball: B(center, radius) tuple defining ball, 
                center an sp.ndarray with ndim==1, len==dimentionallity of vector
        @param tolerance: error tolerance
    @return type==type='max': func_max
            type=='min': func_min
    '''
    #DBG
    print('--------------Ext Val COMPUTATION-------------')
    c,r=ball
    
    if type=='max':
        f=lambda x:-func(x)
    else:
        f=func
    
    optProb=Optimization('ball_val',__objfunc)
    optProb.addVarGroup('p',(2 if len(c)<=1 else len(c)),type='c') #added hack to run 1D case array style

    optProb.addObj('f')
    optProb.addCon('in_ball','i')
    
    #DBG
    #print(optProb)
    
    opt=SOLVOPT()
    opt.setOption('xtol',tolerance)
    opt.setOption('ftol',tolerance)
    opt(optProb,sens_type='FD',ball=ball,func=f)
    
    #the point
    #p=sp.array([optProb._solutions[0].getVar(i).value for i in range(len(c))])
    
    #DBG
    #print(p)
    #if (sum((p-c)**2)<=r**2):
    #    print('-----OK %.10f > %.10f'%(sum((p-c)**2),r**2))
    #else:
    #    print('-----FAIL %.10f > %.10f'%(sum((p-c)**2),r**2))
        
    if type=='max':
        #DBG
        #print('========================= %.10f'%-optProb._solutions[0].getObj(0).value)
        return -optProb._solutions[0].getObj(0).value
    else:
        #DBG
        #print('========================= %.10f'%optProb._solutions[0].getObj(0).value)
        return optProb._solutions[0].getObj(0).value
    

#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------

def monFunc(x):
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return sum(x)
    
def monFunc1D(x):
    
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return x
    
def monFunc5D(x):
    nom=x[0]+x[4]+x[3]
    denom=x[1]+x[2]
    
    return nom**2-denom

if __name__=='__main__':
    
    #tolerance
    tolerance=1e-3
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=4
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    
    #1D test
    print('--------------1D test-------------------')
    import scipy as sp
    computeExtremesFuncValuesInBall(lambda x:x[0], (sp.array([1.0]),1.0),type='max', tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:x[0]**2, (sp.array([1.0]),10.0),type='max',tolerance=tolerance)
        
    #2D test
    print('--------------2D test-------------------')
    import scipy as sp
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0],1.0),type='max',tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0],1.0),type='max',tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:sum(x), (sp.array([1.0,1.0]),1.0),type='max',tolerance=tolerance)
      
    #3D test
    print('--------------3D test-------------------')
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:x[2], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    computeExtremesFuncValuesInBall(lambda x:x[0]+x[1]+x[2], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
      
    
    