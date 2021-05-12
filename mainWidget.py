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

        self.pt_list.append("0135678")
        self.pt_list.append("3847829")
        self.pt_list.append("2342422")

        self.pt_list.sort()
        for ptid in self.pt_list:
            self.ui.no_list.addItem(ptid)
        
        self.tmp_cnt = 0    
        
        # 控制工具列現在選擇的工具為: mouse(defalut), pen, angle, ruler, move 
        self.tool_lock = "mouse"
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
        self.ui.input_no.setCompleter(completer)  # 搜尋紀錄
        self.linkPage2Array() # 將影像處理頁面預設有五頁
        self.ui.pushButton_angle.clicked.connect(self.pushButtonAngleClicked) # 角度按鈕連結
        self.ui.pushButton_add_pic.clicked.connect(self.pushButtonAddPicClicked) # 加照片按鈕連結
        self.ui.pushButton_pen.clicked.connect(self.pushButtonPenClicked)
#工具列-----------------------------------------------------------------------------------------------------------
    def picMouseReleased(self, event, _i, _j):
        if(self.tool_lock == 'mouse'):
            return
        elif(self.tool_lock == 'angle'):
            if event.button() == Qt.LeftButton:
                if(self.pic_clicked[_i][_j]):
                    self.pic_released[_i][_j] = True
                else:
                    if(self.angle_start_x[_i][_j] != self.angle_middle_x[_i][_j] and self.angle_start_y[_i][_j] != self.angle_middle_y[_i][_j]):
                        self.angle_coordinate_list[_i][_j].append(angleCoordinate(
                            self.angle_start_x[_i][_j], self.angle_start_y[_i][_j],
                            self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j],
                            self.angle_end_x[_i][_j], self.angle_end_y[_i][_j]
                            ))
                        self.angle_start_x[_i][_j] = self.angle_middle_x[_i][_j] = 0  
                        self.angle_start_y[_i][_j] = self.angle_middle_y[_i][_j] = 0
                    print(self.angle_coordinate_list[_i][_j])  
                    print(_i, _j, len(self.angle_coordinate_list[_i][_j]))
                    self.pic_released[_i][_j] = False
        elif(self.tool_lock == 'pen'):
            return

    def picMousePressed(self, event, _i, _j):
        self.pic_ith = _i
        self.pic_jth = _j
        if(self.tool_lock == 'mouse'):
            return
        elif(self.tool_lock == 'angle'):
            if event.button() == QtCore.Qt.LeftButton:
                if(not self.pic_clicked[_i][_j]):
                    self.pic_clicked[_i][_j] = True
                    self.angle_start_x[self.pic_ith][self.pic_jth] = event.pos().x()
                    self.angle_start_y[self.pic_ith][self.pic_jth] = event.pos().y()
                else:
                    self.pic_clicked[_i][_j] = False
            # print("clicked:%d, released:%d" % (self.pic_clicked[_i][_j], self.pic_released[_i][_j]))
        elif(self.tool_lock == 'pen'):
            if event.button() == QtCore.Qt.LeftButton:
                self.pen_end_x[_i][_j] = event.x()
                self.pen_end_y[_i][_j] = event.y()
                self.pen_start_x[self.pic_ith][self.pic_jth] = event.pos().x()
                self.pen_start_y[self.pic_ith][self.pic_jth] = event.pos().y()

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
        self.update()

    def picPaint(self, event, pixmap, _i, _j):
        q = QtGui.QPainter(self.pic[_i][_j])
        q.drawPixmap(0, 0, 512, 512, pixmap)
        p = QtGui.QPainter(self.transparent_pix[_i][_j])
        q.drawPixmap(0, 0, self.transparent_pix[_i][_j])
        # show every angle
        # for k in range(1, self.MAXIMUM_PAGE + 1):
        #     for v in range(1, (self.MAXIMUM_PIC + 1)):
        for w in self.angle_coordinate_list[_i][_j]:
            pen = QtGui.QPen()
            pen.setWidth(6)
            q.setPen(pen)
            q.drawLine(w.mx, w.my, w.sx, w.sy)
            q.drawLine(w.ex, w.ey, w.mx, w.my)

        if(self.tool_lock == 'mouse'):
            return
        
        elif(self.tool_lock == 'angle'):
            if(not self.pic_clicked[_i][_j] and not self.pic_released[_i][_j]):
                #self.pic[_i][_j].setMouseTracking(False)
                return
            else:
                self.pic[_i][_j].setMouseTracking(True)
                pen = QtGui.QPen()
                pen.setWidth(6)
                q.setPen(pen)
                q.drawLine(self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j], self.angle_start_x[_i][_j], self.angle_start_y[_i][_j])
                q.drawLine(self.angle_end_x[_i][_j], self.angle_end_y[_i][_j], self.angle_middle_x[_i][_j], self.angle_middle_y[_i][_j])
            
        elif(self.tool_lock == 'pen'):
            self.pic[_i][_j].setMouseTracking(False)
            pen = QtGui.QPen()
            pen.setWidth(6)
            p.setPen(pen)
            p.drawLine(self.pen_end_x[_i][_j], self.pen_end_y[_i][_j], self.pen_start_x[_i][_j], self.pen_start_y[_i][_j])
        q.end()

