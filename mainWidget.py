from os import listdir
import math
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
from PIL import ImageQt
import shutil
WINDOW_SIZE = 0




class initialWidget(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pt_list = []
        self.model = QStandardItemModel()
        self.pic_label_width = 512
        self.pic_label_height = 512

        self.pt_list.append("0135678")
        self.pt_list.append("3847829")
        self.pt_list.append("2342422")

        self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)

        self.tmp_cnt = 0

        # 控制工具列現在選擇的工具為: mouse(defalut), pen, angle, ruler, move
        self.tool_lock = "mouse"
         # patient num map to page
        self.empty_page_stack = []
        for i in range(5, 0, -1):
            self.empty_page_stack.append(i)
        self.patient_mapto_page = {}

        self.ui.patient_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #右键菜单
        self.ui.patient_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.patient_list.customContextMenuRequested.connect(self.myListWidgetContext)

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
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)
        self.ui.no_list.itemClicked.connect(self.no_listItemClicked)
        self.ui.input_no.setCompleter(completer)  # 搜尋紀錄
        self.linkPage2Array() # 將影像處理頁面預設有五頁
        self.ui.pushButton_angle.clicked.connect(self.pushButtonAngleClicked) # 角度按鈕連結
        self.ui.pushButton_add_pic.clicked.connect(self.pushButtonAddPicClicked) # 加照片按鈕連結

        self.ui.pushButton_pen.clicked.connect(self.pushButtonPenClicked)   # 畫筆按鈕連結
        self.ui.pushButton_save.clicked.connect(self.pushButtonSaveClicked) # 儲存照片按鈕連結
        self.ui.pushButton_magnifier.clicked.connect(lambda: self.slideMagnifierZoomInOrOut())  # 打開放大縮小的frame

        self.ui.pushButton_rotate.clicked.connect(lambda: self.slideRotateLeftOrRight())    # 打開旋轉的frame
        self.ui.pushButton_rotate_right.clicked.connect(self.rotate_image_right)    #向右旋轉
        self.ui.pushButton_rotate_left.clicked.connect(self.rotate_image_left)  #向左旋轉
        self.ui.zoomIn.clicked.connect(self.image_zoom_in)
        self.ui.zoomOut.clicked.connect(self.image_zoom_out)
        self.ui.pushButton_move.clicked.connect(self.pushButtonMoveClicked)
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)

