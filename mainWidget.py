from os import listdir
from os.path import join
from PyQt5.QtCore import (QCoreApplication, QDataStream, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect,
                          QSize, QTime, QUrl, QVariant, Qt, QEvent, QPointF)
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
from collections import defaultdict
WINDOW_SIZE = 0

class initialWidget(QtWidgets.QMainWindow):
    pic_ith = 1 
    pic_jth = 1
    pic_windows = [0, 1, 1, 1, 1, 1]
    listShow = [[], [], [], [], [], []]
    listNoShow = [[], [], [], [], [], []]
    for i in range(1, 6):
        listShow[i].append(1)
    for i in range(1, 6):
        for j in range(2, 5):
            listNoShow[i].append(j)
    # dictionary mapping series(str) to Dicoms(.dcm)
    series_2_dicoms = [None] * (5 + 1)
    for i in range(1, 5 + 1):
        series_2_dicoms[i] = defaultdict(lambda: defaultdict(list))
    enlarge = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.search_record = QStandardItemModel()
        initialWidget.ui = self.ui
        self.loadPtList()
        self.pt_list.sort()
        # 在搜尋那頁列出符合醫生輸入的數字的病歷號
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)

        self.tmp_cnt = 0

        # 控制工具列現在選擇的工具為: mouse(defalut), pen, angle, ruler, move, magnifier
        self.tool_lock = "mouse"
         # patient num map to page
        self.empty_page_stack = []
        for i in range(5, 0, -1):
            self.empty_page_stack.append(i)
        self.patient_mapto_page = {}

        self.opened_list = [] # 紀錄打開順序
        self.recent_list = [] # 記錄倒過來

        self.ui.patient_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #右鍵菜單
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
        self.ui.pushButton_magnifier.clicked.connect(self.pushButtonMagnifier)  # 放大 縮小
        self.ui.pushButton_rotate.clicked.connect(lambda: self.slideRotateLeftOrRight())    # 打開旋轉的frame
        self.ui.pushButton_rotate_right.clicked.connect(self.rotate_image_right)    #向右旋轉
        self.ui.pushButton_rotate_left.clicked.connect(self.rotate_image_left)  #向左旋轉
        self.ui.pushButton_move.clicked.connect(self.pushButtonMoveClicked) # 移動
        self.ui.patient_list.itemClicked.connect(self.patient_listItemClicked)
        self.ui.recently_list.itemClicked.connect(self.recently_listItemClicked)


#照片Show Pic----------------------------------------------------------------------

    #brightness 
    def getWindow(self, WL, WW):
        if(WL == 1 and WW == 1): # custom
            WL, WW = self.showCustom()
            if(WL == 0 & WW == 0):
                return
        self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.resetWindow(WL, WW)
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
    @staticmethod
    def mappingWindow(arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))
        
    # 設定照片處理的地方有幾格
    def windows4to3(self):
        tp = [0]
        for t in initialWidget.listShow[initialWidget.pic_ith]:
            tp.append(t)
        self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[1]], 0, 0, 1, 1)
        self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[2]], 0, 1, 1, 1)
        self.gridLayout_list[initialWidget.pic_ith].removeWidget(self.pic_viewer[initialWidget.pic_ith][tp[3]])
        self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[3]], 0, 2, 1, 1)
    def setPicWindows(self, x):
        self.now_windows = initialWidget.pic_jth    # 當前按的照片位置
        if initialWidget.pic_windows[initialWidget.pic_ith] > x:
            for k in range(x + 1, initialWidget.pic_windows[initialWidget.pic_ith] + 1):
                index = initialWidget.listShow[initialWidget.pic_ith][-1]
                initialWidget.listShow[initialWidget.pic_ith].pop()
                initialWidget.listNoShow[initialWidget.pic_ith].append(index)
                self.gridLayout_list[initialWidget.pic_ith].removeWidget(self.pic_viewer[initialWidget.pic_ith][index])
                self.pic_viewer[initialWidget.pic_ith][index].deleteLater()
            if x == 3:
                self.windows4to3()
            
            if self.now_windows > x:    # 如果照片當前位置被刪除，則設為x(如4張照片變3張且當前位置在第四張，則設為第三張)
                initialWidget.pic_jth = x
            initialWidget.pic_windows[initialWidget.pic_ith] = x
        if initialWidget.pic_windows[initialWidget.pic_ith] < x:
            for k in range(initialWidget.pic_windows[initialWidget.pic_ith] + 1, x + 1):
                index = initialWidget.listNoShow[initialWidget.pic_ith][-1]
                initialWidget.listNoShow[initialWidget.pic_ith].pop()
                initialWidget.listShow[initialWidget.pic_ith].append(index)
                self.pic_viewer[initialWidget.pic_ith][index] = PhotoProcessing(self.pic_frame_list[initialWidget.pic_ith], initialWidget.pic_ith, index)
            tp = [0]
            for t in initialWidget.listShow[initialWidget.pic_ith]:
                tp.append(t)
            if x == 2:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[1]], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[2]], 0, 1, 1, 1)
                self.pic_viewer[initialWidget.pic_ith][tp[1]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[2]].pv.show()
            elif x == 3:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[1]], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[2]], 0, 1, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[3]], 0, 2, 1, 1)
                self.pic_viewer[initialWidget.pic_ith][tp[1]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[2]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[3]].pv.show()
            elif x == 4:
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[1]], 0, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[2]], 0, 1, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[3]], 1, 0, 1, 1)
                self.gridLayout_list[initialWidget.pic_ith].addWidget(self.pic_viewer[initialWidget.pic_ith][tp[4]], 1, 1, 1, 1)
                self.pic_viewer[initialWidget.pic_ith][tp[1]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[2]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[3]].pv.show()
                self.pic_viewer[initialWidget.pic_ith][tp[4]].pv.show()
            initialWidget.pic_windows[initialWidget.pic_ith] = x
            initialWidget.pic_jth = self.now_windows    # 設回原本的位置
        self.setToolLock(PhotoViewer.tool_lock)    # 傳到setToolLock更新當前總共幾張照片
    def closeWindowX(self, _i, _j):
        print(_i, _j)

