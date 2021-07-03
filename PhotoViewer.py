from os import environ
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainterPath
from pydicom import dcmread
import numpy as np
from PyQt5.QtCore import Qt


class QGraphicsLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, text):
        super().__init__(text)
        # self.setPen(QtGui.QPen(QtGui.QColor(230, 230, 10)))
        # self.setBrush(QtGui.QBrush(QtGui.QColor(60, 30, 30)))
        self.movable = False
        self.setVisible(False)
        self.setRotation(window.rotate_angle)
        self.category = None # 標明他是ruler或是Protractor的label
    def adjustPos(self, view):
        if self.category == 'ruler':
            nsp = view.mapToScene(int(self.ruler_sp.x()), int(self.ruler_sp.y()))
            nmp = view.mapToScene(int(self.ruler_mp.x()), int(self.ruler_mp.y()))
            print(nsp.x(), nmp.x())
            if nsp.x() <= nmp.x(): 
                self.setPos(self.ruler_mp + QtCore.QPointF(10, 0))
            else:
                self.setPos(self.ruler_sp + QtCore.QPointF(10, 0))
    def setRulerLabel(self, sp, mp):
        self.category = 'ruler'
        self.ruler_sp = sp
        self.ruler_mp = mp
    def setProtractorLabel(self):
        self.category = 'protractor'

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

    def setRotate(self, rotate_angle):
        self.setRotation(-rotate_angle)

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
        #self.setAcceptHoverEvents(enable)
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
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
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


        self.title = self.TitleBar()
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(self.title)
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setContentsMargins(0, 0, 0, 0)



        # self._scene.addWidget(self.title)
    
    def setNewScene(self):
        self._scene = QtWidgets.QGraphicsScene(self)
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

    def Movable(self, enble):
        for item in self._scene.items():
            if isinstance(item, QGraphicsLabel) or isinstance(item, Pen) or isinstance(item, Protractor) or isinstance(item, Ruler):
                item.setMovable(enble)

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        self.sp = self.mapToScene(event.pos())
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
            self.pen_path = QPainterPath()
            self.pen_path.moveTo(self.sp)
            self.pen = Pen(self.pen_path)
            self.pen.setMovable(False)
            self.pen.setPath(self.pen_path)
            self._scene.addItem(self.pen)
            self.pen_start = True
        super(PhotoViewer, self).mousePressEvent(event)

    def labelRotate(self):
        for item in self._scene.items():
            if isinstance(item, QGraphicsLabel):
                item.setRotate(-window.rotate_angle)
                if item.category == 'ruler':
                    item.adjustPos(self)
                    print("1, ", item.pos())
                    print("2, ", self.mapToScene(QtCore.QPoint(int(item.pos().x()), int(item.pos().y()))))
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
            self.ruler_text_label.setRulerLabel(self.sp, self.mp)
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

    class TitleBar(QtWidgets.QDialog):
        def __init__(self, parent=None):
            QtWidgets.QDialog.__init__(self, parent)
            self.setWindowFlags(Qt.FramelessWindowHint)
            css = """
                    QWidget{
                        Background: #000000;
                        color:white;
                        font:12px bold;
                        font-weight:bold;
                        border-radius: 1px;
                        height: 11px;
                    }
                    QDialog{
                        Background-image:url('img/titlebar bg.png');
                        font-size:12px;                    
                        color: black;
                    }
                    QToolButton{
                        Background:#AAAAAA;
                        font-size:11px;
                    }
                    QToolButton:hover{
                        Background: #FFFFFF;
                        font-size:11px;                
                    }
                """
            self.setAutoFillBackground(True)
            self.setBackgroundRole(QtGui.QPalette.Highlight)
            self.setStyleSheet(css)
            self.minimize = QtWidgets.QToolButton(self)
            self.minimize.setIcon(QtGui.QIcon('img/min.png'))
            self.maximize = QtWidgets.QToolButton(self)
            self.maximize.setIcon(QtGui.QIcon('img/max.png'))
            close = QtWidgets.QToolButton(self)
            close.setIcon(QtGui.QIcon('generatedUiFile/res/icons/x 3.png'))
            self.minimize.setMinimumHeight(10)
            close.setMinimumHeight(10)
            self.maximize.setMinimumHeight(10)
            label = QtWidgets.QLabel(self)
            label.setText("Window Title")
            self.setWindowTitle("Window Title")
            hbox = QtWidgets.QHBoxLayout(self)
            hbox.addWidget(label)
            hbox.addWidget(self.minimize)
            hbox.addWidget(self.maximize)
            hbox.addWidget(close)
            hbox.insertStretch(1, 500)
            hbox.setSpacing(0)
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            self.maxNormal = False
            close.clicked.connect(self.close)
            # self.minimize.clicked.connect(self.showSmall)
            # self.maximize.clicked.connect(self.showMaxRestore)

        # def showSmall(self):
        #     box.showMinimized()
        #
        # def showMaxRestore(self):
        #     if (self.maxNormal):
        #         box.showNormal()
        #         self.maxNormal = False
        #         self.maximize.setIcon(QtGui.QIcon('img/max.png'))
        #         print('1')
        #     else:
        #         box.showMaximized()
        #         self.maxNormal = True
        #         print('2')
        #         self.maximize.setIcon(QtGui.QIcon('img/max2.png'))
        #
        def close(self):
            # box.close()
            self.removeWidget(self)
        # def mousePressEvent(self, event):
        #     if event.button() == Qt.LeftButton:
        #         box.moving = True
        #         box.offset = event.pos()
        #
        # def mouseMoveEvent(self, event):
        #     if box.moving: box.move(event.globalPos() - box.offset)



