'''
@author: ak
'''
from GM_Exp.DataStream.InputStream import InputStream
from GM_Exp import Config
from scipy.stats import norm


class InputStreamFactory:
    '''
    A factory of InputStream Instances
    '''


    def __init__(self, lambdaVel=Config.lambdaVel,initXData=Config.defInitXData, velMeanNormalDistr=Config.defMeanN, velStdNormalDistr=Config.defStdN, normalize=Config.streamNormalizing):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial InputStream data
              @param velocityMeanNormalDistr: N(μ,σ) of means of velocities, tuple
              @param velocityStdNormalDistr: N(μ,σ) of stds of velocities, tuple
              @param normalize: normalize velocity updates to specified mean, boolean
        '''
        self.lambdaVel=lambdaVel
        self.initXData=initXData
        self.normalize=normalize
        #create distributions
        #each stream has different distr, the mean and std of each follow a central distribution
        #statistical behavior of each stream's velocity is different
        #BUT mean velocity for each iteration is exactly self.meanN.mean()
        self.meanN=norm(velMeanNormalDistr[0],velMeanNormalDistr[1])
        self.stdN=norm(velStdNormalDistr[0],velStdNormalDistr[1])
        
        self.inputStreams=[] #array of InputStreams created
                                    
    def getInputStream(self):
        '''
        InputStream generator
        @return an InputStream instance
        '''
        while True:
            newStream=InputStream(lambdaVel=self.lambdaVel,initXData=self.initXData,mean=self.meanN.rvs(),std=self.stdN.rvs(),normalize=self.normalize,factory=self)
            self.inputStreams.append(newStream)
            
            #DBG
            #print('stream at generator function:')
            #print(newStream)
            
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
        # DBG
        # print(self.velocities)
        if len(self.velocities) == len(self.inputStreams):
            # DBG
            # print('!!!!normalizing!!!')
            deltaV = self.meanN.mean() - (sum(self.velocities) / float(len(self.velocities)))
            # DBG
            # print("--deltaV:%f"%deltaV)
            for stream in self.inputStreams:
                stream.correctVelocity(deltaV)
            del self.velocities[:]
    
   
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    '''
    factory=InputStreamFactory(0.5,mean=3,std=1)
    streamFetcher=factory.getInputStream()
    print(factory)
    print(streamFetcher)
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
    '''
    factory=InputStreamFactory(0.5,mean=3,std=1)
    streamFetcher=factory.getInputStream()
    print(factory)
    print(streamFetcher)
    l=[]
    l.append(streamFetcher.next().getData())
    print(l)
    print(l[0].next())
    print(l[0].next())
    print(l[0].next())
    l.append(streamFetcher.next().getData())
    print(l)
    for s in l:
        print(s)
        print("data is: %f"%s.next())
