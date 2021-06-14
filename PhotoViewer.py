from PyQt5 import QtCore, QtGui, QtWidgets
from pydicom import dcmread
import numpy as np
class Ruler(QtWidgets.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.setPen(QtGui.QPen(QtGui.QColor(5, 105, 25)))
        self.setAcceptHoverEvents(True)

    # mouse hover event
    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    # mouse click event
    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QtCore.QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        print('x: {0}, y: {1}'.format(self.pos().x(), self.pos().y()))

class PhotoViewer(QtWidgets.QGraphicsView):

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self.tool_lock = 'move'
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.ruler_start = False

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
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
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
        if self.tool_lock == 'move':
            print(self.tool_lock)
            
        if self.tool_lock == 'ruler':
            print(event.pos().x(), event.pos().y())
            self.sp = self.mapToScene(event.pos().x(), event.pos().y())
            self.ruler = Ruler(self.sp.x(), self.sp.y(), self.sp.x(), self.sp.y())
            self._scene.addItem(self.ruler)
            self.ruler_start = True
        super(PhotoViewer, self).mousePressEvent(event)
    def mouseReleaseEvent(self, event):
        if self.tool_lock == 'ruler':
            self.ep = self.mapToScene(event.pos())
            self.ruler.setLine(self.sp.x(), self.sp.y(), self.ep.x(), self.ep.y())
            self.ruler_start = False
        super(PhotoViewer, self).mouseReleaseEvent(event)
    def mouseMoveEvent(self, event):
        if self.tool_lock == 'ruler' and self.ruler_start:
            self.mp = self.mapToScene(event.pos())
            self.ruler.setLine(self.sp.x(), self.sp.y(), self.mp.x(), self.mp.y())
        super(PhotoViewer, self).mouseMoveEvent(event)
        
class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.viewer = PhotoViewer(self)
        # 'Load image' button
        self.btnLoad = QtWidgets.QToolButton(self)
        self.btnLoad.setText('Load image')
        self.btnLoad.clicked.connect(self.loadImage)
        #  tmp
        self.windows_menu = QtWidgets.QMenu()
        self.windows_menu.addAction('ruler', lambda: self.setToolLock('ruler'))
        self.windows_menu.addAction('angle', lambda: self.setToolLock('angle'))
        self.windows_menu.addAction('move', lambda: self.setToolLock('move'))
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        HBlayout.addWidget(self.btnLoad)
        HBlayout.addWidget(self.windows_menu)
        VBlayout.addLayout(HBlayout)
    def setToolLock(self, lock):
        self.viewer.tool_lock = lock
        if self.viewer.tool_lock == 'move':
            self.viewer.toggleDragMode()
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


    
    def mappingWindow(self, arr, WL, WW):
        pixel_max = WL + WW/2
        pixel_min = WL - WW/2
        arr = np.clip(arr, pixel_min, pixel_max)
        arr = (arr - pixel_min) / (pixel_max - pixel_min) * 65535
        return np.copy(np.uint16(arr))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())