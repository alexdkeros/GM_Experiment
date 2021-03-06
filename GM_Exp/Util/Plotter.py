'''
@author: ak
'''
import itertools
import matplotlib
matplotlib.use('Agg')
from matplotlib import cm
from matplotlib import rc
from mpl_toolkits.axisartist.axis_artist import Ticks
from mpl_toolkits.mplot3d.axes3d import Axes3D
import random
from scipy.io.matlab.mio5_utils import scipy
import time

from GM_Exp.Util import Utils
import numpy as np
import pylab as pl


#matplotlib.use('Agg')
colors = itertools.cycle(['r','b','g','c', 'm', 'y', 'k','w'])

#plotting settings
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

def plot2d(plotRange,data,
           yScale='linear',
           xLabel=None, 
           yLabel=None, 
           title=None, 
           saveFlag=False, 
           filename=None, 
           showFlag=True):
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
    pl.close()
        
def multiplePlots2d(plotRanges, data, 
                    labels=None, 
                    yScale='linear',
                    styles=None,
                    xLabel=None,
                    yLabel=None,
                    title=None, 
                    grid=True,
                    saveFlag=False, 
                    filename=None,
                    showFlag=True):
    '''
    function multiplePlots2d:
    creates a 2d plot of many data arrays
    args:
        @param plotRanges: array of ranges for each data array to plot
        @param data: 2d array of data, array of data arrays to plot
        @param labels: array of labels for each data element to plot
        @param yScale: plotting scale 'linear' or 'log'
        @param styles: array of line styles
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param grid: plot grid
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
    '''
    if not any((isinstance(k,list) or isinstance(k,pl.ndarray)) for k in plotRanges):
        plotRanges=[plotRanges]
    if not any((isinstance(k,list) or isinstance(k,pl.ndarray)) for k in data):
        data=[data]
    if labels and (not isinstance(labels, list)):
        labels=[labels]
    if styles and (not isinstance(styles, list)):
        styles=[styles]
        
    fig,axes=pl.subplots(figsize=(9,7))
    for i in range(len(data)):
        if styles:
            axes.plot(plotRanges[i],data[i],styles[i],label=(labels[i] if labels else None))
        else:
            axes.plot(plotRanges[i],data[i],label=(labels[i] if labels else None))
    axes.legend()
    axes.grid(grid)
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
    pl.close()
        
