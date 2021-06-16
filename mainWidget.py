from os import listdir
from os.path import join
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, Qt, QEvent, QPointF)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QTransform, QPainter
from generatedUiFile.Spine_BrokenUi import Ui_MainWindow
from generatedUiFile.customUi import Ui_Dialog
import os, requests
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QInputDialog, QLineEdit, QDialog, QListWidgetItem
from pydicom import dcmread, Dataset
from pydicom.filebase import DicomBytesIO
import numpy as np
from PIL import ImageQt
import shutil
import copy
WINDOW_SIZE = 0

class initialWidget(QtWidgets.QMainWindow):
    pic_ith = 1 
    pic_jth = 1
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.search_record = QStandardItemModel()
        self.pic_label_width = 512
        self.pic_label_height = 512
        self.pic_windows = [0, 1, 1, 1, 1, 1]
        
        self.loadPtList()
        self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)

        self.tmp_cnt = 0

        # 控制工具列現在選擇的工具為: mouse(defalut), pen, angle, ruler, move, zoom_in, zoom_out
        self.tool_lock = "mouse"
         # patient num map to page
        self.empty_page_stack = []
        for i in range(5, 0, -1):
            self.empty_page_stack.append(i)
        self.patient_mapto_page = {}

        self.opened_list = [] # 紀錄打開順序
        self.recent_list = [] # 記錄倒過來

        self.ui.patient_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #右键菜单
        self.ui.patient_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.patient_list.customContextMenuRequested.connect(self.myListWidgetContext)
        self.ui.patient_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


        #brightness相關
        self.custom_window = custom()
        self.aboutBrightness()

        #選幾張照片
        self.aboutWindows()

        self.backend()

        def moveWindow(e):
            if self.isMaximized() == False:  # Not maximized
                if e.buttons() == Qt.LeftButton:
                    self.move(self.pos() + e.globalPos() - self.clickPosition)
                    self.clickPosition = e.globalPos()
                    e.accept()
        self.ui.header.mouseMoveEvent = moveWindow  # 移動視窗
        self.show()


    def closeEvent(self,event):
        self.saveSearchRecord()
        self.saveOpened()
        event.accept()

        
        

    def backend(self):
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.recently_viewed_page)
        self.ui.close_button.clicked.connect(self.close)  # 叉叉
        self.ui.minimize_button.clicked.connect(lambda: self.showMinimized())  # minimize window
        self.ui.restore_button.clicked.connect(lambda: self.restoreOrMaximizeWindow())  # restore window
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隱藏邊框
        self.ui.menu_toggle.clicked.connect(lambda: self.slideLeftMenu())  # slide menu
        self.ui.add_patient.clicked.connect(self.addPatient)
        self.ui.search.clicked.connect(lambda: self.ui.stackedWidget_right.setCurrentWidget(self.ui.search_page))
        self.loadSearchRecord() # 載入搜尋紀錄
        self.loadOpened() # 載入上次開啟紀錄
        self.ui.input_no.editingFinished.connect(self.addEntry)  # 按enter
        self.ui.search_no_button.clicked.connect(self.addEntry)  # 按 search_no
        completer = QCompleter(self.search_record, self)
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)
        self.ui.no_list.itemClicked.connect(self.no_listItemClicked)
        self.ui.input_no.setCompleter(completer)  # 搜尋紀錄
        self.linkPage2Array() # 將影像處理頁面預設有五頁
        self.ui.pushButton_angle.clicked.connect(self.pushButtonAngleClicked) # 角度按鈕連結
        self.ui.pushButton_ruler.clicked.connect(self.pushButtonRulerClicked)
        self.ui.pushButton_add_pic.clicked.connect(self.pushButtonAddPicClicked) # 加照片按鈕連結
        self.ui.pushButton_pen.clicked.connect(self.pushButtonPenClicked)   # 畫筆按鈕連結
        self.ui.pushButton_save.clicked.connect(self.pushButtonSaveClicked) # 儲存照片按鈕連結
        self.ui.pushButton_mouse.clicked.connect(self.pushButtonMouseClicked) # 鼠標
        self.ui.pushButton_erase.clicked.connect(self.pushButtonEraseClicked) # 清除畫筆、角度
        self.ui.pushButton_magnifier.clicked.connect(lambda: self.slideMagnifierZoomInOrOut())  # 打開放大縮小的frame
        self.ui.pushButton_rotate.clicked.connect(lambda: self.slideRotateLeftOrRight())    # 打開旋轉的frame
        self.ui.pushButton_rotate_right.clicked.connect(self.rotate_image_right)    #向右旋轉
        self.ui.pushButton_rotate_left.clicked.connect(self.rotate_image_left)  #向左旋轉
        self.ui.zoomIn.clicked.connect(self.image_zoom_in) # 放大
        self.ui.zoomOut.clicked.connect(self.image_zoom_out) # 縮小 
        self.ui.pushButton_move.clicked.connect(self.pushButtonMoveClicked) # 移動
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)
        self.ui.recently_list.itemClicked.connect(self.recently_listItemClicked)
        self.ui.thumbnail_list_1.itemClicked.connect(self.thumbnail_listItemClicked)
        # self.set_thumbnail('03915480')


