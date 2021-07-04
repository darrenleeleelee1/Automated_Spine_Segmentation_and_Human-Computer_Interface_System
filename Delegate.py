from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.thumbnail_list_1 = QtWidgets.QListWidget(self.centralwidget)
        self.thumbnail_list_1.setGeometry(QtCore.QRect(230, 10, 248, 598))
        self.thumbnail_list_1.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.thumbnail_list_1.setViewMode(QtWidgets.QListView.IconMode)
        self.thumbnail_list_1.setObjectName("thumbnail_list_1")
        
        pixmap = QtGui.QPixmap('dog.jpg')
        icon = QtGui.QIcon(pixmap)
        item = QtWidgets.QListWidgetItem(self.thumbnail_list_1)
        item.setIcon(icon)
        item.setSizeHint(QSize(230, 100))
        self.thumbnail_list_1.addItem(item)
        size = QSize(215, 215)
        self.thumbnail_list_1.setIconSize(size)

        item = QtWidgets.QListWidgetItem(self.thumbnail_list_1)
        self.thumbnail_list_1.addItem(item)
        new_item = MyCustomWidget("Darren")
        item.setSizeHint(QSize(219, 100))
        self.thumbnail_list_1.setItemWidget(item, new_item)


        item = QtWidgets.QListWidgetItem(self.thumbnail_list_1)
        self.thumbnail_list_1.addItem(item)
        new_item = MyCustomWidget("Jamie")
        item.setSizeHint(QSize(219, 100))
        self.thumbnail_list_1.setItemWidget(item, new_item)

        pixmap = QtGui.QPixmap('dog.jpg')
        icon = QtGui.QIcon(pixmap)
        item = QtWidgets.QListWidgetItem(self.thumbnail_list_1)
        item.setIcon(icon)
        item.setSizeHint(QSize(219, 100))
        self.thumbnail_list_1.addItem(item)
        size = QSize(215, 215)
        self.thumbnail_list_1.setIconSize(size)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

class MyCustomWidget(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super(MyCustomWidget, self).__init__(parent)

        self.row = QtWidgets.QHBoxLayout()

        self.row.addWidget(QtWidgets.QLabel(name))
        self.row.addWidget(QtWidgets.QLabel("2021"))
        self.row.addWidget(QtWidgets.QLabel("CT"))
        # self.row.addWidget(QtWidgets.QPushButton("view"))
        # self.row.addWidget(QtWidgets.QPushButton("select"))

        self.setLayout(self.row)
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
