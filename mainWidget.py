from os import listdir
from os.path import join
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from generatedUiFile.Spine_BrokenUi import Ui_MainWindow
import os, requests
from PyQt5.QtWidgets import *
WINDOW_SIZE = 0
        
class initialWidget(QtWidgets.QMainWindow):
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
        dir_choose = QFileDialog.getExistingDirectory(self, "選取資料夾", "/Users/user/Documents/畢專/dicom_data") #第三參數是起始路徑
        if dir_choose == "":
            print("\n取消")
            return

        print("\n選擇的資料夾:")
        print(dir_choose)
        pt_id = os.path.basename(dir_choose)
        self.pt_list.append(pt_id)
        self.ui.patient_list.addItem(pt_id)
        for i in self.pt_list:
            print(i)

        # post
        url = 'http://127.0.0.1:8000/pdicom/' + pt_id
        #headers = {'accept': 'application/json', 'Content-Type': 'multipart/form-data'}
        myfiles = listdir(dir_choose)  # 檔案
        dic_file = []
        for f in myfiles:
            # 產生檔案的絕對路徑
            fullpath = join(dir_choose, f)
            # dicom的名字
            dicom_id = os.path.basename(fullpath)
            print(dicom_id)
            print(fullpath)
            dic_file.append(('files', (dicom_id, open(fullpath, 'rb'))))

        response = requests.post(url, files=dic_file)
        print(response.reason)
        print(response.json())

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
    def __init__(self, _pt_id, _pt_path):
        self.pt_id = _pt_id
        self.pt_path = __pt_path


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    mw.show()
    sys.exit(app.exec_())