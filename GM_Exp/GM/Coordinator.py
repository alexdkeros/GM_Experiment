'''
@author: ak
'''
from GM_Exp import Config
from GM_Exp.GM.Node import Node


class Coordinator(Node):
    '''
    classdocs
    '''


    def __init__(self,env,nodes, id="Coord",threshold=Config.threshold,monitoringFunction=Config.defMonFunc ):
        '''
        Constructor
        '''
        Node.__init__(self, env, id, threshold, monitoringFunction)
        self.nodes=nodes    #dictionary {"id":weight,}
        self.balancingSet=set()
        self.sumW=sum(nodes.values())
        
    '''
    messages methods:
    incoming: methodName(self,data,sender) format
    '''
    def init(self,dat,sender):
            self.balancingSet.add(sender)
            w=dat[1]
            v=dat[0]
            self.e+=(w*v)/self.sumW
            if len(self.balancingSet)==len(self.nodes):
                self.balancingSet.clear()
                self.newEst()
    
    def rep(self,dat, sender):
        #TODO
        pass
    
    '''
    messages methods:
    outgoing: methodName(self) format
    '''
    def newEst(self):
        self.env.send(self.nodes.keys(),"newEst",self.e)
        
    def req(self,nodeId):
        self.env.send(nodeId,"req",None)
        
    def adjSlk(self,nodeId,dat):   
        self.env.send(nodeId,"adjSlk",dat)
    
         
        
        
        
