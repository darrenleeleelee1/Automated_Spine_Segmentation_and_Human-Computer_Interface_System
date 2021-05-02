from PyQt5 import QtCore, QtGui, QtWidgets

background_image_path = '/Users/chien/Desktop/專題照片/startview.jpg'

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(200, 0, 760, 560))
        self.label.setObjectName("label")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 28))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

#        self._image = QtGui.QPixmap(background_image_path)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
#        self.label.setPixmap(self._image)
        self.label.setText(_translate("MainWindow",
                           """
                           It is not recommended to modify the design file, 
                           it is appropriate to create another file 
                           to join the logic with the design.
                           """))



#    def paintEvent(self, event):
#        painter = QtGui.QPainter(self._image)
#        painter.drawPixmap(self.rect(), self._image)
#        pen = QtGui.QPen()
#        pen.setWidth(5)
#        painter.setPen(pen)
#        painter.drawEllipse(300, 300, 70, 70)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MyApp, self).__init__()

        self.setupUi(self)

        self._image = QtGui.QPixmap(background_image_path)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), self._image)

        #pen = QtGui.QPen()
        #pen.setWidth(5)
        #painter.setPen(pen)
        painter.setPen(QtGui.QPen(QtCore.Qt.blue, 5))
        painter.drawEllipse(350, 350, 70, 70)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

#    MainWindow = QtWidgets.QMainWindow()
#    ui = Ui_MainWindow()
#    ui.setupUi(MainWindow)
#    MainWindow.show()
    window = MyApp()
    window.show()

    sys.exit(app.exec_())