#按鈕連結處--------------------------------------------------------------------------------------------------------
    # 鼠標
    def pushButtonMouseClicked(self):
        self.setToolLock('mouse')
    # 移動
    def pushButtonMoveClicked(self):
        self.setToolLock('move')
    # 放大 縮小
    def pushButtonMagnifier(self):
        self.setToolLock('magnifier')
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
    # 儲存
    def pushButtonSaveClicked(self):
        self.setToolLock('save')
    # 清除
    def pushButtonEraseClicked(self):
        self.setToolLock('clear')

    
    # 加照片
    def pushButtonAddPicClicked(self):
        pic_file_path, filetype = QFileDialog.getOpenFileName(self,"選取檔案","/Users/user/Documents/畢專/dicom_data")  #設定副檔名過濾,注意用雙分號間隔
        if pic_file_path == "":
                print("\n取消")
                return
        print(pic_file_path)
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

    def setToolLock(self, lock):
        self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.resetFlags()
        # 預設所有item都不能動且沒有手手
        for k in initialWidget.listShow[initialWidget.pic_ith]:
            self.pic_viewer[initialWidget.pic_ith][k].pv.Movable(False)
            self.pic_viewer[initialWidget.pic_ith][k].pv.toggleDragMode(False)
        PhotoViewer.tool_lock = lock
        if PhotoViewer.tool_lock == 'move':
            for k in initialWidget.listShow[initialWidget.pic_ith]:
                self.pic_viewer[initialWidget.pic_ith][k].pv.toggleDragMode(True)
        elif PhotoViewer.tool_lock == 'mouse':
            for k in initialWidget.listShow[initialWidget.pic_ith]:
                self.pic_viewer[initialWidget.pic_ith][k].pv.Movable(True)
            PhotoViewer.tool_lock = 'mouse'
        elif PhotoViewer.tool_lock == 'save':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.save()
            PhotoViewer.tool_lock = 'mouse'
        elif PhotoViewer.tool_lock == 'rotate_right':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.rotate(90)
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.turnBack(90)
            PhotoViewer.tool_lock = 'mouse'
        elif PhotoViewer.tool_lock == 'rotate_left':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.rotate(-90)
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.turnBack(-90)
            PhotoViewer.tool_lock = 'mouse'
        elif PhotoViewer.tool_lock == 'clear':
            self.pic_viewer[initialWidget.pic_ith][initialWidget.pic_jth].pv.clear()
            PhotoViewer.tool_lock = 'mouse'


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

    def aboutWindows(self): # 格數選單設定
        self.ui.pushButton_windows.setStyleSheet("::menu-indicator{ image: none; }") #remove triangle
        self.windows_menu = QtWidgets.QMenu()
        self.windows_menu.addAction('1', lambda: self.setPicWindows(1))
        self.windows_menu.addAction('2', lambda: self.setPicWindows(2))
        self.windows_menu.addAction('3', lambda: self.setPicWindows(3))
        self.windows_menu.addAction('4', lambda: self.setPicWindows(4))
        self.ui.pushButton_windows.setMenu(self.windows_menu)


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
                src = './tmp_database/' + pt_id
                dst = './tmp/' + pt_id
                if(not os.path.exists(dst)):
                    os.makedirs(dst)
                copytree(src, dst)
                self.openPtPage(pt_id)

                
    def openPtPage(self, pt_id): #記得要先檢查self.empty_page_stack空->Page滿->pageFull, 用在add和pt_list中打開
        temp = self.empty_page_stack[-1]
        self.empty_page_stack.pop()
        self.patient_mapto_page[pt_id] = temp
        initialWidget.pic_ith = temp
        self.ui.patient_list.addItem(pt_id)
        self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
        temp_page = self.patient_mapto_page[pt_id]
        self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
        self.opened_list.append(pt_id)
        self.setThumbnail(pt_id)

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
            initialWidget.enlarge = True
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
    def setThumbnail(self, pt_id):
        pt_path = './tmp/' + pt_id
        i = self.patient_mapto_page[pt_id]
        self.thumbnail_list[i].setViewMode(QListWidget.IconMode)
        self.thumbnail_list[i].setItemAlignment(Qt.AlignCenter)
        self.thumbnail_list[i].setIconSize(QSize(215, 215))
        self.thumbnail_list[i].setContentsMargins(0, 0, 0, 0)
        self.thumbnail_list[i].setDragEnabled(True)
        self.thumbnail_list[i].setDragDropMode(QAbstractItemView.DragOnly)
        self.thumbnail_list[i].setStyleSheet( "QListWidget::item { border-top : 1px solid black }" )
        initialWidget.series_2_dicoms[i].clear()
        #先放pt id
        item = QtWidgets.QListWidgetItem(self.thumbnail_list[i])
        self.thumbnail_list[i].addItem(item)
        new_item = MyCustomWidgetPtid(pt_id)
        item.setTextAlignment(Qt.AlignVCenter)
        item.setSizeHint(QSize(219, 50))

        self.thumbnail_list[i].setItemWidget(item, new_item)
        for filename in os.listdir(pt_path):    #set map
            if not filename.endswith('.dcm') :
                continue
            dicom_path = pt_path + '/' + filename
            ds = customDicom(dicom_path)
            initialWidget.series_2_dicoms[i][ds.study_date, ds.study_time, ds.study_id][ds.series_description].append(ds)
        for study, series in dict(sorted(initialWidget.series_2_dicoms[i].items())).items():
            first = True

            for key, value in dict(sorted(series.items(), key= lambda x: x[1][0].acquisition_time)).items(): # key = series description
                if first:
                    first = False
                    item = QtWidgets.QListWidgetItem(self.thumbnail_list[i])
                    self.thumbnail_list[i].addItem(item)
                    date = "%s/%s/%s" % (study[0][0:4], study[0][4:6], study[0][6:8])
                    time = "%s:%s:%s" % (study[1][0:2], study[1][2:4], study[1][4:6])
                    new_item = MyCustomWidget("%s %s" % (date, time), value[0].study_description, "%s: %d series" % (value[0].modality, len(initialWidget.series_2_dicoms[i][study].keys())))
                    item.setTextAlignment(Qt.AlignVCenter)
                    item.setSizeHint(QSize(219, 90))
                    # item.setBackground(QtGui.QColor('#ffffff') )
                    self.thumbnail_list[i].setItemWidget(item, new_item)
                ds = initialWidget.series_2_dicoms[i][study][key][0]
                arr = initialWidget.mappingWindow(ds.pixel_array, ds.window_level, ds.window_width)
                qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16).copy()
                pixmap = QtGui.QPixmap(qimage)
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint(QSize(219, 250))
                item.setText(key)
                item.setData(Qt.UserRole, study)
                icon = QtGui.QIcon(pixmap)
                item.setIcon(icon)
                item.setFont(QtGui.QFont('Verdana', 8))
                self.thumbnail_list[i].addItem(item) 
    
        
