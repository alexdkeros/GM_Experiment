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

    def __init__(self,lambdaVel ,initXData, mean, std, factory=None):
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
        self.mean=mean
        self.std=std
        self.velocity=0
        self.factory=factory
    
    def getVelocity(self):
        '''
        @return InputStream's velocity
        '''
        return self.velocity
    
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
        xData=self.initXData
        self.velocity=norm.rvs(self.mean, self.std)
        if self.factory:
            self.factory.normalizeVelocities(self.velocity)
        yield xData
        while 1:
            xData=xData+self.velocity
            self.velocity=self.lambdaVel*self.velocity+(1-self.lambdaVel)*norm.rvs(self.mean,self.std)
            if self.factory:
                self.factory.normalizeVelocities(self.velocity)
            yield xData
        
                        
                
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------          
                
if __name__=="__main__":
    '''simple test'''

    streamInst=InputStream(0.5,0,5,1,1)
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