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
        self.pic_label_width = 512
        self.pic_label_height = 512
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
        self.ui.restore_button.clicked.connect(lambda: self.restoreOrMaximizeWindow())  # restore window
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
        self.ui.pushButton_rotate.clicked.connect(lambda: self.slideRotateLeftOrRight())    # 打開旋轉的frame
        self.ui.pushButton_rotate_right.clicked.connect(self.rotate_image_right)    #向右旋轉
        self.ui.pushButton_rotate_left.clicked.connect(self.rotate_image_left)  #向左旋轉
        self.ui.zoomIn.clicked.connect(self.image_zoom_in)
        self.ui.zoomOut.clicked.connect(self.image_zoom_out)
        self.ui.pushButton_move.clicked.connect(self.image_move)
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)
        self.ui.pushButton_angle.clicked.connect(self.pushButtonAngleClicked)
        self.ui.pushButton_add_pic.clicked.connect(self.pushButtonAddPicClicked)


    def rotate_image_right(self):
        self.angle = self.angle + 90
        self.showPic(1, 1, "01372635", "5F327951")
        self.showPic(1, 2, "01372635", "5F327951")
        self.showPic(1, 3, "01372635", "5F327951")
        self.showPic(1, 4, "01372635", "5F327951")


    def rotate_image_left(self):
        self.angle = self.angle - 90
        self.showPic(1, 1, "01372635", "5F327951")
        self.showPic(1, 2, "01372635", "5F327951")
        self.showPic(1, 3, "01372635", "5F327951")
        self.showPic(1, 4, "01372635", "5F327951")

    def image_zoom_in(self):
        # if self.size < ?: #上限

        self.pic[1][3].setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.size = self.size * 1.25
        self.showPic(1, 1, "01372635", "5F327951")
        self.showPic(1, 2, "01372635", "5F327951")
        self.showPic(1, 3, "01372635", "5F327951")
        self.showPic(1, 4, "01372635", "5F327951")


    def image_zoom_out(self):
        if self.size > 1:   #下限
            self.size = self.size * 0.8
            self.showPic(1, 1, "01372635", "5F327951")
            self.showPic(1, 2, "01372635", "5F327951")
            self.showPic(1, 3, "01372635", "5F327951")
            self.showPic(1, 4, "01372635", "5F327951")




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
        # self.showPic(1, 1, "01372635","5F327951")


