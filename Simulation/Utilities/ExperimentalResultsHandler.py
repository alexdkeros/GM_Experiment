'''
@author: ak
'''
import os.path
import cPickle as pickle
from Simulation.Utilities.ArrayOperations import hashable
from Simulation.Utilities.DatasetHandler import saveDataset

def saveExpResults(experimentName,
                   savePath,
                   configData,
                   pairer,
                   nodes,
                   coord,
                   network,
                   train_s,
                   test_s):
    '''
    saves Experiment data in respective folder savePath/experimentName
    creates files:
        1.configData, dict containing {threshold:float,
                                        monFunc:str,
                                        bal_type:str,
                                        pairer_type:str,
                                        network_type:str,
                                        node_num:int,
                                        data_dims:int,
                                        dataset_name:str
                                        node_dict: {nId:w_i, }}
        2.pairerData, dict containing {typeDict: {},
                                        weightDict:{}}
        3.nodeData, dict containing {nId:uLog}
        4.coordData, dict containing {coordId: bLog}
        5.networkData, dict containing {msg_type: list of msgs}
        6.dataset_train, pandas Panel in csv form with training data
        7.dataset_test, pandas Panel in csv form with testing data
    args:
        @param experimentName: name of experiment
        @param savePath: path in string format
        @param configData: dictionary containing configuration data
        @param pairer: pairer instance
        @param nodes: {nId: node_instance}
        @param coord: coordinator instance
        @param network: network instance
        @param train_s: training dataset, pandas Panel
        @param test_s: testing dataset, pandas Panel
    '''
    savePath=os.path.normpath(savePath)
    
    folderPath=savePath+'/'+experimentName
    
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    
    folderPath=folderPath+'/'
    print('===========================================================================================================')
    print('=====================================SAVING EXPERIMENTAL RESULTS===========================================')
    print('==========================path: %s==========================================='%folderPath)
    
    
    #unhash iterable
    unhash=lambda x: x.unwrap() if isinstance(x,hashable) else x
        
    #save configData
    pickle.dump(configData,open(folderPath+'configData.p','wb'))
    
    #save pairerData
    if (pairer.getWeightDict() and pairer.getTypeDict()):
        pDict={'weightDict':pairer.getWeightDict(), 'typeDict':pairer.getTypeDict()}
        pickle.dump(pDict, open(folderPath+'pairerData.p','wb'))
    
    #save nodeData
    wDict={node: nodes[node].getWeight() for node in nodes}
    uLogDict={node: [map(unhash,i) for i in nodes[node].getuLog()] for node in nodes}
    pickle.dump({'weightDict':wDict, 'uLogDict':uLogDict}, open(folderPath+'nodeData.p','wb'))
    
    #save coordData
    pickle.dump([map(unhash,i) for i in coord.getbLog()],open(folderPath+'coordData.p','wb'))
    
    #save networkData
    msgLog=network.getMsgLog()
    netDict={type: [map(unhash,i) for i in msgLog[type]] for type in msgLog}
    pickle.dump({'iterations':network.getIterationCount(),'msgLogDict':netDict}, open(folderPath+'networkData.p','wb'))
    
    #save datasets
    saveDataset(train_s, folderPath+'dataset_train.p')
    saveDataset(test_s,folderPath+'dataset_test.p')
    
    