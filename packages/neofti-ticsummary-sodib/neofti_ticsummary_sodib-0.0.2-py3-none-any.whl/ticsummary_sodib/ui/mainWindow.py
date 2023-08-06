#Project module
from ticsummary_sodib import handlerData
from ticsummary_sodib.ui import  viewGraphicsDialog,profileBeamDock,settingsColorBarDialog,galoBeam, uic as uicFile
#Third party module
from PyQt6 import QtCore, QtGui, QtWidgets, uic
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock
import numpy as np
#Python module
from pkg_resources import resource_listdir,resource_filename
from enum import Enum
import numpy as np
import os
import time
import logging

log = logging.getLogger()

class ModeInterface(Enum):
    DEFFAULT            = (True,False,False,False,False)
    ONLINEDATA          = (True,True,True,True,True)
    MONITORINGDATA      = (True,True,True,False,True)
    
    def __init__(self,editConnectionIsEnabled:bool,editModeShowIsEnabled:bool, plotEnabled:bool,controlDataIsEnabled:bool,calibrationEnabled:bool):
        self.editConnectionIsEnabled = editConnectionIsEnabled
        self.editModeShowIsEnabled = editModeShowIsEnabled
        self.plotEnabled = plotEnabled
        self.controlDataIsEnabled = controlDataIsEnabled
        self.calibrationEnabled = calibrationEnabled

class ColorBarItemWithDoubleClick(pg.ColorBarItem):
    def __init__(self, *args, **kwargs):
        pg.ColorBarItem.__init__(self, *args, **kwargs)
        self.autoscale = True
        # creating a mouse double click event
    def mouseDoubleClickEvent(self, e):
        self.settingsDialog = SettingsColorBarDialog(*self.levels(),self.cmap.name,self.autoscale,self.__setNewparameter__)
        self.settingsDialog.show()
    def __setNewparameter__(self,max,min,cmapstr,autoscale):
        cmap = pg.colormap.get(cmapstr)
        self.setCmap(cmap)
        self._update_items()
        self.maxUser = max
        self.minUser = min
        self.autoscale=autoscale
        if autoscale:
            self.setLevels(values=(self.minImage,self.maxImage))
        else:
            self.setLevels(values=(min,max))
    def setMaxMinImage(self,min,max):
        self.minImage = min
        self.maxImage = max
        if self.autoscale:
            self.setLevels(values=(self.minImage,self.maxImage))
        else:
            self.setLevels(values=(self.minUser,self.maxUser))

class DockAreaWithUncloseableDocks(pg.dockarea.DockArea):
    def makeContainer(self, typ):
        new = super(DockAreaWithUncloseableDocks, self).makeContainer(typ)
        new.setChildrenCollapsible(False)
        return new
            
