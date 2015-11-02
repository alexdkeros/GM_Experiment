'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import scipy as sp
from Simulation.Utilities.ArrayOperations import hashable,weightedAverage
from Simulation.Utilities.Dec import *

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
    bS=list( (id,deDec(v.unwrap()),deDec(u.unwrap()),deDec(fvel)) for (id,v,u,fvel) in balSet )
    
    #DBG
    print('balancing set:%s'%bS)
    
    x=oovars([nid for nid,v,u,vel in bS],tol=0.0)   #oovars
    
    f=[]    #oofuns
    
    startPoint={}
    
    constraints=[]
    
    for i in range(len(bS)):
        #func
        f.append(__optFunc(x[i],bS[i],deDec(appliedThreshold),monFunc))
        
        #point
        startPoint[x[i]]=deDec(b)
    
        #constraints
        constraints.append(monFunc(x[i])<deDec(appliedThreshold))
        constraints.append(__optFunc(x[i],bS[i],deDec(appliedThreshold),monFunc)>=0)

    constraints.append(weightedAverage(x,[deDec(nodeWeightDict[x_i.name]) for x_i in x])==deDec(b))
    
    #min
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    #maxmin
    p=NLP(objective,startPoint,constraints=constraints,tol=0.0,ftol=0.0,xtol=0.0)
    
    r=p.maximize('ralg',plot=False)

    resDict={x_i.name:dec(r(x_i)) for x_i in x} #optimal point dictionary
    
    print('Result Points:%s'%resDict)
    print(appliedThreshold)
    print(r.rf)
    
    #repeat in case of threshold violation
    if any([i>=threshold for i in resDict.values()]) and r.rf:
        heuristicBalancer(coordInstance, balSet, b, threshold, monFunc, nodeWeightDict, residual=residual+r.rf)
    
    
    
    return {nid:(nodeWeightDict[nid]*resDict[nid]-nodeWeightDict[nid]*u.unwrap()) for nid,v,u,fvel in balSet} #(w_i*result_i-w_i*u_i), i in balancingSet
    
       
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
    
    #decimals
    import scipy as sp
    from Simulation.Utilities.Dec import *
    
    #1D test
    bSet=set([
              ('n1', hashable(dec(sp.array([21]))), hashable(dec(sp.array([21]))), 5),
              ('n2', hashable(dec(sp.array([12]))), hashable(dec(sp.array([12]))), 3)])
    b=dec(sp.array([16.5]))
    threshold=dec(20.0)
    monFunc=lambda x:x
    nodeWeightDict={'n1':dec(1.0), 'n2':dec(1.0), 'n3':dec(1.0)}
    
    
    res=heuristicBalancer(None,bSet, b, threshold, monFunc, nodeWeightDict)
    print('--------------collected data--------------')
    print('Balancing set: %s'%bSet)
    print('Balancing vector: %s'%b)
    print('threshold: %s'%threshold)
    print('node weights:%s'%nodeWeightDict)
    print('Ddeltas:%s'%res)
