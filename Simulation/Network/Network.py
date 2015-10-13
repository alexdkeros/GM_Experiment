'''
@author: ak
'''
from Simulation.Nodes.CoordinatorNode import CoordinatorNode

class Network:
    '''
    Network, handles message passing, logging and simulation instrumentation
    '''
    def __init__(self):
        '''
        constructor
        args:
        '''
        self.nodes={}
        self.coordId=None
        
        self.iterationCount=0
        self.globalViolationFlag=False
        
        self.msgLog={}  #EXP-msg logging
        
        #extract coordId
        self.coordId=None
        
        
    '''
    --------------------------------------------
    other functions
    --------------------------------------------
    '''
    def registerNode(self,node):
        '''
        function used by Monitoring Nodes to register themselves to the network
        args:
            @param node: node instance
        '''
        self.nodes[node.getId()]=node
        if isinstance(node, CoordinatorNode):
            self.coordId=node.getId()
        
    '''
    --------------------------------------------
    getters
    --------------------------------------------
    '''
                
    def getCoordId(self):
        '''
        @return: coordinator id
        '''
        return self.coordId
            
    def getMsgLog(self):
        '''
        @return: message log containing {msgType:[(iteration,sender id, target id, msg, data),...], ...}
        '''
        return self.msgLog
    '''
    --------------------------------------------
    message handling
    --------------------------------------------
    '''
    def signal(self,data): 
        '''
        simulate signal transaction
        @param (sender id, target id, msg, data)
        '''
        #EXP-sniff msg
        self.sniffMsg(data)
        
        #DBG
        print("signal received")
        print("Sender: %s, Target: %s , msg: %s , data: %s, complete msg:%s"%(data[0],data[1],data[2],str(data[3]),str(data)))
        
        if data[1]:
            self.nodes[data[1]].rcv(data)
        
        if data[2]=="globalViolation":
            self.globalViolationFlag=True
            
            
    def sniffMsg(self,data):
        '''
        logs sent messages by type
        args:
            @param data: msg contents
        '''
        #create field
        if not data[2] in self.msgLog:
            self.msgLog[data[2]]=[]
        #add to field, append iteration
        self.msgLog[data[2]].append((self.iterationCount,)+data)
    
    '''
    -------------------------------------------
    simulation
    -------------------------------------------
    '''
    def simulate(self,timeLimit=None):
        '''
        process simulation/instrumentation
        args:
            @param timeLimit(optional): runtime limit
        @return (runtime, iterations)
        '''
        raise NotImplementedError