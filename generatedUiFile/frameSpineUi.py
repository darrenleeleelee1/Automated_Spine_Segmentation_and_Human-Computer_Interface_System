from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QAbstractItemView

class frame_spine_Dialog(QWidget):
    def setupUi(self, QWidget):
        w = 1000
        h = 500
        # self.name = None
        QWidget.resize(w, h)
        self.hbox = QtWidgets.QHBoxLayout(QWidget)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.originalLabel = QtWidgets.QLabel()
        self.originalLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Ignored)
        self.originalLabel.setStyleSheet("background-color:#000;")
        self.originalLabel.setAlignment(Qt.AlignCenter)
        self.framedLabel = QtWidgets.QLabel()
        self.framedLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.framedLabel.setStyleSheet("background-color:#000;")
        self.framedLabel.setAlignment(Qt.AlignCenter)
        self.hbox.addWidget(self.originalLabel)
        self.hbox.addWidget(self.framedLabel)
