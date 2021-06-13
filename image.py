from PyQt5 import QtCore, QtGui, QtWidgets

import requests
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import numpy as np
import matplotlib.pyplot as plt
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        btn = QtWidgets.QPushButton(self.centralwidget)
        btn.setGeometry(600, 600, 60, 40)
        btn.clicked.connect(self.btn_clicked)
        self.photo = QtWidgets.QLabel(self.centralwidget)
        self.photo.setText("AAA")
        self.photo.setScaledContents(True)
        self.photo.setObjectName("photo")
        self.photo.setGeometry(QtCore.QRect(0, 0, 400, 500))

        ds = dcmread('./tmp_database/01372635/5F327951.dcm')
        arr = ds.pixel_array
        arr = np.uint16(arr)
        WL = ds[0x0028, 0x1050].value
        WW = ds[0x0028, 0x1051].value
        arr = self.mappingWindow(arr, WL, WW)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.photo.width(), self.photo.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        # self.photo.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addText("Hello, world!")
        scene.addPixmap(pixmap)
        QGline = QtWidgets.QGraphicsLineItem(0, 0, self.photo.width() / 2, self.photo.height() / 2)
        QGline.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        QGline.setAcceptTouchEvents(True)
        QGline.setAcceptTouchEvents(True)
        scene.addItem(QGline)
        self.view = QtWidgets.QGraphicsView(scene, self.photo)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setGeometry(QtCore.QRect(0, 0, self.photo.width(), self.photo.height()))
        self.angle = 0
        self.view.rotate(self.angle)
        self.view.show()

        MainWindow.setCentralWidget(self.centralwidget)
    def btn_clicked(self):
        self.angle += 90
        self.angle %= 360
        self.view.shear(0, 0.1)
    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
