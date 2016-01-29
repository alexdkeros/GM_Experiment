'''
@author: ak
'''

import sys
import pickle
import time
import decimal
import scipy as sp
from scipy import linalg
from Simulation.Utilities.Dec import *
from Simulation.Utilities.ArrayOperations import hashable,weightedAverage
import pandas as pd
from pyOpt import Optimization
from Simulation.Utilities.GeometryFunctions import *
from pyOpt.pySLSQP.pySLSQP import SLSQP



def __objfunc(x,**kwargs):
    '''
    optimization function
    estimate time until next local violation
    args:
        @param var: oovar
        @param (nid,v,u,fvel): balancing set element containing (nodeId, update, drift, velocity of f(drift))
        @param threshold: monitoring threshold
        @param monFunc: the monitoring function
    @return estimated time until next local violation, computed as 
            (T-f(var))
            ----------
            vel(f(u))
    '''
    keys=x.keys()
    
    z=x['z']
    keys.remove('z')
    
    bS=kwargs['balSet']
    b=kwargs['b']
    e=kwargs['e']
    threshold=kwargs['threshold']
    fu=kwargs['func']
    nwd=kwargs['nodeWeightDict']
    tolerance=kwargs['tolerance']
    
    #optimizing func
    f=-z #maximize

    #constraints
    g=[]
    #mean cond
    for dim in range(len(b)):
        g.append((sum([nwd[nid]*x[nid][dim] for nid in keys])/len(keys))-b[dim])
    #min conds
    for (nid,v,u,fvel) in bS:
        g.append(z-__optFunc(x[nid][0:len(b)],(nid,v,u,fvel),threshold,fu,tolerance))
    #max val in balls conds
    for (nid,v,u,fvel) in bS:
        g.append(computeExtremesFuncValuesInBall(fu,
                                                 computeBallFromDiametralPoints(e, x[nid][0:len(b)]), 
                                                 type='max',
                                                 tolerance=tolerance)-threshold)
     
    fail=0
    
    return f,g,fail
    
    
def __optFunc(var,(nid,v,u,fvel),threshold,monFunc,tolerance):
    '''
    optimization function
    estimate time until next local violation
    args:
        @param var: oovar
        @param (nid,v,u,fvel): balancing set element containing (nodeId, update, drift, velocity of f(drift))
        @param threshold: monitoring threshold
        @param monFunc: the monitoring function
    @return estimated time until next local violation, computed as 
            (T-f(var))
            ----------
            vel(f(u))
    '''
    return (threshold-monFunc(var))/(fvel if fvel!=0.0 else tolerance)  

 
    
