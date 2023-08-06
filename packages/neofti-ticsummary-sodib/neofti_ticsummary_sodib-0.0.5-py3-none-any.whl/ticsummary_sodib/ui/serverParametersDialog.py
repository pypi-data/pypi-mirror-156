#Project module
from ticsummary_sodib import mysql
from ticsummary_sodib.ui import  viewGraphicsDialog, uic as uicFile
#Third party module
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import numpy as np
#Python module
from pkg_resources import resource_listdir,resource_filename
import json
import os
import logging

log = logging.getLogger()

class ConnectServerDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, parameters:mysql.ParametersConnection=None):
        super().__init__(parent)
        log.debug("Init connect server dialog")
        str = resource_filename(uicFile.__name__, "connectServer.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.pushButtonRead.clicked.connect(self.readParameters)
        self.pushButtonApply.clicked.connect(self.apply)
        self.pushButtonCancel.clicked.connect(self.cancel)
        if not parameters == None:
            self.__setParameters__(parameters)
        
    def readParameters(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', "", "Json files (*.json)")[0]
        try:
            with open(fname, "r") as file:
                data = json.load(file)
            parameters = mysql.ParametersConnection(username=data['Settings']['SQL']['Username'],
                                    password=data['Settings']['SQL']['Password'],
                                    host=data['Settings']['SQL']['Host'],
                                    database=data['Settings']['SQL']['Database'],
                                    table=data['Settings']['SQL']['Table'],
                                    port=int(data['Settings']['SQL']['Port']))
            self.__setParameters__(parameters)
        except Exception as e:
            print("Error while read configuration:", e)
    def __setParameters__(self,parameters:mysql.ParametersConnection):
        self.lineEditHost.setText(parameters.host)
        self.spinBoxPort.setValue(parameters.port)
        self.lineEditDB.setText(parameters.database)
        self.lineEditUsername.setText(parameters.username)
        self.lineEditPassword.setText(parameters.password)
        self.lineEditTable.setText(parameters.table)
    def getParameters(self):
        return mysql.ParametersConnection(self.lineEditUsername.text(),
                                      self.lineEditPassword.text(),
                                      self.lineEditHost.text(),
                                      self.lineEditDB.text(),
                                      self.lineEditTable.text(),
                                      self.spinBoxPort.value())
    def apply(self):
        if mysql.parametersIsValid(self.getParameters()):
            self.accept()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle("Error message")
            msgBox.setText("Database not connected or table empty.")
            msgBox.exec()
    def cancel(self):
        self.reject()
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = ConnectServerDialog()
    dialog.exec()
    sys.exit(app.exec())    