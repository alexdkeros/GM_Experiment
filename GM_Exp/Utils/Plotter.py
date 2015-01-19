'''
@author: ak
'''
import matplotlib
matplotlib.use('Agg')
import time
import random
from GM_Exp.Utils import Utils
import pylab as pl
from matplotlib import rc
from matplotlib import cm
from mpl_toolkits.mplot3d.axes3d import Axes3D



#plotting settings
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

def plot2d(rangeStart,rangeEnd,data,yScale='linear',xLabel=None, yLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
    '''
    function plot2d:
    creates a 2d plot
    args:
        @param rangeStart: starting point of x axis
        @param rangeEnd: ending point of x axis
        @param data: 1d array of data to plot
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
    '''
    
    #plot range
    plotRange=pl.arange(rangeStart,rangeEnd,float(rangeEnd-rangeStart)/float(len(data)))
    if (len(plotRange)!=len(data)):
        print('Range and Data lengths do not match')
        return
    fig, axes=pl.subplots()
    axes.plot(plotRange, data, 'r')
    axes.grid(True)
    axes.set_xlim([rangeStart, rangeEnd])
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.set_yscale(yScale) #for log use yScale='log'
    axes.set_title(title)
    fig.tight_layout()
    if saveFlag:
        if filename:
            fig.savefig(filename+'.png')
        else:
            print('No filename specified,not saving')
    if showFlag:
        fig.show()
        time.sleep(5)
        
        
def plots2d(rangeStart,rangeEnd,data,label,rangeStart2,rangeEnd2,data2,label2,yScale='linear',xLabel=None, yLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
    '''
    function plots2d:
    creates a 2d plot of two data arrays
    args:
        @param rangeStart: starting point of x axis
        @param rangeEnd: ending point of x axis
        @param data: 1d array of data to plot
        @param label: label of first data
        @param rangeStart2: starting point of x axis
        @param rangeEnd2: ending point of x axis
        @param data2: 1d array of data to plot
        @param label2: label of second data
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
    '''
    
    #plot range
    plotRange=pl.arange(rangeStart,rangeEnd,float(rangeEnd-rangeStart)/float(len(data)))
    plotRange2=pl.arange(rangeStart2,rangeEnd2,float(rangeEnd2-rangeStart2)/float(len(data2)))
    if (len(plotRange)!=len(data)):
        print('Range and Data lengths do not match')
        return
    if (len(plotRange2)!=len(data2)):
        print('Range2 and Data2 lengths do not match')
        return
    fig, axes=pl.subplots()
    axes.plot(plotRange, data,'r',label=label,lw=2)
    axes.plot(plotRange2, data2,'b',label=label2)
    axes.legend()
    axes.grid(True)
    axes.set_xlim([min(rangeStart,rangeStart2), max(rangeEnd,rangeEnd2)])
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.set_yscale(yScale) #for log use yScale='log'
    axes.set_title(title)
    fig.tight_layout()
    if saveFlag:
        if filename:
            fig.savefig(filename+'.png')
        else:
            print('No filename specified,not saving')
    if showFlag:
        fig.show()
        time.sleep(5)
        
def plot3d(rangeXStart, rangeXEnd, data, angleX=60, angleY=30, zScale='linear',xLabel=None, yLabel=None, zLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
    '''
    function plot3d:
    creates a 3d plot
    args:
        @param rangeXStart: starting point of x axis
        @param rangeXEnd: ending point of x axis
        @param data: 2d array of data to plot
        @param angleX: viewing angle
        @param angleY: viewing angle
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param zLabel: label of z axis
        @param title: plot title
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under
        @param showFlag: (boolean) show figure
    '''
    fig=pl.figure()
    axes=fig.add_subplot(1,1,1, projection='3d')
    plotRangeX=pl.arange(rangeXStart, rangeXEnd,float(rangeXEnd-rangeXStart)/float(len(data)))
    plotRangeY=pl.arange(0, max(map(len, data)))
    Y,X=pl.meshgrid(plotRangeX, plotRangeY)
    #DBG
    #print(Y.shape)
    #print(X.shape)
    #print(Utils.toNdArray(data).shape)
    #print(Utils.toNdArray(data).transpose().shape)
    p=axes.plot_surface(X,Y,Utils.toNdArray(data).transpose(),rstride=1, cstride=1, cmap=cm.get_cmap('coolwarm', None), linewidth=0, antialiased=True)
    axes.view_init(angleX, angleY)
    cb=fig.colorbar(p,shrink=0.5)
    axes.set_ylim3d(rangeXStart, rangeXEnd)
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.set_zlabel(zLabel)
    axes.set_zscale(zScale)
    axes.set_title(title)
    if saveFlag:
        if filename:
            fig.savefig(filename+'.png')
        else:
            print('No filename specified, not saving')
    if showFlag:
        fig.show()
        time.sleep(5)
        
if __name__=="__main__":
    #plots2d(1, 10, [random.randint(0,1000) for r in xrange(10)] , "rand1", 10 , 19,[random.randint(0,1000) for r in xrange(10)] ,"rand2",showFlag=True)
    
    l=[pl.array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.]), pl.array([ 0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  1.5,  2. ]), pl.array([ 0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0. ,  0.5,  0. ,  1.5,  3. ,
        1. ])]
    print(l)
    plot3d(1,3,l)
