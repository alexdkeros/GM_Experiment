'''
@author: ak
'''
from scipy.stats import norm





class InputStream:
    '''
    class InputStream
    models a continuous input stream of data having velocities sampled from a normal distribution
    implements a generator of data
    configuration via Config module
    '''

    def __init__(self,lambdaVel=1, initXData=0, mean=5, std=1, normalize=True,  factory=None, velocitiesDataSet=None, updatesDataSet=None):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial stream data
              @param mean: mean of normal distribution
              @param std: standard deviation of normal distribution
              @param normalize: flag to allow velocity normalizing to mean
              @param factory: the factory it came from
        '''
            
        if 0<=lambdaVel<=1:
            self.lambdaVel=lambdaVel
        else:
            self.lambdaVel=1
        self.initXData=initXData
        self.velocityDistr=norm(mean,std)
        self.velocity=0
        self.normalize=normalize
        self.factory=factory
        
        #logging velocities and data updates
        self.velocities=[]
        self.dataUpdates=[]
        
        if velocitiesDataSet and updatesDataSet:
            self.velocities=velocitiesDataSet
            self.dataUpdates=updatesDataSet
            
        
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
        return ((self.mean,self.std))
    
    def correctVelocity(self,deltaV):  
        '''
        applies correction to current velocity
        '''
        self.velocity+=deltaV
    
    def getData(self):
        '''
        data Generator
        @return new data based on velocity scheme
        '''
        if self.velocities and self.dataUpdates:
            for i in range(self.velocities):
                self.velocity=self.velocities[i]
                yield self.dataUpdates[i]
        
        else:
                
            #initial values, stream initialization
            xData=self.initXData
            self.velocity=self.velocityDistr.rvs()
            if self.factory and self.normalize==True:
                self.factory.normalizeVelocities(self.velocity)
            yield xData
            #LOG
            self.dataUpdates.append(xData)
            
            #stream update
            while 1:
                xData=xData+self.velocity
                #LOG
                self.velocities.append(self.velocity)
                
                self.velocity=self.lambdaVel*self.velocity+(1-self.lambdaVel)*self.velocityDistr.rvs()
                if self.factory and self.normalize==True:
                    self.factory.normalizeVelocities(self.velocity)
                
                yield xData
                #LOG
                self.dataUpdates.append(xData)
                        
                
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------          
                
if __name__=="__main__":
    '''simple test'''

    streamInst=InputStream(0.5,0,5,1,1).getData()
    for i in range(10):
        print streamInst.next()
    '''
    print('getattr test:')
    print(getattr(streamInst, "getData"))
    print('-----------------------------------')
    stream=streamInst.getData()
    print(stream)
    stream2=getattr(streamInst, "getData()")
    print(stream2)
    for i in range(10):
        print('-------------------------')
        print('stream data:')
        print(stream.next())
        print('stream velocity:')
        print(streamInst.getVelocity())
    '''