#照片Show Pic----------------------------------------------------------------------

    #brightness 
    def getWindow(self, WL, WW):
        print(WL, WW)
        if(WL == 0 & WW == 0): # default
            ds = self.dicoms[initialWidget.pic_ith][initialWidget.pic_jth]
            WL = ds[0x0028, 0x1050].value
            WW = ds[0x0028, 0x1051].value
        elif(WL == 1 & WW == 1): # custom
            WL, WW = self.showCustom()
            if(WL == 0 & WW == 0):
                return
        self.pic_adjust_pixels[initialWidget.pic_ith][initialWidget.pic_jth] = np.copy(self.pic_original_pixels[initialWidget.pic_ith][initialWidget.pic_jth])
        arr = self.pic_adjust_pixels[initialWidget.pic_ith][initialWidget.pic_jth]
        self.pic_adjust_pixels[initialWidget.pic_ith][initialWidget.pic_jth] = np.copy(np.uint16(self.mappingWindow(arr, WL, WW)))
        self.update()

    def showCustom(self):
        self.custom_window.show()
        if(self.custom_window.exec() == 1):
            WL = self.custom_window.customui.WLinput.value()
            WW = self.custom_window.customui.WWinput.value()
        else:
            WL = 0
            WW = 0
        return WL, WW

    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))
    
    # 設定照片處理的地方有幾格
    def setPicWindows(self, x):
        # print("i ", self.pic_windows[initialWidget.pic_ith], " x ", x)
        if self.pic_windows[initialWidget.pic_ith] > x:
            for k in range(x + 1, self.pic_windows[initialWidget.pic_ith] + 1):
                self.gridLayout_list[initialWidget.pic_ith].removeWidget(self.pic_viewer[initialWidget.pic_ith][k])
                self.pic_viewer[initialWidget.pic_ith][k].deleteLater()
                # self.pic_viewer[initialWidget.pic_ith][k].setNewScence()
            if x == 3:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][1], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][2], 0, 1, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].removeWidget(self.pic_viewer[initialWidget.pic_ith][3])
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][3], 0, 2, 1, 1)
            self.pic_windows[initialWidget.pic_ith] = x
        if self.pic_windows[initialWidget.pic_ith] < x:
            for k in range(self.pic_windows[initialWidget.pic_ith] + 1, x + 1):
                label = QtWidgets.QLabel(self.pic_frame_list[initialWidget.pic_ith])
                label.setStyleSheet("background-color: black; border: 3px solid black;")
                # self.pic_viewer[initialWidget.pic_ith][k] = label
                pointer = PhotoViewer(self, initialWidget.pic_ith, k)
                self.pic_viewer[initialWidget.pic_ith][k] = pointer
            if x == 2:
                print(self.pic_viewer[initialWidget.pic_ith][1].width(), self.pic_viewer[initialWidget.pic_ith][1].height())
                print(self.pic_viewer[initialWidget.pic_ith][2].width(), self.pic_viewer[initialWidget.pic_ith][2].height())
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][1], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][2], 0, 1, 1, 1)
                self.showPic(initialWidget.pic_ith, 1, "01372635","5F3279B8.dcm")
                self.showPic(initialWidget.pic_ith, 2, "01372635","5F327951.dcm")
            elif x == 3:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][1], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][2], 0, 1, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][3], 0, 2, 1, 1)
                self.showPic(initialWidget.pic_ith, 1, "01372635","5F3279B8.dcm")
                self.showPic(initialWidget.pic_ith, 2, "01372635","5F327951.dcm")
                self.showPic(initialWidget.pic_ith, 3, "03915480","5F329172_20170623_CR_2_1_1.dcm")
            elif x == 4:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][1], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][2], 0, 1, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][3], 1, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][4], 1, 1, 1, 1)
                # self.showPic(initialWidget.pic_ith, 1, "01372635","5F3279B8.dcm")
                # self.showPic(initialWidget.pic_ith, 2, "01372635","5F327951.dcm")
                # self.showPic(initialWidget.pic_ith, 3, "03915480","5F329172_20170623_CR_2_1_1.dcm")
                # self.showPic( initialWidget.pic_ith, 4, "03915480","5F329172_20170623_CR_2_1_1.dcm")
            self.pic_windows[initialWidget.pic_ith] = x