# search page----------------------------------------------------------------------------------------------------
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
            if(pt_id not in self.patient_mapto_page):
                src = './tmp_database/' + pt_id
                dst = './tmp/' + pt_id
                if(not os.path.exists(dst)):
                    os.makedirs(dst)
                copytree(src, dst)
                self.openPtPage(pt_id)
            else:
                self.ui.stackedWidget_right.setCurrentWidget(self.ui.thumbnail_page)
                temp_page = self.patient_mapto_page[pt_id]
                initialWidget.pic_ith = self.patient_mapto_page[pt_id]
                self.ui.stackedWidget_patients.setCurrentWidget(self.patient_page[temp_page])
                self.opened_list.append(pt_id)

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
        src = './tmp_database/' + pt_id
        dst = './tmp/' + pt_id
        if(not os.path.exists(dst)):
            os.makedirs(dst)
        copytree(src, dst)
        self.openPtPage(pt_id)

# 其他/初始--------------------------------------------------------------------------------------------------------
    def loadPtList(self):
        url = 'http://127.0.0.1:8000/gmedicalnumbers'
        response = requests.get(url)
        self.ui.no_list.clear()
        medical_count = response.json()['medical_count']
        medical_numbers = response.json()['medical_numbers']
        self.pt_list = []
        for i in medical_numbers:
            self.pt_list.append(i)


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
        
        # pic Viewer
        self.pic_viewer = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 對應到照片的viewer array
        for i in range(1, self.MAXIMUM_PAGE + 1):
            self.pic_viewer[i][1] = PhotoProcessing(self.pic_frame_list[i], i, 1)
            self.gridLayout_list[i].addWidget(self.pic_viewer[i][1], 0, 0, 1, 1)
            self.pic_viewer[i][1].pv.show()
        # Image Processing Attributes
        var_pic = 'self.ui.pic'
        self.pic_clicked = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 哪張照片被clicked
        self.pic_released = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 哪張照片被 released
        self.dicoms = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ] # 存Dicoms
        var_array_pic = 'self.pic'
        self.pic_cnt = [0] * (self.MAXIMUM_PAGE + 1)
        initialWidget.pic_ith = initialWidget.pic_jth = 1


    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def restoreOrMaximizeWindow(self):
        global WINDOW_SIZE
        win_status = WINDOW_SIZE
        if win_status == 0:
            WINDOW_SIZE = 1
            self.showMaximized()
            self.ui.restore_button.setIcon(QtGui.QIcon(u":/icons/icons/window-restore.png"))  # Show minized icon
        else:
            WINDOW_SIZE = 0
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
# classes
class custom(QDialog):
  def __init__(self):
    super().__init__()
    self.customui = Ui_Dialog()
    self.customui.setupUi(self)
    
