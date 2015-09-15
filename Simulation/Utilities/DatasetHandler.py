'''
@author: ak
'''
from __builtin__ import True
import os.path

import pandas as pd
import scipy as sp


def loadDataset(path):
    '''
    load csv dataset
         hdf
         excel
    args:
        @param path: path to dataset
    @return loaded dataset
    '''
    ext=os.path.splitext(path)
    
    if ext==".csv":
        dataset=pd.read_csv(path)
    elif ext==".h5":
        dataset=pd.read_hdf(path, "h5")
    elif ext==".xlsx" or ext==".xls":
        dataset=pd.read_excel(path)
    else:
        raise Exception("Not supported dataset, try csv,hdf of excel file.")
    
    return dataset

def splitTrainTestDataset(dataset,percentage=0.8):
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
        @param loc: distribution mean
        @param scale: distribution std (can use sys.float_info.min)
        @param cumsum: return as cumulative sums
        @param indexes: [,] of index names
        @param columns: [,] of column names
        @param items:[,] of item names (for Panels)
        @param name: object name
    @return dataset
    '''
    dataset=None;
    if len(size)==1:
        dataset=pd.Series(sp.random.normal(loc=loc, scale=scale, size=size), index=index)
    elif len(size)==2:
        dataset=pd.DataFrame(sp.random.normal(loc=loc, scale=scale, size=size),index=index, columns=columns)
    elif len(size)==3:
        dataset=pd.Panel(sp.random.normal(loc=loc,scale=scale, size=size),items=items, major_axis=index, minor_axis=columns)
    else:
        raise ValueError('1<=len(size)<=3, others not supported')
    return dataset if not cumsum else dataset.cumsum()


#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    
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
    