#按鈕連結處--------------------------------------------------------------------------------------------------------
    # 鼠標
    def pushButtonMouseClicked(self):
        self.setToolLock('mouse')
    # 移動
    def pushButtonMoveClicked(self):
        self.setToolLock('move')
    # 放大
    def image_zoom_in(self):
        self.setToolLock('zoom_in')
    # 縮小
    def image_zoom_out(self):
        self.setToolLock('zoom_out')
    # 順時鐘轉
    def rotate_image_right(self):
        self.setToolLock('rotate_right')
    # 逆時鐘轉
    def rotate_image_left(self):
        self.setToolLock('rotate_left')
    # 角度
    def pushButtonAngleClicked(self):
        self.setToolLock('angle')
    # 尺        
    def pushButtonRulerClicked(self):
        self.setToolLock('ruler')
    # 筆
    def pushButtonPenClicked(self):
        self.setToolLock('pen')
    # 清除
    def pushButtonEraseClicked(self):
        self.transparent_pix[initialWidget.pic_ith][initialWidget.pic_jth].fill(Qt.transparent)
        self.angle_coordinate_list[initialWidget.pic_ith][initialWidget.pic_jth].clear()
        self.update()
        # 清除後必須將畫筆設為初始位置，否則會存到上次最後的位置，而有一小黑點
        self.pen_start_x[initialWidget.pic_ith][initialWidget.pic_jth] = self.pen_start_y[initialWidget.pic_ith][initialWidget.pic_jth] = -10
        self.pen_end_x[initialWidget.pic_ith][initialWidget.pic_jth] = self.pen_end_y[initialWidget.pic_ith][initialWidget.pic_jth] = -10
    
    # 加照片
    def pushButtonAddPicClicked(self):
        pic_file_path, filetype = QFileDialog.getOpenFileName(self,"選取檔案","/Users/user/Documents/畢專/dicom_data")  #設定副檔名過濾,注意用雙分號間隔
        if pic_file_path == "":
                print("\n取消")
                return
        print(pic_file_path)
        #print(initialWidget.pic_ith)
        pt_id = list(self.patient_mapto_page.keys())[list(self.patient_mapto_page.values()).index(initialWidget.pic_ith)]
        tmp_dst = './tmp/' + pt_id
        if(os.path.exists(tmp_dst)):
            self.picAlreadyExist()
            return
        database_dst = './tmp_database/' + pt_id
        shutil.copy(pic_file_path, tmp_dst)
        shutil.copy(pic_file_path, database_dst)
    def picAlreadyExist(self):
        picAlreadyExist_msg = QMessageBox()
        picAlreadyExist_msg.setWindowTitle("Warning")
        picAlreadyExist_msg.setText("Dicom already exist !")
        picAlreadyExist_msg.setIcon(QMessageBox.Warning)
        x = picAlreadyExist_msg.exec_() 
    # save photo .png
    def pushButtonSaveClicked(self):
        self.setToolLock('save')
    
    def setToolLock(self, lock):
        self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].resetFlags()
        PhotoViewer.tool_lock = lock
        if PhotoViewer.tool_lock == 'move':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].toggleDragMode()
        elif PhotoViewer.tool_lock == 'clear':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].setNewScene()
        elif PhotoViewer.tool_lock == 'save':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].save()
        elif PhotoViewer.tool_lock == 'rotate_right':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].rotate(90)
        elif PhotoViewer.tool_lock == 'rotate_left':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].rotate(-90)


    # 對比度的選單設定
    def aboutBrightness(self): 
        self.ui.pushButton_brightness.setStyleSheet("::menu-indicator{ image: none; }") #remove triangle
        self.window_menu = QtWidgets.QMenu()
        self.window_menu.addAction('Default window', lambda: self.getWindow(0, 0))
        self.window_menu.addAction('[160/320]', lambda: self.getWindow(160, 320))
        self.window_menu.addAction('[320/640]', lambda: self.getWindow(320, 640))
        self.window_menu.addAction('[640/1280]', lambda: self.getWindow(640, 1280))
        self.window_menu.addAction('[1280/2560]', lambda: self.getWindow(1280, 2560))
        self.window_menu.addAction('[2560/5120]', lambda: self.getWindow(2560, 5120))
        self.window_menu.addAction('Custom window', lambda: self.getWindow(1, 1))
        self.ui.pushButton_brightness.setMenu(self.window_menu)
    
    


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

    def aboutWindows(self): # 對比度的選單設定
        self.ui.pushButton_windows.setStyleSheet("::menu-indicator{ image: none; }") #remove triangle
        self.windows_menu = QtWidgets.QMenu()
        self.windows_menu.addAction('1', lambda: self.setPicWindows(1))
        self.windows_menu.addAction('2', lambda: self.setPicWindows(2))
        self.windows_menu.addAction('3', lambda: self.setPicWindows(3))
        self.windows_menu.addAction('4', lambda: self.setPicWindows(4))
        self.ui.pushButton_windows.setMenu(self.windows_menu)


    # def pushButtonBrightnessClicked(self):
