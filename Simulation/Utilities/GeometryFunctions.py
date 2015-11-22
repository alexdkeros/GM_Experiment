'''
@author: ak
'''
import pickle
import time
import math
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
    print(p1)
    print(p2)
    
    d=(p1-p2)/(dec(2.0) if (all(isinstance(i,Decimal) for i in p1) and all(isinstance(i,Decimal) for i in p2)) else 2.0)
    center=p2+d
    radius=linalg.norm(d)
    
    return (center,radius)

def computeExtremesFuncValuesInBall(func,ball,type='both',residual=0.0,tolerance=1e-7):
    '''
    compute the extremes (min, max) of f(ball)
    !NO DECIMALS!
    args:
        @param func: the function
        @param ball: B(center, radius) tuple defining ball, 
                center an sp.ndarray with ndim==1, len==dimentionallity of vector
        @param residual: residual for correct value convergence (i.e. not violating constraint)
        @param tolerance: error tolerance
    @return type=='max': func_max
            type=='min': func_min
            type=='both':(func_min, func_max) tuple
    '''
    #DBG
    print('--------------Ext Val COMPUTATION-------------')
    
    #bounding sphere constraint
    c,r=ball
    
    #check function
    inb=lambda x,c,r: math.fsum((dec(x)-dec(c))**2)<=dec(r)**2 #constraint (messy statement because we get complaints by openopt: sum((x[i]-c[i])**2 for i in range(len(c)))<=r**2 if (isinstance(c,list) or isinstance(c,sp.ndarray) and len(c)>1) else ...)

    #openopt specific vars
    p=oovar('p')   #oovar
    f=(func(p))   #oofunc
    s=oosystem(f)
    
    #constraint
    s&=(sum((p-c)**2)<=r**2)('inball',tol=-residual)
    #starting point
    sP={p:sp.array(c)+tolerance}
    #result
    res=None
    try:
        if type=='max':
            res=s.maximize(f,sP)
            
            point=res(p)
            
            currentResidual=(math.fsum((point-c)**2)-r**2)#+(res.rf if (math.fsum((point-c)**2)-r**2)==0.0 else 0.0)

            #DBG
            print(ball)
            print(point)
            print('residual:%.20f'%currentResidual)
            print('algo residual:%.20f'%res.rf)
            print('In ball:%s'%inb(point,c,r))
            print('condition:%s (True means mismatch)'%(not inb(point,c,r) and currentResidual>0.0))
            
            if not inb(point,c,r):# and currentResidual>0.0:
                
                #DBG
                print('*MISMATCH VALUES:')
                print(math.fsum((point-c)**2))
                print('must be <=')
                print(r**2)
                print(inb(point,c,r))
                
                print('current residual:%.10f'%currentResidual)
            else:
                
                #DBG
                print('SUCCESS')
                print('%.20f'%math.fsum((point-c)**2))
                print('must be <=')
                print('%.20f'%r**2)
                print(inb(point,c,r))
                
                return f(res)
        elif type=='min':
            res=s.minimize(f,sP) #,tol=0.0,ftol=0.0,xtol=0.0
            
            point=res(p)
            
            currentResidual=(math.fsum((point-c)**2)-r**2)#+(res.rf if (math.fsum((point-c)**2)-r**2)==0.0 else 0.0)

            if not inb(point,c,r) or currentResidual>0.0:
                assert currentResidual<tolerance
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

        return computeExtremesFuncValuesInBall(func, ball, type=type, residual=currentResidual,tolerance=tolerance)
    
    except:
        print 'Error:', sys.exc_info()[0]
        di={'Error':str(sys.exc_info()[0]),
            'ball':ball,
            'residual':residual,
            'currentResidual':currentResidual,
            'tol':tolerance}
        
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
    
def monFunc1D(x):
    
    if (isinstance(x,sp.ndarray) and len(x)==1):
        return x[0]
    else:
        return x
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
    #tolerance
    tolerance=1e-3
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=4
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    
    monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
    inb=lambda x,c,r: sum((x-c)**2)<=r**2 
    
    
    c,r=(sp.array([ 475.39881759,  475.40572972,  475.40520089,  475.40929382,
         475.39886487,  475.40345798,  475.39859597,  475.39966051,
         475.40450612,  475.40586027]), 1438.8456229000603)
    c,r=dec(c),dec(r)
    
    print(computeBallFromDiametralPoints(dec(sp.array([0.0]*10)),c))
          
    res=computeExtremesFuncValuesInBall(monfunc10D,(deDec(c),deDec(r)),'max')
    
    print(res)
    
    ''' 
    ball=computeBallFromDiametralPoints(sp.array([dec(5)]), sp.array([dec(20)]))
    
    res=computeExtremesFuncValuesInBall(monFunc1D,(deDec(ball[0]),deDec(ball[1])),'max', tolerance=tolerance)
    
    print(res)
    '''
    

    