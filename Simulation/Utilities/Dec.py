'''
@author: ak
'''
import decimal
import scipy as sp
import pandas as pd

def dec(data):
    '''
    args:
        @param data(single value or array/list): data to convert to decimal
    @return decimal representation of data
    '''
    if isinstance(data, list):
        return list(dec(d) for d in data) 
    elif isinstance(data,sp.ndarray):
        return sp.array([dec(d) for d in data])
    
    #pandas data types
    elif isinstance(data,pd.Series):
        return data.map(dec)
    elif isinstance(data,pd.DataFrame):
        return data.applymap(dec)
    elif isinstance(data,pd.Panel):
        return pd.Panel({i:dec(data[i]) for i in data})
    
    else:
        return decimal.Decimal(str(data))
        

def deDec(data):
    '''
    args:
        @param data(single value or array/list): data to de-convert from decimal
    @return decoded data, float
    '''
    if isinstance(data, list):
        return list(deDec(d) for d in data) 
    elif isinstance(data,sp.ndarray):
        return sp.array([deDec(d) for d in data])
    
    #pandas data types
    elif isinstance(data,pd.Series):
        return data.map(deDec)
    elif isinstance(data,pd.DataFrame):
        return data.applymap(deDec)
    elif isinstance(data,pd.Panel):
        return pd.Panel({i:deDec(data[i]) for i in data})
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
    
    print('-------panda testing------')
    print('Series:')
    p=pd.Series([3.2,4.5,1000,234.23],index=['a','b','c','d'])
    print(p)
    dp=dec(p)
    print(type(dp))
    print(dp)
    print(type(dp[0]))
    print('deDec:')
    print(deDec(dp))
    print(type(deDec(dp)))
    print(type(deDec(dp)[0]))
          
    
    
    print('DataFrames:')
    p=pd.DataFrame([p]*3)
    print(p)
    dp=dec(p).cumsum()
    print(type(dp))
    print(dp)
    print(type(dp.iloc[0,0]))
    print('deDec:')
    print(deDec(dp))
    print(type(deDec(dp)))
    print(type(deDec(dp).iloc[0,0]))
    
    
    print('Panels:')
    p=pd.Panel({'a':p,'b':p})
    print(p)
    dp=dec(p)
    print(type(dp))
    print(dp)
    print(type(dp.iloc[0,0,0]))
    print('deDec:')
    print(deDec(dp))
    print(type(deDec(dp)))
    print(type(deDec(dp).iloc[0,0,0]))
    