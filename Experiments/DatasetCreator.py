'''
create datasets for tests

@author: ak
'''
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory

if __name__ == '__main__':
    
    iterations=10000
    
    datal=[0,0.5,1] #lambda
    dataNodes=[2,3,5,10,20,30] #nodes
    dataMeanDist=[(1,1),(10,10)] #mean distribution
    dataStdDist=[(0,1),(10,10)] #std distribution
    
    for l in datal:
        for nodes in dataNodes:
            for mDist in dataMeanDist:
                for stdDist in dataStdDist:
                    print('---DATASET l-'+str(l).replace('.', '')+'_n-'+str(nodes)+'_m-'+str(mDist[0])+'_std-'+str(stdDist[0])+'--------')
                    factory=InputStreamFactory(lambdaVel=l,
                                               initXData=0,
                                               velMeanNormalDistr=mDist,
                                               velStdNormalDistr=stdDist)
                    
                    factory.generateDataSet(iterations, 
                                            nodes, 
                                            normalize=True, 
                                            filename='./datasets/DATASET_l-'+str(l).replace('.', '')+'_n-'+str(nodes)+'_m-'+str(mDist[0])+'_std-'+str(stdDist[0]))
                    