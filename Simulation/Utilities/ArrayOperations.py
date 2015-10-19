'''
@author: ak
'''
import pandas as pd
import scipy as sp

from hashlib import sha1

from numpy import all, array, uint8


class hashable(object):
    r'''Hashable wrapper for ndarray objects by Helio Perroni Filho:
        
        http://machineawakening.blogspot.gr/2011/03/making-numpy-ndarrays-hashable.html

        Instances of ndarray are not hashable, meaning they cannot be added to
        sets, nor used as keys in dictionaries. This is by design - ndarray
        objects are mutable, and therefore cannot reliably implement the
        __hash__() method.

        The hashable class allows a way around this limitation. It implements
        the required methods for hashable objects in terms of an encapsulated
        ndarray object. This can be either a copied instance (which is safer)
        or the original object (which requires the user to be careful enough
        not to modify it).
    '''
    def __init__(self, wrapped, tight=False):
        r'''Creates a new hashable object encapsulating an ndarray.

            wrapped
                The wrapped ndarray.

            tight
                Optional. If True, a copy of the input ndaray is created.
                Defaults to False.
        '''
        self.__tight = tight
        self.__wrapped = array(wrapped) if tight else wrapped
        self.__hash = int(sha1(wrapped.view()).hexdigest(), 16)

    def __eq__(self, other):
        return all(self.__wrapped == other.__wrapped)

    def __hash__(self):
        return self.__hash

    def unwrap(self):
        r'''Returns the encapsulated ndarray.

            If the wrapper is "tight", a copy of the encapsulated ndarray is
            returned. Otherwise, the encapsulated ndarray itself is returned.
        '''
        if self.__tight:
            return array(self.__wrapped)

        return self.__wrapped


def avgListsOverIters(array2d):
    '''
    function to average list data into a single list or value
    args:
        @param array2d: 2d array, rows=trials
                                  columns=iterations
    @return list containing average of multiple lists len(list)==max(len(r) for r in array2d rows)
    '''
    array2d=toNdArray(array2d)  #normalizes row lengths
    if len(sp.shape(array2d))==2:   #2-dim case
        return sp.array([sp.mean(array2d[:,i]) for i in range(sp.shape(array2d)[1])])
    elif len(sp.shape(array2d))==1: #1-dim case
        return sp.average(array2d)
    else:
        return array2d


def toNdArray(array2d):
    '''
    args:
        @param a 2d array
    @return an Nd array
    '''
    if any(isinstance(el,list) or isinstance(el,sp.ndarray) for el in array2d):
        nda=sp.array([sp.concatenate((l,[0]*(max(map(len,array2d))-len(l)))) for l in array2d])
        return nda
    else:
        return array2d


def computeMean(dataset, weightDict=None):
        '''
        computes global mean time series from a collection of node updates
        args:
            @param dataset: training dataset, a pandas panel
            @param weightDict: weight dictionary, dataset.items must match weightDict.keys()
        @return pandas DataFrame containing Global mean, index==dataset.major_axis, columns==dataset.minor_axis
        '''
        if weightDict:
            return pd.DataFrame(sp.average(dataset.values,axis=0,weights=[weightDict[nid] for nid in dataset.items]),
                                     index=dataset.major_axis,
                                     columns=dataset.minor_axis)
        else:
            return pd.DataFrame(sp.average(dataset.values,axis=0),
                                     index=dataset.major_axis,
                                     columns=dataset.minor_axis)


def weightedAverage(itemList, weightList):
    '''
    computes weighted average of iterable of sp.arrays
    args:
        @param itemList: items to be averaged in list like form
        @param weightList: list of weights
    @return weightedAverage
    '''    
    if len(itemList)!=len(weightList):
        raise ValueError('itemList and weightList must match')
    else:
        size=len(itemList)
    
    nominator=sum([itemList[i]*weightList[i] for i in range(size)])
    denominator=sum(weightList)
    
    if not denominator:
        raise ValueError('division by zero,sum of weights equals zero')
    return nominator/denominator

    


#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------

if __name__=='__main__':
    test2DArray=[range(1,3),range(6,10)]
    test1DArray=range(10)
    print('start 2D array:')
    print(test2DArray)
    print(test1DArray)
    print('to Nd Array:')
    print(toNdArray(test2DArray))
    print(toNdArray(test1DArray))
    print('AvgListsOverIters:')
    print(avgListsOverIters(test2DArray))
    print(avgListsOverIters(test1DArray))
    
    print('----hashable test----')
    a=sp.array([2,3])
    b=sp.array([34,34,34,34])
    t0=(4,hashable(a),10)
    t1=(10,hashable(b),3000)
    s=set()
    s.add(t0)
    s.add(t1)
    print(s)
    print([isinstance(b.unwrap(),sp.ndarray) for a,b,c in s])
    
    from Simulation.Utilities.Dec import *
    
    print('------dec hashable test---------')
    g=dec(sp.array([2,3]))
    gh=hashable(g)
    print(isinstance(gh,hashable))
    print(hashable(g).unwrap())
    
    print('-------weighted average test---------')
    nL=sp.array([sp.array([3,4,5]),sp.array([10,11,12])])
    w=[1.0,0.01]
    print(weightedAverage(nL,w))
    
    print('------weighted mean test--------------')
    import random as r
    from Simulation.Utilities.DatasetHandler import createNormalsDataset

    ds=pd.Panel({i:createNormalsDataset(r.randint(0, 7), 0.01, [20,2], cumsum=True) for i in range(4)})
    ds=deDec(ds)
    print(ds)
    print(ds.values)
    wd={i:1.0 for i in range(4)}
    mds=computeMean(ds, wd)
    
    print(mds)