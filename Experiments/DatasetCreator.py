'''
create datasets for tests

@author: ak
'''
from GM_Exp.DataStream.InputStreamFactory import InputStreamFactory

if __name__ == '__main__':
    
    iterations=20000
    
    datal=[1] #lambda 0,0.5,
    dataNodes=[2,3,4] #nodes 2,3,5,10,20,30
    dataMeanDist=[(5,4)] #mean distribution (2,1),(10,10)
    dataStdDist=[(0,1)] #std distribution (0,1),(10,10)
    
    for l in datal:
        for nodes in dataNodes:
            for mDist in dataMeanDist:
                for stdDist in dataStdDist:
                    print('---TEST DATASET l-'+str(l).replace('.', '')+'_n-'+str(nodes)+'_m-'+str(mDist[0])+'_std-'+str(stdDist[0])+'--------')
                    factory=InputStreamFactory(lambdaVel=l,
                                               initXData=0,
                                               velMeanNormalDistr=mDist,
                                               velStdNormalDistr=stdDist)
                    
                    factory.generateDataSet(iterations, 
                                            nodes, 
                                            normalize=True, 
                                            filename='./test_datasets/TEST_DATASET_l-'+str(l).replace('.', '')+'_n-'+str(nodes)+'_m-'+str(mDist[0])+'_std-'+str(stdDist[0]))
                    