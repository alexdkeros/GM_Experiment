'''
@author: ak
'''
from GM_Exp.DataStream.InputStream import InputStream
from GM_Exp import Config
from scipy.stats import norm
import numpy as np
import pickle
import sys
from GM_Exp.Utils.Plotter import multiplePlots2d


class InputStreamFactory:
    '''
    A factory of InputStream Instances
    '''


    def __init__(self, lambdaVel=Config.lambdaVel,initXData=Config.defInitXData, velMeanNormalDistr=Config.defMeanN, velStdNormalDistr=Config.defStdN, dataSetfile=None):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial InputStream data
              @param velocityMeanNormalDistr: N(mean,std) of means of velocities, tuple
              @param velocityStdNormalDistr: N(mean,std) of stds of velocities, tuple
              @param dataSetFile: file to load dataset from. Must be a pickle file containing dictionary {"iterations": ,"streams": , "velocities":, "updates": } 
              @raise ValueError: std of Mean distribution or Std distribution less or equal to zero
        '''
        
        if velMeanNormalDistr[1]==0 or velStdNormalDistr[1]==0:
            raise ValueError('std must be greater than zero. Can add sys.float_info.min')
        
        self.lambdaVel=lambdaVel
        self.initXData=initXData
        
        #create distributions
        #each stream has different distr, the mean and std of each follow a central distribution
        #statistical behavior of each stream's velocity is different
        #BUT mean velocity for each iteration is exactly self.meanN.mean()
        
        self.meanN=norm(velMeanNormalDistr[0],velMeanNormalDistr[1])
        self.stdN=norm(velStdNormalDistr[0],velStdNormalDistr[1])
        
        self.inputStreams=[] #array of InputStreams created
        self.dataSetFlag=False
        
        if dataSetfile:
            self.loadDataSet(dataSetfile)
                                    
    def getInputStream(self):
        '''
        InputStream generator
        @return an InputStream instance
        @raise StopIteration: if Dataset is loaded and no more streams remaining
        '''
        #------------------------------------------------------------------------
        # DataSet loaded
        #------------------------------------------------------------------------
        if self.dataSetFlag:
            for stream in self.inputStreams:
                yield stream
        
        #------------------------------------------------------------------------
        # no DataSet, create streams
        #------------------------------------------------------------------------
        else:
            
            while True:
                newStream=InputStream(lambdaVel=self.lambdaVel,initXData=self.initXData,mean=self.meanN.rvs(),std=abs(self.stdN.rvs())+sys.float_info.min) #avoid <=0 std
                self.inputStreams.append(newStream)
                yield newStream
    
    def getInputStreams(self):
        '''
        @return: array of created InputStreams
        '''
        return self.inputStreams
    
    def getAvgVelocity(self):
        '''
        computes and returns the average velocity of all created InputStreams
        @return the average velocity of all created InputStreams
        '''
        return np.mean(list(stream.getVelocity() for stream in self.inputStreams))
   
   
    def normalizeVelocities(self):
        '''
        normalizes true mean velocity of all created InputStreams to the specified mean
        '''
        deltaV = self.meanN.mean() - self.getAvgVelocity()
        for stream in self.inputStreams:
            stream.correctVelocity(deltaV)
            
            
    def getVelocityLogs(self):
        '''
        @return: array of velocities of each stream
        '''
        velocitiesLogs=[]
        for stream in self.inputStreams:
            velocitiesLogs.append(stream.getVelocitiesLog())
        return velocitiesLogs
    
    def getDataUpdateLogs(self):
        '''
        @return: array of updates of each stream
        '''
        dataUpdateLogs=[]
        for stream in self.inputStreams:
            dataUpdateLogs.append(stream.getDataUpdatesLog())
        return dataUpdateLogs
    
    
    def generateDataSet(self, iterations, streamsNum, normalize=False, filename=None):
        '''
        creates synthetic Dataset
        @param iterations: number of iterations for simulation to run
        @param streams: number of streams
        @param normalize: mean steam velocities to specified mean
        @param filename: filename to save DataSet
        @return: created Dataset
        '''
        streamFetcher=self.getInputStream()
        #creating Streams
        streams=[]
        for i in range(streamsNum):
            streams.append(streamFetcher.next().getData())
        
        #creating data
        for i in range(iterations+1):
            if normalize:
                self.normalizeVelocities()
            for stream in streams:
                stream.next()
        
        dataset={"iterations":iterations, "streams":len(streams),"velocities":self.getVelocityLogs(),"updates":self.getDataUpdateLogs()}
        if filename:
            pickle.dump(dataset, open(filename+".p","wb"))
        return dataset
    
        
    def loadDataSet(self,dataSetfile):
        '''
        load created dataset
        '''
        dataSet=pickle.load(open(dataSetfile,"rb"))
        for i in range(dataSet["streams"]):
            self.inputStreams.append(InputStream(velocitiesDataSet=dataSet["velocities"][i], updatesDataSet=dataSet["updates"][i]))
        self.dataSetFlag=True
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #stream fetching test - OK
    '''
    l=0
    initX=0
    velMeanDist=(5,1+sys.float_info.min)
    velStdDist=(0,1+sys.float_info.min)
    factory=InputStreamFactory(lambdaVel=l, initXData=initX, velMeanNormalDistr=velMeanDist, velStdNormalDistr=velStdDist)
    fetcher=factory.getInputStream()
    print(factory)
    print(fetcher)
    for i in range(2):
        fetcher.next()
    streams=factory.getInputStreams()
    for stream in streams:
        print(stream)
        print(stream.getVelocityDistr())
        st=stream.getData()
        for i in range(10):
            print("Data:%f"%st.next())
            print("Velocity:%f"%stream.getVelocity())
    '''
    
    #dataset generating test - vals seem OK
    l=0
    initX=0
    velMeanDist=(5,5+sys.float_info.min)
    velStdDist=(10,10+sys.float_info.min)
    factory=InputStreamFactory(lambdaVel=l, initXData=initX, velMeanNormalDistr=velMeanDist, velStdNormalDistr=velStdDist)
    ds=factory.generateDataSet(50, 2, normalize=False)
    v0=ds['velocities'][0]
    v1=ds['velocities'][1]
    
    print(np.mean(v0))
    print(np.std(v0))
    print(v0)

    print(np.mean(v1))
    print(np.std(v1))
    print(v1)
    
    m=[]
    for i in range(len(v0)):
        print np.mean([v0[i],v1[i]])
        m.append(np.mean([v0[i],v1[i]]))
    print("mean of means is:%f"%np.mean(m))

    from GM_Exp.Utils import Plotter
    ranges=[np.arange(1,51),np.arange(1,51)]
    multiplePlots2d(ranges,[v0,v1],['one','two'],title="vels")
    multiplePlots2d(ranges, ds['updates'], ['one','two'],title='updates')
    




