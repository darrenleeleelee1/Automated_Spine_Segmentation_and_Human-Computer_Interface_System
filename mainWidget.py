from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from generatedUiFile.Spine_BrokenUi import Ui_MainWindow
from generatedUiFile.addPtWidget import Ui_Dialog
# class addDialog(QtWidgets.QDialog()):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.ui = Ui_Dialog()
#         self.ui.setupUi(self)
#         self.status
#     def closeEvent(self, event):
WINDOW_SIZE = 0;
        
class initailWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pt_list = []
        self.backend()
        self.ui.menu_toggle.clicked.connect(lambda: self.slideLeftMenu())

        self.ui.minimize_button.clicked.connect(lambda: self.showMinimized())
        self.ui.restore_button.clicked.connect(lambda: self.restore_or_maximize_window())


        def moveWindow(e):
            if self.isMaximized() == False:  # Not maximized

                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.ui.header.mouseMoveEvent = moveWindow

        self.show()

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

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()


    def slideLeftMenu(self):

        width = self.ui.frame_left_menu.width()

        if width == 70:
            newWidth = 200

        else:
            newWidth = 70

        self.animation = QPropertyAnimation(self.ui.frame_left_menu, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(newWidth)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()



    def restore_or_maximize_window(self):
        global WINDOW_SIZE
        win_status = WINDOW_SIZE

        if win_status == 0:
            WINDOW_SIZE = 1
            self.showMaximized()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/cil-window-restore.png"))  # Show minized icon

        else:
            WINDOW_SIZE = 0
            self.showNormal()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/cil-window-maximize.png"))



    
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