def plot3d(xRange, yRange, data, 
           angleX=60, 
           angleY=30, 
           zScale='linear',
           xLabel=None, 
           yLabel=None, 
           zLabel=None, 
           title=None, 
           saveFlag=False, 
           filename=None, 
           showFlag=True):
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
        
    to rotate change viewing angle, angleX is up/down, angleY is left/right
    to match maximum data length, use max(map(len,data))
    '''
    fig=pl.figure()
    axes=fig.add_subplot(1,1,1, projection='3d')
    Y,X=pl.meshgrid(yRange, xRange)
    p=axes.plot_surface(X,Y,Utils.toNdArray(data).transpose(),rstride=1, cstride=1, cmap=cm.get_cmap('coolwarm', None), linewidth=0, antialiased=True)
    axes.view_init(angleX, angleY)
    cb=fig.colorbar(p,shrink=0.5)
    axes.set_ylim3d(yRange[0], yRange[-1])
    axes.set_xlim3d(xRange[0], xRange[-1]) 
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
    pl.close()
        
def __autolabel(rects,axes):
    # attach some text labels
        for rect in rects:
            height = rect.get_height()
            axes.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%height,
                    ha='center', va='bottom')        
        
def barChart(data,
             labels=None,
             xLabel=None,
             yLabel=None,
             title=None,
             xticks=None,
             totalBarWidth=0.5,
             saveFlag=False,
             filename=None,
             showFlag=True,
             figsize=(50,18)):
    '''
    function barChart:
    creates simple bar chart
    args:
        @param data: array, columns=#data groups, rows=#of bars for each group
        @param labels: data labels
        @param xLabel: label of x axis
        @param yLabel: label of y axis
        @param title: plot title
        @param xticks: x axis ticks
        @param totalBarWidth: total width of bars in group
        @param saveFlag: (boolean) save figure
        @param filename: filename to save under (no .ext required)
        @param showFlag: (boolean) show figure
        @param figsize: tuple, figure size
    '''
    if not any((isinstance(k,list) or isinstance(k,pl.ndarray)) for k in data):
        data=[data]
    data=pl.array(data)
        
    if labels and (not isinstance(labels, list)):
        labels=[labels]
        
    bars=data.shape[0]
    
    fig, axes = pl.subplots(figsize=figsize)
    
    bar_width = totalBarWidth/bars
    
    maxIndex=[]
    
    opacity = 0.4
    
    for i in range(bars):
        index=pl.arange(len(data[i]))
        maxIndex=(index if len(index)>len(maxIndex) else maxIndex)
        rect=pl.bar(index+i*bar_width, 
                    data[i], 
                    bar_width,
                    alpha=opacity,
                    color=next(colors),
                    label=None if i>=len(labels) else labels[i])
        __autolabel(rect,axes)
    
    axes.set_ylim([0,max(max(k) for k in data)*1.5])
    axes.set_xlim([0,(len(maxIndex))])
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.set_title(title)
    axes.set_xticks((maxIndex) + bar_width)
    axes.set_xticklabels(xticks,rotation=90)
    axes.legend()

    fig.tight_layout()
    
    if saveFlag:
        if filename:
            fig.savefig(filename+'.png')
        else:
            print('No filename specified,not saving')
    if showFlag:
        fig.show()
        time.sleep(5)
    pl.close()
    
#----------------------------------------------------------------------------
#---------------------------------TEST---------------------------------------
#----------------------------------------------------------------------------          

if __name__=="__main__":
    #testing simple 2d plot - OK
    '''
    import decimal
    range=map(decimal.Decimal,map(str,[0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8]))
    dataa=map(decimal.Decimal,map(str,[1,1,2,2,3,3,4,5,7,7,8,8,9,14,34,34,35,35]))
    #plot2d(range, dataa,saveFlag=False, showFlag=True)
    plot2d(map(float,range), map(float,dataa),saveFlag=False, showFlag=True)
    '''
    '''
    start=0
    end=3000
    data=pl.arange(0,1000)
    plotRange=pl.linspace(start,end,len(data))
    multiplePlots2d(plotRange,data,yScale='log',xLabel='x',yLabel='y', title='test')
    '''
    #testing multiple 2d Plots - OK
    '''
    data=[pl.arange(10), pl.arange(40,100), pl.arange(.1,1,.1)]
    plotRanges=[]
    labels=[]
    styles=[]
    for dat in data:
        plotRanges.append(pl.linspace(dat[3],dat[-5],len(dat)))
        labels.append("test"+str(dat[0]))
        styles.append('-')
    print(data)
    print(plotRanges)
    print(labels)
    print(styles)
    multiplePlots2d(plotRanges, data, labels=labels,styles=styles)

    '''
    '''
    data=range(10)
    plotRanges=range(10)
    labels='vlakas'
    multiplePlots2d(plotRanges, data, labels=labels)
    '''
    #testing 3d plots - OK
    '''
    data=[range(10), range(40,100), pl.arange(.1,1,.1)]
    yRange=pl.arange(0,3)
    xRange=pl.linspace(0,100,max(map(len,data)))
    plot3d(xRange, yRange, data)
    '''
    
    #testing bar chart - OK
    
    from scipy.stats import norm
    print("---plotting---")
    d=norm(5,1)
    data=[]
    xticks=[]
    for i in range(170):
        xticks.append("REALLY BIG NAME GOES HERE %d"%i)
    for i in range(8):
        t=[]
        for j in range(170):
            t.append(d.rvs())
        data.append(t)
    
    labels=['two','three','four','five','a','b','g','h']
    barChart(data, labels=labels,xticks=xticks,showFlag=False,saveFlag=True,filename='test_bar',figsize=(155,15),totalBarWidth=0.82)
    