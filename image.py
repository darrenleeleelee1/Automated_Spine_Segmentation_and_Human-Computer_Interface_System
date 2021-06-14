from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsLineItem
import requests
from PyQt5.QtCore import QPointF
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import numpy as np
import matplotlib.pyplot as plt

class GraphicView(QtWidgets.QGraphicsView):
    def __init__(self, sence_width, sence_height, parent):
        super().__init__(parent)
        super().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        super().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)       
        self.setSceneRect(0, 0, sence_width, sence_height)


class MovingObject(QGraphicsLineItem):
    def __init__(self):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.setPos(100, 100)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        btn = QtWidgets.QPushButton(self.centralwidget)
        btn.setGeometry(600, 600, 60, 40)
        btn.clicked.connect(self.btn_clicked)
        btn2 = QtWidgets.QPushButton(self.centralwidget)
        btn2.setGeometry(400, 600, 60, 40)
        btn2.clicked.connect(self.btn_clicked2)
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
        QGline = QtWidgets.QGraphicsLineItem(0, 0, self.photo.width() / 2, self.photo.height() / 2)
        QGline.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.view = GraphicView(self.photo.width(), self.photo.height(), self.photo)
        self.view.scene.addPixmap(pixmap)
        self.view.scene.addItem(QGline)
        self.view.show()

        MainWindow.setCentralWidget(self.centralwidget)



    def btn_clicked(self):
        self.view.rotate(90)

    def btn_clicked2(self):
        self.moveObject = MovingObject()
        #self.view.scene.addItem(self.moveObject)

    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))

    def mousePressEvent(self, event):
        pass



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
