'''
@author: ak
'''
import pickle
import time
from FuncDesigner import *
from openopt import *
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
    d=(p1-p2)/(dec(2.0) if (isinstance(p2,Decimal) and isinstance(p1,Decimal)) else 2.0)
    center=p2+d
    radius=linalg.norm(d)
    
    return (center,radius)

def computeExtremesFuncValuesInBall(func,ball,type='both',residual=0.0):
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
    
    #check function
    inb=lambda x,c,r: sum((x[i]-c[i])**2 for i in range(len(c)))<=r**2 if (isinstance(c,list) or isinstance(c,sp.ndarray) and len(c)>1) else sum((x-c)**2)<=r**2 #constraint (messy statement because we get complaints by openopt)

    #openopt specific vars
    p=oovar('p',tol=0.0)   #oovar
    f=(func(p))('f')   #oofunc
    s=oosystem(f)
    
    #constraint
    s&=(sum((p[i]-c[i])**2 for i in range(len(c)))<=r**2-residual if (isinstance(c,list) or isinstance(c,sp.ndarray) and len(c)>1) else sum((p-c)**2)<=r**2-residual)('inball',tol=0.0)
    #starting point
    sP={p:sp.array(c)+r}
    try:
        if type=='max':
            res=s.maximize(f,sP,tol=0.0,ftol=0.0,xtol=0.0)
            
            point=res(p)
            if not inb(point,c,r):
                residual=sum((point-c)**2)-r**2
                assert residual<1e-5
            else:
                return f(res)
        elif type=='min':
            res=s.minimize(f,sP,tol=0.0,ftol=0.0,xtol=0.0)
            
            point=res(p)
            if not inb(point,c,r):
                residual=sum((point-c)**2)-r**2
                assert residual<1e-5
            else:
                return f(res)
            
        elif type=='both':
            #results
            resMin=s.minimize(f,sP,tol=0.0,ftol=0.0,xtol=0.0)
            #DBG
            print(resMin.xf)
            
            minPoint=resMin(p)
            
            
            resMax=s.maximize(f,sP,tol=0.0,ftol=0.0,xtol=0.0)
            #DBG
            print(resMax.xf)
            
            maxPoint=resMax(p)
            
            if not inb(minPoint,c,r) or not inb(maxPoint,c,r):
                raise
            else:
                return f(resMin),f(resMax)
        
        print('*********************************************************************')
        print('********************************REPEAT*******************************')
        print('*********************************************************************')
        print(ball)
        print(residual)
        return computeExtremesFuncValuesInBall(func, ball, type, residual)
    
    except:
        print "Error:", sys.exc_info()[0]
        di={'Error':str(sys.exc_info()[0]),
            'ball':ball}
        pickle.dump(di,open('/home/ak/git/GM_Experiment/Experiments/geometryError'+time.asctime()+'.log.p','wb'))
        raise

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
    monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
    inb=lambda x,c,r: sum((x-c)**2)<=r**2 
    
    c,r=(sp.array([ 475.39881759,  475.40572972,  475.40520089,  475.40929382,
         475.39886487,  475.40345798,  475.39859597,  475.39966051,
         475.40450612,  475.40586027]), 1438.8456229000603)
    res,p=computeExtremesFuncValuesInBall(monfunc10D,(c,r),'max')
    
    print(res)
    print(inb(p,c,r))
    