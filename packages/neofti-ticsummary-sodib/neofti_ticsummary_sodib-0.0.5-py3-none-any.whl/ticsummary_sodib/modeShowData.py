#Project module
from ticsummary_sodib.ui.mainWindow import ModeInterface
from ticsummary_sodib import backWorking, inputDataHandler,mysql
#Third party module
import numpy as np
from PyQt6.QtCore import QTimer
#Python module
from enum import Enum
import logging

log = logging.getLogger()

def onlineInit(model):
    model.mainWindow.setIdValue(model.currentOnlineIdData)
    __onlineSetData(model)
    if model.currentOnlineIdData != 1:
        model.mainWindow.setModeControlDataButton(prevEnabled=True)
    if model.currentOnlineIdData != model.countRecordsInDB:
        model.mainWindow.setModeControlDataButton(nextEnabled=True)
    log.debug("Manual mode init")
def onlineUninit(model):
    pass
def __onlineSetData(model):
    data =  mysql.getRecordByIdFirstBankWithGS(model.mysqlParameters.table, model.connector, model.currentOnlineIdData)
    model.setData(data)
def onlineIterationId(model, it):
    if (model.currentOnlineIdData + it > -1 or model.currentOnlineIdData + it < model.countRecordsInDB):
        model.mainWindow.flagControlKeysOff = True
        model.currentOnlineIdData = model.currentOnlineIdData + it
        model.mainWindow.setIdValue(model.currentOnlineIdData)
        __onlineSetData(model)
        #model.controlerBWTask = factoryThreadByTask(model.__loadDataById__, model.__plotData__,id=model.currentManualIdData,connector=model.connector)
        #model.controlerBWTask.start()
def onlineSetId(model, value):
    if (value > -1 or value < model.countRecordsInDB):
        model.currentOnlineIdData = value
        model.mainWindow.setIdValue(value)
        __onlineSetData(model)

def __stepMonitoring__(model):
    count = mysql.getCountRecords(model.mysqlParameters.table, model.connector)
    if count > model.countRecordsInDB:
        model.countRecordsInDB = count
        data =  mysql.getRecordByIdFirstBankWithGS(model.mysqlParameters.table, model.connector, model.countRecordsInDB)
        model.setData(data)

def monitoringInit(model):
    log.debug("Online mode init")
    #model.realTimeModeOn = True
    model.realTimeModeTimer = QTimer()
    model.realTimeModeTimer.timeout.connect(lambda:__stepMonitoring__(model))
    model.lastCount = 0
    model.realTimeModeTimer.start(1000)
def monitoringUninit(model):
    model.realTimeModeTimer.stop()
def monitoringIterationId(model, it):
    pass
def monitoringSetId(model, value):
    pass

def __emptyMethod__(*args, **kwargs):
    pass

class ModeShowData(Enum):
    DEFAULT     = (__emptyMethod__,__emptyMethod__,__emptyMethod__,__emptyMethod__,__emptyMethod__)
    ONLINE      = (onlineInit,onlineUninit,onlineSetId,onlineIterationId,ModeInterface.ONLINEDATA)
    MONITORING  = (monitoringInit,monitoringUninit,monitoringSetId,monitoringIterationId,ModeInterface.MONITORINGDATA)
    def __init__(self,init,uninit,setId,iterationId,modeInterface):
        self.init = init
        self.uninit = uninit
        self.setId = setId
        self.iterationId = iterationId
        self.modeInterface = modeInterface