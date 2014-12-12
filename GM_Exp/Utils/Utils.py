'''
@author: ak
'''
from __future__ import division
import numpy as np


def avgListsOverIters(array2d):
    '''
    function to average list data into a single list or value
    args:
        @param array2d: 2d array, rows=experimental iterations to average over
                            columns=iterations till global violation
    @return list containing average of multiple lists
    '''
    array2d=toNdArray(array2d)
    if len(np.shape(array2d))==2:
        avgList=np.array([np.mean(array2d[:,i]) for i in range(np.shape(array2d)[1])])
        return avgList
    elif len(np.shape(array2d))==1:
        return np.average(array2d)
    else:
        return array2d


def toNdArray(array2d):
    '''
    @param a 2d array
    @return an Nd array
    '''
    if any(isinstance(el,list) or isinstance(el,np.ndarray) for el in array2d):
        nda=np.array([np.concatenate((l,[0]*(max(map(len,array2d))-len(l)))) for l in array2d])
        return nda
    else:
        return array2d


if __name__=='__main__':
    l=[[5,543,3,2],[5]]
    print(l)
    #l=[np.array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.]), np.array([ 0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  1.5,  2. ]), np.array([ 0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0.5,  0. ,  1.5,  3. ,
    #    1. ])]
    print(avgListsOverIters(l))
    #l=[range(10),range(5,16),range(20,30)]
    ##print(l)
    #f=avgListsOverIters(l)
    #print(np.shape(f))
    ##print(f)
    #print("----------")
    #g=[[0, 0, 0, 0, 0, 0, 0,0,0, 0, 4], [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2]]
    #print(g)
    #h=avgListsOverIters(g)
    #print(np.shape(h))
    #print(h)
    #print("------------")
    #print(toNdArray(l))
    #print(toNdArray(g))
    # print(toNdArray(l))
    # print('------------')
    # print(np.shape(l))
    # print(np.array(l))
    # f=avgListsOverIters(l)
    # print(np.shape(f))
    # print(f)
    