'''
@author: ak
'''
import pickle
import time
import math
from pyOpt import Optimization
import scipy as sp
from scipy import linalg
from Simulation.Utilities.Dec import *
from decimal import Decimal
from pyOpt.pyCONMIN.pyCONMIN import CONMIN

def computeBallFromDiametralPoints(p1,p2):
    '''
    computes a ball given two diametric points
    args:
        @param p1: point vector
        @param p2: point vector
    @return (center point vector,radius)
    '''
    #print(p1)
    #print(p2)
    
    d=(p1-p2)/(dec(2.0) if (all(isinstance(i,Decimal) for i in p1) and all(isinstance(i,Decimal) for i in p2)) else 2.0)
    center=p2+d
    radius=linalg.norm(d)
    
    return (center,radius)


def __objfunc(xgroups,**kwargs):
    x=xgroups['p']
    
    
    c,r=kwargs['ball']
    fu=kwargs['func']
    
    f=fu(x) #opt func
    
    g=[0.0] #constraints
    g[0]=sum((x[0:len(c)]-c)**2)-r**2

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
    #print('--------------Ext Val COMPUTATION-------------')
    #print(ball)
    c,r=ball
    
    if type=='max':
        f=lambda x:-func(x)
    else:
        f=func
    
    optTol=1e-12
    
    optProb=Optimization('ball_val',__objfunc,use_groups=True)
    optProb.addVarGroup('p',
                        (2 if len(c)<=1 else len(c)),
                        type='c',
                        upper=[1.00e+21]*len(c)+([] if len(c)>1 else [0.1]),
                        lower=[-1.00e+21]*len(c)+([] if len(c)>1 else [0])) #added hack to run 1D case array style
    
    optProb.addObj('f')
    optProb.addCon('in_ball','i', upper=0.0)
    
    #DBG
    #print(optProb)
    
    opt=CONMIN()
    #opt.setOption('IPRINT', 0)
    opt(optProb,sens_type='FD',ball=ball,func=f)
    
    #the point
    p=sp.array([optProb._solutions[0].getVar(i).value for i in range(len(c))])
    
    #DBG
    #print("POINT CAUSING MAX VAL:")
    #print(p)

    #if (sum((p-c)**2)<=r**2):
    #    print('-----OK %.10f > %.10f'%(sum((p-c)**2),r**2))
    #else:
    #    print('-----FAIL %.10f > %.10f'%(sum((p-c)**2),r**2))
       
    #print(optProb._solutions[0])
    if sp.isnan(optProb._solutions[0].getObj(0).value):
        return computeExtremesFuncValuesInBall(func, (c,r-tolerance),type, tolerance) #hack to not return nan
    
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

def monFunc10D(x):
    return ((x[0]+x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9]))**2

if __name__=='__main__':
    
    #tolerance
    tolerance=1e-3
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=4
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    
    #===========================================================================
    # #1D test
    # print('--------------1D test-------------------')
    # import scipy as sp
    # computeExtremesFuncValuesInBall(lambda x:x[0], (sp.array([1.0]),1.0),type='max', tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:x[0]**2, (sp.array([0.0]),1.0),type='max',tolerance=tolerance)
    #        
    # #2D test
    # print('--------------2D test-------------------')
    # import scipy as sp
    # computeExtremesFuncValuesInBall(lambda x:x[0]**2-x[1]*2, computeBallFromDiametralPoints(sp.array([0.0,0.0]), sp.array([9.684168,31.001823])),type='max',tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0],1.0),type='max',tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:sum(x), (sp.array([1.0,1.0]),1.0),type='max',tolerance=tolerance)
    #      
    # #3D test
    # print('--------------3D test-------------------')
    # computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:x[2], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    # computeExtremesFuncValuesInBall(lambda x:x[0]+x[1]+x[2], ([1.0,1.0,1.0],2.0),type='max',tolerance=tolerance)
    #      
    # computeExtremesFuncValuesInBall(monFunc5D,
    #                                 computeBallFromDiametralPoints(sp.array([6.0,6.0,6.0,6.0,6.0]),
    #                                                                sp.array([303.463323 ,135.839161,190.179845,323.928338,333.407561])),
    #                                 type='max',
    #                                 tolerance=tolerance)
    # 
    # 
    # computeExtremesFuncValuesInBall(lambda x:x[0],
    #                                 (sp.array([-84.8]),88.2),
    #                                 type='max',
    #                                 tolerance=tolerance)
    # 
    # computeExtremesFuncValuesInBall(monFunc5D,
    #                                 (sp.array([3.7,3.7,3.7,3.7,3.7]),14.53),
    #                                 type='max',
    #                                 tolerance=tolerance)
    # 
    #===========================================================================
    #===========================================================================
    # print(monFunc5D(sp.array([ -6.60378012e+07,  -2.35134034e+08,  -2.34504426e+08,1.72184751e+07,   4.85269403e+07])))
    # computeExtremesFuncValuesInBall(monFunc5D,
    #                                 (sp.array([ -6.60378012e+07,  -2.35134034e+08,  -2.34504426e+08,1.72184751e+07,   4.85269403e+07]), 342480175.7627804),
    #                                 type='max',
    #                                 tolerance=tolerance)
    #===========================================================================
    
    computeExtremesFuncValuesInBall(monFunc10D,
                                    computeBallFromDiametralPoints(
                                                                   sp.zeros(10),
                                                                   sp.array([23.99,6.316,27.25,3.962,19.91,38.04,23.69,12.92,3.360,27.98])),
                                                                    type='max', tolerance=tolerance)
    
    computeExtremesFuncValuesInBall(monFunc10D,
                                    computeBallFromDiametralPoints(
                                                                   sp.zeros(10),
                                                                   sp.array([6.385,5.217,10.49,5.300,4.014,12.38,7.153,5.289,9.161,7.913])),
                                                                    type='max', tolerance=tolerance)
    
    b=sp.array([23.99,6.316,27.25,3.962,19.91,38.04,23.69,12.92,3.360,27.98])+sp.array([6.385,5.217,10.49,5.300,4.014,12.38,7.153,5.289,9.161,7.913])
    b=b/2
    print("!!!! B IS:")
    print(b)
    
    computeExtremesFuncValuesInBall(monFunc10D,
                                    computeBallFromDiametralPoints(
                                                                   sp.zeros(10),
                                                                   b),
                                                                    type='max', tolerance=tolerance)
    