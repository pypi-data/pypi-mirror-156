#Project module
from ticsummary_sochi.ui.mainWindow import *
from ticsummary_sochi.readerCSV import *
from ticsummary_sochi.handlerData import *
from ticsummary_sochi.readerFiles import *
from ticsummary_sochi.dataWriter import *
from ticsummary_sochi.modeShowData import ModeShowData
from ticsummary_sochi import dataTIC,mysql,inputDataHandler,modeShowData, callibrationGalo
from ticsummary_sochi.ui import serverParametersDialog,dialogCalibrationGalo
#Third party module
from PyQt6 import QtCore
#Python module
import os
import logging
from collections import namedtuple

log = logging.getLogger()

class Model(QtCore.QObject):
    newDataSignal = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.__initValue__()
        self.__initView__()
        self.__initSignal__()
    def __initView__(self):
        self.mainWindow = MainWindow()
        self.mainWindow.show()
    def __initValue__(self):
        self.currentModeSD = ModeShowData.DEFAULT
        self.profile16MCPDescriptionDevice = dataTIC.DescriptionDevice("profile16MCP", 0, 15)
        self.scintillatorLeftUpDescriptionDevice = dataTIC.DescriptionDevice("scintillatorLeftUp", 64, 64)
        self.scintillatorRightUpDescriptionDevice = dataTIC.DescriptionDevice("scintillatorRightUp", 65, 65)
        self.scintillatorLeftBottomDescriptionDevice = dataTIC.DescriptionDevice("scintillatorLeftBottom", 66, 66)
        self.scintillatorRightBottomDescriptionDevice = dataTIC.DescriptionDevice("scintillatorRightBottom", 67, 67)
        self.scintillatorCenterDescriptionDevice = dataTIC.DescriptionDevice("scintillatorCenter", 68, 68)
        self.monitoringData = list()
        self.monitoringTime = list()
        self.currentOnlineIdData = 1
        self.__coefGaloCalibration = callibrationGalo.CalibrationGaloHandler(1, 1, 1, 1)
    def __initSignal__(self):
        self.mainWindow.actionEditConnection.triggered.connect(self.connectDatabase)
        self.mainWindow.comboBoxModeShow.currentTextChanged.connect(self.modeShowIsChanged)
        self.mainWindow.setIdSignal.connect(self.setId)
        self.mainWindow.pushButtonPrev.clicked.connect(self.prevData)
        self.mainWindow.pushButtonNext.clicked.connect(self.nextData)
        self.mainWindow.dGaloMonitoring.clearDataSignal.connect(self.clearMonitoringData)
        self.mainWindow.actionDetectorCoeffiecient.triggered.connect(self.openCalibrationGaloDialog)
    def __del__(self):
        if hasattr(self, "connector"):
            self.connector.close()
    def connectDatabase(self):
        dialog = serverParametersDialog.ConnectServerDialog(self.mainWindow)
        dialog.setModal(True)
        dialog.exec()
        if dialog.result():
            log.debug("server is connected")
            self.mysqlParameters = dialog.getParameters()
            self.connector = mysql.openConnection(self.mysqlParameters)
            self.updateCountRecordDB(mysql.getCountRecords(self.mysqlParameters.table, self.connector))
            self.setModeShow(ModeShowData.ONLINE)
    def setModeShow(self,mode:ModeShowData):
        self.currentModeSD.uninit(self)
        self.currentModeSD = mode
        self.currentModeSD.init(self)
        self.mainWindow.setMode(self.currentModeSD.modeInterface)
    def modeShowIsChanged(self,mode:str):
        if mode == "Online":
            self.setModeShow(ModeShowData.ONLINE)
        elif mode == "Monitoring": 
            self.setModeShow(ModeShowData.MONITORING)
    def setData(self,data:mysql.DownloadData):
        self.dataProfile = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.profile16MCPDescriptionDevice.channelFrom, self.profile16MCPDescriptionDevice.channelTo)
        self.dataScLU = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.scintillatorLeftUpDescriptionDevice.channelFrom, self.scintillatorLeftUpDescriptionDevice.channelTo)
        self.dataScRU = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.scintillatorRightUpDescriptionDevice.channelFrom, self.scintillatorRightUpDescriptionDevice.channelTo)
        self.dataScLB = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.scintillatorLeftBottomDescriptionDevice.channelFrom, self.scintillatorLeftBottomDescriptionDevice.channelTo)
        self.dataScRB = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.scintillatorRightBottomDescriptionDevice.channelFrom, self.scintillatorRightBottomDescriptionDevice.channelTo)
        self.dataScC = inputDataHandler.getMatrixByFromToFilter(data.matrix, self.scintillatorCenterDescriptionDevice.channelFrom, self.scintillatorCenterDescriptionDevice.channelTo)
        x = np.zeros(shape=np.size(self.dataScLU))
        for i in range(np.size(self.dataScLU)):
            x[i] = i
        self.mainWindow.setDataMCP(self.dataProfile, 1, 1)
        self.mainWindow.setDataGalo(self.dataScRU, self.dataScLU, self.dataScRB, self.dataScLB, self.dataScC, x,self.__coefGaloCalibration)
        self.newDataSignal.emit()
    def updateCountRecordDB(self,count = None):
        if count == None: self.countRecordsInDB = mysql.getCountRecords(self.mysqlParameters.table, self.connector)
        else: self.countRecordsInDB = count
        self.mainWindow.setMinMaxValueId(1,self.countRecordsInDB)
    def setId(self,value):
        self.currentModeSD.setId(self,value)
        if self.currentOnlineIdData == self.countRecordsInDB:
            self.mainWindow.setModeControlDataButton(nextEnabled=False)
        else: 
            self.mainWindow.setModeControlDataButton(nextEnabled=True)
        if self.currentOnlineIdData == 1:
            self.mainWindow.setModeControlDataButton(prevEnabled=False)
        else: 
            self.mainWindow.setModeControlDataButton(prevEnabled=True)
    def nextData(self):
        self.currentModeSD.iterationId(self,+1)
        if self.currentOnlineIdData == self.countRecordsInDB:
            self.mainWindow.setModeControlDataButton(nextEnabled=False)
        elif self.currentOnlineIdData == 2:
            self.mainWindow.setModeControlDataButton(prevEnabled=True)
    def prevData(self):
        self.currentModeSD.iterationId(self,-1)
        if self.currentOnlineIdData == 1:
            self.mainWindow.setModeControlDataButton(prevEnabled=False)
        if self.currentOnlineIdData == self.countRecordsInDB - 1:
            self.mainWindow.setModeControlDataButton(nextEnabled=True)
    def getCountRecords(self,table, connector):
        self.countRecordsInDB = self.countRecordsInDB+1
        return self.countRecordsInDB
    def clearMonitoringData(self):
        self.monitoringData = list()
        self.monitoringTime = list()
    def getGaloData(self):
        dataGalo = namedtuple("DataGalo","LeftTop RightTop LeftBottom RightBottom Center")
        result = dataGalo(self.dataScLU,
                        self.dataScRU,
                        self.dataScLB,
                        self.dataScRB,
                        self.dataScC)
        return result
    def openCalibrationGaloDialog(self):
        self.dialogCalibration = dialogCalibrationGalo.CalibrationGaloDialog(self)
        self.newDataSignal.connect(self.dialogCalibration.handlingNewData)
        self.dialogCalibration.accepted.connect(self.getResultCalibration)
        self.dialogCalibration.show()
    def getResultCalibration(self):
        self.__coefGaloCalibration = self.dialogCalibration.getCoefGalo()
    '''def doTimer(self):
        resrand =  mysql.getRecordByRandomDebug(None, None, None)
        randprofile = inputDataHandler.getMatrixByFromToFilter(resrand, self.profile16MCPDescriptionDevice.channelFrom, self.profile16MCPDescriptionDevice.channelTo)
        randscLU = inputDataHandler.getMatrixByFromToFilter(resrand, self.scintillatorLeftUpDescriptionDevice.channelFrom, self.scintillatorLeftUpDescriptionDevice.channelTo)
        randscRU = inputDataHandler.getMatrixByFromToFilter(resrand, self.scintillatorRightUpDescriptionDevice.channelFrom, self.scintillatorRightUpDescriptionDevice.channelTo)
        randscLB = inputDataHandler.getMatrixByFromToFilter(resrand, self.scintillatorLeftBottomDescriptionDevice.channelFrom, self.scintillatorLeftBottomDescriptionDevice.channelTo)
        randscRB = inputDataHandler.getMatrixByFromToFilter(resrand, self.scintillatorRightBottomDescriptionDevice.channelFrom, self.scintillatorRightBottomDescriptionDevice.channelTo)
        randscSC = inputDataHandler.getMatrixByFromToFilter(resrand, self.scintillatorCenterDescriptionDevice.channelFrom, self.scintillatorCenterDescriptionDevice.channelTo)
        x = np.zeros(shape=np.size(randscLB))
        for i in range(np.size(randscLB)):
            x[i] = i
        self.mainWindow.setDataMCP(randprofile, 1, 1)
        self.mainWindow.setDataGalo(randscLU, randscLU, randscLB, randscLB, randscSC, x)'''
    '''def openFolder(self):
        path = self.mainWindow.showExistingFolderDialog(os.curdir)
        if (path !=""):
            self.path = path
            self.filesList = readListFilesInFolder(self.path)
            self.mainWindow.setFileLists(self.filesList)
            self.mainWindow.setMode(ModeInterface.LOCALDATA)
    def setIndexData(self, id:int):
        resultRead = readCSV("{0}/{1}".format(self.path, self.filesList[id]))
        
        self.resultProcess = processDataByMatrix(resultRead.matrix,resultRead.timeSlice)
        
        self.mainWindow.setDataMCP(self.resultProcess.mcp,self.resultProcess.time[1],4)  
        self.mainWindow.setDataGalo(self.resultProcess.scRightUp,self.resultProcess.scLeftUp,self.resultProcess.scRightBottom,self.resultProcess.scLeftBottom,self.resultProcess.scCenter,self.resultProcess.time)
        
    def exportData(self):
        fileName = self.mainWindow.getSaveFile()
        if fileName != '': writeData('{0}.csv'.format(fileName), self.resultProcess)'''