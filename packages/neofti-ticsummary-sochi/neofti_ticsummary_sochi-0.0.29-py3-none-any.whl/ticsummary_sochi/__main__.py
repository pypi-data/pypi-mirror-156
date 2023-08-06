#Python module
import logging
#Third party module
from PyQt6 import QtWidgets
#Project module
from ticsummary_sochi.model import Model

try:
    import pydevd
    FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
except ImportError:
    log = logging.getLogger()

class EntryPoint:    
    def run(self):
        import sys
        app = QtWidgets.QApplication(sys.argv)
        model = Model()
        log.debug("App Initialize")
        sys.exit(app.exec())

def startup():
    entryPoint = EntryPoint()
    entryPoint.run()

if __name__ == "__main__":
    startup()