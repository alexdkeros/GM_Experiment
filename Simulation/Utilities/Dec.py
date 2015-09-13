'''
@author: ak
'''
import decimal
import scipy as sp

def dec(data):
    '''
    args:
        @param data(single value or array/list): data to convert to decimal
    @return decimal representation of data
    '''
    if isinstance(data, list) or isinstance(data,sp.ndarray):
        return list(dec(d) for d in data) if isinstance(data,list) else sp.array([dec(d) for d in data]) 
    else:
        return decimal.Decimal(str(data))
        

def deDec(data):
    '''
    args:
        @param data(single value or array/list): data to de-convert from decimal
    @return decoded data, float
    '''
    if isinstance(data, list) or isinstance(data,sp.ndarray):
        return list(deDec(d) for d in data) if isinstance(data,list) else sp.array([deDec(d) for d in data]) 
    else:
        if isinstance(data,decimal.Decimal):
            return float(data)
        else:
            return data
        

#----------------------------------------------------------------------------
#---------------------------------TEST-OK------------------------------------
#----------------------------------------------------------------------------

if __name__=='__main__':
    td=213.2
    tdArray=[[3.2,4.5],[5.2,6.7,8]]
    print(str(td)+' '+str(type(td)))
    print(str(tdArray)+' '+str(type(tdArray)))
    
    print(str(dec(td))+' '+str(type(dec(td))))
    print(str(dec(tdArray))+' '+str(type(dec(tdArray))))
    
    
    print(str(deDec(dec(td)))+' '+str(type(td)))
    print(str(deDec(dec(tdArray)))+' '+str(type(tdArray)))
    
    assert deDec(dec(td))==td
    assert deDec(dec(tdArray))==tdArray
    