class customDicom():
    def __init__(self, _dcm_path):
        self.dcm_path = _dcm_path 
        # self.dicom = self.dcmreader(self.dcm_path) # 若要存dicom
        self.pixel_array = None
        self.study_description = None
        self.study_instance_UID = None
        self.series_description = None
        self.series_number = None
        self.instance_no_of_series = None
        self.echotime = None
        self.content_time = None
        self.repetition_time = None
        self.magnetic = None
        self.window_level = None # WL
        self.window_width = None # WW
        self.study_date = None
        self.study_time = None
        self.study_id = None
        self.modality = None
        self.series_data_time_stamp = None
        self.acquisition_time = None
        self.content_date = None
        self.content_time = None
        self.content_time = None
        self.window_center= None
        self.window_width = None
        self.tr = None
        self.te = None
        self.scropInfo(self.dcmreader(self.dcm_path))
    def dcmreader(self, _dcm_path):
        ds = dcmread(_dcm_path)
        # print(ds)
        return ds

    def scropInfo(self, ds):
        self.pixel_array = np.uint16(ds.pixel_array).copy()
        self.study_description = ds[0x0008, 0x1030].value if (0x0008, 0x1030) in ds else None
        self.study_instance_UID = ds[0x0020, 0x000d].value if (0x0020, 0x000d) in ds else None
        self.series_description = ds[0x0008, 0x103e].value if (0x0008, 0x103e) in ds else None
        self.series_number = ds[0x0020, 0x0011].value if (0x0020, 0x0011) in ds else None
        self.instance_no_of_series = ds[0x0020, 0x0013].value if (0x0020, 0x0013) in ds else None
        self.echotime = ds[0x0018, 0x0081].value if (0x0018, 0x0081) in ds else None
        self.content_time = ds[0x0008, 0x0033].value if (0x0008, 0x0033) in ds else None
        self.repetition_time = ds[0x0019, 0x1087].value if (0x0019, 0x1087) in ds else None
        self.magnetic = ds[0x0018, 0x0087].value if (0x0018, 0x0087) in ds else None
        self.window_level = ds[0x0028, 0x1050].value if (0x0028, 0x1050) in ds else None
        self.window_width = ds[0x0028, 0x1051].value if (0x0028, 0x1051) in ds else None
        self.study_date = ds[0x0008, 0x0020].value if (0x0008, 0x0020) in ds else None
        self.study_time = ds[0x0008, 0x0030].value if (0x0008, 0x0030) in ds else None
        self.study_id = ds[0x0020, 0x0010].value if (0x0020, 0x0010) in ds else None
        self.modality = ds[0x0008, 0x0060].value if (0x0008, 0x0060) in ds else None
        self.series_data_time_stamp = ds[0x0009, 0x10e9].value if (0x0009, 0x10e9) in ds else None
        self.acquisition_time = ds[0x0008, 0x0032].value if (0x0008, 0x0032) in ds else "300000"
        self.content_date = ds[0x0008, 0x0023].value if (0x0008, 0x0023) in ds else None
        self.window_center = ds[0x0028, 0x1050].value if (0x0028, 0x1050) in ds else None
        self.window_width = ds[0x0028, 0x1051].value if (0x0028, 0x1051) in ds else None
        self.tr = ds[0x0018, 0x0080].value if (0x0018, 0x0080) in ds else None
        self.te = ds[0x0018, 0x81].value if (0x0018, 0x81) in ds else None

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
            self.parentItem().mouseMoveEvent(event) # 可以跟parent同時移動
            # orig_cursor_position = event.lastScenePos()
            # updated_cursor_position = event.scenePos()
            # orig_position = self.scenePos()
            # updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            # updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            # self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        pass