#MENU選單---------------------------------------------------------------------------------------------------------
    #add patient
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
                # print(dicom_id)
                # print(fullpath)
                dic_file.append(('files', (dicom_id, open(fullpath, 'rb'))))
            response = requests.post(url, files=dic_file)
            print(response.reason)
            print(response.json())
            if(response.json()['Result'] == 'Directory already exists.'):
                self.duplicateAdd()
            else:
                self.pt_list.append(pt_id)
                self.pt_list.sort()
                self.ui.no_list.clear()
                for ptid in self.pt_list:
                    self.ui.no_list.addItem(ptid)
                for i in self.pt_list:
                    print(i)    
                src = './tmp_database/' + pt_id
                dst = './tmp/' + pt_id
                if(not os.path.exists(dst)):
                    os.makedirs(dst)
                copytree(src, dst)
                self.open_pt_page(pt_id)

                
    def open_pt_page(self, pt_id): #記得要先檢查self.empty_page_stack空->Page滿->pageFull, 用在add和pt_list中打開
        temp = self.empty_page_stack[-1]
        self.empty_page_stack.pop()
        self.patient_mapto_page[pt_id] = temp
        initialWidget.pic_ith = temp
        self.ui.patient_list.addItem(pt_id)
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
        temp_page = self.patient_mapto_page[pt_id]
        self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
        self.opened_list.append(pt_id)
        self.set_thumbnail(pt_id)

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
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
        temp = str(item.text())
        temp_page = self.patient_mapto_page[temp]
        initialWidget.pic_ith = self.patient_mapto_page[temp]
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
        self.patient_mapto_page.pop(close_id)
        self.ui.patient_list.takeItem(self.ui.patient_list.currentRow())
        close_path = "./tmp/" + close_id
        for filename in os.listdir(close_path):
            file_path = close_path + '/' + filename
            os.remove(file_path)
        os.rmdir(close_path)
        if(self.ui.patient_list.count() == 0 & curRow == 0): # if close the last one
            self.ui.stackedWidget_right.setCurrentWidget(self.ui.search_page)
        elif(curRow == 0): # close first
            get_next_id = self.ui.patient_list.item(curRow)
            next_pt = str(get_next_id.text())
            temp_page = self.patient_mapto_page[next_pt]
            initialWidget.pic_ith = temp_page
            self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
        else: # close other patient
            get_next_id = self.ui.patient_list.item(curRow - 1)
            next_pt = str(get_next_id.text())
            temp_page = self.patient_mapto_page[next_pt]
            initialWidget.pic_ith = temp_page
            self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])


# Thumbnail-------------------------------------------------------------------------------------------------------
    def set_thumbnail(self, pt_id):
        pt_path = './tmp/' + pt_id
        i = self.patient_mapto_page[pt_id]
        self.thumbnail_list[i].setViewMode(QListWidget.IconMode)
        self.thumbnail_list[i].setItemAlignment(Qt.AlignCenter)
        for filename in os.listdir(pt_path):
            if not filename.endswith('.dcm') :
                continue
            dicom_path = pt_path + '/' + filename
            ds = dcmread(dicom_path)
            arr = ds.pixel_array
            arr = np.uint16(arr)
            dicom_WL = ds[0x0028, 0x1050].value
            dicom_WW = ds[0x0028, 0x1051].value
            SD = ds[0x0008, 0x103e].value #Series_Description
            # SN = str(ds[0x0020, 0x0011].value) #Series Number
            arr = self.mappingWindow(arr, dicom_WL, dicom_WW)
            qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16).copy()
            pixmap = QtGui.QPixmap(qimage)
            item = QListWidgetItem()
            item.setSizeHint(QSize(219, 250))
            item.setText(SD)
            icon = QtGui.QIcon(pixmap)
            item.setIcon(icon)
            self.thumbnail_list[i].addItem(item) 

        size = QSize(215, 215)
        self.thumbnail_list[i].setIconSize(size)

    def thumbnail_listItemClicked(self):
        print("test")
