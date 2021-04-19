from os import listdir
from os.path import join
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
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
        self.model = QStandardItemModel()

        self.pt_list.append("0135678")
        self.pt_list.append("3847829")
        self.pt_list.append("2342422")

        self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)

        self.backend()

        def moveWindow(e):
            if self.isMaximized() == False:  # Not maximized

                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()

        self.ui.header.mouseMoveEvent = moveWindow  # 移動視窗
        self.show()

    def backend(self):
        self.ui.close_button.clicked.connect(QCoreApplication.instance().quit)  # 叉叉
        self.ui.minimize_button.clicked.connect(lambda: self.showMinimized())  # minimize window
        self.ui.restore_button.clicked.connect(lambda: self.restore_or_maximize_window())  # restore window
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隱藏邊框
        self.ui.menu_toggle.clicked.connect(lambda: self.slideLeftMenu())  # slide menu
        self.ui.add_patient.clicked.connect(self.addPatient)
        self.ui.search.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.search_page))
        self.ui.input_no.editingFinished.connect(self.addEntry)  # 按enter
        self.ui.search_no_button.clicked.connect(self.addEntry)  # 按 search_no
        completer = QCompleter(self.model, self)

        self.ui.patient_list.itemClicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.thumbnail_page))

        self.ui.input_no.setCompleter(completer)  # 搜尋紀錄
        
        

    def addEntry(self):
        entryItem = self.ui.input_no.text()
        if entryItem != '':
            self.ui.input_no.clear()
            self.ui.no_list.clear()

            for id in self.pt_list:
                if id.startswith(entryItem):
                    self.ui.no_list.addItem(id)
        else:
            self.ui.no_list.clear()
            for id in self.pt_list:
                self.ui.no_list.addItem(id)

        list1 = []
        list1.insert(0, entryItem)  # 也把 entryItem 存在 list1 裡傳給後端
        # print("list = ", list1)

        completer = QCompleter(self.model, self)
        self.ui.input_no.setCompleter(completer)

        if not self.model.findItems(entryItem):
            self.model.insertRow(0, QStandardItem(entryItem))
    def duplicate_add(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Patient already exist !")
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()
    def addPatient(self):
        dir_choose = QFileDialog.getExistingDirectory(self, "選取資料夾", "/Users/user/Documents/畢專/dicom_data")  # 第三參數是起始路徑
        if dir_choose == "":
            print("\n取消")
            return

        print("\n選擇的資料夾:")
        print(dir_choose)
        pt_id = os.path.basename(dir_choose)
        
        self.pt_list.append(pt_id)
        self.ui.patient_list.addItem(pt_id)

        self.ui.no_list.clear()
        self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)


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
        if(response.json()['Result'] == 'Directory already exists.'):
            self.duplicate_add()
        


    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def slideLeftMenu(self):
        width = self.ui.frame_left_menu.width()
        if width == 50:
            newWidth = 200
        else:
            newWidth = 50
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