from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QWidget, QAbstractItemView
class dicom_Dialog(QWidget):
    def setupUi(self, QWidget):
        w = 1000
        h = 500
        # self.name = None
        QWidget.resize(w, h)
        self.lo = QtWidgets.QVBoxLayout(QWidget)
        self.lo.setContentsMargins(0, 0, 0, 0)
        self.dicom_table = QtWidgets.QTableWidget()
        self.dicom_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lo.addWidget(self.dicom_table)
        self.dicom_table.setStyleSheet(
                """QTabelWidget { background-color : #aaa;
                padding: 10px 10px 10px 10px;}""") # Top Right Bottom Left
        self.dicom_table.horizontalHeader().setStretchLastSection(True)
        self.dicom_table.setColumnCount(4)

        self.dicom_table.setColumnWidth(0, 100)
        self.dicom_table.setColumnWidth(1, 250)
        self.dicom_table.setColumnWidth(2, 150)
        self.dicom_table.setColumnWidth(3, 500)
        self.dicom_table.setHorizontalHeaderLabels(["Tag", "Name", "VR", "Value"])
        self.dicom_table.verticalHeader().setVisible(False)
        self.dicom_table.setRowCount(320)
        self.dicom_table.setItem(1, 1, QtWidgets.QTableWidgetItem(1))

        QWidget.setWindowTitle("Meta Data")

            
