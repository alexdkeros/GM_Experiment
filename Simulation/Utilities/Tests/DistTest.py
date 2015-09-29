'''
@author: ak

'''
from FuncDesigner import *
from openopt import *

import scipy as sp
import scipy.linalg as la
import sys
def minDist():
    thresh=10
    dim=3
    
    ball=lambda x,y,z:(x)**2+(y)**2+(z)**2<=1**2
    func=lambda x,y,z:(x**2+y+z)
    
    x=oovars(['x','y','z'])
    print(x)
    
    f=[]
    constraints=[]
    
    f.append(func(x[0],x[1],x[2]))
    
    constraints.append(ball(x[0],x[1],x[2]))
    
    startPoint={x[0]:1,x[1]:0,x[2]:0}
    
    p=NLP(f,startPoint,constraints=constraints)
    
    r=p.maximize('ralg',plot=False)
    
    print({v.name:r(v) for v in x})
    
    r=p.minimize('ralg',plot=False)
    
    print({v.name:r(v) for v in x})
    
    return r

if __name__=='__main__':
    r=minDist()
    
    