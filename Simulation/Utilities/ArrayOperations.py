'''
@author: ak
'''
import scipy as sp

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