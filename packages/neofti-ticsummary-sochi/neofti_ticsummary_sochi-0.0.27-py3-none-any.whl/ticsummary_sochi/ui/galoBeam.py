#Python module
from abc import ABC, abstractmethod
#Third party module
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
from PyQt6 import QtWidgets,QtGui,QtCore
#Project module

labelAxisStyle = {'color': '#FFF', 'font-size': '14pt'}
titlePlotStyle = {'color': '#FFF', 'font-size': '20pt'}
font=QtGui.QFont()
font.setPixelSize(10)

class __GaloCorrectionAbstract__():
    def __init__(self,correctionValue):
        self.correctionValue = correctionValue
    def setCorrectionValue(self,value:float):
        self.correctionValue = value
        self.__updateData__()
    def __updateData__(self):
        raise NotImplementedError
class GaloCounterDock(Dock,__GaloCorrectionAbstract__):
    def __init__(self,keyEventHandler=None, *args, **kwargs):
        Dock.__init__(self,*args, **kwargs)
        __GaloCorrectionAbstract__.__init__(self,1)
        self.keyEventHandler = keyEventHandler
        self.__initGraph__()
        self.correctionValue = 1
    def __initGraph__(self):
        font=QtGui.QFont()
        font.setPixelSize(10)
        self.viewBoxPlot = pg.plot()
        self.viewBoxPlot.setMouseEnabled(False,False)
        '''pos = np.array([
            [0,0],
            [10,0],
            [0,10],
            [10,10],
            [5,5]
            ])'''
        pos = np.array([
            [0,0],   # Left bottom
            [10,0],  # Right bottom
            [0,10],  # Left up
            [10,10], # Right up
            [5,5]    # Center
            ])
        symbols = ['o','o','o','o','o']
        g = pg.GraphItem()
        g.setData(pos=pos,symbol=symbols,pxMode=False,size=2)
        self.viewBoxPlot.addItem(g)
        self.viewBoxPlot.setAspectLocked(1.0)
        self.viewBoxPlot.hideAxis('bottom')
        self.viewBoxPlot.hideAxis('left')
        font=QtGui.QFont()
        font.setPixelSize(20)
        self.scRUTextItem=pg.TextItem("")
        self.scRUTextItem.setFont(font)
        self.scLUTextItem=pg.TextItem("")
        self.scLUTextItem.setFont(font)
        self.scRBTextItem=pg.TextItem("")
        self.scRBTextItem.setFont(font)
        self.scLBTextItem=pg.TextItem("")
        self.scLBTextItem.setFont(font)
        self.scCTextItem=pg.TextItem("")
        self.scCTextItem.setFont(font)
        self.viewBoxPlot.addItem(self.scLBTextItem)
        self.scLBTextItem.setPos(*pos[0])
        self.viewBoxPlot.addItem(self.scRBTextItem)
        self.scRBTextItem.setPos(*pos[1])
        self.viewBoxPlot.addItem(self.scLUTextItem)
        self.scLUTextItem.setPos(*pos[2])
        self.viewBoxPlot.addItem(self.scRUTextItem)
        self.scRUTextItem.setPos(*pos[3])
        self.viewBoxPlot.addItem(self.scCTextItem)
        self.scCTextItem.setPos(*pos[4])
        self.addWidget(self.viewBoxPlot)
    def updateStyle(self):
        Dock.updateStyle(self)
        self.setOrientation("horizontal")
    def setData(self,scRUSum,scLUSum,scRBSum,scLBSum,scCTSum):
        self.scRUSum = scRUSum
        self.scLUSum = scLUSum
        self.scRBSum = scRBSum
        self.scLBSum = scLBSum
        self.scCTSum = scCTSum
        self.__updateData__()
    def clearData(self):
        self.setData(0, 0, 0, 0, 0)
    def __updateData__(self):
        self.scRUTextItem.setText("{:.2e}".format(self.scRUSum * self.correctionValue))
        self.scLUTextItem.setText("{:.2e}".format(self.scLUSum * self.correctionValue))
        self.scRBTextItem.setText("{:.2e}".format(self.scRBSum * self.correctionValue))
        self.scLBTextItem.setText("{:.2e}".format(self.scLBSum * self.correctionValue))
        self.scCTextItem.setText("{:.2e}".format(self.scCTSum * self.correctionValue))
