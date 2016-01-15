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
    optProb.addVarGroup('p',(2 if len(c)<=1 else len(c)),type='c')

    optProb.addObj('f')
    optProb.addCon('in_ball','i')
    
    #DBG
    #print(optProb)
    
    opt=SOLVOPT()
    opt.setOption('xtol',tolerance)
    opt.setOption('ftol',tolerance)
    opt(optProb,sens_type='FD',ball=ball,func=f)
    
    p=sp.array([optProb._solutions[0].getVar(i).value for i in range(len(c))])
    
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
      
    
    
    
    
    
    
#===============================================================================
# OLD IMPLEMENTATION
#===============================================================================
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
    @return type==type='max': func_max
            type=='min': func_min
            type=='both':(func_min, func_max) tuple
    '''
    #DBG
    print('--------------Ext Val COMPUTATION-------------')
    print(ball)
    
    
    #bounding sphere constraint
    c,r=ball
    
    if r==0.0:
        if type=='max' or type=='min':
            return func(c)
        else:
            return func(c),func(c)
    
    #check function
    inb=lambda x,c,r: sum((x-c)**2)<=r**2 #constraint (messy statement because we get complaints by openopt: sum((x[i]-c[i])**2 for i in range(len(c)))<=r**2 if (isinstance(c,list) or isinstance(c,sp.ndarray) and len(c)>1) else ...)

    #openopt specific vars
    p=oovar('p')   #oovar
    f=(func(p))   #oofunc
    s=oosystem(f)
    
    #constraint
    s&=(sum((p-c)**2)<=r**2)('inball',tol=-abs(residual))
    #starting point
    sP={p:sp.array(c)+r}
    #result
    res=None
    try:
        if type=='max':
            res=s.maximize(f,sP)
            
            point=res(p)
            
            currentResidual=(sum((point-c)**2)-r**2)#+(res.rf if (math.fsum((point-c)**2)-r**2)==0.0 else 0.0)

            #DBG
            print(ball)
            print(point)
            print(func(point))
            print('residual:%.20f'%currentResidual)
            print('algo residual res.rf:%.20f'%res.rf)
            print('In ball:%s'%inb(point,c,r))
            print('condition:%s (True means mismatch)'%(not inb(point,c,r)))
            
            if not res.isFeasible:
                
                return f(res)
            
            if not inb(point,c,r) and currentResidual>0.0:
                
                #DBG
                print('*MISMATCH VALUES:')
                print(sum((point-c)**2))
                print('must be <=')
                print(r**2)
                print(inb(point,c,r))
                
                print('current residual:%.10f'%currentResidual)
            else:
                
                #DBG
                print('SUCCESS')
                print('%.20f'%sum((point-c)**2))
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
                #raise
                print('NOT IN BALL')
            else:
                return f(resMin),f(resMax)
        
        print('*********************************************************************')
        print('********************************REPEAT*GEOM**************************')
        print('*********************************************************************')

        return computeExtremesFuncValuesInBall(func, ball, type=type, residual=currentResidual,tolerance=tolerance)
    
    except:
        print 'Error:', sys.exc_info()[0]
        di={'Error':str(sys.exc_info()[0]),
            'ball':ball,
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
    
def monFunc5D(x):
    nom=x[0]+x[4]+x[3]
    denom=x[1]+x[2]
    
    return nom**2-denom

if __name__=='__main__':
    
    #1D test
    print('--------------1D test-------------------')
    import scipy as sp
    computeExtremesFuncValuesInBall(lambda x:x, (sp.array([1.0]),1.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:x**2, (sp.array([1.0]),10.0),type='max')
     
    #2D test
    print('--------------2D test-------------------')
    import scipy as sp
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0],1.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0],1.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:sum(x), (sp.array([1.0,1.0]),1.0),type='max')
     
    #3D test
    print('--------------3D test-------------------')
    computeExtremesFuncValuesInBall(lambda x:x[0], ([1.0,1.0,1.0],2.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:x[1], ([1.0,1.0,1.0],2.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:x[2], ([1.0,1.0,1.0],2.0),type='max')
    computeExtremesFuncValuesInBall(lambda x:x[0]+x[1]+x[2], ([1.0,1.0,1.0],2.0),type='max')
    '''
    #tolerance
    tolerance=1e-3
    
    #global decimal context
    context=decimal.getcontext()
    context.prec=4
    context.rounding=getattr(decimal,'ROUND_HALF_EVEN')
    '''
#===============================================================================
#     monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
#     inb=lambda x,c,r: sum((x-c)**2)<=r**2 
#     
#     
#     c,r=(sp.array([ 475.39881759,  475.40572972,  475.40520089,  475.40929382,
#          475.39886487,  475.40345798,  475.39859597,  475.39966051,
#          475.40450612,  475.40586027]), 1438.8456229000603)
#     c,r=dec(c),dec(r)
#     
#     print(computeBallFromDiametralPoints(dec(sp.array([0.0]*10)),c))
#           
#     res=computeExtremesFuncValuesInBall(monfunc10D,(deDec(c),deDec(r)),type='max')
#     
#     print(res)
#     '''
#     d=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/geometryErrorWed Nov 25 01:11:07 2015.log.p')
#     
#     (c,r)=d['ball']
#     
#     res=computeExtremesFuncValuesInBall(monFunc5D,(deDec(c),deDec(r)),type='max')
# 
#     print res
#     ''' 
#     ball=computeBallFromDiametralPoints(sp.array([dec(5)]), sp.array([dec(20)]))
#     
#     res=computeExtremesFuncValuesInBall(monFunc1D,(deDec(ball[0]),deDec(ball[1])),type='max', tolerance=tolerance)
#     
#     print(res)
#     '''
#     
#===============================================================================

    
    
    
     
    
    