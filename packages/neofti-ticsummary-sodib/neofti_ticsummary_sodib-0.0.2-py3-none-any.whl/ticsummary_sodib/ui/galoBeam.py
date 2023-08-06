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
            [0,0],   # Left
            [10,0],  # Right
            [0,10],  # Top
            [10,10], # Bottom
            [5,5]    # Center
            ])'''
        pos = np.array([
            [0,5],   # Left
            [10,5],  # Right
            [5,10],  # Top
            [5,0], # Bottom
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
        self.scLTextItem=pg.TextItem("")
        self.scLTextItem.setFont(font)
        self.scRTextItem=pg.TextItem("")
        self.scRTextItem.setFont(font)
        self.scTTextItem=pg.TextItem("")
        self.scTTextItem.setFont(font)
        self.scBTextItem=pg.TextItem("")
        self.scBTextItem.setFont(font)
        self.scCTextItem=pg.TextItem("")
        self.scCTextItem.setFont(font)
        self.viewBoxPlot.addItem(self.scLTextItem)
        self.scLTextItem.setPos(*pos[0])
        self.viewBoxPlot.addItem(self.scRTextItem)
        self.scRTextItem.setPos(*pos[1])
        self.viewBoxPlot.addItem(self.scTTextItem)
        self.scTTextItem.setPos(*pos[2])
        self.viewBoxPlot.addItem(self.scBTextItem)
        self.scBTextItem.setPos(*pos[3])
        self.viewBoxPlot.addItem(self.scCTextItem)
        self.scCTextItem.setPos(*pos[4])
        self.addWidget(self.viewBoxPlot)
    def updateStyle(self):
        Dock.updateStyle(self)
        self.setOrientation("horizontal")
    def setData(self,scLSum,scRSum,scTSum,scBSum,scCTSum):
        self.scLSum = scLSum
        self.scRSum = scRSum
        self.scTSum = scTSum
        self.scBSum = scBSum
        self.scCTSum = scCTSum
        self.__updateData__()
    def clearData(self):
        self.setData(0, 0, 0, 0, 0)
    def __updateData__(self):
        self.scLTextItem.setText("{:.2e}".format(self.scLSum * self.correctionValue))
        self.scRTextItem.setText("{:.2e}".format(self.scRSum * self.correctionValue))
        self.scTTextItem.setText("{:.2e}".format(self.scTSum * self.correctionValue))
        self.scBTextItem.setText("{:.2e}".format(self.scBSum * self.correctionValue))
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
        self.scLeftPlotDataItem = self.lineCounterPlot.plot(pen=(170,120,0),name="scLeft")
        self.scTopPlotDataItem = self.lineCounterPlot.plot(pen=(20,200,20),name="scTop")
        self.scBottomPlotDataItem = self.lineCounterPlot.plot(pen=(0,255,50),name="scBottom")
        self.scRightPlotDataItem = self.lineCounterPlot.plot(pen=(0,120,120),name="scRight") 
    def updateStyle(self):
        Dock.updateStyle(self)
        self.setOrientation("horizontal")
    def setData(self,scL,scR,scT,scB,scCT,x):
        self.scL = scL * self.correctionValue
        self.scR = scR * self.correctionValue
        self.scT = scT * self.correctionValue
        self.scB = scB * self.correctionValue
        self.scCT = scCT * self.correctionValue
        self.x = x
        self.__updateData__()
    def __updateData__(self):
        self.scCenterPlotDataItem.setData(x=self.x,y=self.scCT)
        self.scLeftPlotDataItem.setData(x=self.x,y=self.scL)
        self.scTopPlotDataItem.setData(x=self.x,y=self.scT)
        self.scBottomPlotDataItem.setData(x=self.x,y=self.scB)
        self.scRightPlotDataItem.setData(x=self.x,y=self.scR)
    def clearData(self):
        self.scCenterPlotDataItem.clear()
        self.scLeftPlotDataItem.clear()
        self.scTopPlotDataItem.clear()
        self.scBottomPlotDataItem.clear()
        self.scRightPlotDataItem.clear()
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