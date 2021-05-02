import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import requests
import pydicom
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QStyleOption, QStyle
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import matplotlib.pyplot as plt
import numpy as np

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 1200
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.lastPoint = QPoint()  # 起始点
        self.endPoint = QPoint()  # 终点

        self.photo = QtWidgets.QLabel()
        self.photo.setText("")
        self.photo.setScaledContents(True)
        self.photo.setObjectName("photo")

        # self.retranslateUi(MainWindow)
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.show_dog()

    # def retranslateUi(self, MainWindow):
    #     _translate = QtCore.QCoreApplication.translate
    #     MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def show_dog(self):
        # 後端傳回的為FileResponse response.content為bytes
        # response = requests.get('http://127.0.0.1:8000/gdicom/13726235')
        # raw = DicomBytesIO(response.content)
        # ds = dcmread(raw)


        ds = dcmread('./tmp/01372635/5F32917A.dcm')
        arr = ds.pixel_array
        arr = np.uint8(arr)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
        print(type(qimage))

        self.pix = QtGui.QPixmap('/Users/chien/Desktop/專題照片/startview.jpg')
        #self.pix = QPixmap(qimage)
        print(type(self.pix))

        self._image = QtGui.QPixmap(qimage)
        print(type(self._image))

        #self.photo.setPixmap(self.pix)
        #self.photo.setGeometry(QtCore.QRect(0, 0, 500, 500))

        self.photo.setPixmap(QtGui.QPixmap(qimage))
        self.photo.setGeometry(QtCore.QRect(0, 0, 500, 500))



    def paintEvent(self, event):
        #有問題加這四行
        # opt = QStyleOption()
        # opt.initFrom(self)
        # p = QPainter(self)
        # self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

        print("87878787")
        pp = QtGui.QPainter(self._image)
        pen = QPen()  # 定义笔格式对象
        pen.setWidth(5)  # 设置笔的宽度
        pp.setPen(pen)  # 将笔格式赋值给 画笔

        # 根据鼠标指针前后两个位置绘制直线
        pp.drawLine(self.lastPoint, self.endPoint)
        # 让前一个坐标值等于后一个坐标值，
        # 这样就能实现画出连续的线
        self.lastPoint = self.endPoint
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._image)  # 在画布上画出

        # self.photo.setPixmap(self._image)
        # self.photo.setGeometry(QtCore.QRect(0, 0, 500, 500))
        #print(type(self.photo))


    # 鼠标按压事件
    def mousePressEvent(self, event):
        # 鼠标左键按下
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.endPoint = self.lastPoint

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        # 鼠标左键按下的同时移动鼠标
        if event.buttons() and Qt.LeftButton:
            self.endPoint = event.pos()
            # 进行重新绘制
            self.update()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        # 鼠标左键释放
        if event.button() == Qt.LeftButton:
            self.endPoint = event.pos()
            # 进行重新绘制
            self.update()
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())