'''
@author: ak
'''
from FuncDesigner import *
from openopt import *
import numpy as np
from GM_Exp import Config


def heuristicNLP(data,threshold, mean,fu,plot=Config.NLPPlot):
    '''
    inputs:
    @param data : list of (id,velocity) tuples
    @param threshold : monitoring threshold (of function)
    @param mean : constrain of data
    @param fu : monitoring function
    @return: dict {id:optimizedVal,}
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
        f.append(func(x[i],u[i],threshold,fu))
        
        #point
        startPoint[x[i]]=mean
    
        #constraints
        constraints.append(fu(x[i])<threshold)
        constraints.append(func(x[i],u[i],threshold,fu)>=0)
    #min
    fmin=min(f)
    objective=fmin('maxmin_f')
    
    constraints.append(np.mean(x)==mean)
    
    #maxmin
    p=NLP(objective,startPoint,constraints=constraints)
    
    #FIX wrong bounds
    #p.implicitBounds=[None,threshold]
    r=p.maximize('ralg',plot=plot)

    #DBG
    print("-----------------!!!results!!!---------------------")
    print({v.name:r(v) for v in x})
    print("-----------------^^^^^^^^^^^^^---------------------")
    return {v.name:r(v) for v in x}
    
    
     
def func(var,u,threshold,fu):
    return (threshold-fu(var))/u
    
if __name__=='__main__':
    data=[('one',3),('two',5)]
    threshold=80
    mean=8
    heuristicNLP(data,threshold,mean,Config.defMonFunc)
    