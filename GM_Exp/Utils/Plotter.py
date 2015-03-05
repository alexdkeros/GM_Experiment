'''
@author: ak
'''
import matplotlib
#matplotlib.use('Agg')
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

def plot2d(plotRange,data,yScale='linear',xLabel=None, yLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
    '''
    function plot2d:
    creates a 2d plot
    args:
        @param plotRange: x axis values
        @param data: 1d array of data to plot
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
        
    len(range) and len(data) must match, use linspace
    '''
    fig, axes=pl.subplots()
    axes.plot(plotRange, data, 'r')
    axes.grid(True)
    axes.set_xlim([plotRange[0], plotRange[-1]])
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
        
        
def multiplePlots2d(plotRanges, data, labels=None, yScale='linear',xLabel=None,yLabel=None, title=None, saveFlag=False, filename=None,showFlag=True):
    '''
    function multiplePlots2d:
    creates a 2d plot of many data arrays
    args:
        @param plotRanges: array of ranges for each data array to plot
        @param data: 2d array of data, array of data arrays to plot
        @param labels: array of labels for each data element to plot
        @param yScale: plotting scale 'linear' or 'log'
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
    '''
    if not isinstance(plotRanges, list):
        plotRanges=[plotRanges]
    if not isinstance(data, list):
        data=[data]
    if labels and (not isinstance(labels, list)):
        labels=[labels]
        
    fig,axes=pl.subplots()
    for i in range(len(data)):
        axes.plot(plotRanges[i],data[i],label=(labels[i] if labels else None))
    axes.legend()
    axes.grid(True)
    axes.set_xlim([min(i[0] for i in plotRanges), max(i[-1] for i in plotRanges)])
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
        
        
def plot3d(xRange, yRange, data, angleX=60, angleY=30, zScale='linear',xLabel=None, yLabel=None, zLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
    '''
    function plot3d:
    creates a 3d plot
    args:
        @param xRange: x axis range
        @param yRange: y axis range
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
        
    to rotate change xRange/yRange to different order accordingly
    to match maximum data length, use max(map(len,data))
    '''
    fig=pl.figure()
    axes=fig.add_subplot(1,1,1, projection='3d')
    Y,X=pl.meshgrid(yRange, xRange)
    p=axes.plot_surface(X,Y,Utils.toNdArray(data).transpose(),rstride=1, cstride=1, cmap=cm.get_cmap('coolwarm', None), linewidth=0, antialiased=True)
    axes.view_init(angleX, angleY)
    cb=fig.colorbar(p,shrink=0.5)
    axes.set_ylim3d(yRange[0], yRange[-1])
    
    #FIX if left > right shows wrong graph orientation and x axis labels 
    #axes.set_xlim3d(xRange[0], xRange[-1]) 
    
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
    #testing simple 2d plot - OK
    '''
    start=0
    end=3000
    data=pl.arange(0,1000)
    plotRange=pl.linspace(start,end,len(data))
    multiplePlots2d(plotRange,data,yScale='log',xLabel='x',yLabel='y', title='test')
    '''
    
    #testing multiple 2d Plots - OK
    '''
    data=[range(10), range(40,100), pl.arange(.1,1,.1)]
    plotRanges=[]
    labels=[]
    for dat in data:
        plotRanges.append(pl.linspace(dat[3],dat[-5],len(dat)))
        labels.append("test"+str(dat[0]))
    multiplePlots2d(plotRanges, data, labels)
    '''
    
    #testing 3d plots - mostly OK
    data=[range(10), range(40,100), pl.arange(.1,1,.1)]
    yRange=pl.arange(0,3)
    xRange=pl.linspace(100,0,max(map(len,data)))
    plot3d(xRange, yRange, data)