'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import scipy as sp
from scipy import linalg

def computeBallFromDiametralPoints(p1,p2):
    '''
    computes a ball given two diametric points
    args:
        @param p1: point vector
        @param p2: point vector
    @return (center point vector,radius)
    '''
    d=(p1-p2)/2.0
    center=p2+d
    radius=linalg.norm(d)
    
    return (center,radius)

def computeExtremesFuncValuesInBall(func,ball,type='both'):
    '''
    compute the extremes (min, max) of f(ball)
    args:
        @param func: the function
        @param ball: B(center, radius) tuple defining ball, 
                center an sp.ndarray with ndim==1, len==dimentionallity of vector
    @return type=='max': func_max
            type=='min': func_min
            type=='both':(func_min, func_max) tuple
    '''
    
    #bounding sphere constraint
    c,r=ball
    inb=lambda x,c,r: sum((x[i]-c[i])**2 for i in range(len(c)))<=r**2 if (isinstance(c,list or sp.array) and len(c)>1) else (x-c)**2<=r**2 #constraint (messy statement because we get complaints by openopt)

    #openopt specific vars
    p=oovar('p')    #oovar
    f=(func(p))('f')   #oofunc
    s=oosystem(f)
    
    #constraint
    s&=inb(p,c,r)
    #starting point
    sP={p:sp.array(c)}
    
    if type=='max':
        res=s.maximize(f,sP)
        return f(res)
    elif type=='min':
        res=s.minimize(f,sP)
        return f(res)
    elif type=='both':
        #results
        resMin=s.minimize(f,sP)
        #DBG
        #print(resMin.xf)
        
        resMax=s.maximize(f,sP)
        #DBG
        #print(resMax.xf)
        
        return f(resMin),f(resMax)


#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------

def monFunc(x):
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return sum(x)
    
    
if __name__=='__main__':
    '''
    #1D test
    print('--------------1D test-------------------')
    computeExtremesFuncValuesInBall(lambda x:x, (1.0,1.0))
    computeExtremesFuncValuesInBall(lambda x:x**2, (1.0,1.0))
    
    #2D test
    print('--------------2D test-------------------')
    import scipy as sp
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0],1.0))
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0],1.0))
    computeExtremesFuncValuesInBall(lambda x:sum(x), (sp.array([1.0,1.0]),1.0))
    
    #3D test
    print('--------------3D test-------------------')
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0,1.0],2.0))
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0,1.0],2.0))
    computeExtremesFuncValuesInBall(lambda x:x[2], ([1.0,1.0,1.0],2.0))
    computeExtremesFuncValuesInBall(lambda x:x[0]+x[1]+x[2], ([1.0,1.0,1.0],2.0))
    '''
    computeExtremesFuncValuesInBall(monFunc, (sp.array([1.0,1.0]),1.0))
    