'''
Show what new velocity model can do.

@author: ak
'''
import numpy as np
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory
from GM_Exp.Utils.Plotter import multiplePlots2d

def __velSchemeShower(meanDistr,stdDistr,initX,iters,streamsNum,l,normalizing,comment=None):


    factory=InputStreamFactory(lambdaVel=l,
                               initXData=initX,
                               velMeanNormalDistr=meanDistr,
                               velStdNormalDistr=stdDistr)
    
    data=factory.generateDataSet(iters, streamsNum,normalize=normalizing)
    
    #velocities
    velPlotData=data["velocities"]
        
    velPlotData.append([meanDistr[0]]*iters) #true mean
    velPlotData.append([np.mean(i) for i in zip(*velPlotData)]) #computed mean
    
    ranges=[range(1,iters+1)]*(data["streams"]+2)
    labels=["stream "+str(i) for i in range(data["streams"])]+["true mean","computed mean"]

    multiplePlots2d(ranges,
                    velPlotData,
                    labels=labels,
                    yScale="linear",
                    xLabel="time",
                    yLabel="velocities",
                    title="Stream's velocities plot,"+comment,
                    saveFlag=True,
                    filename="vels_streams-"+str(streamsNum)+"_l-"+str(l)+"_norm-"+str(normalizing),
                    showFlag=True)

    #updates
    updPlotData=data["updates"]
        
    updPlotData.append([np.mean(i) for i in zip(*updPlotData)]) #computed mean
    
    ranges=[range(1,iters+1)]*(data["streams"]+1)
    labels=["stream "+str(i) for i in range(data["streams"])]+["computed mean"]

    multiplePlots2d(ranges,
                    updPlotData,
                    labels=labels,
                    yScale="linear",
                    xLabel="time",
                    yLabel="updates",
                    title="Stream's updates plot,"+comment,
                    saveFlag=True,
                    filename="upds_streams-"+str(streamsNum)+"_l-"+str(l)+"_norm-"+str(normalizing),
                    showFlag=True)
    



if __name__ == '__main__':
    
    
    streamsNum=5
    '''
    #l=0
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(3,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=0,
                      normalizing=False,
                      comment="l=0,w/o normalizing")
    
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(3,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=0,
                      normalizing=True,
                      comment="l=0,w normalizing")
    
    #l=0.5
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(3,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=0.5,
                      normalizing=False,
                      comment="l=0.5,w/o normalizing")
    
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(3,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=0.5,
                      normalizing=True,
                      comment="l=0.5,w normalizing")
    '''
    #l=1
    '''
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(5,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=1,
                      normalizing=False,
                      comment="l=1,w/o normalizing")
    '''
    __velSchemeShower(meanDistr=(5,5),
                      stdDistr=(5,2),
                      initX=0,
                      iters=100,
                      streamsNum=streamsNum,
                      l=1,
                      normalizing=True,
                      comment="l=1,w normalizing")
                    