def heuristicBalancer(coordInstance, balSet, b, threshold, monFunc, nodeWeightDict,tolerance=1e-7):
    '''
    Heuristic balancing function maximizing the expected time until next violation
    args:
        @param coordInstance: to successfully setattr in Coordinator
        @param balSet: balancing set containing (nodeId, v, u, fvel) tuples
        @param b: balancing vector
        @param threshold: the monitoring threshold
        @param monFunc: the monitoring function
        @param nodeWeightDict: dictionary containing {id: w, }
        @param residual: residual for correct value convergence (i.e. not violating constraint)
        @param tolerance: error tolerance
    @return {id: dDelta} dictionary
    
    NOTE: PAY ATTENTION TO DECIMALS, pyOpt and sp.average() do not accept them!
    '''
    print('#######in heuristic ffunc##############')
    print(balSet)
    print(b)
    
    #optimization instance
    optProb=Optimization('optimal_points', __objfunc, use_groups=True)
    
    #variables
    optProb.addVar('z',type='c',lower=0.0)
    
    
    for (nid,v,u,fvel) in balSet:
        optProb.addVarGroup(nid,
                            (2 if len(b)<=1 else len(b)),   #add dummy variable in 1D case in order to handle sp.arrays
                            type='c',
                            value=(b if len(b)>1 else list(b)+[0.0]),
                            upper=[1.00e+21]*len(b)+([] if len(b)>1 else [0.1]),
                            lower=[-1.00e+21]*len(b)+([] if len(b)>1 else [0]))
    
    #objective function
    optProb.addObj('helper function')
    
    #constraints
    optProb.addConGroup('mean_cond',len(b),type='e')
    optProb.addConGroup('min_conds',len(balSet), type='i')
    optProb.addConGroup('max_val_in_balls_conds', len(balSet), type='i',upper=0.0)

    print(optProb)
    
    opt=SLSQP()

    #solver options
    opt.setOption('ACC', tolerance)
    opt.setOption('MAXIT', 100)

                                                #!!!must add coordInstance.e here
    opt(optProb,sens_type='FD',
        balSet=balSet,
        b=b,
        e=sp.zeros(1), #coordInstance.getEst(),
        threshold=threshold,
        func=monFunc,
        nodeWeightDict=nodeWeightDict,
        tolerance=tolerance)
    
    points={}
    for i in optProb.getVarGroups():
        if any([nid==optProb.getVarGroups()[i]['name'] for (nid,v,u,fvel) in balSet]):
            respectiveIds=optProb.getVarGroups()[i]['ids'].values()
            respectiveIds.sort()
            points[optProb.getVarGroups()[i]['name']]=sp.array([optProb._solutions[0].getVar(j).value for j in respectiveIds[0:len(b)]]) 
            
    print(optProb._solutions[0]) 
    return {nid:(nodeWeightDict[nid]*points[nid]-nodeWeightDict[nid]*u) for (nid,v,u,vel) in balSet}

#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------


if __name__=='__main__':
    
    #===========================================================================
    # #1D test
    # bSet=set([
    #           ('n1', hashable(dec(sp.array([21]))), hashable(dec(sp.array([21]))), -5),
    #           ('n2', hashable(dec(sp.array([12]))), hashable(dec(sp.array([12]))), 3),
    #           ('n3', hashable(dec(sp.array([16.5]))), hashable(dec(sp.array([16.5]))),10)])
    # b=dec(sp.array([16.5]))
    # threshold=dec(20.0)
    # monFunc=lambda x:x
    # nodeWeightDict={'n1':dec(1.0), 'n2':dec(1.0), 'n3':dec(1.0)}
    # 
    # 
    # res=heuristicBalancer(None,bSet, b, threshold, monFunc, nodeWeightDict)
    # print('--------------collected data--------------')
    # print('Balancing set: %s'%bSet)
    # print('Balancing vector: %s'%b)
    # print('threshold: %s'%threshold)
    # print('node weights:%s'%nodeWeightDict)
    # print('Ddeltas:%s'%res)
    #===========================================================================
    #1D test
    c=decimal.getcontext()
    c.prec=4
    tolerance=1e-3
    #===========================================================================
    # bSet=[
    #           ('n1',sp.array([21]), sp.array([21]), 1),
    #           ('n2', sp.array([12]), sp.array([12]), 3),
    #           ('n3', sp.array([16.5]), sp.array([16.5]),20)]
    # b=sp.array([16.5])
    # threshold=20.0
    # monFunc=lambda x:x[0]
    # nodeWeightDict={'n1':1.0, 'n2':1.0, 'n3':1.0}
    #    
    #    
    # res=heuristicBalancer(None,bSet, b, threshold, monFunc, nodeWeightDict,tolerance=tolerance)
    # print('--------------collected data--------------')
    # print('Balancing set: %s'%bSet)
    # print('Balancing vector: %s'%b)
    # print('threshold: %s'%threshold)
    # print('node weights:%s'%nodeWeightDict)
    # print('Ddeltas:%s'%res)
    #===========================================================================
    #===========================================================================
    # 
    # #2D test
    # 
    # c=decimal.getcontext()
    # c.prec=4
    # tolerance=1e-3
    # 
    # bSet=set([
    #           ('n1', hashable(dec(sp.array([21,21]))), hashable(dec(sp.array([21,21]))), -5),
    #           ('n2', hashable(dec(sp.array([12,12]))), hashable(dec(sp.array([12,12]))), 3)])
    # b=dec(sp.array([16,15]))
    # threshold=dec(390.0)
    # monFunc=lambda x:x[0]**2-x[1]*2
    # for i in bSet:
    #     print(i[0])
    #     print(monFunc(i[1].unwrap()))
    #  
    # nodeWeightDict={'n1':dec(1.0), 'n2':dec(1.0), 'n3':dec(1.0)}
    #  
    #  
    # res=heuristicBalancer(None,bSet, b, threshold, monFunc, nodeWeightDict)
    # print('--------------collected data--------------')
    # print('Balancing set: %s'%bSet)
    # print('Balancing vector: %s'%b)
    # print('threshold: %s'%threshold)
    # print('node weights:%s'%nodeWeightDict)
    # print('Ddeltas:%s'%res)
    # 
    #===========================================================================
    
         
    #2D test
       
    c=decimal.getcontext()
    c.prec=4
    tolerance=1e-3
       
    bSet=[('n1', sp.array([ 8211.0174]), sp.array([ 3984.]), 8.622), ('n7', sp.array([ 0.0063]), sp.array([ 4000.]), 0.0)]

    b=sp.array([3992.])
    threshold=4*10**3
    monFunc=lambda x:x[0]
    for i in bSet:
        print(i[0])
        print(monFunc(i[1]))
        
    nodeWeightDict={'n1':1.0, 'n2':1.0, 'n7':1.0}
        
        
    res=heuristicBalancer(None,bSet, b, threshold, monFunc, nodeWeightDict,tolerance=tolerance)
    print('--------------collected data--------------')
    print('Balancing set: %s'%bSet)
    print('Balancing vector: %s'%b)
    print('threshold: %s'%threshold)
    print('node weights:%s'%nodeWeightDict)
    print('Ddeltas:%s'%res)
    