#工具列-----------------------------------------------------------------------------------------------------------
    def picMouseReleased(self, event, _i, _j):
        if event.button()== Qt.LeftButton:
            if(self.pic_clicked[_i][_j]):
                self.pic_released[_i][_j] = True
            else:
                self.pic_released[_i][_j] = False
        print("clicked:%d, released:%d" % (self.pic_clicked[_i][_j], self.pic_released[_i][_j]))

    def picMousePressed(self, event, _i, _j):
        self.pic_ith = _i
        self.pic_jth = _j
        # self.pic_start_x[self.pic_ith][self.pic_jth] = None
        # self.pic_start_y[self.pic_ith][self.pic_jth] = None
        if event.button() == QtCore.Qt.LeftButton:
            if(not self.pic_clicked[_i][_j]):
                self.pic_clicked[_i][_j] = True
                self.pic_start_x[self.pic_ith][self.pic_jth] = event.pos().x()
                self.pic_start_y[self.pic_ith][self.pic_jth] = event.pos().y()
            else:
                self.pic_clicked[_i][_j] = False
        print("clicked:%d, released:%d" % (self.pic_clicked[_i][_j], self.pic_released[_i][_j]))
                
        # if(self.pic_start_x[self.pic_ith][self.pic_jth] != None):
            # print("clicked pic[%s][%s] at (%d, %d)" % (_i, _j, self.pic_start_x[self.pic_ith][self.pic_jth], self.pic_start_y[self.pic_ith][self.pic_jth])) # 說明是哪個pic[_i][_j]被按

    def picMouseMove(self, event):
        # distance_from_center = round(((event.y() - self.pic_start_y[self.pic_ith][self.pic_jth])**2 + (event.x() - self.pic_start_x[self.pic_ith][self.pic_jth])**2)**0.5)
        # self.label.setText('Coordinates: ( %d : %d )' % (event.x(), event.y()) + "Distance from center: " + str(distance_from_center))       
        # print(distance_from_center)
        # q = QtGui.QPainter(self.pic[self.pic_ith][self.pic_jth])
        # q.drawLine(event.x(), event.y(), self.pic_start_x[self.pic_ith][self.pic_jth], self.pic_start_y[self.pic_ith][self.pic_jth])
        if event.buttons() == QtCore.Qt.NoButton:
            if(self.pic_clicked[self.pic_ith][self.pic_jth] and self.pic_released[self.pic_ith][self.pic_jth]):
                self.pic_end_x[self.pic_ith][self.pic_jth] = event.x()
                self.pic_end_y[self.pic_ith][self.pic_jth] = event.y()
        elif event.buttons() == QtCore.Qt.LeftButton:
            if(self.pic_clicked[self.pic_ith][self.pic_jth] and not self.pic_released[self.pic_ith][self.pic_jth]):
                self.pic_middle_x[self.pic_ith][self.pic_jth] = self.pic_end_x[self.pic_ith][self.pic_jth] = event.x()
                self.pic_middle_y[self.pic_ith][self.pic_jth] = self.pic_end_y[self.pic_ith][self.pic_jth] = event.y()
        
        self.update()

    def picPaint(self, event, pixmap, _i, _j):
        """
        print("start(%d, %d)" % (self.pic_start_x[_i][_j], self.pic_start_y[_i][_j]))
        print("middle(%d, %d)" % (self.pic_middle_x[_i][_j], self.pic_middle_y[_i][_j]))
        print("end(%d, %d)" % (self.pic_end_x[_i][_j], self.pic_end_y[_i][_j]))
        """
        q = QtGui.QPainter(self.pic[_i][_j])
        p = QtGui.QPen()
        p.setWidth(6)
        q.setPen(p)
        img_width = self.pic_label_width * self.size
        img_height = self.pic_label_height * self.size
        q.resetTransform()
        q.translate(self.pic_label_width/2, self.pic_label_height/2)
        q.rotate(self.angle)
        q.translate(-self.pic_label_width/2, -self.pic_label_height/2)

        # q.drawPixmap(0, 0, img_width, img_height, pixmap)
        q.drawPixmap(0, 0, img_width, img_height, pixmap)

        q.drawLine(self.pic_middle_x[_i][_j], self.pic_middle_y[_i][_j], self.pic_start_x[_i][_j], self.pic_start_y[_i][_j])
        q.drawLine(self.pic_end_x[_i][_j], self.pic_end_y[_i][_j], self.pic_middle_x[_i][_j], self.pic_middle_y[_i][_j])
        q.end()

    def pushButtonAngleClicked(self):
        return       

    def pushButtonAddPicClicked(self):
        fileName1, filetype = QFileDialog.getOpenFileName(self,"選取檔案","/Users/user/Documents/畢專/dicom_data","All Files (*);;Text Files (*.txt)")  #設定副檔名過濾,注意用雙分號間隔
        print(filetype)
        # fileName2, ok2 = QFileDialog.getSaveFileName(self,"檔案儲存","./","All Files (*);;Text Files (*.txt)")




#MENU選單---------------------------------------------------------------------------------------------------------
    #add patient
    def addPatient(self): 
        dir_choose = QFileDialog.getExistingDirectory(self, "選取資料夾", "/Users/user/Documents/畢專/dicom_data")  # 第三參數是起始路徑
        if dir_choose == "":
            print("\n取消")
            return
        print("\n選擇的資料夾:")
        print(dir_choose)
        pt_id = os.path.basename(dir_choose)

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
            self.duplicateAdd()
        else:
            self.pt_list.append(pt_id)
            self.ui.patient_list.addItem(pt_id)
            self.ui.no_list.clear()
            self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)
        for i in self.pt_list:
            print(i)


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


    def duplicateAdd(self):
        print("test")
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Patient already exist !")
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def image_move(self):
        self.moveImage = True


    def mousePressEvent(self, event):
        if self.moveImage:
            self.ui.pic_1_3.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
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
            self.showPic(1, 1, "01372635", "5F327951")




    # search
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
            
    # list item clicked
    def patient_listItemClicked(self, item):
        print(str(item.text()))
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)

    # menu 伸縮
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

