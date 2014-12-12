'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import numpy as np
from GM_Exp import Config



def heuristicNLP(data,threshold, mean):
    '''
    data are list of (id,velocity) tuples
    '''
    print(data)
    
    ids=[id for id,u in data]
    u=[u for id,u in data]
    
    x=oovars(ids) #oovars
    f=[]          #oofuns
    startPoint={}
    constraints=[]
    
    for i in range(len(x)):
        #func
        f.append(func(x[i],u[i],threshold))
        
        #point
        startPoint[x[i]]=mean
    
        #constraints
        constraints.append(x[i]<threshold)
        
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    constraints.append(np.mean(x)==mean)

    
    p=NLP(objective,startPoint,constraints=constraints)
    p.implicitBounds=[None,threshold]
    r=p.maximize('ralg',plot=Config.NLPPlot)

    #DBG
    print("-----------------!!!results!!!---------------------")
    print({v.name:r(v) for v in x})
    print("-----------------^^^^^^^^^^^^^---------------------")
    return {v.name:r(v) for v in x}
    
    
     
def func(var,u,threshold):
    return (threshold-var)/u
    
   