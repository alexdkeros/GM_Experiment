'''
@author: ak
'''
from __builtin__ import True
import os.path

import pandas as pd
import scipy as sp
from Simulation.Utilities.Dec import *

def loadDataset(path):
    '''
    load csv dataset
         hdf
         excel
    args:
        @param path: path to dataset
    @return loaded dataset
    '''
    ext=os.path.splitext(path)[1]
    
    if ext==".csv":
        dataset=pd.read_csv(path)
    elif ext==".h5":
        dataset=pd.read_hdf(path, "h5")
    elif ext==".xlsx" or ext==".xls":
        dataset=pd.read_excel(path)
    elif ext==".p":
        dataset=pd.read_pickle(path)
    else:
        raise ValueError("Not supported dataset, try csv,hdf of excel file.")
    
    return dec(dataset)

def saveDataset(dataset,path):
    ext=os.path.splitext(path)[1]
    
    if ext==".csv":
        dataset.to_csv(path)
    elif ext==".h5":
        dataset.to_hdf(path,'df')
    elif ext==".xlsx" or ext==".xls":
        dataset.to_excel(path)
    elif ext==".p":
        dataset.to_pickle(path)
    else:
        raise ValueError("Not supported dataset, try csv,hdf,pickle or excel file.")
     

def splitTrainTestDataset(dataset,percentage=0.2):
    '''
    split dataset into training and testing samples
    args:
        @param percentage: percentage of dataset for testing, rest for training
    @return (training, testing) dataset subsets
    '''
    assert percentage<1.0
    
    train=None;
    test=None;
    if dataset.ndim in [1,2]:
        msk=sp.random.rand(len(dataset))<percentage
        train=dataset[msk]
        test=dataset[~msk]
    elif dataset.ndim==3:
        msk=sp.random.rand(len(dataset.major_axis))<percentage
        train={}
        test={}
        for it in dataset.items:
            train[it]=dataset[it][msk]
            test[it]=dataset[it][~msk]
        train=pd.Panel.from_dict(train)
        test=pd.Panel.from_dict(test)
    else:
        raise ValueError('Unsupported dataset size')
    return train,test

def createNormalsDataset(loc, scale, size, cumsum=True, index=None, columns=None, items=None):
    '''
    create dataset drawn from normal distribution
    args:
        @param loc: distribution mean or list of means, len==size[0]
        @param scale: distribution std (can use sys.float_info.min) or list of stds, len==size[0]
        @param size: dataset size as list of dimentions
        @param cumsum: return as cumulative sums
        @param indexes: [,] of index names
        @param columns: [,] of column names
        @param items:[,] of item names (for Panels)
        @param name: object name
    @return dataset
    '''
    dataset=None;
    if not isinstance(loc,list) and not isinstance(scale,list):
        if isinstance(size,int) or len(size)==1:
            dataset=pd.Series(sp.random.normal(loc=loc, scale=scale, size=size), index=index)
        elif len(size)==2:
            dataset=pd.DataFrame(sp.random.normal(loc=loc, scale=scale, size=size),index=index, columns=columns)
        elif len(size)==3:
            dataset=pd.Panel(sp.random.normal(loc=loc,scale=scale, size=size),items=items, major_axis=index, minor_axis=columns)
        else:
            raise ValueError('1<=len(size)<=3, others not supported')

        return dec(dataset) if not cumsum else dec(dataset).cumsum()
    else:
        if len(size)==3:
            if not items:
                items=range(size[0])
            dataset=pd.Panel({items[i]:createNormalsDataset(loc=loc[i], scale=scale[i], size=size[1:], cumsum=cumsum, index=index, columns=columns) for i in range(size[0])})
        elif len(size)==2:
            if not columns:
                columns=range(size[1])
            dataset=pd.DataFrame({columns[i]:createNormalsDataset(loc=loc[i], scale=scale[i], size=size[0], cumsum=cumsum, index=index) for i in range(size[1])})
        
        return dec(dataset)
    

#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    '''
    ds1D=createNormalsDataset(loc=10, scale=3, size=[4], cumsum=True, index=['a','b','c','d'])
    ds2D=createNormalsDataset(loc=10, scale=3, size=[4,2], cumsum=True, index=['a','b','c','d'],columns=['col1','col2'])
    ds3D=createNormalsDataset(loc=10, scale=3, size=[2,4,2], cumsum=True,items=['it1','it2'], index=['a','b','c','d'],columns=['col1','col2'])
    print(ds1D)
    print(ds2D)
    print(ds3D)
    
    for ds in [ds1D, ds2D, ds3D]:
        train,test=splitTrainTestDataset(ds, 0.3)
        print('Train and Test datasets:')
        print(train)
        print(test)
    print('----------------------')
    ds=createNormalsDataset(loc=[[4,5],[100,200]], scale=[[0.01,10],[0.001,1000]], size=[2,4,2], cumsum=True,index=['a','b','c','d'])
    print(ds)
    print(ds.values)
    '''
    n=2
    d=10
    loc=[10,2]
    scale=[10,2]
    ds=createNormalsDataset(loc=loc, scale=[0.001]*n, size=[n,3000,d], cumsum=True, items=['n'+str(i) for i in range(n)])
    saveDataset(ds, '/home/ak/git/GM_Experiment/Experiments/datasets/linear'+str(d)+'D'+str(n)+'N.p')
    ds=createNormalsDataset(loc=loc, scale=scale, size=[n,3000,d], cumsum=True, items=['n'+str(i) for i in range(n)])
    saveDataset(ds, '/home/ak/git/GM_Experiment/Experiments/datasets/random'+str(d)+'D'+str(n)+'N.p')
    