#工具列-----------------------------------------------------------------------------------------------------------
    def picMouseReleased(self, event, _i, _j):
        if(self.tool_lock == 'mouse'):
            return
        elif(self.tool_lock == 'angle'):
            if event.button() == Qt.LeftButton:
                if(self.pic_clicked[_i][_j]):
                    self.pic_released[_i][_j] = True
                else:
                    if(self.tsx[_i][_j] != self.tmx[_i][_j] and self.tsy[_i][_j] != self.tmy[_i][_j]):
                        self.angle_coordinate_list[_i][_j].append(angleCoordinate(
                            self.tsx[_i][_j], self.tsy[_i][_j],
                            self.tmx[_i][_j], self.tmy[_i][_j],
                            self.tex[_i][_j], self.tey[_i][_j]
                            ))
                        self.tsx[_i][_j] = self.tmx[_i][_j] = 0
                        self.tsy[_i][_j] = self.tmy[_i][_j] = 0
                    self.pic_released[_i][_j] = False
        elif(self.tool_lock == 'pen'):
            return
        elif(self.tool_lock == 'zoom_in'):
            self.size_last[_i][_j] = self.size[_i][_j]
            # print(self.size[self.pic_ith][self.pic_jth])

        elif (self.tool_lock == 'zoom_out'):
            self.size_last[_i][_j] = self.size[_i][_j]
            # print(self.size[self.pic_ith][self.pic_jth])


        elif(self.tool_lock == 'move'):

            self.move_x[_i][_j] = self.move_x[_i][_j] + event.x() - self.move_start_x[_i][_j]
            self.move_y[_i][_j] = self.move_y[_i][_j] + event.y() - self.move_start_y[_i][_j]
            return

    def picMousePressed(self, event, _i, _j):
        self.pic_ith = _i
        self.pic_jth = _j
        if(self.tool_lock == 'mouse'):
            # print(_i, _j)
            return
        elif(self.tool_lock == 'angle'):
            if event.button() == QtCore.Qt.LeftButton:
                if(not self.pic_clicked[_i][_j]):
                    self.pic_clicked[_i][_j] = True
                    self.angle_start_x[self.pic_ith][self.pic_jth] = event.pos().x()
                    self.angle_start_y[self.pic_ith][self.pic_jth] = event.pos().y()
                    print("i ", self.pic_ith, " j ", self.pic_jth)
                else:
                    self.pic_clicked[_i][_j] = False
        elif(self.tool_lock == 'pen'):
            if event.button() == QtCore.Qt.LeftButton:
                self.pen_end_x[_i][_j] = event.x()
                self.pen_end_y[_i][_j] = event.y()
                self.pen_start_x[self.pic_ith][self.pic_jth] = event.pos().x()
                self.pen_start_y[self.pic_ith][self.pic_jth] = event.pos().y()

        elif (self.tool_lock == 'zoom_in'):
            self.size[_i][_j] = self.size_last[_i][_j] * 1.25
            self.magnifier_pad_x[_i][_j] = self.magnifier_pad_x[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().x()
            self.magnifier_pad_y[_i][_j] = self.magnifier_pad_y[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().y()

            print("size", self.size_last[_i][_j], self.size[_i][_j])
        elif(self.tool_lock == 'zoom_out'):
            if (self.size[_i][_j] > 1):
                # self.size[_i][_j] = self.size[_i][_j] * 0.75
                # self.move_moving_x[_i][_j] = self.move_moving_x[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().x()
                # self.move_moving_y[_i][_j] = self.move_moving_y[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().y()

                self.size[_i][_j] = self.size[_i][_j] * 0.8
                self.magnifier_pad_x[_i][_j] = self.magnifier_pad_x[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().x()
                self.magnifier_pad_y[_i][_j] = self.magnifier_pad_y[_i][_j] - (self.size[_i][_j] - self.size_last[_i][_j]) * event.pos().y()


                # print(self.move_moving_x[_i][_j], self.move_moving_y[_i][_j])
        elif(self.tool_lock == 'move'):
            if event.button() == QtCore.Qt.LeftButton:
                self.move_start_x[_i][_j] = event.x()
                self.move_start_y[_i][_j] = event.y()
        self.update()

    def picMouseMove(self, event, _i, _j):
        # distance_from_center = round(((event.y() - self.pic_start_y[self.pic_ith][self.pic_jth])**2 + (event.x() - self.pic_start_x[self.pic_ith][self.pic_jth])**2)**0.5)
        # self.label.setText('Coordinates: ( %d : %d )' % (event.x(), event.y()) + "Distance from center: " + str(distance_from_center))
        # print(distance_from_center)
        if(self.tool_lock == 'mouse'):
            return
        elif(self.tool_lock == 'angle'):
            if event.buttons() == QtCore.Qt.NoButton:
                if(self.pic_clicked[self.pic_ith][self.pic_jth] and self.pic_released[self.pic_ith][self.pic_jth]):
                    self.angle_end_x[self.pic_ith][self.pic_jth] = event.x()
                    self.angle_end_y[self.pic_ith][self.pic_jth] = event.y()
            elif event.buttons() == QtCore.Qt.LeftButton:
                if(self.pic_clicked[self.pic_ith][self.pic_jth] and not self.pic_released[self.pic_ith][self.pic_jth]):
                    self.angle_middle_x[self.pic_ith][self.pic_jth] = self.angle_end_x[self.pic_ith][self.pic_jth] = event.x()
                    self.angle_middle_y[self.pic_ith][self.pic_jth] = self.angle_end_y[self.pic_ith][self.pic_jth] = event.y()
        elif(self.tool_lock == 'pen'):
            if event.buttons() == QtCore.Qt.LeftButton:
                self.pen_start_x[self.pic_ith][self.pic_jth] = self.pen_end_x[_i][_j]
                self.pen_start_y[self.pic_ith][self.pic_jth] = self.pen_end_y[_i][_j]
                self.pen_end_x[_i][_j] = event.x()
                self.pen_end_y[_i][_j] = event.y()
        elif(self.tool_lock == 'move'):
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move_end_x[_i][_j] = event.x()
                self.move_end_y[_i][_j] = event.y()
                self.move_moving_x[_i][_j] = self.move_end_x[_i][_j] - self.move_start_x[_i][_j] +self.move_x[_i][_j]
                self.move_moving_y[_i][_j] = self.move_end_y[_i][_j] - self.move_start_y[_i][_j] +self.move_y[_i][_j]
        self.update()



    def picPaint(self, event, pixmap, _i, _j):
        # if _i == self.pic_ith and _j == self.pic_jth:
        #     self.rotate_angle[_i][_j] = self.rotate_angle[self.pic_ith][self.pic_jth]
        q = QtGui.QPainter(self.pic[_i][_j])
        q.resetTransform()
        q.translate(self.pic_label_width / 2, self.pic_label_height / 2)  # 把旋轉中心設成（pic_label_width/2, pic_label_height/2）
        q.rotate(self.rotate_angle[_i][_j])
        q.translate(-self.pic_label_width / 2, -self.pic_label_height / 2)
        img_width = self.pic_label_width * self.size[_i][_j]
        img_height = self.pic_label_height * self.size[_i][_j]

        x = self.move_moving_x[_i][_j]+ self.magnifier_pad_x[_i][_j]
        y = self.move_moving_y[_i][_j]+ self.magnifier_pad_y[_i][_j]
        q.drawPixmap(x, y, img_width, img_height, pixmap)
        p = QtGui.QPainter(self.transparent_pix[_i][_j])

        if(self.tool_lock == 'mouse'):
            return
        elif(self.tool_lock == 'angle'):
            if(not self.pic_clicked[_i][_j] and not self.pic_released[_i][_j]):
                pass
            else:
                self.pic[_i][_j].setMouseTracking(True)

                pen = QtGui.QPen()
                pen.setWidth(6)
                q.setPen(pen)

                # tsx = transitved start x
                self.tsx[_i][_j], self.tsy[_i][_j] = self.transitiveMatrix(self.angle_start_x[_i][_j], self.angle_start_y[_i][_j], self.rotate_angle[_i][_j])
                self.tmx[_i][_j], self.tmy[_i][_j] = self.transitiveMatrix(self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j], self.rotate_angle[_i][_j])
                self.tex[_i][_j], self.tey[_i][_j] = self.transitiveMatrix(self.angle_end_x[_i][_j], self.angle_end_y[_i][_j], self.rotate_angle[_i][_j])


                # q.drawLine(self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j], self.angle_start_x[_i][_j], self.angle_start_y[_i][_j])
                # q.drawLine(self.angle_end_x[_i][_j], self.angle_end_y[_i][_j], self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j])


                q.drawLine(self.tmx[_i][_j], self.tmy[_i][_j], self.tsx[_i][_j], self.tsy[_i][_j])
                q.drawLine(self.tex[_i][_j], self.tey[_i][_j], self.tmx[_i][_j], self.tmy[_i][_j])

        elif(self.tool_lock == 'pen'):
            self.pic[_i][_j].setMouseTracking(False)
            pen = QtGui.QPen()
            pen.setWidth(6)
            p.setPen(pen)
            tpsx, tpsy = self.transitiveMatrix(self.pen_start_x[_i][_j], self.pen_start_y[_i][_j], self.rotate_angle[_i][_j])
            tpex, tpey = self.transitiveMatrix(self.pen_end_x[_i][_j], self.pen_end_y[_i][_j], self.rotate_angle[_i][_j])
            p.drawLine(tpex, tpey, tpsx, tpsy)

        q.drawPixmap(0, 0, self.transparent_pix[_i][_j])
        # show every angle
        for w in self.angle_coordinate_list[_i][_j]:
            pen = QtGui.QPen()
            pen.setWidth(6)
            q.setPen(pen)
            q.drawPolyline(w.points)


        q.end()
        # q.resetTransform()


#按鈕連結處--------------------------------------------------------------------------------------------------------

    def pushButtonAngleClicked(self):
        self.tool_lock = 'angle'

    def pushButtonAddPicClicked(self):
        pic_file_path, filetype = QFileDialog.getOpenFileName(self,"選取檔案","/Users/user/Documents/畢專/dicom_data","All Files (*);;Text Files (*.txt)")  #設定副檔名過濾,注意用雙分號間隔
        print(filetype)
        # copyfile(pic_file_path, dst)
        #backend
        # fileName2, ok2 = QFileDialog.getSaveFileName(self,"檔案儲存","./","All Files (*);;Text Files (*.txt)")

    def pushButtonPenClicked(self):
        self.tool_lock = 'pen'

    # save photo .png
    def pushButtonSaveClicked(self):
        image = ImageQt.fromqpixmap(self.pic[self.pic_ith][self.pic_jth].grab())
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png)") # ;;JPEG(*.jpg *.jpeg);;All Files(*.*) 
        if filePath == "":
            return
        image.save(filePath)

    def rotate_image_right(self):
        self.tool_lock = 'rotate'
        self.rotate_angle[self.pic_ith][self.pic_jth] = self.rotate_angle[self.pic_ith][self.pic_jth] + 90
        self.update()


    def rotate_image_left(self):
        self.tool_lock = 'rotate'
        self.rotate_angle[self.pic_ith][self.pic_jth] = self.rotate_angle[self.pic_ith][self.pic_jth] - 90
        self.update()

    def image_zoom_in(self):
        self.tool_lock = 'zoom_in'

    def image_zoom_out(self):
        self.tool_lock = 'zoom_out'

    def pushButtonMoveClicked(self):
        self.tool_lock = 'move'

    #MENU選單---------------------------------------------------------------------------------------------------------
    #add patient
    


    def slideMagnifierZoomInOrOut(self):
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




    # def pushButtonBrightnessClicked(self):
#MENU選單---------------------------------------------------------------------------------------------------------
    def addPatient(self): 
        if(not self.empty_page_stack):
                self.pageFull()
        else:
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
                self.open_pt_page(pt_id)
                self.pt_list.append(pt_id)
                self.ui.patient_list.addItem(pt_id)
                self.ui.no_list.clear()
                self.pt_list.sort()
                for ptid in self.pt_list:
                    self.ui.no_list.addItem(ptid)
                for i in self.pt_list:
                    print(i)    
                self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
                temp_page = self.patient_mapto_page[pt_id]
                self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])

                
    def open_pt_page(self, pt_id): #記得要先檢查self.empty_page_stack空->Page滿->pageFull, 用在add和pt_list中打開
        temp = self.empty_page_stack[-1]
        self.empty_page_stack.pop()
        self.patient_mapto_page[pt_id] = temp

    def pageFull(self):
        pageFull_msg = QMessageBox()
        pageFull_msg.setWindowTitle("Warning")
        pageFull_msg.setText("Patient page full !\nPlease close some pages and try again.")
        pageFull_msg.setIcon(QMessageBox.Warning)
        x = pageFull_msg.exec_() 

    def duplicateAdd(self):
        duplicateAdd_msg = QMessageBox()
        duplicateAdd_msg.setWindowTitle("Warning")
        duplicateAdd_msg.setText("Patient already exist !")
        duplicateAdd_msg.setIcon(QMessageBox.Warning)
        x = duplicateAdd_msg.exec_() 

    # list item clicked
    def patient_listItemClicked(self, item):
        print(str(item.text()))
        if(str(item.text()) == '1'):
            self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
            self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[0])
        else:
            self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
            temp = str(item.text())
            temp_page = self.patient_mapto_page[temp]
            self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])

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

    def closePatient(self): # 關閉patient編輯，tmp 也要刪除
        curRow = self.ui.patient_list.currentRow()
        get_close_id = self.ui.patient_list.item(curRow)
        close_id = str(get_close_id.text())
        tmp = self.patient_mapto_page[close_id]
        self.empty_page_stack.append(tmp)
        self.patient_mapto_page[close_id] = -1
        self.ui.patient_list.takeItem(self.ui.patient_list.currentRow())
        close_path = "./tmp/" + close_id
        for filename in os.listdir(close_path):
            file_path = close_path + '/' + filename
            print(file_path)
            os.remove(file_path)
        os.rmdir(close_path)