class MainWindow(QtWidgets.QMainWindow):
    setIdSignal = QtCore.pyqtSignal(int)
    def __init__(self,parent=None):
        super().__init__(parent)
        log.debug("Init main window")
        str = resource_filename(uicFile.__name__, "mainWindow.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.__initValue__()
        self.__initView__()
        self.__initSignal__()

    def __initValue__(self):
        pass

    def __initSignal__(self):
        self.actionControl.triggered.connect(self.openViewGraphicsDialog)
        self.actionResetWindows.triggered.connect(self.__restoreState__)
    
    def __initView__(self):        
        self.dockAreaChart = DockAreaWithUncloseableDocks()
        self.windowsState = self.dockAreaChart.saveState()
        
        self.dProfile = profileBeamDock.ProfileBeamDock(name="MCP profile",size=(1, 1))
        self.dGaloLine = galoBeam.GaloLineDock(name="Counter line", size=(1, 1))
        self.dGaloCounter = galoBeam.GaloCounterDock(name="Counter value", size=(1, 1))
        self.dGaloMonitoring = galoBeam.GaloMonitoringDock(name="Monitoring", size=(1, 1))
        
        self.dockAreaChart.addDock(self.dProfile,"left")
        self.dockAreaChart.addDock(self.dGaloLine,"right")
        self.dockAreaChart.addDock(self.dGaloCounter,"right",self.dGaloLine)
        self.dockAreaChart.addDock(self.dGaloMonitoring,"right",self.dGaloCounter)

        self.verticalLayoutCentral.addWidget(self.dockAreaChart)
        self.setMode(ModeInterface.DEFFAULT)
        self.comboBoxModeShow.addItems(("Online","Monitoring"))
    def setValueLabelDescriptionText(self,sum=None,x=0,y=0,z=0):
        if sum == None:
            sum = self.oldSum
        else:
            self.oldSum = sum
        self.labelDescriptionProfile.setText("Sum={0:.0f} X={1:.0f} Y={2:.0f} Z={3:.0f}".format(sum,x,y,z), size="12pt")
    
    def __restoreState__(self):
        self.dockAreaChart.restoreState(self.windowsState)

    def setMode(self,mode:ModeInterface):
        self.actionEditConnection.setEnabled(mode.editConnectionIsEnabled)
        self.dProfile.setEnabled(mode.plotEnabled)
        self.dGaloLine.setEnabled(mode.plotEnabled)
        self.dGaloCounter.setEnabled(mode.plotEnabled)
        self.dGaloMonitoring.setEnabled(mode.plotEnabled)
        self.spinBoxId.setEnabled(mode.controlDataIsEnabled)
        self.comboBoxModeShow.setEnabled(mode.editModeShowIsEnabled)
        self.pushButtonNext.setEnabled(mode.controlDataIsEnabled)
        self.pushButtonNext.setEnabled(mode.controlDataIsEnabled)
        self.actionDetectorCoeffiecient.setEnabled(mode.calibrationEnabled)

    def setFileLists(self, list:list):
        for file in list:
            self.comboBoxListFiles.addItem(file)

    def setDataMCP(self,data,scaleX,scaleY):
        self.dProfile.setData(data, scaleX, scaleY)
        
    def setDataGalo(self,scL,scR,scT,scB,scCT,x,calibrationGalo = None):
        self.dGaloLine.setData(scL, scR, scT, scB, scCT,x)
        sumScL = np.sum(np.sum(scL))
        sumScR = np.sum(np.sum(scR))
        sumScT = np.sum(np.sum(scT))
        sumScB = np.sum(np.sum(scB))
        sumScCT = np.sum(np.sum(scCT))

        self.dGaloCounter.setData(sumScL, sumScR, sumScT, sumScB, sumScCT)
        if calibrationGalo:
            self.dGaloMonitoring.setData(time.time(), calibrationGalo.getCalibratedValueByGaloValue(sumScL, sumScR, sumScT, sumScB))
        else:
            self.dGaloMonitoring.setData(time.time(), (sumScL+sumScR+sumScT+sumScB)/4)  
    def setIdValue(self,value):
        self.spinBoxId.setValue(value)
    def setMinMaxValueId(self,min,max):
        self.spinBoxId.setMaximum(max)
        self.spinBoxId.setMinimum(min)
    def setModeControlDataButton(self,nextEnabled=None,prevEnabled=None):
        if nextEnabled != None: self.pushButtonNext.setEnabled(nextEnabled)
        if prevEnabled != None: self.pushButtonPrev.setEnabled(prevEnabled)
        
    def showExistingFolderDialog(self, path:str):
        return str(QtWidgets.QFileDialog.getExistingDirectory(parent=self.centralwidget, directory=path))
    def getSaveFile(self):
        return str(QtWidgets.QFileDialog.getSaveFileName(self,directory=os.getcwd(),filter='CSV files (*.csv);')[0])
    def openViewGraphicsDialog(self):
        vgDialog = viewGraphicsDialog.ViewGraphicsDialog(self,not self.dProfile.isHidden(), not self.dGaloLine.isHidden(), not self.dGaloCounter.isHidden(), not self.dGaloMonitoring.isHidden())
        vgDialog.checkBoxProfile.stateChanged.connect(lambda : self.dProfile.show() if self.dProfile.isHidden() else self.dProfile.hide())
        vgDialog.checkBoxLineScintillators.stateChanged.connect(lambda : self.dGaloLine.show() if self.dGaloLine.isHidden() else self.dGaloLine.hide())
        vgDialog.checkBoxValueScintillators.stateChanged.connect(lambda : self.dGaloCounter.show() if self.dGaloCounter.isHidden() else self.dGaloCounter.hide())
        vgDialog.checkBoxMonitoringGalo.stateChanged.connect(lambda : self.dGaloMonitoring.show() if self.dGaloMonitoring.isHidden() else self.dGaloMonitoring.hide())
        vgDialog.show()
    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key.Key_Enter or event.key() ==  QtCore.Qt.Key.Key_Return:
            if self.spinBoxId.hasFocus():
                self.setIdSignal.emit(self.spinBoxId.value())
        
        
        
        
        
        
        