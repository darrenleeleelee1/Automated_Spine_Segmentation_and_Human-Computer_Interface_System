from PyQt5 import QtCore, QtGui, QtWidgets

import requests
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import numpy as np
import matplotlib.pyplot as plt
from PhotoViewer import PhotoViewer
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.photo = QtWidgets.QLabel(self.centralwidget)
        ds = dcmread('./tmp_database/01372635/5F327951.dcm')
        arr = ds.pixel_array
        arr = np.uint16(arr)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16)
        pointer = PhotoViewer()
        pointer.setPhoto(qimage)
        self.gridLayout_1 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_1.addWidget(qimage)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