# search page-----------------------------------------------------------------------------------------------------
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

    # open patient
    def no_listItemClicked(self, item):
        #print(str(item.text()))
        if(not self.empty_page_stack):
                self.pageFull()
        else:
            pt_id = str(item.text())
            if(self.patient_mapto_page[pt_id] == -1): # patient list還沒有 -> 打開新page並加到patient list
                # 檔案加到tmp還沒做 ???
                self.open_pt_page(pt_id)
                self.ui.patient_list.addItem(pt_id)
                #self.databaseToTmp(pt_id)
            # patient list中已存在 直接打開
            self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
            temp_page = self.patient_mapto_page[pt_id]
            self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
            #dir_choose = QFileDialog.getExistingDirectory(self, "選取資料夾", "/Users/user/Documents/畢專/dicom_data")  # 第三參數是起始路徑
            print(pt_id + "test")

            # 至後端拿資料(未做)
            # post
            # url = 'http://127.0.0.1:8000/pdicom/' + pt_id
            # #headers = {'accept': 'application/json', 'Content-Type': 'multipart/form-data'}
            # myfiles = listdir(dir_choose)  # 檔案
            # dic_file = []
            # for f in myfiles:
            #     # 產生檔案的絕對路徑
            #     fullpath = join(dir_choose, f)
            #     # dicom的名字
            #     dicom_id = os.path.basename(fullpath)
            #     print(dicom_id)
            #     print(fullpath)
            #     dic_file.append(('files', (dicom_id, open(fullpath, 'rb'))))
            # response = requests.post(url, files=dic_file)
            # print(response.reason)
            # print(response.json())

