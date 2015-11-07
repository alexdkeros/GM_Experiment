'''
@author: ak
'''
import sys
import pickle
import time
from FuncDesigner import *
from openopt import *
import scipy as sp
from scipy import linalg
from Simulation.Utilities.Dec import *
from Simulation.Utilities.ArrayOperations import hashable,weightedAverage
import pandas as pd
from Simulation.Utilities.GeometryFunctions import *

def heuristicBalancer(coordInstance, balSet, b, threshold, monFunc, nodeWeightDict,residual=0.0):
    '''
    Heuristic balancing function maximizing the expected time until next violation
    args:
        @param coordInstance: to successfully setattr in Coordinator
        @param balSet: balancing set containing (nodeId, v, u, fvel) tuples
        @param b: balancing vector
        @param threshold: the monitoring threshold
        @param monFunc: the monitoring function
        @param nodeWeightDict: dictionary containing {id: w, }
    @return {id: dDelta} dictionary
    
    NOTE: PAY ATTENTION TO DECIMALS, openopt and sp.average() do not accept them!
    '''
    if residual:
        appliedThreshold=deDec(threshold)-residual
    else:
        appliedThreshold=threshold
    
    #fix order, unwrap hashable sp.arrays
    bS=list( (id,deDec(v.unwrap() if isinstance(v,hashable) else v),deDec(u.unwrap() if isinstance(u,hashable) else u),deDec(fvel)) for (id,v,u,fvel) in balSet )
    
    #DBG
    #print('balancing set:%s'%bS)
    
    
    x=oovars([nid for nid,v,u,vel in bS],tol=0.0)   #oovars
    
    f=[]    #oofuns
    
    startPoint={}
    
    constraints=[]
    
    for i in range(len(bS)):
        #func
        f.append(__optFunc(x[i],bS[i],deDec(appliedThreshold),monFunc))
        
        #point
        startPoint[x[i]]=deDec(bS[i][1])
    
        #constraints
        constraints.append(monFunc(x[i])<deDec(appliedThreshold))
        constraints.append(__optFunc(x[i],bS[i],deDec(appliedThreshold),monFunc)>=0)

    constraints.append(weightedAverage(x,[deDec(nodeWeightDict[x_i.name]) for x_i in x])==deDec(b))
    
    #min
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    #maxmin
    p=NLP(objective,startPoint,constraints=constraints,tol=0.0,ftol=0.0,xtol=0.0)
    
    try:
        r=p.maximize('ralg',plot=False)
    except:
        print "Error:", sys.exc_info()[0]
        di={'Error':str(sys.exc_info()[0]),
            'balset':bS,
            'b':b,
            'thresh':threshold,
            'residual':residual,
            'nwd':nodeWeightDict}
        pickle.dump(di,open('/home/ak/git/GM_Experiment/Experiments/heuristicError'+time.asctime()+'.log.p','wb'))
        #try again
        #heuristicBalancer(coordInstance, balSet, b, threshold, monFunc, nodeWeightDict, residual=residual)
        raise
        
    resDict={x_i.name:dec(r(x_i)) for x_i in x} #optimal point dictionary
    
    #DBG
    print('Result Points:%s'%resDict)
    print(appliedThreshold)
    print(r.rf)
    print({i:monFunc(resDict[i]) for i in resDict})
    print(weightedAverage(deDec(resDict.values()),[1.0]*len(resDict)))
    
    if not r.isFeasible:
        print('*********************************************************************')
        print('***********************NOT FEASIBLE, SET TO b************************')
        print('*********************************************************************')
        return {nid:(nodeWeightDict[nid]*b-nodeWeightDict[nid]*(u.unwrap() if isinstance(u,hashable) else u)) for nid,v,u,fvel in balSet}
    elif any([monFunc(i)>=threshold for i in resDict.values()]) and r.rf:
        print('*********************************************************************')
        print('********************************REPEAT*******************************')
        print('*********************************************************************')
        return heuristicBalancer(coordInstance, balSet, b, threshold, monFunc, nodeWeightDict, residual=residual+r.rf)
    
    
    return {nid:(nodeWeightDict[nid]*resDict[nid]-nodeWeightDict[nid]*(u.unwrap() if isinstance(u,hashable) else u)) for nid,v,u,fvel in balSet} #(w_i*result_i-w_i*u_i), i in balancingSet
    
       
def __optFunc(var,(nid,v,u,fvel),threshold,monFunc):
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
    return (threshold-monFunc(var))/fvel


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
    
    #===========================================================================
    # #2D test
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
    #===========================================================================

    
    d=pd.read_pickle('/home/ak/git/GM_Experiment/Experiments/errors.log.p')
    bs=d['balset']
    bs=[(i[0],dec(i[1]),dec(i[2]), dec(i[3])) for i in bs]

    b=d['b']
    t=d['thresh']
    nwd={'n'+str(i):dec(1.0) for i in [0,3]}

    monfunc10D=lambda x:((x[0]-x[1]+x[2]-x[3]+x[4]-x[5]+x[6]-x[7]+x[8]-x[9])/10)**2
    
    print('---------initial checks---------------')    
    print('f(b)<T:    (should be True)')
    print(monfunc10D(b)<t)
    print('el<T and maxballval<T for el in bset: (one must be False)')
    for i in bs:
        lm=computeExtremesFuncValuesInBall(monfunc10D, computeBallFromDiametralPoints(0.0, deDec(i[2])), 'max')
        print('*NODE:'+i[0])
        print(monfunc10D(i[2])<t)
        print(lm<t)
    print('ball from points:')
    (c,r)=computeBallFromDiametralPoints(0.0, deDec(b))
    (c,r)=(sp.array(list(c)),r)
    ba=(c,r)
    print(ba)
    print('max value in ball:')
    fmax=computeExtremesFuncValuesInBall(monfunc10D,ba,'max')

    print(fmax)
    print('FAILED BALANCE CHECK:    (MUST BE TRUE)')
    print(fmax<t)
    print('--------------------------------------')
    res=heuristicBalancer(None, bs, b, t, monfunc10D, nwd)
    #print(res)
    