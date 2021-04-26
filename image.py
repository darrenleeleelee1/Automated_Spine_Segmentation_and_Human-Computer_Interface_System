from PyQt5 import QtCore, QtGui, QtWidgets

import requests
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import matplotlib.pyplot as plt
import numpy as np

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo.setText("")
        self.photo.setScaledContents(True)
        self.photo.setObjectName("photo")
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.show_dog()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def show_dog(self):
        # 後端傳回的為FileResponse response.content為bytes
        # response = requests.get('http://127.0.0.1:8000/gdicom/13726235')
        # raw = DicomBytesIO(response.content)
        # ds = dcmread(raw)
        
        ds = dcmread(r'.\tmp\01372635\5F327951')
        print(ds)
        arr = ds.pixel_array
        arr = np.uint8(arr)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
        self.photo.setPixmap(QtGui.QPixmap(qimage))
        self.photo.setGeometry(QtCore.QRect(0, 0, 400, 500))
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())