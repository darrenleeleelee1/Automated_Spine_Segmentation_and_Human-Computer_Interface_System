from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene,
                             QGraphicsView, QGraphicsWidget)
from PyQt5.QtCore import Qt, QPointF
import requests
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import numpy as np
import matplotlib.pyplot as plt


class Protractor(QtWidgets.QGraphicsPathItem):
    def __init__(self, qpainterpath):
        super().__init__(qpainterpath)
        self.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.movable = False
    def setMovable(self, enable):
        self.setAcceptHoverEvents(enable)
        self.movable = enable

class Ruler(QtWidgets.QGraphicsItem):
    pass


class GraphicView(QtWidgets.QGraphicsView):
    def __init__(self, sence_width, sence_height, parent):
        super().__init__(parent)
        super().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        super().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, sence_width, sence_height)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        btn = QtWidgets.QPushButton(self.centralwidget)
        btn.setGeometry(600, 600, 60, 40)
        btn.clicked.connect(self.btn_clicked)

        # btn_zoom_in = QtWidgets.QPushButton(self.centralwidget)
        # btn_zoom_in.setGeometry(700, 600, 80, 40)
        # btn_zoom_in.clicked.connect(self.btn_zoom_in_clicked)
        # btn_zoom_in.setText("zoom in")
        #
        # btn_zoom_out = QtWidgets.QPushButton(self.centralwidget)
        # btn_zoom_out.setGeometry(700, 700, 80, 40)
        # btn_zoom_out.clicked.connect(self.btn_zoom_out_clicked)
        # btn_zoom_out.setText("zoom out")

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
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1] * 2, QtGui.QImage.Format_Grayscale16)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.photo.width(), self.photo.height(), QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.SmoothTransformation)
        # self.photo.setPixmap(pixmap)
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(pixmap)
        QGline = QtWidgets.QGraphicsLineItem(0, 0, self.photo.width() / 2, self.photo.height() / 2)
        QGline.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        # self.view = GraphicView(self.photo.width(), self.photo.height(), self.photo)
        self.view = QtWidgets.QGraphicsView(scene, self.photo)
        
        # self.view.scene.addPixmap(pixmap)
        # self.view.scene.addItem(QGline)
        qpoint = QtGui.QPainterPath(QtCore.QPointF(50, 50))
        qpoint.lineTo(QtCore.QPointF(100, 100))
        qpoly = Protractor(qpoint)
        qpoint.lineTo(QtCore.QPointF(300, 200))
        qpoint.moveTo(QtCore.QPointF(512, 512))
        qpoint.lineTo(QtCore.QPointF(300, 200))
        qpoint.clear()
        qpoint.moveTo(QtCore.QPointF(50, 50))
        qpoint.lineTo(QtCore.QPointF(100, 100))
        qpoly.setPath(qpoint)
        scene.addPixmap(pixmap)
        scene.addItem(qpoly)
        print(self.view.size())

        self.view.show()

        MainWindow.setCentralWidget(self.centralwidget)

    def btn_clicked(self):
        self.view.rotate(90)
    #
    # def btn_zoom_in_clicked(self):
    #     self.view.scale(2, 2)
    #
    # def btn_zoom_out_clicked(self):
    #     self.view.scale(0.5, 0.5)

    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW / 2
        pixel_min = WL - WW / 2
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