class Protractor(QtWidgets.QGraphicsPathItem):
    def __init__(self, qpainterpath):
        super().__init__(qpainterpath)
        self.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.angle_degree = 0
        self.sp = None
        self.mp = None
        self.ep = None
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
        self.sp = None
        self.ep = None
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
            print(orig_position)
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
    def __init__(self, _i, _j, parent = None):
        super(PhotoViewer, self).__init__(parent)
        self.in_ith = _i
        self.in_jth = _j
        self.ds_copy = None
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._pixmap = None
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setAcceptDrops(True)
        self.ruler_start = False
        self.protractor_start = False
        self.pen_start = False
        self.press_key = None
        self.instance_of_series = 0
        self.number_of_instance = 0
        self.rotate_degree = 0
        self.delete = False
        # self.hbox = QtWidgets.QHBoxLayout(self)
        self.dicomGrid = QtWidgets.QGridLayout(self)
        self.dicomGrid.setContentsMargins(10, 0, 10, 0) # L,T,R,B
        self.dicomListRT = QListWidget(self)
        self.dicomListRT.setStyleSheet("color:#fff; background-color:transparent;")
        self.dicomListRT.setContentsMargins(0, 0, 0, 0)
        self.dicomListRT.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dicomListLT = QListWidget(self)
        self.dicomListLT.setStyleSheet("color:#fff; background-color:transparent;")
        self.dicomListLT.setContentsMargins(0, 0, 0, 0)
        self.dicomListLT.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dicomListLB = QListWidget(self)
        self.dicomListLB.setStyleSheet("color:#fff; background-color:transparent;")
        self.dicomListLB.setContentsMargins(0, 0, 0, 0)
        self.dicomListLB.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dicomListLB.setMaximumSize(100, 50)
        self.dicomListRB = QListWidget(self)
        self.dicomListRB.setStyleSheet("color:#fff; background-color:transparent;")
        self.dicomListRB.setContentsMargins(0, 0, 0, 0)
        self.dicomListRB.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.dicomListRB.setMaximumSize(100, 50)
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(10)
        self.dicomListRT.setFont(font)
        self.dicomListLT.setFont(font)
        self.dicomListRB.setFont(font)
        self.dicomListLB.setFont(font)
        # self.hbox.addWidget(self.dicomListLT)
        # self.hbox.addStretch(1)
        # self.hbox.addWidget(self.dicomListRT)
        # self.hbox.setStretch(0, 1.5)
        # self.hbox.setStretch(1, 4)
        # self.hbox.setStretch(2, 1.95)
        # self.hbox.setSpacing(self.width()-200)
        space = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.dicomGrid.addWidget(self.dicomListLT, 0, 0)
        # self.dicomGrid.addItem(space, 0, 1)
        self.dicomGrid.addWidget(self.dicomListRT, 0, 2)
        # self.dicomGrid.addItem(space, 1, 0)
        # self.dicomGrid.addItem(space, 1, 1)
        # self.dicomGrid.addItem(space, 1, 2)
        self.dicomGrid.addWidget(self.dicomListLB, 2, 0)
        # self.dicomGrid.addItem(space, 2, 1)
        self.dicomGrid.addWidget(self.dicomListRB, 2, 2)
        print("888")
        self.dicomGrid.setRowStretch(0, 1)
        self.dicomGrid.setRowStretch(1, 5)
        self.dicomGrid.setRowStretch(2, 1)
        self.dicomGrid.setColumnStretch(0, 1)
        self.dicomGrid.setColumnStretch(1, 3)
        self.dicomGrid.setColumnStretch(2, 1)





    def resetWindow(self, WL, WW):
        if (WL == 0 and WW == 0):
            WL = self.ds_copy[self.instance_of_series].window_level
            WW = self.ds_copy[self.instance_of_series].window_width
        arr = self.ds_copy[self.instance_of_series].pixel_array
        arr = np.copy(np.uint16(initialWidget.mappingWindow(arr, WL, WW)))
        print(WL, WW)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16).copy()
        pixmap = QtGui.QPixmap(qimage)
        pixmap = pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.setPhoto(pixmap)

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

    def clear(self):
        for item in self._scene.items():
            if isinstance(item, QGraphicsLabel) or isinstance(item, Pen) or isinstance(item, Protractor) or isinstance(item, Ruler):
                self._scene.removeItem(item)

    def hasPhoto(self):
        return not self._empty

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.fitInView()
        return super().resizeEvent(event)

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
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._pixmap = pixmap
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self._empty = True
            self.pixmap = None
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self.press_key = event.key()
        if self.delete:
            item = self._scene.itemAt(self.sp, QTransform())
            # 刪除所選item
            if self.press_key == 16777223 and PhotoViewer.tool_lock == 'mouse':
                if isinstance(item, Pen) or isinstance(item, Protractor) or isinstance(item, Ruler):
                    self._scene.removeItem(item)
                elif isinstance(item, QGraphicsLabel):
                    fi = item.parentItem()
                    self._scene.removeItem(fi)
                    app.instance().restoreOverrideCursor()  # label需要兩次hoverLeaveEvent
                app.instance().restoreOverrideCursor()  # 需要hoverLeaveEvent，否則會刪掉後會一直有手手
        return super().keyPressEvent(event)
    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.press_key = None
        return super().keyReleaseEvent(event)
    def wheelEvent(self, event):
        if PhotoViewer.tool_lock == 'magnifier' or self.press_key == 16777249:
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
        else:
            if self.number_of_instance > 1:
                self.instance_of_series += 1
                self.instance_of_series %= self.number_of_instance
                # print(self.instance_of_series) 
                pixmap = self.ndarray2QPixmap(self.instance_of_series)
                self.setPhoto(pixmap)
                self.dicomListLT.clear()
                self.dicomListRT.clear()
                self.dicomListRB.clear()
                self.dicomListLB.clear()
                self.dicomListLT.addItem((str(self.instance_of_series + 1)+"/"+str(self.number_of_instance)))

                se = self.ds_copy[self.instance_of_series].series_number
                tr = self.ds_copy[self.instance_of_series].tr
                te = self.ds_copy[self.instance_of_series].te
                # 要靠右邊，需寫成QListWidgetItem
                cd = self.ds_copy[self.instance_of_series].content_date  # 拍攝照片日期
                cd = cd[:4] + "/" + cd[4:6] + "/" + cd[6:]
                itemcd = QListWidgetItem(cd)
                itemcd.setTextAlignment(Qt.AlignRight)
                ct = self.ds_copy[self.instance_of_series].content_time  # 拍攝照片時間
                ct = ct[:2]+":"+ct[2:4]+":"+ct[4:]
                itemct = QListWidgetItem(ct)
                itemct.setTextAlignment(Qt.AlignRight)
                sd = self.ds_copy[self.instance_of_series].series_description
                itemsd = QListWidgetItem(sd)
                itemsd.setTextAlignment(Qt.AlignRight)
                wc = self.ds_copy[self.instance_of_series].window_center
                ww = self.ds_copy[self.instance_of_series].window_width

                self.dicomListLT.addItem(("se: "+str(se)))
                self.dicomListLB.addItem(("TR: "+str(tr)))
                self.dicomListLB.addItem(("TE: "+str(te)))
                self.dicomListRB.addItem(itemcd)
                self.dicomListRB.addItem(itemct)
                self.dicomListRT.addItem(itemsd)


    # 控制item能否移動
    def Movable(self, enble):
        for item in self._scene.items():
            if isinstance(item, QGraphicsLabel) or isinstance(item, Pen) or isinstance(item, Protractor) or isinstance(item, Ruler):
                item.setMovable(enble)

    def rotate(self, angle: float) -> None:
        self.rotate_degree += angle
        self.rotate_degree %= 360
        return super().rotate(angle)
    # 控制Label轉正
    def turnBack(self, angle):
        for item in self._scene.items():
            if isinstance(item, QGraphicsLabel):
                if isinstance(item.parentItem(), Ruler):
                    pitem = item.parentItem()
                    if self.mapFromScene(pitem.sp).x() <= self.mapFromScene(pitem.ep).x(): 
                        tmp = self.mapFromScene(pitem.ep) + QtCore.QPoint(10, 0)
                        item.setPos(self.mapToScene(tmp))
                    else:
                        tmp = self.mapFromScene(pitem.sp) + QtCore.QPoint(10, 0)
                        item.setPos(self.mapToScene(tmp))
                elif isinstance(item.parentItem(), Protractor):
                    pitem = item.parentItem()
                    scale = 1 if self.mapFromScene(pitem.sp).x() < self.mapFromScene(pitem.ep).x() else -4
                    if self.mapFromScene(pitem.mp).x() > self.mapFromScene(pitem.ep).x() and self.mapFromScene(pitem.mp).y() < self.mapFromScene(pitem.ep).y(): 
                        tmp = self.mapFromScene(pitem.ep) + QtCore.QPoint(scale * 5, 10)
                        item.setPos(self.mapToScene(tmp))
                    else:
                        tmp = self.mapFromScene(pitem.ep) + QtCore.QPoint(scale * 5, -25)
                        item.setPos(self.mapToScene(tmp))
                item.setRotation(item.rotation() - angle)

    # move時True,有手手
    def toggleDragMode(self, enble):
        if enble:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def mousePressEvent(self, event):
        self.sp = self.mapToScene(event.pos())
        self.delete = True
        initialWidget.pic_ith = self.in_ith
        initialWidget.pic_jth = self.in_jth
        if PhotoViewer.tool_lock == 'move':
            pass
        elif PhotoViewer.tool_lock == 'ruler':
            self.ruler = Ruler(self.sp.x(), self.sp.y(), self.sp.x(), self.sp.y())
            self.ruler_text_label = QGraphicsLabel("")
            self.ruler_text_label.setRotation(-self.rotate_degree)
            self._scene.addItem(self.ruler_text_label)
            self.ruler.setMovable(False)
            self._scene.addItem(self.ruler)
            self.ruler_start = True
        elif PhotoViewer.tool_lock == 'angle':
            if not self.protractor_start and not self.ruler_start:
                self.qpainterpath = QtGui.QPainterPath(self.sp)
                self.protractor = Protractor(self.qpainterpath)
                self.protractor_text_label = QGraphicsLabel("")
                self.protractor_text_label.setRotation(-self.rotate_degree)
                self._scene.addItem(self.protractor_text_label)
                self._scene.addItem(self.protractor)
                self.protractor_start = True
            elif not self.protractor_start and self.ruler_start:
                self.protractor.setMovable(False)
                self.protractor_text_label.setMovable(False)
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
            self.ruler.sp = self.sp
            self.ruler.ep = self.ep
            self.ruler.setMovable(False)
            self.ruler_text_label.setMovable(False)
            self.ruler_start = False
            self.ruler_text_label.setParentItem(self.ruler)
        elif PhotoViewer.tool_lock == 'angle':
            if self.protractor_start:
                self.qpainterpath.clear()
                self.qpainterpath.moveTo(self.sp)
                self.qpainterpath.lineTo(self.ep)
                self.protractor.setPath(self.qpainterpath)
                self.protractor.setMovable(False)
                self.protractor_text_label.setMovable(False)
                self.protractor_start = False
                self.ruler_start = True
                self.protractor_text_label.setParentItem(self.protractor)
        if PhotoViewer.tool_lock == 'pen':
            self.pen_path.lineTo(self.ep)
            self.pen.setPath(self.pen_path)
            self.pen.setMovable(False)
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
            if self.mapFromScene(self.sp.toPoint()).x() <= self.mapFromScene(self.mp.toPoint()).x(): 
                tmp = self.mapFromScene(self.mp.toPoint()) + QtCore.QPoint(10, 0)
                self.ruler_text_label.setPos(self.mapToScene(tmp))
            else:
                tmp = self.mapFromScene(self.sp.toPoint()) + QtCore.QPoint(10, 0)
                self.ruler_text_label.setPos(self.mapToScene(tmp))
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
                self.protractor.sp = self.sp
                self.protractor.mp = self.mp
                self.protractor.ep = self.ep
                spToep = np.sqrt(QtCore.QPointF.dotProduct(self.sp - self.ep, self.sp - self.ep))
                epTomp = np.sqrt(QtCore.QPointF.dotProduct(self.mp - self.ep, self.mp - self.ep))
                self.protractor.angle_degree = np.arccos(QtCore.QPointF.dotProduct(self.ep - self.sp, self.ep - self.mp) / spToep / epTomp) * 180 / np.pi
                # self.protractor_text_label.setText("%.1f°" % self.protractor.angle_degree)
                self.protractor_text_label.setHtml("<div style='background-color:#3c1e1e;font-size:10px;color:#e6e60a;'>" + "%.1f°" % self.protractor.angle_degree + "</div>")
                scale = 1 if self.mapFromScene(self.sp.toPoint()).x() < self.mapFromScene(self.ep.toPoint()).x() else -4
                if self.mapFromScene(self.mp.toPoint()).x() > self.mapFromScene(self.ep.toPoint()).x() and self.mapFromScene(self.mp.toPoint()).y() < self.mapFromScene(self.ep.toPoint()).y(): 
                    tmp = self.mapFromScene(self.ep.toPoint()) + QtCore.QPoint(scale * 5, 10)
                    self.protractor_text_label.setPos(self.mapToScene(tmp))
                else:
                    tmp = self.mapFromScene(self.ep.toPoint()) + QtCore.QPoint(scale * 5, -25)
                    self.protractor_text_label.setPos(self.mapToScene(tmp))
        if PhotoViewer.tool_lock == 'pen' and self.pen_start:
            self.pen_path.lineTo(self.mp)
            self.pen.setPath(self.pen_path)
        super(PhotoViewer, self).mouseMoveEvent(event)

    def decode_data(self, bytearray):
        data = []
        item = {}
        ds = QtCore.QDataStream(bytearray)
        while not ds.atEnd():
            row = ds.readInt32()
            column = ds.readInt32()
            map_items = ds.readInt32()
            for i in range(map_items):
                key = ds.readInt32()
                value = QtCore.QVariant()
                ds >> value
                item[Qt.ItemDataRole(key)] = value
            data.append(item)
        return data
    def ndarray2QPixmap(self, index):
        arr = initialWidget.mappingWindow(self.ds_copy[index].pixel_array, self.ds_copy[index].window_level, self.ds_copy[index].window_width)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16).copy()
        pixmap = QtGui.QPixmap(qimage)
        pixmap = pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        return pixmap
    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        super().dropEvent(event)
        event.accept()
        fake_model = QtGui.QStandardItemModel()
        fake_model.dropMimeData(
            event.mimeData(), event.dropAction(), 0, 0, QtCore.QModelIndex()
        )
        for r in range(fake_model.rowCount()):
            for c in range(fake_model.columnCount()):
                ix = fake_model.index(r, c)
                key_study = ix.data(Qt.UserRole)
                key_series = ix.data(Qt.DisplayRole)
        self.ds_copy = initialWidget.series_2_dicoms[initialWidget.pic_ith][key_study][key_series]
        self.instance_of_series = 0
        self.number_of_instance = len(initialWidget.series_2_dicoms[initialWidget.pic_ith][key_study][key_series])
        pixmap = self.ndarray2QPixmap(self.instance_of_series)
        self.setPhoto(pixmap)
        self.dicomListLT.clear()
        self.dicomListRT.clear()
        self.dicomListRB.clear()
        self.dicomListLB.clear()
        self.dicomListLT.addItem((str(self.instance_of_series + 1)+"/"+str(self.number_of_instance)))
        
        se = self.ds_copy[self.instance_of_series].series_number
        tr = self.ds_copy[self.instance_of_series].tr
        te = self.ds_copy[self.instance_of_series].te
        # 要靠右邊，需寫成QListWidgetItem
        cd = self.ds_copy[self.instance_of_series].content_date  # 拍攝照片日期
        if cd: # 有人的cd是 None
            cd = cd[:4] + "/" + cd[4:6] + "/" + cd[6:]
        itemcd = QListWidgetItem(cd)
        itemcd.setTextAlignment(Qt.AlignRight)
        ct = self.ds_copy[self.instance_of_series].content_time  # 拍攝照片時間
        if ct: # 有人的ct是 None
            ct = ct[:2]+":"+ct[2:4]+":"+ct[4:]
        itemct = QListWidgetItem(ct)
        itemct.setTextAlignment(Qt.AlignRight)
        sd = self.ds_copy[self.instance_of_series].series_description
        itemsd = QListWidgetItem(sd)
        itemsd.setTextAlignment(Qt.AlignRight)
        wc = self.ds_copy[self.instance_of_series].window_center
        ww = self.ds_copy[self.instance_of_series].window_width

        self.dicomListLT.addItem(("se: "+str(se)))
        self.dicomListLB.addItem(("TR: "+str(tr)))
        self.dicomListLB.addItem(("TE: "+str(te)))
        self.dicomListRB.addItem(itemcd)
        self.dicomListRB.addItem(itemct)
        self.dicomListRT.addItem(itemsd)
        print(ct)

        """
        mimeReader = event.mimeData().data('application/x-qabstractitemmodeldatalist')
        data_items = self.decode_data(mimeReader)
        series = data_items[0][Qt.DisplayRole].value()
        print(series)
        self.ds_copy = initialWidget.series_2_dicoms[initialWidget.pic_ith][series]
        self.number_of_instance = len(initialWidget.series_2_dicoms[initialWidget.pic_ith][series])
        self.instance_of_series = 0
        pixmap = self.ndarray2QPixmap(self.instance_of_series)
        self.setPhoto(pixmap)
        # """
    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()
