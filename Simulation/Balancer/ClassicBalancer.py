'''
@author: ak
'''
from Simulation.Utilities.ArrayOperations import hashable

def classicBalancer(coordInstance,balSet, b, threshold, monFunc, nodeWeightDict,tolerance=None):
    '''
    Classic balancing function, as in the original Geometric Monitoring Method
    args:
        @param coordInstance: to successfully setattr in Coordinator
        @param balSet: balancing set containing (nodeId, v, u, vel) tuples
        @param b: balancing vector
        @param threshold: the monitoring threshold
        @param monFunc: the monitoring function
        @param nodeWeightDict: dictionary containing {id: w, }
    @return {id: dDelta} dictionary
    '''
    return {nid:(nodeWeightDict[nid]*b-nodeWeightDict[nid]*u.unwrap()) for (nid,v,u,vel) in balSet}
    
    
#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    
    #decimals
    import scipy as sp
    from Simulation.Utilities.Dec import *
    
    bSet=set([
              ('n1', hashable(dec(sp.array([400]))), hashable(dec(sp.array([400,1]))), dec(0)),
              ('n2', hashable(dec(sp.array([400]))), hashable(dec(sp.array([450.70,450.71]))), dec(0)),
               ('n3', hashable(dec(sp.array([400]))), hashable(dec(sp.array([-1.70,-1000]))), dec(0))])
    b=dec(sp.array([0,0]))
    threshold=10
    monFunc=lambda x:x**2
    nodeWeightDict={'n1':dec(1), 'n2':dec(1), 'n3':dec(1)}
    
    res=classicBalancer(bSet, b, threshold, monFunc, nodeWeightDict)
    print(res)