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
    avgList=np.zeros(max(map(len,array2d)))
    for l in array2d:
        for i in range(len(l)):
            avgList[i]+=l[i]
    
    avgList=[x/np.shape(array2d)[0] for x in avgList]
    
    return avgList



def toNdArray(array2d):
    '''
    @param a 2d array
    @return an Nd array
    '''
    nda=np.zeros(shape=(np.shape(array2d)[0],max(map(len,array2d))))
    for i in range(np.shape(nda)[0]):
        for j in range(np.shape(nda)[1]):
            if j<len(array2d[i][:]):
                nda[i][j]=array2d[i][j]
            else:
                nda[i][j]=0
    return nda