from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QWidget
class dicom_Dialog(QWidget):
    def setupUi(self, QWidget):
        w = 500
        h = 500
        # self.central_widget = QtWidgets.QWidget(Dialog)
        self.name = None
        QWidget.resize(w, h)
        self.layou = QtWidgets.QVBoxLayout(QWidget)
        self.layou.setContentsMargins(0, 0, 0, 0)
        self.meta_label = QtWidgets.QLabel()
        self.layou.addWidget(self.meta_label)
        # self.meta_label.setMinimumSize(QtCore.QSize(10000, 10000))
        self.meta_label.setStyleSheet(
            """QLabel { background-color : #aaa; 
            padding: 10px 10px 10px 10px;}""") # Top Right Bottom Left
        QWidget.setWindowTitle("Meta Data")

            