# search page-----------------------------------------------------------------------------------------------------
    # search
    def loadSearchRecord(self):
        self.search_record_cnt = 0
        with open('./record/search_record.txt', 'r') as f:
            medical_numbers = f.read().splitlines()
            for k in medical_numbers:
                self.search_record.insertRow(self.search_record_cnt, QStandardItem(k))
                self.search_record_cnt += 1
        
    def saveSearchRecord(self):
        with open('./record/search_record.txt', 'w') as f:
            #print(self.search_record_cnt)
            for i in range(self.search_record_cnt):
                f.write(self.search_record.item(i).text() + "\n")

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

        completer = QCompleter(self.search_record, self)
        self.ui.input_no.setCompleter(completer)

        if not self.search_record.findItems(entryItem) and len(entryItem) != 0:
            self.search_record_cnt += 1
            self.search_record.insertRow(0, QStandardItem(entryItem))


    # open patient
    def no_listItemClicked(self, item):
        #print(str(item.text()))
        if(not self.empty_page_stack):
                self.pageFull()
        else:
            pt_id = str(item.text())
            print(pt_id)
            if(pt_id not in self.patient_mapto_page):
                print("no")
                src = './tmp_database/' + pt_id
                dst = './tmp/' + pt_id
                if(not os.path.exists(dst)):
                    os.makedirs(dst)
                copytree(src, dst)
                self.open_pt_page(pt_id)
            else:
                self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
                temp_page = self.patient_mapto_page[pt_id]
                initialWidget.pic_ith = self.patient_mapto_page[pt_id]
                self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
                self.opened_list.append(pt_id)
            # print(pt_id + "test")

# Recently viewed page--------------------------------------------------------------------------------------------
    def loadOpened(self):
        with open('./record/tmpOpened.txt', 'r') as f:
            pt_id = f.read().splitlines()
            for k in pt_id:
                self.recent_list.append(k)
                self.ui.recently_list.addItem(k)
            self.opened_list = self.recent_list[::-1]

    def saveOpened(self):
        self.recent_list = self.opened_list[::-1]
        self.recent_list = list(dict.fromkeys(self.recent_list))
        while(len(self.recent_list) > 10):
            self.recent_list.pop()
        with open('./record/tmpOpened.txt', 'w') as f:
            for k in self.recent_list:
                f.write(k + "\n")
        for filename in os.listdir('./tmp'):
            shutil.rmtree('./tmp/'+ filename) 

    def recently_listItemClicked(self, item):
        pt_id = str(item.text())
        # self.ui.patient_list.addItem(pt_id)
        src = './tmp_database/' + pt_id
        dst = './tmp/' + pt_id
        if(not os.path.exists(dst)):
            os.makedirs(dst)
        copytree(src, dst)
        self.open_pt_page(pt_id)

