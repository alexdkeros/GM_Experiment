'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import scipy as sp
from Simulation.Utilities.ArrayOperations import hashable,weightedAverage

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
    
    NOTE: PAY ATTENTION TO DECIMALS, openopt and sp.average() do not accept them!
    '''
    #fix order, unwrap hashable sp.arrays
    bS=list( (id,deDec(v.unwrap()),deDec(u.unwrap()),deDec(fvel)) for (id,v,u,fvel) in balSet )
    
    x=oovars([nid for nid,v,u,vel in bS])   #oovars
    
    f=[]    #oofuns
    
    startPoint={}
    
    constraints=[]
    
    for i in range(len(bS)):
        #func
        f.append(__optFunc(x[i],bS[i],deDec(threshold),monFunc))
        
        #point
        startPoint[x[i]]=deDec(b)
    
        #constraints
        constraints.append(monFunc(x[i])<deDec(threshold))
        constraints.append(__optFunc(x[i],bS[i],deDec(threshold),monFunc)>=0)
    #min
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    constraints.append(weightedAverage(x,[deDec(nodeWeightDict[x_i.name]) for x_i in x])==deDec(b))
    
    #maxmin
    p=NLP(objective,startPoint,constraints=constraints)
    
    r=p.maximize('ralg',plot=False)

    resDict={x_i.name:dec(r(x_i)) for x_i in x} #optimal point dictionary
    
    #DBG
    print(resDict)
    
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
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    
    #decimals
    import scipy as sp
    from Simulation.Utilities.Dec import *
    
    bSet=set([
              ('n1', hashable(dec(sp.array([400]))), hashable(dec(sp.array([11,6]))), 5.5),
              ('n2', hashable(dec(sp.array([400]))), hashable(dec(sp.array([6,11]))), 3)])
    b=dec(sp.array([8.5,2]))
    threshold=20
    monFunc=lambda x:sum(x)
    nodeWeightDict={'n1':dec(1.0), 'n2':dec(1.0), 'n3':dec(1.0)}
    
    
    res=heuristicBalancer(bSet, b, threshold, monFunc, nodeWeightDict)
    print('--------------collected data--------------')
    print(bSet)
    print(b)
    print(threshold)
    print(nodeWeightDict)
    print(res)
