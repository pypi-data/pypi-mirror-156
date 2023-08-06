#Project module
from ticsummary_sodib.ui import uic as uicFile
from ticsummary_sodib import callibrationGalo
#Third party module
from PyQt6 import QtCore, QtGui, QtWidgets, uic
import numpy as np
#Python module
from pkg_resources import resource_listdir,resource_filename
import logging
from enum import Enum

log = logging.getLogger()

class ModeInterface(Enum):
    CENTER     = (True,True,False)
    ANOTHER    = (True,True,True)
    CONST      = (False,False,False)
    def __init__(self,coefficientIsReadOnly:bool,startable:bool, anotherValueEnabled:bool):
        self.coefficientIsReadOnly = coefficientIsReadOnly
        self.startable = startable
        self.anotherValueEnabled = anotherValueEnabled

class CalibrationGaloDialog(QtWidgets.QDialog):
    typeCenter = "center scintillator detector"
    typeAnother = "another detector"
    typeConst = "const value"

    def __init__(self, model, parent = None,coefGalo = None):
        super().__init__(parent)
        log.debug("Init connect calibration galo dialog")
        str = resource_filename(uicFile.__name__, "dialogCalibrationGalo.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.model = model
        self.__initValue__()
        self.__initView__(coefGalo)
        self.__initSignal__()
    def __initValue__(self):
        self.handling = False
        self.firstValueNeedInit = False
    def __initView__(self,coefGalo=None):
        self.comboBoxType.addItem(self.typeCenter)
        self.comboBoxType.addItem(self.typeAnother)
        self.comboBoxType.addItem(self.typeConst)
        self.comboBoxTypeIsChanged(self.typeCenter)
        if coefGalo:
            self.doubleSpinBoxLT.setValue(coefGalo.getLeftTop())
            self.doubleSpinBoxRT.setValue(coefGalo.getRightTop())
            self.doubleSpinBoxLB.setValue(coefGalo.getLeftBottom())
            self.doubleSpinBoxRB.setValue(coefGalo.getRightBottom())
    def __initSignal__(self):
        self.comboBoxType.currentTextChanged.connect(self.comboBoxTypeIsChanged)
        self.pushButtonStartStopCalculation.clicked.connect(self.pushButtonStartStopCalculationClicked)
        self.pushButtonSave.clicked.connect(self.pushButtonSaveClicked)
        self.pushButtonCancel.clicked.connect(self.pushButtonCancelClicked)
    def comboBoxTypeIsChanged(self,item):
        if item == self.typeCenter:
            self.setModeInterface(ModeInterface.CENTER)
            self.handlingDef = self.__calculationCoefficientByCenter__
        elif item == self.typeAnother:
            self.setModeInterface(ModeInterface.ANOTHER)
            self.handlingDef = self.__calculationCoefficientByAnother__
        elif item == self.typeConst:
            self.setModeInterface(ModeInterface.CONST)
            self.handlingDef = None
    def setModeInterface(self,mode:ModeInterface):
        self.doubleSpinBoxLT.setReadOnly(mode.coefficientIsReadOnly)
        self.doubleSpinBoxRT.setReadOnly(mode.coefficientIsReadOnly)
        self.doubleSpinBoxLB.setReadOnly(mode.coefficientIsReadOnly)
        self.doubleSpinBoxRB.setReadOnly(mode.coefficientIsReadOnly)
        self.doubleSpinBoxAnotherValue.setEnabled(mode.anotherValueEnabled)
        self.pushButtonStartStopCalculation.setEnabled(mode.startable)
    def pushButtonStartStopCalculationClicked(self):
        if self.pushButtonStartStopCalculation.text() == "Start":
            log.debug("start calculation")
            self.pushButtonStartStopCalculation.setText("Stop")
            self.comboBoxType.setEnabled(False)
            self.firstValueNeedInit = True
            self.handling = True
        elif self.pushButtonStartStopCalculation.text() == "Stop":
            self.handling = False
            log.debug("stop calculation")
            self.pushButtonStartStopCalculation.setText("Start")
            self.comboBoxType.setEnabled(True)
    def pushButtonSaveClicked(self):
        self.__coefGaloResult = callibrationGalo.CalibrationGaloHandler(self.doubleSpinBoxLT.value(), self.doubleSpinBoxRT.value(), self.doubleSpinBoxLB.value(), self.doubleSpinBoxRB.value())
        self.accept()
    def getCoefGalo(self):
        return self.__coefGaloResult
    def pushButtonCancelClicked(self):
        self.close()
    def handlingNewData(self):
        if not self.handling: return
        self.handlingDef()
    def __calculationCoefficientByCenter__(self):
        data = self.model.getGaloData()
        self.__calculationCoefficientByValue__(data,data.Center)
    def __calculationCoefficientByAnother__(self):
        data = self.model.getGaloData()
        self.__calculationCoefficientByValue__(data,self.doubleSpinBoxAnotherValue.value())
    def __calculationCoefficientByValue__(self,data,valueForCalculation):
        if self.firstValueNeedInit:
            self.doubleSpinBoxLT.setValue(np.sum(data.LeftTop)/np.sum(valueForCalculation))
            self.doubleSpinBoxRT.setValue(np.sum(data.RightTop)/np.sum(valueForCalculation))
            self.doubleSpinBoxLB.setValue(np.sum(data.LeftBottom)/np.sum(valueForCalculation))
            self.doubleSpinBoxRB.setValue(np.sum(data.RightBottom)/np.sum(valueForCalculation))
            firstValueNeedInit = False
        else:
            self.doubleSpinBoxLT.setValue((np.sum(data.LeftTop)/np.sum(valueForCalculation) + self.doubleSpinBoxLT)/2)
            self.doubleSpinBoxRT.setValue((np.sum(data.RightTop)/np.sum(valueForCalculation) +  self.doubleSpinBoxRT)/2)
            self.doubleSpinBoxLB.setValue((np.sum(data.LeftBottom)/np.sum(valueForCalculation) + self.doubleSpinBoxLB)/2)
            self.doubleSpinBoxRB.setValue((np.sum(data.RightBottom)/np.sum(valueForCalculation) + self.doubleSpinBoxRB)/2)