# 其他/初始--------------------------------------------------------------------------------------------------------
    def loadPtList(self):
        url = 'http://127.0.0.1:8000/gmedicalnumbers'
        response = requests.get(url)
        self.ui.no_list.clear()
        medical_count = response.json()['medical_count']
        medical_numbers = response.json()['medical_numbers']
        self.pt_list = []
        for i in medical_numbers:
            # print(i)
            # print(type(i))
            self.pt_list.append(i)

        # print(type(response.json()['medical_numbers']))

    def myListWidgetContext(self,position): # 設定patient list 右鍵功能 關閉
        popMenu = QMenu()
        closeAct = QAction("Close",self)
        if self.ui.patient_list.itemAt(position): #查看右键是否點在item上面
            popMenu.addAction(closeAct)
        closeAct.triggered.connect(self.closePatient)
        popMenu.exec_(self.ui.patient_list.mapToGlobal(position))

    def transitiveMatrix(self, _x, _y, theda):
        radi = np.deg2rad(theda)
        tx = _x * np.cos(radi) + _y * np.sin(radi)
        ty = _x * np.sin(-radi) + _y * np.cos(radi)
        return tx, ty

    def transitiveWithBiasMatrix(self, _x, _y, theda):
        index = int((-theda % 360) / 90)
        tx, ty = self.transitiveMatrix(_x, _y, theda)        
        tx += self.rotate_coordinate_system[index][0]
        ty += self.rotate_coordinate_system[index][1]
        return tx, ty

    def picPixelMapping(self, arr,  WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2

        rows = arr.shape[0]
        cols = arr.shape[1]
        for x in range(0, rows):
            for y in range(0, cols):
                if(arr[x, y]>pixel_max):
                    arr[x, y] = pixel_max
                elif(arr[x, y] < pixel_min):
                    arr[x, y] = pixel_min
        for x in range(0, rows):
            for y in range(0, cols):
                arr[x, y] = (arr[x, y] - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(arr)

    def showPic(self, i, j, patient_no, patient_dics):
        dicom_path = "./tmp_database/" + patient_no + "/" + patient_dics
        ds = dcmread(dicom_path)

        self.dicoms[i][j] = ds
        arr = copy.deepcopy(ds.pixel_array)
        arr = np.uint16(arr)
        self.pic_original_pixels[i][j] = np.copy(arr)
        initialWidget.pic_ith = i
        initialWidget.pic_jth = j
        dicom_WL = ds[0x0028, 0x1050].value
        dicom_WW = ds[0x0028, 0x1051].value
        self.pic_adjust_pixels[i][j] = self.mappingWindow(arr, dicom_WL, dicom_WW)
        qimage = QtGui.QImage(self.pic_adjust_pixels[i][j], self.pic_adjust_pixels[i][j].shape[1], self.pic_adjust_pixels[i][j].shape[0], self.pic_adjust_pixels[i][j].shape[1]*2, QtGui.QImage.Format_Grayscale16).copy()
        pixmap = QtGui.QPixmap(qimage)
        pixmap = pixmap.scaled(self.pic_viewer[i][j].width(), self.pic_viewer[i][j].height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        # print(self.pic_viewer[i][j].width(), self.pic_viewer[i][j].height())
        self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].setPhoto(pixmap)
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
        # gridLayout
        var_gridLayout_list = 'self.ui.gridLayout'
        self.gridLayout_list = [None] * (self.MAXIMUM_PAGE + 1)
        var_array_gridLayout_list = 'self.gridLayout_list'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_gridLayout_list, i, var_gridLayout_list, i))
        # pic_frame
        var_pic_frame_list = 'self.ui.pic_frame'
        self.pic_frame_list = [None] * (self.MAXIMUM_PAGE + 1)
        var_array_pic_frame_list = 'self.pic_frame_list'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            exec("%s[%d] = %s_%d" % (var_array_pic_frame_list, i, var_pic_frame_list, i))
        # # pic
        # self.pic = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 對應到照片的label array
        # var_pic_list = 'self.ui.pic'
        # var_array_pic_list = 'self.pic'
        # for i in range(1, self.MAXIMUM_PAGE + 1):
        #     exec("%s[%d][1] = %s_%d_1" % (var_array_pic_list, i, var_pic_list, i))
        #     self.pic[i][1].setStyleSheet("background-color: black; border: 3px solid black;")
        # pic Viewer
        self.pic_viewer = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 對應到照片的viewer array
        for i in range(1, self.MAXIMUM_PAGE + 1):
            pointer = PhotoViewer(self, i, 1)
            self.pic_viewer[i][1] = pointer
            self.gridLayout_list[i].addWidget(self.pic_viewer[i][1], 0, 0, 1, 1)
        # Image Processing Attributes
        var_pic = 'self.ui.pic'
        self.pen_start_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] #---筆---
        self.pen_start_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_end_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pen_end_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.tsx = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tsy = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmx = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmy = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tex = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tey = [[None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] #---筆---
        self.ruler_start_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] #---尺---
        self.ruler_start_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.ruler_end_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.ruler_end_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.trex = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.trey = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]  # ---尺---
        self.angle_start_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] #---角度---
        self.angle_start_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_middle_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_middle_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_end_x = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_end_y = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # ---角度---
        self.pic_clicked = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 哪張照片被clicked
        self.pic_released = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 哪張照片被 released
        self.ruler_coordinate_list = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 每張照片中的所有尺存在[][]中
        self.angle_coordinate_list = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 每張照片中的所有角度存在[][]中
        self.rotate_angle = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # 旋轉角度
        self.size = [[1] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # 每張照片被放大縮小的倍率
        self.magnifier_pad_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # --magnifier--
        self.magnifier_pad_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmpx = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmpy = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # --magnifier--
        self.move_start_x = [ [0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # --move--
        self.move_start_y = [ [0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.move_moving_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_moving_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmmx = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.tmmy = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]
        self.move_y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)]  # # --move--
        self.pic_adjust_pixels = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 照片對比度須存改過的pixel array用
        self.pic_original_pixels = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 照片對比度須存原本的pixel array用

        self.dicoms = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 存Dicoms
        self.x = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # 每張照片的總位移量 x
        self.y = [[0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1)] # 每張照片的總位移量 y

        var_array_pic = 'self.pic'
        for i in range(1, self.MAXIMUM_PAGE + 1):
            for j in range(1, (self.MAXIMUM_PIC + 1)):
                # exec("%s[%d][%d] = %s_%d_%d" % (var_array_pic, i, j, var_pic, i, j))
                # self.pic[i][j].setText("%d-%d" % (i, j))
                # self.pic[i][j].setStyleSheet("background-color: black; border: 3px solid black;")
                self.pen_start_x[i][j] = self.pen_start_y[i][j] = 0
                self.pen_end_x[i][j] = self.pen_end_y[i][j] = 0

                self.pen_start_x[i][j] = self.pen_start_y[i][j] = -10
                self.pen_end_x[i][j] = self.pen_end_y[i][j] = -10

                self.ruler_start_x[i][j] = self.ruler_start_y[i][j] = 0
                self.ruler_end_x[i][j] = self.ruler_end_y[i][j] = 0                
                self.angle_start_x[i][j] = self.angle_start_y[i][j] = 0
                self.angle_middle_x[i][j] = self.angle_middle_y[i][j] = 0
                self.angle_end_x[i][j] = self.angle_end_y[i][j] = 0
                self.tsx[i][j] = self.tsy[i][j] = 0
                self.tmx[i][j] = self.tmy[i][j] = 0
                self.tex[i][j] = self.tey[i][j] = 0
                self.angle_coordinate_list[i][j] = []
                self.ruler_coordinate_list[i][j] = []

        self.pic_cnt = [0] * (self.MAXIMUM_PAGE + 1)
        initialWidget.pic_ith = initialWidget.pic_jth = 1
        self.rotate_coordinate_system = [[0, 0], [512, 0], [512, 512], [0, 512]]
        # 畫圖透明canvas
        self.transparent_pix = [ [0] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        for i in range(1, self.MAXIMUM_PAGE + 1):
            for j in range(1, (self.MAXIMUM_PIC + 1)):
                self.transparent_pix[i][j] = QtGui.QPixmap(1114 ,701) # 有改
                self.transparent_pix[i][j].fill(Qt.transparent)


        # 暫時試試放照片

        # self.showPic(1, 1, "01372635","5F3279B8.dcm")
        # self.showPic(1, 2, "01372635","5F327951.dcm")
        # self.showPic(1, 3, "03915480","5F329172_20170623_CR_2_1_1.dcm")
        # self.showPic(1, 4, "03915480","5F329172_20170623_CR_2_1_1.dcm")



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

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

class custom(QDialog):
  def __init__(self):
    super().__init__()
    self.customui = Ui_Dialog()
    self.customui.setupUi(self)
    
class QGraphicsLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, text):
        super().__init__(text)
        # self.setPen(QtGui.QPen(QtGui.QColor(230, 230, 10)))
        # self.setBrush(QtGui.QBrush(QtGui.QColor(60, 30, 30)))
        self.movable = False
        self.setVisible(False)
    def setMovable(self, enable):
        self.setAcceptHoverEvents(enable)
        self.movable = enable
    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.movable:
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()
            orig_position = self.scenePos()
            updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        pass

class Protractor(QtWidgets.QGraphicsPathItem):
    def __init__(self, qpainterpath):
        super().__init__(qpainterpath)
        self.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.angle_degree = 0
        self.movable = False
    def setMovable(self, enable):
        self.setAcceptHoverEvents(enable)
        self.movable = enable
    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.movable:
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()
            orig_position = self.scenePos()
            updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        pass

class Ruler(QtWidgets.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.movable = False
        self.length = 0
    def setMovable(self, enable):
        self.setAcceptHoverEvents(enable)
        self.movable = enable
    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.movable:
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()
            orig_position = self.scenePos()
            updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        pass
    

class Pen(QtWidgets.QGraphicsPathItem):
    def __init__(self, x1):
        super().__init__(x1)
        self.setPen(QtGui.QPen(QtGui.QColor(250, 25, 0)))
        self.movable = False
    def setMovable(self, enable):
        self.setAcceptHoverEvents(enable)
        self.movable = enable
    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.movable:
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()
            orig_position = self.scenePos()
            updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        pass
    
class PhotoViewer(QtWidgets.QGraphicsView):
    tool_lock = 'mouse'
    def __init__(self, parent, _i, _j):
        super(PhotoViewer, self).__init__(parent)
        self.in_ith = _i
        self.in_jth = _j
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.ruler_start = False
        self.protractor_start = False
        self.pen_start = False
    
    def setNewScene(self):
        self._scene = QtWidgets.QGraphicsScene(self)
        self._empty = True
        self.setScene(self._scene)
    def resetFlags(self):
        self.ruler_start = False
        self.protractor_start = False
        self.pen_start = False
    #save photo
    def save(self):
        save_image = QtGui.QPixmap(self.viewport().size())
        self.viewport().render(save_image)
        filePath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png)")  # ;;JPEG(*.jpg *.jpeg);;All Files(*.*)
        if filePath == "":
            return
        save_image.save(filePath)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


    def mousePressEvent(self, event):
        self.sp = self.mapToScene(event.pos())
        initialWidget.pic_ith = self.in_ith
        initialWidget.pic_jth = self.in_jth
        if PhotoViewer.tool_lock == 'move':
            print(PhotoViewer.tool_lock)
        elif PhotoViewer.tool_lock == 'ruler':
            self.ruler = Ruler(self.sp.x(), self.sp.y(), self.sp.x(), self.sp.y())
            self.ruler_text_label = QGraphicsLabel("")
            self._scene.addItem(self.ruler_text_label)
            self.ruler.setMovable(False)
            self._scene.addItem(self.ruler)
            self.ruler_start = True
        elif PhotoViewer.tool_lock == 'angle':
            if not self.protractor_start and not self.ruler_start:
                self.qpainterpath = QtGui.QPainterPath(self.sp)
                self.protractor = Protractor(self.qpainterpath)
                self.protractor_text_label = QGraphicsLabel("")
                self._scene.addItem(self.protractor_text_label)
                self._scene.addItem(self.protractor)
                self.protractor_start = True
            elif not self.protractor_start and self.ruler_start:
                self.protractor.setMovable(True)
                self.protractor_text_label.setMovable(True)
                self.protractor_start = False
                self.ruler_start = False
        if PhotoViewer.tool_lock == 'pen':
            self.pen_path = QtGui.QPainterPath()
            self.pen_path.moveTo(self.sp)
            self.pen = Pen(self.pen_path)
            self.pen.setMovable(False)
            self.pen.setPath(self.pen_path)
            self._scene.addItem(self.pen)
            self.pen_start = True
        super(PhotoViewer, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.ep = self.mapToScene(event.pos())
        if PhotoViewer.tool_lock == 'ruler':
            self.ruler.setLine(self.sp.x(), self.sp.y(), self.ep.x(), self.ep.y())
            self.ruler.setMovable(True)
            self.ruler_text_label.setMovable(True)
            self.ruler_start = False
        elif PhotoViewer.tool_lock == 'angle':
            if self.protractor_start:
                self.qpainterpath.clear()
                self.qpainterpath.moveTo(self.sp)
                self.qpainterpath.lineTo(self.ep)
                self.protractor.setPath(self.qpainterpath)
                self.protractor_start = False
                self.ruler_start = True
        if PhotoViewer.tool_lock == 'pen':
            self.pen_path.lineTo(self.ep)
            self.pen.setPath(self.pen_path)
            self.pen.setMovable(True)
            self.pen_start = False
        super(PhotoViewer, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.mp = self.mapToScene(event.pos())
        if PhotoViewer.tool_lock == 'ruler' and self.ruler_start:
            self.ruler.setLine(self.sp.x(), self.sp.y(), self.mp.x(), self.mp.y())
            self.length = np.sqrt(QtCore.QPointF.dotProduct(self.sp - self.mp, self.sp - self.mp))
            self.ruler_text_label.setVisible(True)
            # self.ruler_text_label.setText("%.2f pixels" % self.length)
            self.ruler_text_label.setHtml("<div style='background-color:#3c1e1e;font-size:10px;color:#e6e60a;'>" + "%.2f pixels" % self.length + "</div>")
            if self.sp.x() <= self.mp.x(): 
                self.ruler_text_label.setPos(self.mp + QtCore.QPointF(10, 0))
            else:
                self.ruler_text_label.setPos(self.sp + QtCore.QPointF(10, 0))
        elif PhotoViewer.tool_lock == 'angle':
            if self.protractor_start:
                self.qpainterpath.clear()
                self.qpainterpath.moveTo(self.sp)
                self.qpainterpath.lineTo(self.mp)
                self.protractor.setPath(self.qpainterpath)
            elif not self.protractor_start and self.ruler_start:
                self.qpainterpath.clear()
                self.qpainterpath.moveTo(self.sp)
                self.qpainterpath.lineTo(self.ep)
                self.qpainterpath.lineTo(self.mp)
                self.protractor.setPath(self.qpainterpath)
                self.protractor_text_label.setVisible(True)
                spToep = np.sqrt(QtCore.QPointF.dotProduct(self.sp - self.ep, self.sp - self.ep))
                epTomp = np.sqrt(QtCore.QPointF.dotProduct(self.mp - self.ep, self.mp - self.ep))
                self.protractor.angle_degree = np.arccos(QtCore.QPointF.dotProduct(self.ep - self.sp, self.ep - self.mp) / spToep / epTomp) * 180 / np.pi
                # self.protractor_text_label.setText("%.1f°" % self.protractor.angle_degree)
                self.protractor_text_label.setHtml("<div style='background-color:#3c1e1e;font-size:10px;color:#e6e60a;'>" + "%.1f°" % self.protractor.angle_degree + "</div>")
                if self.mp.x() > self.ep.x() and self.mp.y() < self.ep.y(): 
                    self.protractor_text_label.setPos(self.ep + QtCore.QPointF(5, 10))
                else:
                    self.protractor_text_label.setPos(self.ep + QtCore.QPointF(5, -25))
        if PhotoViewer.tool_lock == 'pen' and self.pen_start:
            self.pen_path.lineTo(self.mp)
            self.pen.setPath(self.pen_path)
        super(PhotoViewer, self).mouseMoveEvent(event)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    # custom = customDialog()
    mw.show()
    sys.exit(app.exec_())