#其他/初始--------------------------------------------------------------------------------------------------------
    def showPic(self, i, j, patient_no, patient_dics):
        dicom_path = "./tmp/" + patient_no + "/" + patient_dics
        ds = dcmread(dicom_path)
        arr = ds.pixel_array
        arr = np.uint8(arr)
        self.qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
        t = QtGui.QTransform()
        t = t.scale(-1, 1)
        self.pic[i][j].move(10, 10)



        # t.rotate(self.angle)
        rotated_img = self.qimage.transformed(t)
        pixmap = QtGui.QPixmap(rotated_img)
        pixmap_resized = pixmap.scaled(self.pic_label_width * self.size, self.pic_label_height * self.size,
                                       QtCore.Qt.KeepAspectRatio)


        self.pic[i][j].setPixmap(pixmap_resized)
        self.pic[i][j].setGeometry(QtCore.QRect(100, 100, 400, 500))
        self.pic[i][j].mousePressEvent = lambda pressed: self.picMousePressed(pressed, i, j) # 讓每個pic的mousePressEvent可以傳出告訴自己是誰
        self.pic[i][j].mouseReleaseEvent = lambda released: self.picMouseReleased(released, i, j)
        self.pic[i][j].mouseMoveEvent = self.picMouseMove
        self.pic[i][j].paintEvent = lambda painted: self.picPaint(painted, pixmap_resized, i, j)

        
    def linkPage2Array(self, MAXIMUM_PAGE = 5, MAXIMUM_PIC = 4):
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
        self.pic = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_start_x = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_start_y = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_middle_x = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_middle_y = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_end_x = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_end_y = [ [None] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_clicked = [ [False] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        self.pic_released = [ [False] * (MAXIMUM_PIC + 1) for i in range(MAXIMUM_PAGE + 1) ]
        var_array_pic = 'self.pic'
        for i in range(1, MAXIMUM_PAGE + 1):
            for j in range(1, (MAXIMUM_PIC + 1)):
                exec("%s[%d][%d] = %s_%d_%d" % (var_array_pic, i, j, var_pic, i, j))
                self.pic[i][j].setText("%d-%d" % (i, j))
                self.pic[i][j].setMouseTracking(True)
                self.pic_start_x[i][j] = self.pic_start_y[i][j] = 0
                self.pic_middle_x[i][j] = self.pic_middle_y[i][j] = 0
                self.pic_end_x[i][j] = self.pic_end_y[i][j] = 0
        # pic_cnt
        self.pic_cnt = [0] * (MAXIMUM_PAGE + 1)
        self.pic_ith = self.pic_jth = 1
        # 暫時試試放照片
        self.showPic(1, 1, "01372635","5F327951")
        self.showPic(1, 2, "01372635","5F327951")
        self.showPic(1, 3, "01372635","5F327951")
        self.showPic(1, 4, "01372635","5F327951")

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def restoreOrMaximizeWindow(self):
        global WINDOW_SIZE
        win_status = WINDOW_SIZE
        if win_status == 0:
            self.pic_1_1_pos_x = 700
            self.pic_1_1_pos_y = 15
            # self.showPic(1, 1, "01372635", "5F327951")
            WINDOW_SIZE = 1
            self.showMaximized()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/window-restore.png"))  # Show minized icon


        else:
            WINDOW_SIZE = 0
            self.pic_1_1_pos_x = 350
            self.pic_1_1_pos_y = 15
            # self.showPic(1, 1, "01372635", "5F327951")
            self.showNormal()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/window-maximize.png"))


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