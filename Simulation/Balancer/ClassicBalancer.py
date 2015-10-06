'''
@author: ak
'''

def classicBalancer(balSet, b, threshold, monFunc, nodeWeightDict):
    '''
    Classic balancing function, as in the original Geometric Monitoring Method
    args:
        @param balSet: balancing set containing (nodeId, v, u, vel) tuples
        @param b: balancing vector
        @param threshold: the monitoring threshold
        @param monFunc: the monitoring function
        @param nodeWeightDict: dictionary containing {id: w, }
    @return {id: dDelta} dictionary
    '''
    return {nid:(nodeWeightDict[nid]*b-nodeWeightDict[nid]*u) for (nid,v,u,vel) in balSet}
    
    