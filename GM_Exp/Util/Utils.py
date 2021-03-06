'''
@author: ak
'''
from __future__ import division

import decimal
import pickle
from GM_Exp import Config
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

def dec(data):
    '''
    @param data: data to convert to decimal
    @return decimal representation of data
    '''
    if isinstance(data, list) or isinstance(data,np.ndarray):
        return list(dec(d) for d in data) if isinstance(data,list) else np.array([dec(d) for d in data]) 
    else:
        return decimal.Decimal(str(data))
        

def deDec(data):
    '''
    @param data: data to de-convert from decimal
    @return decoded data, float
    '''
    if isinstance(data, list) or isinstance(data,np.ndarray):
        return list(deDec(d) for d in data) if isinstance(data,list) else np.array([deDec(d) for d in data]) 
    else:
        if isinstance(data,decimal.Decimal):
            return float(data)
        else:
            return data
        
def loadDataSet(filename):
    '''
    @param filename: filename of dataset
    @return dictionary with dataset data
    '''
    if isinstance(filename,str):
        return pickle.load(open(filename,"rb"))
        
if __name__=='__main__':
    #avg lists over iters
    a=[[[2,3,4,5,6,6,7,7,8,8,9,9],[54,5,5],[4,5,6,6,7,65,5,4,3,2,2]],[[2,3,4,5,6,6,7,7,8,8,9,9],[54,5,5],[4,5,6,6,7,65,5,4,3,2,2]]]
    print(toNdArray(a))
    #dec function test
    '''
    dat=[]
    print(dec(dat))
    dat.append(4.5)
    print(dat)
    print(dec(dat))
    print(deDec(dec(dat)))
    
    dat=4.3
    print(dec(dat))
    print(isinstance(dec(dat),decimal.Decimal))
    
    print(deDec(dec(dat)))
    print(isinstance(deDec(dec(dat)),float))
    
    
    dat=[4.3,6.5,7.3]
    dat_dec=dec(dat)
    print(dat_dec)
    print([isinstance(d,decimal.Decimal) for d in dat_dec])
    
    print(deDec(dat_dec))
    print([isinstance(d,float) for d in deDec(dat_dec)])
    
    
    dat=np.array([4.3,6.5,7.3])
    dat_dec=dec(dat)
    print(dat_dec)
    print(isinstance(dat_dec,np.ndarray))
    print(dat_dec.shape)
    
    print(deDec(dat_dec))
    
    dat=[[4.3,6.5,7.3],[5.4,[6.7,1.2]],[44,4.3]]
    dat_dec=dec(dat)
    print(dat_dec)

    print(deDec(dat_dec))
    
    dat=np.array([[4.3,6.5,7.3],[5.4,[6.7,1.2]],[44,4.3]])
    dat_dec=dec(dat)
    print(dat_dec)
    print(isinstance(dat_dec,np.ndarray))
    print(dat_dec.shape)
    
    print(deDec(dat_dec))
    print(isinstance(deDec(dat_dec),np.ndarray))

    dat=np.array([[4.3,6.5,7.3],[5.4,6.7,1.2],[44,4.3,0.1]])
    dat_dec=dec(dat)
    print(dat_dec)
    print(isinstance(dat_dec,np.ndarray))
    print(dat_dec.shape)
    print(deDec(dat_dec))
    print(isinstance(deDec(dat_dec),np.ndarray))
    
    dat=np.array([[4.3,6.5,7.3],[5.4,6.7,1.2],[44,4.3,0.1]])
    print(dec(dat))
    
    d=loadDataSet('/home/ak/workspace/GM_Experiment/Experiments/datasets/DATASET_l-1_n-5_m-5_std-5.p')
    print(d)
    '''