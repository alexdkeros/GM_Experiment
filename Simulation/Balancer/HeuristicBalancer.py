'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import scipy as sp
from Simulation.Utilities.ArrayOperations import hashable

def heuristicBalancer(balSet, b, threshold, monFunc, nodeWeightDict):
    '''
    Heuristic balancing function maximizing the expected time until next violation
    args:
        @param balSet: balancing set containing (nodeId, v, u, fvel) tuples
        @param b: balancing vector
        @param threshold: the monitoring threshold
        @param monFunc: the monitoring function
        @param nodeWeightDict: dictionary containing {id: w, }
    @return {id: dDelta} dictionary
    '''
    #fix order, unwrap hashable sp.arrays
    bS=list( (id,v.unwrap(),u.unwrap(),fvel) for (id,v,u,fvel) in balSet )
    
    x=oovars([nid for nid,v,u,vel in bS])   #oovars
    
    f=[]    #oofuns
    
    startPoint={}
    
    constraints=[]
    
    for i in range(len(bS)):
        #func
        f.append(__optFunc(x[i],bS[i],threshold,monFunc))
        
        #point
        startPoint[x[i]]=b
    
        #constraints
        constraints.append(monFunc(x[i])<threshold)
        constraints.append(__optFunc(x[i],bS[i],threshold,monFunc)>=0)
    #min
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    constraints.append(sp.average(x,weights=[nodeWeightDict[x_i.name] for x_i in x], axis=0)==b)
    
    #maxmin
    p=NLP(objective,startPoint,constraints=constraints)
    
    #FIX wrong bounds
    #p.implicitBounds=[None,threshold]
    r=p.maximize('ralg',plot=False)

    resDict={x_i.name:r(x_i) for x_i in x} #optimal point dictionary
    
    
    return {nid:(nodeWeightDict[nid]*resDict[nid]-nodeWeightDict[nid]*u) for nid,v,u,fvel in bS} #(w_i*result_i-w_i*u_i), i in balancingSet
    
       
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

