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
        self.nodes=nodes
        self.balancingSet=set()
        
        