# 其他/初始--------------------------------------------------------------------------------------------------------
    def myListWidgetContext(self,position): # 設定patient list 右鍵功能 關閉
        popMenu = QMenu()
        closeAct =QAction("Close",self)
        if self.ui.patient_list.itemAt(position): #查看右键是否點在item上面
            popMenu.addAction(closeAct)
        closeAct.triggered.connect(self.closePatient)
        popMenu.exec_(self.ui.patient_list.mapToGlobal(position))

#其他/初始--------------------------------------------------------------------------------------------------------
    def transitiveMatrix(self, _x, _y, theda):
        radi = np.deg2rad(theda)
        index = int((-self.rotate_angle[self.pic_ith][self.pic_jth] % 360) / 90)
        tx = _x * np.cos(radi) + _y * np.sin(radi) + self.rotate_coordinate_system[index][0]
        ty = _x * np.sin(-radi) + _y * np.cos(radi) + self.rotate_coordinate_system[index][1]
        return tx, ty

    def showPic(self, i, j, patient_no, patient_dics):
        # print("showpic")
        dicom_path = "./tmp/" + patient_no + "/" + patient_dics
        ds = dcmread(dicom_path)
        arr = ds.pixel_array
        arr = np.uint8(arr)
        self.qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)

        pixmap = QtGui.QPixmap(self.qimage)
        # pixmap_resized = pixmap.scaled(self.pic_label_width * self.size, self.pic_label_height * self.size,QtCore.Qt.KeepAspectRatio)
        # self.pic[i][j].move(200, 0)
        self.pic[i][j].setPixmap(pixmap)
        # self.pic[i][j].setGeometry(QtCore.QRect(100, 100, 400, 500))
        self.pic[i][j].mousePressEvent = lambda pressed: self.picMousePressed(pressed, i, j) # 讓每個pic的mousePressEvent可以傳出告訴自己是誰
        self.pic[i][j].mouseReleaseEvent = lambda released: self.picMouseReleased(released, i, j)
        self.pic[i][j].mouseMoveEvent = lambda moved: self.picMouseMove(moved, i, j)


        # self.pic[i][j].paintEvent = lambda painted: self.picPaint(painted,  pixmap_resized, i, j)

        self.pic[i][j].paintEvent = lambda painted: self.picPaint(painted, pixmap, i, j)

    def linkPage2Array(self, _MAXIMUM_PAGE = 5, _MAXIMUM_PIC = 4):
        # 把QtDesigner的一些重複的Widget用array對應
        # patient_page
        self.MAXIMUM_PAGE = _MAXIMUM_PAGE
        self.MAXIMUM_PIC = _MAXIMUM_PIC
        var_patient_page = 'self.ui.patient_page'
        self.patient_page = [None] * (self.MAXIMUM_PAGE + 1)
        var_array_patient_page = 'self.patient_page'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_patient_page, i, var_patient_page, i))
        # thumbnail_list
        var_thumbnail_list = 'self.ui.thumbnail_list'
        self.thumbnail_list = [None] * (self.MAXIMUM_PAGE + 1)
        var_array_thumbnail_list = 'self.thumbnail_list'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_thumbnail_list, i, var_thumbnail_list, i))
        # pics
        var_pic = 'self.ui.pic'
        self.pic = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_start_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_start_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_end_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_end_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_start_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_start_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_middle_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_middle_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_end_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_end_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tsx = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tsy = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tmx = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tmy = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tex = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tey = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        
        self.pic_clicked = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pic_released = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_coordinate_list = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.rotate_angle = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.size = [[1] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.size_last = [[1] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.magnifier_pad_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.magnifier_pad_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_start_x = [ [0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.move_start_y = [ [0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.move_moving_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_moving_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_end_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_end_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]

        var_array_pic = 'self.pic'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            for j in range(1, (self.MAXIMUM_PIC + 1)):
                exec("%s[%d][%d] = %s_%d_%d" % (var_array_pic, i, j, var_pic, i, j))
                self.pic[i][j].setText("%d-%d" % (i, j))
                self.pen_start_x[i][j] = self.pen_start_y[i][j] = 0
                self.pen_end_x[i][j] = self.pen_end_y[i][j] = 0
                self.angle_start_x[i][j] = self.angle_start_y[i][j] = 0
                self.angle_middle_x[i][j] = self.angle_middle_y[i][j] = 0
                self.angle_end_x[i][j] = self.angle_end_y[i][j] = 0
                self.tsx[i][j] = self.tsy[i][j] = 0
                self.tmx[i][j] = self.tmy[i][j] = 0
                self.tex[i][j] = self.tey[i][j] = 0
                self.angle_coordinate_list[i][j] = []
        self.pic_cnt = [0] * (self.MAXIMUM_PAGE + 1)
        self.pic_ith = self.pic_jth = 1
        self.rotate_coordinate_system = [[0, 0], [512, 0], [512, 512], [0, 512]]
        # 畫圖透明canvas
        self.transparent_pix = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        for i in range(1, self.MAXIMUM_PAGE + 1):
            for j in range(1, (self.MAXIMUM_PIC + 1)):
                self.transparent_pix[i][j] = QtGui.QPixmap(512, 512)
                self.transparent_pix[i][j].fill(Qt.transparent)

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
class angleCoordinate():
    def __init__(self, _sx, _sy, _mx, _my, _ex, _ey):
        self.points = QtGui.QPolygonF()
        self.sp = QtCore.QPointF(_sx, _sy)
        self.mp = QtCore.QPointF(_mx, _my)
        self.ep = QtCore.QPointF(_ex, _ey)
        self.points.append(self.sp)
        self.points.append(self.mp)
        self.points.append(self.ep)
        self.length_sp2mp = ((self.sp.x() - self.mp.x()) ** 2 + (self.sp.y() - self.mp.y()) ** 2) ** 0.5
        self.length_mp2ep = ((self.mp.x() - self.ep.x()) ** 2 + (self.mp.y() - self.ep.y()) ** 2) ** 0.5
        self.inner_product = (self.sp.x() - self.mp.x()) * (self.ep.x() - self.mp.x()) + (self.sp.y() - self.mp.y()) * (self.ep.y() - self.mp.y())
        self.cos_theda = self.inner_product / self.length_sp2mp / self.length_mp2ep
        self.angle = np.arccos(self.inner_product / self.length_sp2mp / self.length_mp2ep) * 180 / np.pi
    def printDetail(self):
        print("angle: ", self.angle)
        print("inner product: ", self.inner_product, "cos: ", self.cos_theda)
        print("length1: ", self.length_sp2mp, "length2: ", self.length_mp2ep)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    mw.show()
    sys.exit(app.exec_())