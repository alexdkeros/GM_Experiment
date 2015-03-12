'''
Heuristic method test

@author: ak
'''
import numpy as np
from GM_Exp.Utils import Plotter
from GM_Exp.Heuristics.NonLinearProgramming import heuristicNLP
from GM_Exp.Utils.Plotter import multiplePlots2d


def __heuristicTester(data,threshold,b,fu,comment):
    
    #running heuristic
    res=heuristicNLP(data, threshold,b,fu,False)
    
    #formulating plot
    val=0.
    plotData=[[threshold],[b]]
    ranges=[[np.zeros_like(threshold)+val],[np.zeros_like(b)+val]]
    labels=['threshold:'+str(threshold),'b:'+str(b)]
    styles=['|','*']
    #appending data previous
    for d in data:
        plotData.append([d[1]])
        ranges.append([np.zeros_like(d[1])+val])
        labels.append(d[0]+' prev:'+str(d[1]))
        styles.append('x')
    #appending data after
    for d in res:
        plotData.append([res[d]])
        ranges.append([np.zeros_like(res[d])+val])
        labels.append(d+' after:'+str(res[d]))
        styles.append('x')
        
    #plotting
    multiplePlots2d(plotRanges=plotData,
                    data=ranges,
                    styles=styles,
                    labels=labels,
                    xLabel='optimization axis',
                    title='NLP heuristic '+comment,
                    grid=False,
                    saveFlag=True,
                    filename='b-'+str(b)+'_optimization_'+comment,
                    showFlag=True)
    
    
if __name__ == '__main__':
    

    #data=[(id,velocity),]
    data=[('dat1',4),
          ('dat2',11)]
    threshold=10
    b=np.mean([j for i,j in data])
    fu=lambda x:x
    
    
    __heuristicTester(data,threshold,b,fu,"2valsFeasibleFx")
    
    #data=[(id,velocity),]
    data=[('dat1',4),
          ('dat2',12)]
    threshold=10
    b=np.mean([j for i,j in data])
    fu=lambda x:x**2
    
    
    __heuristicTester(data,threshold,b,fu,"2valsNonFeasibleFx2")
    
    #data=[(id,velocity),]
    data=[('dat1',4),
          ('dat2',12),
          ('dat3',7.4)]
    threshold=10
    b=np.mean([j for i,j in data])
    fu=lambda x:x
    
    
    __heuristicTester(data,threshold,b,fu,"3valsFeasibleFx")
    
    #data=[(id,velocity),]
    data=[('dat1',4),
          ('dat2',12),
          ('dat3',7.4)]
    threshold=10
    b=np.mean([j for i,j in data])
    fu=lambda x:x**2
    
    
    __heuristicTester(data,threshold,b,fu,"3valsNonFeasibleFx2")
    
    #data=[(id,velocity),]
    data=[('dat1',4),
          ('dat2',12),
          ('dat3',7.4)]
    threshold=100
    b=np.mean([j for i,j in data])
    fu=lambda x:x**2

    __heuristicTester(data,threshold,b,fu,"3valsFeasibleFx2")
    