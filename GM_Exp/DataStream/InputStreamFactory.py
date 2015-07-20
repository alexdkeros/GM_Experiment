'''
@author: ak
'''
import pickle
from scipy.stats import norm
import sys

from GM_Exp import Config
from GM_Exp.DataStream.InputStream import InputStream
from GM_Exp.Util.Plotter import multiplePlots2d, plot2d
from GM_Exp.Util.Utils import dec, deDec
import numpy as np


class InputStreamFactory:
    '''
    A factory of InputStream Instances
    '''


    def __init__(self, 
                 lambdaVel=Config.lambdaVel, 
                 initXData=Config.defInitXData, 
                 velMeanNormalDistr=Config.defMeanN, 
                 velStdNormalDistr=Config.defStdN, 
                 dataSetFile=None):
        '''
        Constructor
        args:
              @param lambdaVel: velocity changing factor lambdaVel*u+(1-lambdaVel)u', where u: old velocity, u':new velocity, lambdaVel:[0,1]
              @param initXData: initial InputStream data
              @param velMeanNormalDistr: N(mean,std) of means of velocities, tuple
              @param velStdNormalDistr: N(mean,std) of stds of velocities, tuple
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
        
        if dataSetFile:
            self.loadDataSet(dataSetFile)
        
        #convert to decimal
        self.lambdaVel=dec(self.lambdaVel)
        self.initXData=dec(self.initXData)
                                 
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
    
    def getInputStreamPopulation(self):
        '''
        @return: number of active streams
        '''
        return len(self.inputStreams)
    
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
        deltaV = dec(self.meanN.mean()) - dec(self.getAvgVelocity())
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
        @return: created Dataset, dict {"normalize":,"iterations":, "streams":, "velocities":, "updates":,"lambdaVel":, "meanDistr":, "stdDistr":}
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
        
        dataset={"iterations":iterations, 
                 "streams":len(streams),
                 "velocities":self.getVelocityLogs(),
                 "updates":self.getDataUpdateLogs(),
                 "lambdaVel":self.lambdaVel,
                 "meanDistr":(self.meanN.mean(),self.meanN.std()),
                 "stdDistr":(self.stdN.mean(),self.stdN.std()),
                 "normalizing":normalize}
        if filename:
            pickle.dump(dataset, open(filename+".p","wb"))
        return dataset
    
        
    def loadDataSet(self,dataSetFile):
        '''
        load created dataset
        '''
        if isinstance(dataSetFile,str):
            dataSet=pickle.load(open(dataSetFile,"rb"))
        elif isinstance(dataSetFile,dict):
            dataSet=dataSetFile
        #DBG
        for i in range(dataSet["streams"]):
            self.inputStreams.append(InputStream(velocitiesDataSet=dataSet["velocities"][i], updatesDataSet=dataSet["updates"][i]))
        self.dataSetFlag=True
        
    
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------
            
if __name__=="__main__":
    #stream fetching test - OK
    '''
    l=1
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
    print(factory.getVelocityLogs())
    print(factory.getDataUpdateLogs())
    '''
    #dataset generating test - OK
    '''
    import decimal
    decimal.getcontext().prec=Config.prec
    decimal.getcontext().rounding=Config.rounding
    
    print(decimal.getcontext())
    l=0
    initX=0
    velMeanDist=(5,5+sys.float_info.min)
    velStdDist=(10,10+sys.float_info.min)
    factory=InputStreamFactory(lambdaVel=l, initXData=initX, velMeanNormalDistr=velMeanDist, velStdNormalDistr=velStdDist)
    ds=factory.generateDataSet(50, 3, normalize=True, filename='datasetTest')
    v0=ds['velocities'][0]
    v1=ds['velocities'][1]
    v2=ds['velocities'][2]
    
    print(np.mean(v0))
    print(np.std(v0))
    print(v0)
    print(ds['updates'][0])

    print(np.mean(v1))
    print(np.std(v1))
    print(v1)

    print(np.mean(v2))
    print(np.std(v2))
    print(v2)
        
    m=[]
    for i in range(len(v0)):
        print((v0[i],v1[i],v2[i]))
        print dec(np.mean([v0[i],v1[i],v2[i]]))
        m.append(np.mean([v0[i],v1[i],v2[i]]))
    print("mean of means is:%f"%np.mean(m))

    from GM_Exp.Util import Plotter
    ranges=[np.arange(1,51),np.arange(1,51), np.arange(1,51)]
    multiplePlots2d(ranges,[v0,v1,v2],['one','two','three'],title="vels")
    multiplePlots2d(ranges, ds['updates'], ['one','two','three'],title='updates')
    
    print('---LOADING DATASET---')
    
    factory2=InputStreamFactory(dataSetFile='/home/ak/git/GM_Experiment/Experiments/datasets/DATASET_l-0_n-5_m-10_std-10.p')
    fetcher2=factory2.getInputStream()
    print(factory2)
    print(fetcher2)
    for i in range(3):
        print(fetcher2.next())
    streams=factory2.getInputStreams()
    for stream in streams:
        print(stream)
        print(stream.getVelocityDistr())
        st=stream.getData()
        for i in range(10):
            print("Data:%f"%st.next())
            print("Velocity:%f"%stream.getVelocity())
    ranges=[np.arange(1,51),np.arange(1,51), np.arange(1,51)]
    multiplePlots2d(ranges, factory2.getDataUpdateLogs())
    
    '''
    '''
    import matplotlib.pyplot as plt
    import scipy
    import scipy.stats

    factory2=InputStreamFactory(dataSetFile='/home/ak/git/GM_Experiment/Experiments/datasets/DATASET_l-0_n-5_m-10_std-10.p')
    fetcher2=factory2.getInputStream()
    print(factory2)
    print(fetcher2)
    for i in range(3):
        print(fetcher2.next())
    streams=factory2.getInputStreams()
    print(streams)
    y=deDec(streams[1].getDataUpdatesLog()[1:1000])
    
    plot2d(np.arange(len(y)),y)
    h = plt.hist(y,bins=30)

    dist_names = ['alpha', 'beta', 'arcsine',
              'weibull_min', 'weibull_max', 'rayleigh']

    for dist_name in dist_names:
        dist = getattr(scipy.stats, dist_name)
        param = dist.fit(y)
        pdf_fitted = dist.pdf(scipy.arange(len(y)), *param[:-2], loc=param[-2], scale=param[-1]) * len(y)
        plt.plot(pdf_fitted, label=dist_name.replace("_"," "))
        plt.xlim(0,47)
    plt.legend()
    plt.show()
    '''