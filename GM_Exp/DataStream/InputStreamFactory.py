'''
@author: ak
'''
from GM_Exp.DataStream.InputStream import InputStream
from GM_Exp import Config

class InputStreamFactory:
    '''
    A factory of InputStream Instances
    '''


    def __init__(self, lambdaVel=Config.lambdaVel,initXData=Config.defInitXData, mean=Config.defMean, std=Config.defStd, interval=Config.defInterval):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial InputStream data
              @param mean: mean of normal distribution
              @param std: standard deviation of normal distribution
              @param interval: update interval in case of changing velocities
        '''
        self.lambdaVel=lambdaVel
        self.initXData=initXData
        self.mean=mean
        self.std=std
        self.interval=interval
        
        self.inputStreams=[] #array of InputStreams created
        self.velocities=[]  #array of InputStream velocities
                                    
    def getInputStream(self):
        '''
        InputStream generator
        @return an InputStream instance
        '''
        while True:
            newStream=InputStream(lambdaVel=self.lambdaVel,initXData=self.initXData,mean=self.mean,std=self.std,interval=self.interval,factory=self)
            self.inputStreams.append(newStream)
            print('stream at generator function:')
            print(newStream)
            yield newStream
    
    
    def getAvgVelocity(self):
        '''
        computes and returns the average velocity of all created InputStreams
        @return the average velocity of all created InputStreams
        '''
        avgV=0
        for stream in self.inputStreams:
            avgV+=stream.getVelocity()
        return avgV/len(self.inputStreams)
    
    def normalizeVelocities(self,vel):
        '''
        normalizes true mean velocity of all created InputStreams to the specified mean
        '''
        self.velocities.append(vel)
        print(self.velocities)
        if len(self.velocities)==len(self.inputStreams):
            print('!!!!normalizing!!!')
            deltaV=self.mean-(sum(self.velocities)/float(len(self.velocities)))
            print("--deltaV:%f"%deltaV)
            for stream in self.inputStreams:
                stream.correctVelocity(deltaV)
            del self.velocities[:]

   
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    factory=InputStreamFactory(0.5,mean=3,std=1)
    streamFetcher=factory.getInputStream()
    print(factory)
    streams=[]
    dataFetchers=[]
    for i in range(10):
        streams.append(streamFetcher.next())
    for stre in streams:
        d=stre.getData()
        print(d)
        dataFetchers.append(d)
    
    for iter in range(10):
        print('-----------iter:%d----------------'%(iter))
        print('avgVel:%f'%factory.getAvgVelocity())
        for i in range(len(streams)):
            print('stream %d, data %f'%(i, dataFetchers[i].next()))
        print('avgVel:%f'%factory.getAvgVelocity())
        