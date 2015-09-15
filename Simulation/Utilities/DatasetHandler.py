'''
@author: ak
'''
import os.path
import scipy as sp
import pandas as pd
from __builtin__ import True

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
    msk=sp.random.rand(len(dataset))<percentage
    train=dataset[msk]
    test=dataset[~msk]
    return train,test

def createNormalsDataset(loc, scale, size, cumsum=True, colNames=None):
    '''
    create dataset drawn from normal distribution
    args:
        @param loc: distribution mean
        @param scale: distribution std (can use sys.float_info.min)
        @param cumsum: return as cumulative sums
        @param colNames: [,] of column names
    @return dataset
    '''
    dataset=pd.DataFrame(sp.random.normal(loc=loc, scale=scale, size=size), columns=colNames)
    
    return dataset if not cumsum else dataset.cumsum()


#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------
if __name__=='__main__':
    ds=createNormalsDataset(10, 3, [10,2], True, ['a','b'])
    print(ds)
    
    train,test=splitTrainTestDataset(ds, 0.3)
    print('Train and Test datasets:')
    print(train)
    print(test)
    