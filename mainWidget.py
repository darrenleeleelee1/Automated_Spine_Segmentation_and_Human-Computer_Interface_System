from os import listdir
from os.path import join
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent, QPointF)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QTransform, QPainter
from generatedUiFile.Spine_BrokenUi import Ui_MainWindow
import os, requests
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from pydicom import dcmread
from pydicom.filebase import DicomBytesIO
import numpy as np
WINDOW_SIZE = 0




class initialWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pt_list = []
        self.model = QStandardItemModel()
        self.angle = 0
        self.size = 1
        self.pic_1_1_pos_x = 350
        self.pic_1_1_pos_y = 15
        self.img_width = 300
        self.img_height = 300
        self.moveImage = False
        self.moveX = 0
        self.moveY = 0


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
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.recently_viewed_page)
        self.ui.close_button.clicked.connect(QCoreApplication.instance().quit)  # 叉叉
        self.ui.minimize_button.clicked.connect(lambda: self.showMinimized())  # minimize window
        self.ui.restore_button.clicked.connect(lambda: self.restore_or_maximize_window())  # restore window
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隱藏邊框
        self.ui.menu_toggle.clicked.connect(lambda: self.slideLeftMenu())  # slide menu
        self.ui.add_patient.clicked.connect(self.addPatient)
        self.ui.search.clicked.connect(lambda: self.ui.stackedWidget_right.setCurrentWidget(self.ui.search_page))
        self.ui.input_no.editingFinished.connect(self.addEntry)  # 按enter
        self.ui.search_no_button.clicked.connect(self.addEntry)  # 按 search_no
        completer = QCompleter(self.model, self)
        self.ui.patient_list.itemClicked.connect(lambda: self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page))

        self.ui.input_no.setCompleter(completer)  # 搜尋紀錄
        self.linkPage2Array() # 將影像處理頁面預設有五頁

        self.ui.pushButton_magnifier.clicked.connect(lambda: self.slideZoomInOrOut())  # 打開放大縮小的frame
        self.ui.pushButton_rotate.clicked.connect(lambda: self.slideRotateLeftOrRight())    # 打開左旋or右旋的frame
        self.ui.pushButton_rotate_right.clicked.connect(self.rotate_image_right)
        self.ui.pushButton_rotate_left.clicked.connect(self.rotate_image_left)
        self.ui.zoomIn.clicked.connect(self.image_zoom_in)
        self.ui.zoomOut.clicked.connect(self.image_zoom_out)
        self.ui.pushButton_move.clicked.connect(self.image_move)


    def show_pic(self, i, j, patient_no, patient_dics):
        dicom_path = "./tmp/" + patient_no + "/" + patient_dics
        ds = dcmread(dicom_path)
        arr = ds.pixel_array
        arr = np.uint8(arr)
        self.qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
        # self.pic[i][j].setPixmap(QtGui.QPixmap(self.qimage))
        # self.pic[i][j].setGeometry(QtCore.QRect(self.pic_1_1_pos_x - (self.size - 1)*self.img_width, self.pic_1_1_pos_y - (self.size - 1)*self.img_width, self.img_width * self.size, self.img_width * self.size))
        # self.pic[i][j].move(self.pic_1_1_pos_x + self.moveX, self.pic_1_1_pos_y+self.moveY)
        self.pic[i][j].move(self.pic_1_1_pos_x, self.pic_1_1_pos_y)
        # self.pic[i][j].setGeometry(QtCore.QRect(300, 15, 300, 300))

        t = QtGui.QTransform()
        t.translate(150, 150)
        realAngle = self.angle * 90
        t.rotate(realAngle)
        rotated_img = self.qimage.transformed(t)

        pixmap = QtGui.QPixmap(rotated_img)
        pixmap_resized = pixmap.scaled(self.img_width * self.size, self. img_height * self.size, QtCore.Qt.KeepAspectRatio)


        # self.pic[i][j].adjustSize()



        self.pic[i][j].setPixmap(pixmap_resized)


    def rotate_image_right(self):
        self.angle = self.angle + 1
        self.show_pic(1, 1, "01372635", "5F327951")

    def rotate_image_left(self):
        self.angle = self.angle - 1
        self.show_pic(1, 1, "01372635", "5F327951")

    def image_zoom_in(self):
        self.size = self.size * 1.25
        self.show_pic(1, 1, "01372635", "5F327951")

    def image_zoom_out(self):
        if self.size > 1:
            self.size = self.size * 0.8
            self.show_pic(1, 1, "01372635", "5F327951")





    def linkPage2Array(self, MAXIMUM_PAGE = 5):
        # 把QtDesigner的一些重複的Widget用array對應
        # patient_page
        var_patient_page = 'self.ui.patient_page'
        self.patient_page = [None] * (MAXIMUM_PAGE + 1)
        var_array_patient_page = 'self.patient_page'
        for i in range(1, MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_patient_page, i, var_patient_page, i))
        # thumbnail_list
        var_thumbnail_list = 'self.ui.thumbnail_list'
        self.thumbnail_list = [None] * (MAXIMUM_PAGE + 1)
        var_array_thumbnail_list = 'self.thumbnail_list'
        for i in range(1, MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_thumbnail_list, i, var_thumbnail_list, i))
        # pics
        var_pic = 'self.ui.pic'
        self.pic = [ [None] * 5 for i in range(MAXIMUM_PAGE + 1)]
        var_array_pic = 'self.pic'
        for i in range(1, MAXIMUM_PAGE + 1):
            for j in range(1, 5):
                exec("%s[%d][%d] = %s_%d_%d" % (var_array_pic, i, j, var_pic, i, j))
                self.pic[i][j].setText("%d-%d" % (i, j))

        # pic_cnt
        self.pic_cnt = [0] * (MAXIMUM_PAGE + 1)


        # 暫時試試放照片
        self.show_pic(1, 1, "01372635","5F327951")


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


    def slideZoomInOrOut(self):
        zoom_frame_width = self.ui.zoom_frame.width()
        if zoom_frame_width == 0:
            new_zoom_frame_width = 100

        else:
            new_zoom_frame_width = 0
        self.animation = QPropertyAnimation(self.ui.zoom_frame, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(zoom_frame_width)
        self.animation.setEndValue(new_zoom_frame_width)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()


    def slideRotateLeftOrRight(self):
        rotate_frame_width = self.ui.rotate_frame.width()
        if rotate_frame_width == 0:
            new_rotate_frame_width = 100

        else:
            new_rotate_frame_width = 0
        self.animation = QPropertyAnimation(self.ui.rotate_frame, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(rotate_frame_width)
        self.animation.setEndValue(new_rotate_frame_width)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()




    def mousePressEvent(self, event):
        if self.moveImage:
            self.clickPosition = event.globalPos()
            self.moveX = event.x()
            self.moveY = event.y()
            print(event.globalPos())



    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.LeftButton:
    #         self.destion = event.pos()
    #         self.update()

    def mouseReleaseEvent(self, event):
        if self.moveImage:
            self.moveX = event.x() - self.moveX
            self.moveY = event.y() - self.moveY
            print(event.globalPos())
            print(self.moveX, self.moveY)
            self.show_pic(1, 1, "01372635", "5F327951")



    def image_move(self):
        self.moveImage = True








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
            self.pic_1_1_pos_x = 700
            self.pic_1_1_pos_y = 15
            self.show_pic(1, 1, "01372635", "5F327951")
            WINDOW_SIZE = 1
            self.showMaximized()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/window-restore.png"))  # Show minized icon


        else:
            WINDOW_SIZE = 0
            self.pic_1_1_pos_x = 350
            self.pic_1_1_pos_y = 15
            self.show_pic(1, 1, "01372635", "5F327951")
            self.showNormal()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/window-maximize.png"))



class Patient():
    def __init__(self, _pt_id, _pt_path):
        self.pt_id = _pt_id
        self.pt_path = __pt_path

class image(QtWidgets.QLabel):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        self.updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        self.updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(self.updated_cursor_x, self.updated_cursor_y))

    def mouseReleaseEvent(self, event):
        print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    mw.show()
    sys.exit(app.exec_())