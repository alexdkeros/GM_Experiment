'''
@author: ak
'''
import uuid
from GM_Exp import Config


class Node:
    
    def __init__(self,env, id=uuid.uuid4(),threshold=Config.threshold,monitoringFunction=Config.defMonFunc):
        self.env=env
        self.id=id
        self.threshold=threshold
        self.monitoringFunction=monitoringFunction
        self.v=0    #statistics vector
        self.e=0    #estimate vector
        
    def getId(self):
        return self.id
    
    def getV(self):
        return self.v
    
    def getE(self):
        return self.e
    
    def send(self,target,msg,data):
        if len(target)==len(data):
            for i in range(len(target)):
                self.env.signal((self.id,target[i] , msg, data[i]))
        
    def rcv(self,data):
        if data[1]==self.id:
            getattr(self, data[2])(data[3],sender=data[0])
        
        
