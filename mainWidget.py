from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from generatedUiFile.Spine_Broken import Ui_MainWindow
from generatedUiFile.addPtWidget import Ui_Dialog
# class addDialog(QtWidgets.QDialog()):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.ui = Ui_Dialog()
#         self.ui.setupUi(self)
#         self.status
#     def closeEvent(self, event):

        
class initailWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pt_list = []
        self.backend()

    def backend(self):
        self.ui.close_button.clicked.connect(QCoreApplication.instance().quit)#叉叉
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint) # 隱藏邊框
        self.ui.add_patient.clicked.connect(self.addPatient)

    def addPatient(self):
        # 開啟add patient
        Dialog = QtWidgets.QDialog()
        apt_widget = Ui_Dialog()
        apt_widget.setupUi(Dialog)
        Dialog.show()
        if (Dialog.exec_() == 1):
            self.pt_list.append(Patient(apt_widget.name_line_edt.text(), apt_widget.bd_day_edt.text(), apt_widget.no_line_edt.text()))
        for i in self.pt_list:
            print(i.name, i.bd, i.no)
    
    
class Patient():
    def __init__(self, _name, _bd, _no):
        self.name = _name
        self.bd = _bd
        self.no = _no
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initailWidget()
    mw.show()
    sys.exit(app.exec_())