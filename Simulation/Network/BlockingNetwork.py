'''
@author: ak
'''
import time
from Simulation.Network.Network import Network

class BlockingNetwork(Network):
    '''
    Network implementing group node handling
    see Simulation.Network.Network
    '''
    def __init__(self,nodes):
        '''
        constructor
        see Simulation.Network.Network
        args:
            @param nodes: dictionary {id: node_instance, }, node_instance instance of MonitoringNode or CoordinatorNode.
        '''
        Network.__init__(self, nodes)  
    
    
    '''
    -------------------------------------------
    simulation
    -------------------------------------------
    '''
    def simulate(self,timeLimit=None):
        '''
        process simulation/instrumentation, group node handling
        args:
            @param timeLimit(optional): runtime limit
        '''
        
        #=======================================================================
        # initializing simulation
        #=======================================================================
        
        #initialize timer 
        startTime=time.time()
        elapsedT=0
        
        #initialize nodes
        for nId in self.nodes:
            self.signal((None, nId, "init", None))
        
        #make sure coordinator auto-balance is False
        self.nodes[self.coordId].autoBalance=False
            
        #=======================================================================
        # simulation
        #=======================================================================
        
        #simulation
        while (elapsedT<timeLimit if timeLimit else True) and self.globalViolationFlag==False:
            
            #===================================================================
            # iteration start
            #===================================================================
            self.iterationCount+=1
            
            #node updates
            for node in self.nodes:
                node.run()
            
            #node checking
            for node in self.nodes:
                node.check()
            
            #balancing
            self.nodes[self.coordId].balance()
            
            if self.globalViolationFlag==True:
                elapsedT=time.time()-startTime
                break
            
            
            elapsedT=time.time()-startTime
            
            #===================================================================
            # iteration end
            #===================================================================
            
        
        #DBG
        if (elapsedT>=timeLimit if timeLimit else False):
            print("TIMEOUT")
        if self.globalViolationFlag:
            print("GLOBAL VIOLATION")
        
        return (elapsedT,self.iterationCount)  
        