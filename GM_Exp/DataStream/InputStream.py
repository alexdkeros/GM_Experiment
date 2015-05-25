'''
@author: ak
'''
from scipy.stats import norm

from GM_Exp.Utils.Utils import dec, deDec
import numpy as np


class InputStream:
    '''
    class InputStream
    models a continuous input stream of data having velocities sampled from a normal distribution
    implements a generator of data
    configuration via Config module
    '''

    def __init__(self,lambdaVel=1, initXData=0, mean=None, std=None, velocitiesDataSet=None, updatesDataSet=None):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial stream data
              @param mean: mean of normal distribution
              @param std: standard deviation of normal distribution
        '''
            
        if 0<=lambdaVel<=1:
            self.lambdaVel=lambdaVel
        else:
            self.lambdaVel=1
        self.initXData=initXData
        self.velocityDistr=norm(mean,std)
            
        self.velocity=0
        
        #logging velocities and data updates
        self.velocities=[]
        self.dataUpdates=[]
        
        #dataset import
        if velocitiesDataSet and updatesDataSet:
            self.velocityDistr=None
            self.velocities=velocitiesDataSet
            self.dataUpdates=updatesDataSet
            
        #convert all to decimal
        self.lambdaVel=dec(self.lambdaVel)
        self.initXData=dec(self.initXData)
        self.velocity=dec(self.velocity)
        self.velocities=dec(self.velocities)
        self.dataUpdates=dec(self.dataUpdates)
    '''
    --Getter methods
    '''
    def getVelocitiesLog(self):
        '''
        @return: logged velocities
        '''
        return self.velocities
    
    def getDataUpdatesLog(self):
        '''
        @return: logged data Updates
        '''
        return self.dataUpdates
    
    def getVelocity(self):
        '''
        @return InputStream's velocity
        '''
        return self.velocity
    
    def getVelocityDistr(self):
        '''
        @return InputStream's velocity distribution, tuple (mean, std)
        '''
        if not self.velocityDistr:
            return ((np.mean(self.velocities),np.std(self.velocities)))
        else:
            return ((self.velocityDistr.mean(),self.velocityDistr.std()))
    
    '''
    --Other methods
    '''
    
    def correctVelocity(self,deltaV):  
        '''
        applies correction to current velocity
        '''
        self.velocity+=dec(deltaV)
        
    
    '''
    --Main InputStream method
    '''
    def getData(self):
        '''
        data Generator
        @return new data based on velocity scheme
        @raise StopIteration: when DataSet loaded and no more updates in DataSet
        '''
        
        #----------------------------------------------------------------------
        # DataSet loaded
        #----------------------------------------------------------------------
        if self.velocities and self.dataUpdates:
        
            for i in range(len(self.velocities) if len(self.velocities)<=len(self.dataUpdates) else len(self.dataUpdates)):
                self.velocity=self.velocities[i]
                yield self.dataUpdates[i]
        
        #----------------------------------------------------------------------
        # no DataSet, producing updates
        #----------------------------------------------------------------------
        else:
            
            #--initial values, stream initialization
            xData=self.initXData
            self.velocity=dec(self.velocityDistr.rvs())
            
            yield xData
            
            #LOG
            self.dataUpdates.append(xData)
            
            #--stream update
            while 1:
                xData=xData+self.velocity
                
                #LOG
                self.velocities.append(self.velocity)
                
                self.velocity=self.lambdaVel*self.velocity+(dec(1)-self.lambdaVel)*dec(self.velocityDistr.rvs())

                yield xData
                
                #LOG
                self.dataUpdates.append(xData)
                        
                
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------          
                
if __name__=="__main__":
    
    #NO DATASET test - OK
    '''
    l=0
    xInit=0
    mean=2.0
    std=1.0
    ist=InputStream(lambdaVel=l, initXData=xInit, mean=mean, std=std)
    st=ist.getData()
    print(ist)
    print(st)
    
    for i in range(20):
        print("velocity:"+str(ist.getVelocity()))
        #ist.correctVelocity(mean-ist.getVelocity())
        print("update:"+str(st.next()))
    
    print(ist.getVelocityDistr())
    print("velocities:")
    print(len(ist.getVelocitiesLog()))
    print(ist.getVelocitiesLog())
    print(np.mean(ist.getVelocitiesLog()))
    print(np.std(ist.getVelocitiesLog()))
    print("updates:")
    print(len(ist.getDataUpdatesLog()))
    print(ist.getDataUpdatesLog())
    '''
    #DATASET test - OK
    '''
    vels=[3,2,4,2,3,2,5,6,4,3,2,2,3,5,4,3,2]
    ups=[1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5]
    print(len(vels))
    print(len(ups))
    ist=InputStream(velocitiesDataSet=vels, updatesDataSet=ups)
    st=ist.getData()
    print(ist)
    print(st)
    
    for i in range(20):
        try:
            print("velocity:"+str(ist.getVelocity()))
            #ist.correctVelocity(mean-ist.getVelocity())
            print("update:"+str(st.next()))
        except StopIteration:
            print("NO MORE")
            
    print(ist.getVelocityDistr())
    print("velocities:")
    print(ist.getVelocitiesLog())
    print(np.mean(ist.getVelocitiesLog()))
    print(np.std(ist.getVelocitiesLog()))
    print("updates:")
    print(ist.getDataUpdatesLog())
    '''
    
    
    