class MyCustomWidget(QtWidgets.QWidget):#thumbnail list study分隔
    def __init__(self, t1, t2, t3, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        self.row = QtWidgets.QVBoxLayout()
        self.label_1 = QtWidgets.QLabel(t1)
        self.label_1.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_1.setFont(QtGui.QFont('Verdana', 9))
        self.label_1.setStyleSheet("QLabel { background-color : rgb(162, 196, 201); padding: 10px 0px 0px 0px;}")
        self.label_2 = QtWidgets.QLabel(t2)
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_2.setFont(QtGui.QFont('Verdana', 9))
        self.label_2.setStyleSheet("QLabel { background-color : rgb(162, 196, 201); padding: 5px 0px 5px 0px;}")
        self.label_3 = QtWidgets.QLabel(t3)
        self.label_3.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_3.setFont(QtGui.QFont('Verdana', 9))
        self.label_3.setStyleSheet("QLabel { background-color : rgb(162, 196, 201); padding: 0px 0px 10px 0px;}")
        self.row.setSpacing(0)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.addWidget(self.label_1)
        self.row.addWidget(self.label_2)
        self.row.addWidget(self.label_3)
        # self.row.addWidget(QtWidgets.QPushButton("view"))
        # self.row.addWidget(QtWidgets.QPushButton("select"))
        self.setLayout(self.row)
class MyCustomWidgetPtid(QtWidgets.QWidget): #thumbnail list第一格放patient id
    def __init__(self, t1, parent=None):
        super(MyCustomWidgetPtid, self).__init__(parent)
        self.row = QtWidgets.QVBoxLayout()
        self.label_1 = QtWidgets.QLabel(t1)
        self.label_1.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_1.setFont(QtGui.QFont('Verdana', 10))
        self.label_1.setStyleSheet("QLabel { background-color : rgb(118, 165, 175); padding: 10px 0px 7px 0px;color: white;font-weight: bold;}")
        self.row.setSpacing(0)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.addWidget(self.label_1)
        self.setLayout(self.row)

class PhotoProcessing(QtWidgets.QWidget):
    def __init__(self, parent: None, _i, _j):
        super().__init__(parent)
        self.pv = PhotoViewer(_i, _j)
        # title bar
        self.title = TitleBar(self.pv.in_ith, self.pv.in_jth)
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.pv)
        self.title.close_button.clicked.connect(self.close)
    def close(self):
        if initialWidget.pic_windows[self.title.t_ith] != 1:
            initialWidget.pic_windows[self.title.t_ith] -= 1
            initialWidget.listShow[initialWidget.pic_ith].remove(self.pv.in_jth)
            initialWidget.listNoShow[initialWidget.pic_ith].append(self.pv.in_jth)
            print(initialWidget.pic_windows[self.title.t_ith])
            super().close()


