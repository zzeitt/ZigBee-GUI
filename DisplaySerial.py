import sys
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import (Qt, QTimer, QPointF,
                          QIODevice, pyqtSlot)
from PyQt5.QtGui import (QPixmap, QPen, QBrush, QColor,
                         QPainterPath)
from PyQt5.QtWidgets import (QWidget, QSpinBox, QGroupBox,
                             QCheckBox, QLineEdit, QLabel,
                             QGraphicsScene, QGraphicsView,
                             QGraphicsTextItem,
                             QVBoxLayout, QGridLayout,
                             QApplication,
                             QDesktopWidget)


GUI_NAME = 'ZigBee GUI'
NODE_NUM = 8
STR_COM = 'COM3'
REFRESH_TIME_MS = 100


class MyWinMap(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.initWidget()  # 初始化组件
        self.initLayout()  # 初始化布局
        self.initWindow(800, 700)  # 初始化窗口
        self.initMap()  # 初始化地图
        self.initSerial(STR_COM)  # 初始化串口
        self.show()

    '''----------------------------------------------'''

    def initWidget(self):
        '''地图显示控件'''
        self.gscene_map = QGraphicsScene()
        self.gview_map = QGraphicsView(self.gscene_map)
        '''设定节点及阈值区'''
        self.chb_mark = QCheckBox('进入标记模式')
        self.chb_mark.toggle()
        self.sp_thre = QSpinBox()
        self.sp_thre.setRange(0, 10)  # 设置上界和下界
        '''数据显示区'''

    def initLayout(self):
        '''箱组声明'''
        self.gpbx_map = QGroupBox('地图', self)
        self.gpbx_mark_and_thre = QGroupBox('设定节点及阈值', self)
        self.gpbx_data = QGroupBox('数据', self)
        '''箱组布局类型'''
        self.lot_v_map = QVBoxLayout()
        self.lot_g_mark_and_thre = QGridLayout()
        self.lot_g_data = QGridLayout()
        self.lot_v_all = QVBoxLayout()
        '''箱组map布局设置'''
        self.lot_v_map.addWidget(self.gview_map, alignment=Qt.AlignHCenter)
        self.gpbx_map.setLayout(self.lot_v_map)
        '''箱组mark and thre布局设置'''
        #  _ __ __ _ _
        # |_|__|__|_|_|
        self.lot_g_mark_and_thre.addWidget(
            self.chb_mark, 0, 1, 1, 1, Qt.AlignCenter)
        self.lot_g_mark_and_thre.addWidget(
            self.sp_thre, 0, 3, 1, 1, Qt.AlignCenter)
        self.lot_g_mark_and_thre.setColumnStretch(0, 1)
        self.lot_g_mark_and_thre.setColumnStretch(1, 2)
        self.lot_g_mark_and_thre.setColumnStretch(2, 2)
        self.lot_g_mark_and_thre.setColumnStretch(3, 1)
        self.lot_g_mark_and_thre.setColumnStretch(4, 1)
        self.gpbx_mark_and_thre.setLayout(self.lot_g_mark_and_thre)
        '''箱组data布局设置'''
        for i in range(NODE_NUM):
            # 数据框
            le_temp = QLineEdit('*')
            le_temp.setReadOnly(True)
            le_temp.setAlignment(Qt.AlignHCenter)
            self.lot_g_data.addWidget(le_temp, 0, i)
        for i in range(NODE_NUM):
            # 节点号框
            lb_temp = QLabel('<div style="color:#d648ac;"><b>'+str(i+1)+'</b></div>')
            lb_temp.setAlignment(Qt.AlignCenter)
            self.lot_g_data.addWidget(lb_temp, 1, i)
        self.gpbx_data.setLayout(self.lot_g_data)
        '''总布局设置'''
        self.lot_v_all.addWidget(self.gpbx_map)
        self.lot_v_all.addWidget(self.gpbx_mark_and_thre)
        self.lot_v_all.addWidget(self.gpbx_data)
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
        self.win_name = GUI_NAME  # 窗口标题
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
        try:
            # 地图加载部分
            self.pixmap_map = QPixmap('平面图_走廊_房间.png')
            if self.pixmap_map.isNull():  # 空图处理
                self.initMapErrorHandle()
                return
            self.pixmap_map = self.pixmap_map.scaled(
                700, 600, Qt.KeepAspectRatio,
                Qt.SmoothTransformation)
            self.gscene_map.addPixmap(self.pixmap_map)
            # 固定边界以禁用滑动条
            self.f_pixmap_map_x = float(self.pixmap_map.rect().x())
            self.f_pixmap_map_y = float(self.pixmap_map.rect().y())
            self.f_pixmap_map_w = float(self.pixmap_map.rect().width())
            self.f_pixmap_map_h = float(self.pixmap_map.rect().height())
            self.gview_map.setSceneRect(self.f_pixmap_map_x,
                                        self.f_pixmap_map_y,
                                        self.f_pixmap_map_w,
                                        self.f_pixmap_map_h)
            # 地图加载成功的标志位
            self.b_map_loaded = True
            # 复选框信号连接
            self.chb_mark.stateChanged.connect(self.updateMap)
            # view视图鼠标响应
            self.gview_map.mousePressEvent = self.markMap
            w = self.width()
            h = self.height()
            self.moveToCenter(w, h)
            # 节点相关部分
            self.node_list = []  # 存储节点的坐标及邻域信息
        except Exception as e:
            print(e)
            self.initMapErrorHandle()

    def initMapErrorHandle(self):
        self.b_map_loaded = False
        self.text_warning = '<div style="font:20px;\
                            color:red;\
                            text-align:center;">\
                            <b>⚠ WARNING ⚠</b><br /><br />\
                            地图加载出错啦<br /><br />\
                            ::＞﹏＜::\
                            </div>'
        self.gtext_warning = QGraphicsTextItem()
        self.gtext_warning.setHtml(self.text_warning)
        self.gscene_map.addItem(self.gtext_warning)

    def markMap(self, event):
        if self.b_map_loaded:
            if self.chb_mark.isChecked():
                self.node_pos = self.gview_map.mapToScene(event.pos())
                # 左键创建标记
                if event.button() == Qt.LeftButton:
                    if len(self.node_list) < NODE_NUM:
                        _is_near_init = False  # 标记模式下，初始化无近邻rssi
                        _append_iter = [self.node_pos,
                                        _is_near_init]  # 用list存储复合信息
                        self.node_list.append(_append_iter)
                        # 绘图部分
                        self.drawNode(len(self.node_list),
                                      _append_iter[0], _append_iter[1])
                # 右键回退标记
                if event.button() == Qt.RightButton:
                    if len(self.node_list) > 0:
                        self.node_list.pop()
                        self.gscene_map.clear()  # 清空scene
                        self.gscene_map.addPixmap(self.pixmap_map)  # 重新加载地图
                        for i in range(len(self.node_list)):
                            self.drawNode(i+1, self.node_list[i][0],
                                          self.node_list[i][1])

    def updateMap(self):
        if self.b_map_loaded:
            if not self.chb_mark.isChecked():
                self.timer_map_refresh = QTimer(self)  # 设定地图刷新定时器
                self.timer_map_refresh.timeout.connect(self.redrawMap)
                self.timer_map_refresh.start(REFRESH_TIME_MS)  # 设置刷新时间为100毫秒

    def redrawMap(self):
        self.gscene_map.clear()  # 清空scene
        self.gscene_map.addPixmap(self.pixmap_map)  # 重新加载地图
        for i in range(len(self.node_list)):
            self.drawNode(i+1, self.node_list[i][0], self.node_list[i][1])

    '''----------------------------------------------'''

    def drawNode(self, index, node_pos, is_near):
        # 样式设置
        node_draw_r = 15
        node_draw_x = node_pos.x() - node_draw_r
        node_draw_y = node_pos.y() - node_draw_r
        # node_draw_pos = QPointF(node_draw_x, node_draw_y)
        node_draw_pen = QPen(
            QColor(204, 47, 105), 3, Qt.SolidLine)
        node_draw_brush = QBrush(
            QColor(255, 110, 151), Qt.SolidPattern)
        # 正式画圆
        self.gellipse_node = self.gscene_map.addEllipse(
            node_draw_x, node_draw_y, 2*node_draw_r, 2*node_draw_r,
            node_draw_pen, node_draw_brush)
        # 索引号
        self.text_index = '<div style=\"font:26px;color:black;font-weight:900;\">' + \
            str(index) + '</div>'
        self.gtext_index = QGraphicsTextItem()
        self.gtext_index.setHtml(self.text_index)
        self.gtext_index.setParentItem(self.gellipse_node)
        self.gtext_index.setPos(node_draw_x+4, node_draw_y-2)
        if is_near:  # 若附近rssi判断有效
            node_draw_r = 20
            node_draw_x = node_pos.x() - node_draw_r
            node_draw_y = node_pos.y() - node_draw_r
            node_draw_pen = QPen(
                QColor(245, 229, 143), 10, Qt.DashLine)
            self.gscene_map.addEllipse(
                node_draw_x, node_draw_y, 2*node_draw_r, 2*node_draw_r,
                node_draw_pen)

    '''----------------------------------------------'''

    def initSerial(self, str_com):
        self.data_zigbee_list = []
        # 初始化串口
        self.ser_data = QSerialPort(
            'COM3',
            baudRate=QSerialPort.Baud115200,
            readyRead=self.receive)
        self.ser_data.open(QIODevice.ReadWrite)
        if self.ser_data.isOpen():
            print('串口开启成功！')
        else:
            print('串口打开失败……')

    @pyqtSlot()
    def receive(self):
        _data = self.ser_data.readLine().data()  # 读取数据
        if _data != b'':
            self.data_zigbee_list = []  # 清空数据
            self.data = _data[0:16].decode("gbk")
            # 存储数据
            for i in range(len(self.data)//2):
                # 每两位存储，用tuple存储，只读
                data_iter = (self.data[2*i:2*i+1],
                             self.data[2*i+1:2*i+2])
                self.data_zigbee_list.append(data_iter)
            # print('data_zigbee_list：', self.data_zigbee_list)
            self.updateSerial()
        else:
            print('串口接收内容为空！')

    def updateSerial(self):
        if not self.chb_mark.isChecked():
            for i in range(NODE_NUM):
                if i < len(self.node_list):
                    value_update = self.data_zigbee_list[i][1]
                    # 更新节点列表
                    self.node_list[i][1] = (
                        True if value_update == '1' else False)
                else:
                    value_update = '*'
                self.lot_g_data.itemAt(i).widget().setText(value_update)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win_map = MyWinMap()
    sys.exit(app.exec_())
