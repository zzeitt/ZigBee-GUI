import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QSpinBox, QGroupBox,
                             QVBoxLayout, QApplication,
                             QDesktopWidget)


gui_name = 'Show Map'


class MyWinMap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initWidget()  # 初始化组件
        self.initLayout()  # 初始化布局
        self.initWindow(500, 500)  # 初始化窗口
        self.initMap()  # 初始化地图
        self.show()

    def initWidget(self):
        '''地图显示控件'''
        self.lb_map = QLabel('正在加载地图……')
        self.lb_map.setAlignment(Qt.AlignCenter)
        '''阈值调节区'''
        # self.lb_thre = QLabel('设定阈值')
        self.sp_thre = QSpinBox()
        self.sp_thre.setRange(0, 10)  # 设置上界和下界

    def initLayout(self):
        self.gpbx_map = QGroupBox('地图', self)
        self.gpbx_thre = QGroupBox('阈值调节', self)
        '''箱组布局类型'''
        self.lot_v_map = QVBoxLayout()
        self.lot_v_thre = QVBoxLayout()
        self.lot_v_all = QVBoxLayout()
        '''箱组map布局设置'''
        self.lot_v_map.addWidget(self.lb_map, alignment=Qt.AlignHCenter)
        self.gpbx_map.setLayout(self.lot_v_map)
        '''箱组thre布局设置'''
        # self.lot_v_thre.addWidget(self.lb_thre, alignment=Qt.AlignHCenter)
        self.lot_v_thre.addWidget(self.sp_thre, alignment=Qt.AlignHCenter)
        self.gpbx_thre.setLayout(self.lot_v_thre)
        '''总布局设置'''
        self.lot_v_all.addWidget(self.gpbx_map)
        self.lot_v_all.addWidget(self.gpbx_thre)
        self.setLayout(self.lot_v_all)

    def initWindow(self, w, h):
        '''获取屏幕居中点信息'''
        center_point = QDesktopWidget().availableGeometry().center()
        self.center_point_x = center_point.x()
        self.center_point_y = center_point.y()
        '''窗口初始化'''
        self.setGeometry(0, 0, w, h)
        self.max_w = (self.center_point_x-10)*2  # 窗口允许的最大宽
        self.max_h = (self.center_point_y-20)*2  # 窗口允许的最大高
        self.setMaximumSize(self.max_w, self.max_h)  # 防止窗口尺寸过大
        self.moveToCenter(w, h)
        self.win_name = gui_name  # 窗口标题
        self.setWindowTitle(self.win_name)

    def moveToCenter(self, w, h):
        '''窗口过大则先进行调整'''
        if (w > self.max_w) or (h > self.max_h):
            self.adjustSize()
        '''窗口居中'''
        topleft_point_x = (int)(self.center_point_x-w/2)
        topleft_point_y = (int)(self.center_point_y-h/2)
        self.move(topleft_point_x, topleft_point_y)

    def initMap(self):
        self.i_pixmap_count = 0  # 对已加载的图计数
        self.b_need_center = True  # 标志位，标志窗口是否需要居中
        self.timer_map_refresh = QTimer(self)  # 设定地图刷新定时器
        self.timer_map_refresh.timeout.connect(self.showMap)
        self.timer_map_refresh.start(10)  # 设置刷新时间为100毫秒

    def showMap(self):
        try:
            self.pixmap_map = QPixmap('平面图_走廊_房间.png')
            if self.pixmap_map.isNull():
                self.showMapErrorHandle()
                return
            self.pixmap_map = self.pixmap_map.scaled(
                800, 500, Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
            self.lb_map.setPixmap(self.pixmap_map)
            '''实现居中一次'''
            if self.i_pixmap_count < 2:  # 第一帧加载空label，第二帧加载地图
                w = self.width()
                h = self.height()
                self.moveToCenter(w, h)
                self.i_pixmap_count += 1

        except Exception as e:
            self.showMapErrorHandle()

    def showMapErrorHandle(self):
        self.lb_map.setText(
            '<font color=red>\
            <b>⚠ WARNING ⚠</b><br /><br />\
            地图加载出错啦<br /><br />\
            ::＞﹏＜::</font>')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_map = MyWinMap()
    sys.exit(app.exec_())