# title bar
class TitleBar(QtWidgets.QDialog):
    def __init__(self, _i, _j,  parent = None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.t_ith = _i
        self.t_jth = _j
        self.parent = parent
        css = """
                QWidget{
                    Background: #000000;
                    color:white;
                    font:11px bold;
                    font-weight:bold;
                    border-radius: 1px;
                    height:30px;
                }
                QDialog{
                    font-size:30px;                    
                    color: black;
                }
                QToolButton{
                    Background:#AAAAAA;
                    font-size:30px;
                    height: 30px;
                    width: 30px;
                }
                QToolButton:hover{
                    Background: #FFFFFF;
                    font-size:30px;                
                }
            """
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.Highlight)
        self.setStyleSheet(css)

        self.button_frame_spine = QtWidgets.QToolButton(self)
        self.button_frame_spine.setIcon(QtGui.QIcon('generatedUiFile/res/icons/img_frame_spine.png'))
        self.button_frame_spine.setIconSize(QtCore.QSize(25, 25))

        self.button_heat_map = QtWidgets.QToolButton(self)
        self.button_heat_map.setIcon(QtGui.QIcon('generatedUiFile/res/icons/img_heat_map.png'))
        self.button_heat_map.setIconSize(QtCore.QSize(25, 25))

        self.button_scoliosis_angle = QtWidgets.QToolButton(self)
        self.button_scoliosis_angle.setIcon(QtGui.QIcon('generatedUiFile/res/icons/img_scoliosis_angle.png'))
        self.button_scoliosis_angle.setIconSize(QtCore.QSize(25, 25))

        self.close_button = QtWidgets.QToolButton(self)
        self.close_button.setIcon(QtGui.QIcon('generatedUiFile/res/icons/x 3.png'))
        self.close_button.setIconSize(QtCore.QSize(15, 15))
        self.close_button.setStyleSheet("""
                            QToolButton{
                                Background:#000;
                            }
                            QToolButton::hover{
                                Background: #fff;
                            }
                            """)
        label = QtWidgets.QLabel(self)
        # label.setText(" ")
        # self.setWindowTitle("patient number")


        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.button_frame_spine)
        hbox.addWidget(self.button_heat_map)
        hbox.addWidget(self.button_scoliosis_angle)
        hbox.addWidget(self.close_button)
        hbox.insertStretch(1, 500)
        hbox.setSpacing(10)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.button_frame_spine.clicked.connect(self.frameSpine)
        self.button_heat_map.clicked.connect(self.heatMap)
        self.button_scoliosis_angle.clicked.connect(self.scoliosis_angle)

    def mousePressEvent(self, event):
        self.sp = self.mapToScene(event.pos())
        initialWidget.pic_ith = self.t_ith
        initialWidget.pic_jth = self.t_jth

    def mapToScene(self, x):
        initialWidget.pic_ith = self.t_ith
        initialWidget.pic_jth = self.t_jth

    def frameSpine(self):
        print("frameSpine", self.t_ith, self.t_jth)

    def heatMap(self):
        print("heatmap", self.t_ith, self.t_jth)

    def scoliosis_angle(self):
        print("scoliosis_angle", self.t_ith, self.t_jth)

    # def close(self):
    #     # print("close", self.t_ith, self.t_jth)
    #     super(TitleBar, self).close()
        # initialWidget.closePicWindowX(self.t_ith, self.t_jth)
        # initialWidget.gridLayout_list[self.t_ith].removeWidget(initialWidget.pic_viewer[self.t_ith][self.t_jth])




if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    mw.show()
    sys.exit(app.exec_())
