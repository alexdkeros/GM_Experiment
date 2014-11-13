'''
@author: ak
'''
from __future__ import division
import numpy as np


def avgListsOverIters(array2d):
    '''
    function to average list data into a single list
    args:
        @param array2d: 2d array, rows=experimental iterations to average over
                            columns=iterations till global violation
    @return list containing average of multiple lists
    '''
    array2d=toNdArray(array2d)
    if len(np.shape(array2d))==2:
        avgList=np.array([np.mean(array2d[:,i]) for i in range(np.shape(array2d)[1])])
        return avgList
    else:
        return array2d


def toNdArray(array2d):
    '''
    @param a 2d array
    @return an Nd array
    '''
    if any(isinstance(el,list) or isinstance(el,np.ndarray) for el in array2d) and len(np.shape(array2d))==1 :
        nda=np.array([l+[0]*(max(map(len,array2d))-len(l)) for l in array2d])
        return nda
    else:
        return array2d


if __name__=='__main__':
    l=[[2.,3,4],[5]]
    print(toNdArray(l))
    print('------------')
    print(np.shape(l))
    print(np.array(l))
    f=avgListsOverIters(l)
    print(np.shape(f))
    print(f)
    