#===============================================================================
#     
#     c=decimal.getcontext()
#     c.prec=4
#     tolerance=1e-3
#     
#     d=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/errors.log.p')
#     bs=d['balset']
#     bs=[(i[0],dec(i[1]),dec(i[2]), dec(i[3])) for i in bs]
# 
#     b=d['b']
#     t=d['thresh']
#     nwd={'n'+str(i):dec(1.0) for i in [0,3]}
# 
#     monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
#     
#     print('---------initial checks---------------')    
#     print('f(b)<T:    (should be True)')
#     print(monfunc10D(b)<t)
#     print('el<T and maxballval<T for el in bset: (one must be False)')
#     for i in bs:
#         lm=computeExtremesFuncValuesInBall(monfunc10D, computeBallFromDiametralPoints(sp.zeros(10), deDec(i[2])), 'max')
#         print('*NODE:'+i[0])
#         print(monfunc10D(i[2])<t)
#         print(lm<t)
#     print('ball from points:')
#     (c,r)=computeBallFromDiametralPoints(sp.zeros(10), deDec(b))
#     (c,r)=(sp.array(list(c)),r)
#     ba=(c,r)
#     print(ba)
#     print('max value in ball:')
#     fmax=computeExtremesFuncValuesInBall(monfunc10D,ba,'max')
# 
#     print(fmax)
#     print('FAILED BALANCE CHECK:    (MUST BE TRUE)')
#     print(fmax<t)
#     print('--------------------------------------')
#     res=heuristicBalancer(None, bs, b, t, monfunc10D, nwd)
#     #print(res)
#===============================================================================
#===============================================================================
# 
#     c=decimal.getcontext()
#     c.prec=4
#     tolerance=1e-3
#     
#     d=pd.read_pickle('/home/ak/git/GM_Experiment/test/coordData.p')
#     
#     bset=d[1][1]
# 
#     bs=[tuple(i) for i in bset]
#     print(bs)
#     b=d[1][2]
#     print(b)
#     t=5000
#     print(t)
#     nwd={'n'+str(i):dec(1.0) for i in [0,1]}
# 
#     res=heuristicBalancer(None, bs, b, t, monFunc1D, nwd)
#     print(res)
#===============================================================================