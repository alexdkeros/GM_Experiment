'''
@author: ak
'''
import time
from GM_Exp.Utils import Utils
import pylab as pl
import matplotlib
# matplotlib.use('Agg')
from matplotlib import rc
from matplotlib import cm
from mpl_toolkits.mplot3d.axes3d import Axes3D



#plotting settings
rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

def plot2d(rangeStart,rangeEnd,data,xLabel=None, yLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
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
    plotRange=pl.arange(rangeStart,rangeEnd+1)
    if (len(plotRange)!=len(data)):
        print('Range and Data lengths do not match')
        return
    fig, axes=pl.subplots()
    axes.plot(plotRange, data, 'r')
    axes.grid(True)
    axes.set_xlim([rangeStart, rangeEnd])
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
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
        
def plot3d(rangeXStart, rangeXEnd, data, angleX=60, angleY=30, xLabel=None, yLabel=None, zLabel=None, title=None, saveFlag=False, filename=None, showFlag=True):
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
    plotRangeX=range(rangeXStart, rangeXEnd+1)
    plotRangeY=range(0, max(map(len, data)))
    Y,X=pl.meshgrid(plotRangeX, plotRangeY)
    p=axes.plot_surface(X,Y,Utils.toNdArray(data).transpose(),rstride=1, cstride=1, cmap=cm.get_cmap('coolwarm', None), linewidth=0, antialiased=True)
    axes.view_init(angleX, angleY)
    cb=fig.colorbar(p,shrink=0.5)
    axes.set_ylim3d(rangeXStart, rangeXEnd)
    axes.set_xlabel(xLabel)
    axes.set_ylabel(yLabel)
    axes.set_zlabel(zLabel)
    axes.set_title(title)
    if saveFlag:
        if filename:
            fig.savefig(filename+'.png')
        else:
            print('No filename specified, not saving')
    if showFlag:
        fig.show()
        time.sleep(5)
        
