from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QWidget, QAbstractItemView

class frame_spine_Dialog(QWidget):
    def setupUi(self, QWidget):
        w = 1000
        h = 500
        # self.name = None
        QWidget.resize(w, h)
        self.hbox = QtWidgets.QHBoxLayout(QWidget)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.framedLabel = QtWidgets.QLabel()
        self.framedLabel.setScaledContents(True)
        self.originalLabel = QtWidgets.QLabel()
        self.hbox.addWidget(self.framedLabel)
        self.hbox.addWidget(self.originalLabel)

        
        # QWidget.setWindowTitle("")

            