#按鈕連結處--------------------------------------------------------------------------------------------------------

    def pushButtonAngleClicked(self):
        self.tool_lock = 'angle'

    def pushButtonAddPicClicked(self):
        fileName1, filetype = QFileDialog.getOpenFileName(self,"選取檔案","/Users/user/Documents/畢專/dicom_data","All Files (*);;Text Files (*.txt)")  #設定副檔名過濾,注意用雙分號間隔
        print(filetype)
        # fileName2, ok2 = QFileDialog.getSaveFileName(self,"檔案儲存","./","All Files (*);;Text Files (*.txt)")

    def pushButtonPenClicked(self):
        self.tool_lock = 'pen'

    

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
    
    def duplicateAdd(self):
        print("test")
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Patient already exist !")
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_() 

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
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], QtGui.QImage.Format_Grayscale8)
        self.pic[i][j].setPixmap(QtGui.QPixmap(qimage))
        self.pic[i][j].setGeometry(QtCore.QRect(0, 0, 400, 500))
        self.pic[i][j].mousePressEvent = lambda pressed: self.picMousePressed(pressed, i, j) # 讓每個pic的mousePressEvent可以傳出告訴自己是誰
        self.pic[i][j].mouseReleaseEvent = lambda released: self.picMouseReleased(released, i, j)
        self.pic[i][j].mouseMoveEvent = lambda moved: self.picMouseMove(moved, i, j)
        self.pic[i][j].paintEvent = lambda painted: self.picPaint(painted, QtGui.QPixmap(qimage), i, j)
        
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
        self.pic_clicked = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.pic_released = [ [False] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        self.angle_coordinate_list = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
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
                self.angle_coordinate_list[i][j] = []
        self.pic_cnt = [0] * (self.MAXIMUM_PAGE + 1)
        self.pic_ith = self.pic_jth = 1

        # 畫圖透明canvas
        self.transparent_pix = [ [None] * (self.MAXIMUM_PIC + 1) for i in range(self.MAXIMUM_PAGE + 1) ]
        for i in range(1, self.MAXIMUM_PAGE + 1):
            for j in range(1, (self.MAXIMUM_PIC + 1)):
                self.transparent_pix[i][j] = QtGui.QPixmap(512, 512)
                self.transparent_pix[i][j].fill(Qt.transparent)

        # 暫時試試放照片
        self.showPic(1, 1, "01372635","5F327951.dcm")
        self.showPic(1, 2, "01372635","5F327951.dcm")
        self.showPic(1, 3, "01372635","5F327951.dcm")
        self.showPic(1, 4, "01372635","5F327951.dcm")

    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def restoreOrMaximizeWindow(self):
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
class angleCoordinate():
    def __init__(self, _sx, _sy, _mx, _my, _ex, _ey):
        self.sx = _sx
        self.sy = _sy
        self.mx = _mx
        self.my = _my
        self.ex = _ex
        self.ey = _ey

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mw = initialWidget()
    mw.show()
    sys.exit(app.exec_())