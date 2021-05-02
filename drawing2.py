import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen


class App(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 image - tastones.com'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 1200
        self.initUI()
        self.lastPoint = QPoint()  # 起始点
        self.endPoint = QPoint()  # 终点

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        self.pix = QPixmap('/Users/chien/Desktop/專題照片/startview.jpg')


    def paintEvent(self, event):
        pp = QPainter(self.pix)

        pen = QPen()  # 定义笔格式对象
        pen.setWidth(5)  # 设置笔的宽度
        pp.setPen(pen)  # 将笔格式赋值给 画笔

        # 根据鼠标指针前后两个位置绘制直线
        pp.drawLine(self.lastPoint, self.endPoint)
        # 让前一个坐标值等于后一个坐标值，
        # 这样就能实现画出连续的线
        self.lastPoint = self.endPoint
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pix)  # 在画布上画出
        print(type(self.pix))

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())