class GaloLineDock(Dock):
    def __init__(self,keyEventHandler=None, *args, **kwargs):
        Dock.__init__(self,*args, **kwargs)
        __GaloCorrectionAbstract__.__init__(self,1)
        self.keyEventHandler = keyEventHandler
        self.__initGraph__()
    def __initGraph__(self):
        self.lineCounterPlot = pg.plot()
        self.lineCounterPlot.addLegend(offset=(30,30))
        self.lineCounterPlot.getAxis("bottom").setTickFont(font)
        self.lineCounterPlot.getAxis("left").setTickFont(font)
        self.addWidget(self.lineCounterPlot)
        self.lineCounterPlot.setTitle("Counter", **titlePlotStyle)
        self.lineCounterPlot.setLabel('left', "count", units="qty", **labelAxisStyle)
        self.lineCounterPlot.setLabel('bottom', "time", units="sec", **labelAxisStyle)
        self.scCenterPlotDataItem = self.lineCounterPlot.plot(pen=(255,0,0),name="scCenter")
        self.scLeftBottomPlotDataItem = self.lineCounterPlot.plot(pen=(170,120,0),name="scLeftBottom")
        self.scLeftUpPlotDataItem = self.lineCounterPlot.plot(pen=(20,200,20),name="scLeftUp")
        self.scRightUpPlotDataItem = self.lineCounterPlot.plot(pen=(0,255,50),name="scRightUp")
        self.scRightBottomPlotDataItem = self.lineCounterPlot.plot(pen=(0,120,120),name="scRightBottom") 
    def updateStyle(self):
        Dock.updateStyle(self)
        self.setOrientation("horizontal")
    def setData(self,scRU,scLU,scRB,scLB,scCT,x):
        self.scRU = scRU * self.correctionValue
        self.scLU = scLU * self.correctionValue
        self.scRB = scRB * self.correctionValue
        self.scLB = scLB * self.correctionValue
        self.scCT = scCT * self.correctionValue
        self.x = x
        self.__updateData__()
    def __updateData__(self):
        self.scCenterPlotDataItem.setData(x=self.x,y=self.scCT)
        self.scLeftBottomPlotDataItem.setData(x=self.x,y=self.scLB)
        self.scLeftUpPlotDataItem.setData(x=self.x,y=self.scLU)
        self.scRightBottomPlotDataItem.setData(x=self.x,y=self.scRB)
        self.scRightUpPlotDataItem.setData(x=self.x,y=self.scRU)
    def clearData(self):
        self.scCenterPlotDataItem.clear()
        self.scLeftBottomPlotDataItem.clear()
        self.scLeftUpPlotDataItem.clear()
        self.scRightUpPlotDataItem.clear()
        self.scRightBottomPlotDataItem.clear()
        self.lineCounterPlot.replot()
class GaloMonitoringDock(Dock):
    clearDataSignal = QtCore.pyqtSignal()
    def __init__(self,keyEventHandler=None, *args, **kwargs):
        Dock.__init__(self,*args, **kwargs)
        __GaloCorrectionAbstract__.__init__(self,1)
        self.keyEventHandler = keyEventHandler
        self.__initView__()
        self.__initValue__()
    def __initValue__(self):
        self.timeLineMonitor = list()
        self.dataLineMonitor = list()
    def __initView__(self):
        #self.layout = QtWidgets.QVBoxLayout(self)
        #self.addWidget(self.layout)
        self.pusnButtonClear = QtWidgets.QPushButton(text="Clear",enabled=True)
        self.pusnButtonClear.clicked.connect(self.clearData)
        self.addWidget(self.pusnButtonClear)
        self.lineMonitoringPlot = pg.PlotWidget(axisItems = {'bottom': pg.DateAxisItem()})
        self.timeLineMonitor = list()
        self.dataLineMonitor = list()
        #self.lineMonitoringPlot.addLegend()
        self.lineMonitoringPlot.getAxis("bottom").setTickFont(font)
        self.lineMonitoringPlot.getAxis("left").setTickFont(font)
        self.layout.addWidget(self.lineMonitoringPlot)
        self.lineMonitoringPlot.setTitle("Monitor", **titlePlotStyle)
        self.lineMonitoringPlot.setLabel('left', "fluence", units="p", **labelAxisStyle)
        self.lineMonitoringPlot.setLabel('bottom', "time", units='', **labelAxisStyle)
        self.lineMonitoringPlotDataItem = self.lineMonitoringPlot.plot(pen=(255,0,0), name="Monitoring", axisItems = {'bottom': pg.DateAxisItem()})
    def updateStyle(self):
        Dock.updateStyle(self)
        self.setOrientation("horizontal")
    def setData(self,time,point):
        self.timeLineMonitor.append(time)
        self.dataLineMonitor.append(point)
        self.__updateData__()
    def __updateData__(self):
        self.lineMonitoringPlotDataItem.setData(x=self.timeLineMonitor, y=self.dataLineMonitor)
    def clearData(self):
        self.timeLineMonitor = list()
        self.dataLineMonitor = list()
        self.clearDataSignal.emit()
        self.lineMonitoringPlotDataItem.clear()
        self.lineMonitoringPlot.replot()