class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        self.viewer2 = PhotoViewer(self)
        self.rotate_angle = 0
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        # title bar
        self.m_titleBar = PhotoViewer.TitleBar(self)
        self.m_titleBar2 = PhotoViewer.TitleBar(self)

        #  tmp

        self.windows_menu = QtWidgets.QMenu()
        self.windows_menu.addAction('ruler', lambda: self.setToolLock('ruler'))
        self.windows_menu.addAction('angle', lambda: self.setToolLock('angle'))
        self.windows_menu.addAction('pen', lambda: self.setToolLock('pen'))
        self.windows_menu.addAction('move', lambda: self.setToolLock('move'))
        self.windows_menu.addAction('mouse', lambda: self.setToolLock('mouse'))
        self.windows_menu.addAction('clear', lambda: self.setToolLock('clear'))
        self.windows_menu.addAction('save', lambda: self.setToolLock('save'))
        self.windows_menu.addAction('rotate_right', lambda: self.setToolLock('rotate_right'))
        self.windows_menu.addAction('rotate_left', lambda: self.setToolLock('rotate_left'))

        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        # VBlayout.addWidget(self.m_titleBar)
        VBlayout.addWidget(self.viewer)

        # VBlayout.addWidget(self.m_titleBar2)
        # VBlayout.addWidget(self.viewer2)

        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.windows_menu)
        VBlayout.addLayout(HBlayout)

    def setToolLock(self, lock):
        self.viewer.resetFlags()
        self.viewer.Movable(False)
        PhotoViewer.tool_lock = lock
        if PhotoViewer.tool_lock == 'move':
            self.viewer.toggleDragMode()
            self.viewer.Moveable(True)
        elif PhotoViewer.tool_lock == 'clear':
            self.viewer.setNewScene()
        elif PhotoViewer.tool_lock == 'save':
            self.save()
        elif PhotoViewer.tool_lock == 'rotate_right':
            self.rotate_right()
        elif PhotoViewer.tool_lock == 'rotate_left':
            self.rotate_left()

    def loadImage(self):
        ds = dcmread('./tmp_database/01372635/5F327951.dcm')
        arr = ds.pixel_array
        arr = np.uint16(arr)
        WL = ds[0x0028, 0x1050].value
        WW = ds[0x0028, 0x1051].value
        arr = self.mappingWindow(arr, WL, WW)
        qimage = QtGui.QImage(arr, arr.shape[1], arr.shape[0], arr.shape[1]*2, QtGui.QImage.Format_Grayscale16)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        # pixmap = pixmap.scaled(self.photo.width(), self.photo.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.viewer.setPhoto(pixmap)

    def save(self):
        self.viewer.save()

    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))

    def save(self):
        self.viewer.save()

    def rotate_right(self):
        self.viewer.rotate(90)
        self.rotate_angle -= 90
        self.viewer.labelRotate()

    def rotate_left(self):
        self.viewer.rotate(-90)
        self.rotate_angle += 90
        self.viewer.labelRotate()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())