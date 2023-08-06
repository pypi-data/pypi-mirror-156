from ticsummary_sochi.ui import  uic as uicFile

from PyQt6 import QtCore, QtGui, QtWidgets, uic

from pkg_resources import resource_listdir,resource_filename
import logging

log = logging.getLogger()

class ViewGraphicsDialog(QtWidgets.QDialog):
    def __init__(self, parent, checkBoxProfileEnabled, checkBoxLineScintillatorsEnabled, checkBoxValueScintillatorsEnabled, checkBoxMonitoringGaloEnabled):
        super().__init__(parent)
        log.debug("Init main window")
        str = resource_filename(uicFile.__name__, "viewGraphics.ui")
        log.debug(str)
        uic.loadUi(str, self)
        self.checkBoxProfile.setChecked(checkBoxProfileEnabled)
        self.checkBoxLineScintillators.setChecked(checkBoxLineScintillatorsEnabled)
        self.checkBoxValueScintillators.setChecked(checkBoxValueScintillatorsEnabled)
        self.checkBoxMonitoringGalo.setChecked(checkBoxMonitoringGaloEnabled)
        self.pushButtonClose.clicked.connect(self.close)
    def close(self):
        self.accept()
    def getUI(self):
        return self.ui

if __name__ == "__main__":
    import sys
    
