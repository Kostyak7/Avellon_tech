import os
import numpy as np
import pandas as pd
import pathlib
from PySide6.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QSizePolicy, QFileDialog
from PySide6.QtCore import QPoint, QSize, QRect, QLine
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt
from pyqtgraph import PlotWidget, mkPen
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from third_party import MyWarning, get_num_file_by_default
import config as cf


def select_files(self_widget_: QWidget, filter_str_: str) -> list:
    file_dialog = QFileDialog(self_widget_)
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    file_dialog.setNameFilter(filter_str_)
    file_dialog.setDirectory(str(pathlib.Path().resolve() / cf.DEFAULT_FOLDER_NAME_FOR_SELECT))
    if not file_dialog.exec():
        return list()
    filenames = file_dialog.selectedFiles()
    print(filenames)
    for i in range(len(filenames)):
        if filenames[i].split('.')[-1].lower() not in cf.ALLOWED_FILE_LOAD_FORMATS:
            QMessageBox.warning(self_widget_, cf.WRONG_TYPE_WARNING_TITLE,
                                f"Выбранный файл: - {filenames[i]} - имеет неправильный формат!", QMessageBox.Ok)
    return filenames


class AbstractDataFrame:
    def __init__(self, name_: str, widget_owner_: QWidget):
        self.name = name_
        self.active = True
        self.data = None
        self.header = None
        self.widget_owner = widget_owner_

    def is_correct_read(self) -> bool:
        return self.data is not None

    def clear(self):
        self.active = False
        self.data = self.header = None

    def data_init(self): ...


class XYDataFrame(AbstractDataFrame):
    def __init__(self, filename_: str, widget_owner_: QWidget):
        super().__init__(os.path.basename(filename_), widget_owner_)
        self.filename = filename_
        self.data = pd.read_csv(self.filename, header=None)
        is_exception = False

        try:
            self.header = self.header_init()
        except MyWarning as mw:
            QMessageBox.warning(widget_owner_, mw.exception_title, mw.message, QMessageBox.Ok)
            is_exception = True
        except:
            QMessageBox.warning(widget_owner_, cf.UNKNOWN_WARNING_TITLE, cf.UNKNOWN_WARNING_MESSAGE, QMessageBox.Ok)
            is_exception = True

        if is_exception:
            self.clear()
        self.data_init()

    def is_correct_read(self) -> bool:
        return self.data is not None and self.header is not None

    def header_init(self) -> dict:
        res = dict()
        for i in range(cf.CSV_FILE_HEADER_SIZE):
            dot_index = self.data.iloc[i][0].find(':')
            if dot_index == -1 or \
                    self.data.iloc[i][0][:dot_index] not in cf.CSV_FILE_HEADER_CONTENT:
                raise MyWarning(cf.INCORRECT_FILE_CONTENT_WARNING_TITLE,
                                f"Выбранный файл: - {self.filename} - имеет неправильное наполнение в хедере!")
            header_name = self.data.iloc[i][0][:dot_index]
            res[header_name] = cf.CSV_FILE_HEADER_CONTENT[header_name] \
                .get(self.data.iloc[i][0][dot_index + 1:])
        return res

    def data_init(self) -> None:
        if not self.is_correct_read():
            return
        step = self.header['Time Base'] * 16 / self.header['Data points']
        steps = [None] * 6
        for i in range(self.header['Data points']):
            steps.append((i - 1) * step)
        self.data["Steps"] = steps
        self.data = self.data.drop(index=[0, 1, 2, 3, 4, 5])
        self.data.loc[5] = ["y", "x"]
        self.data = self.data.sort_index()
        self.data.to_csv(cf.TMP_FOR_WORK_FILENAME, index=False, header=None)
        self.data = pd.read_csv(cf.TMP_FOR_WORK_FILENAME)
        os.remove(cf.TMP_FOR_WORK_FILENAME)


class Max1SectionDataFrame(AbstractDataFrame):
    def __init__(self, name_: str, filename_list_: list, widget_owner_: QWidget):
        super().__init__(name_, widget_owner_)
        self.data = []
        self.relative_data = []
        self.filename_list = filename_list_
        self.maxes_list = [-1] * cf.SENSOR_AMOUNT

        if not self.data_init():
            self.clear()
        print(self.data)
        print(self.relative_data)

    def clear(self):
        self.active = False
        self.data = self.relative_data = self.header = None

    def data_init(self) -> bool:
        for filename in self.filename_list:
            if os.path.exists(filename) and os.path.isfile(filename):
                tmp_value = XYDataFrame(filename, self.widget_owner).data['y'].max()
                base_name = os.path.basename(filename)
                measurement_num, sensor_num = get_num_file_by_default(base_name, cf.SENSOR_AMOUNT)
                if measurement_num == -1 or sensor_num == -1:
                    QMessageBox.warning(self.widget_owner, cf.WRONG_FILENAME_WARNING_TITLE,
                                        f"{filename} - имеет не соответстующее требованиям название!", QMessageBox.Ok)
                    return False
                if self.maxes_list[sensor_num] is None:
                    self.maxes_list[sensor_num] = tmp_value
                elif tmp_value > self.maxes_list[sensor_num]:
                    self.maxes_list[sensor_num] = tmp_value
                for i in range(max(0, 1 + measurement_num - len(self.data))):
                    self.data.append(np.array([None] * (cf.SENSOR_AMOUNT + 1)))
                self.data[measurement_num][sensor_num] = tmp_value
                if sensor_num == 0:
                    self.data[measurement_num][-1] = tmp_value
            else:
                QMessageBox.warning(self.widget_owner, cf.FILE_NOT_EXIST_WARNING_TITLE,
                                    f"{filename} - не существует или не является файлом!", QMessageBox.Ok)
                return False
        self.__compute_data()
        self.compute_relative_data()
        return True

    def __compute_data(self):
        tmp_i = 0
        while tmp_i < len(self.data):
            c = 0
            for i in range(cf.SENSOR_AMOUNT):
                if self.data[tmp_i][i] is None:
                    self.data[tmp_i][i] = 0
                    if i == 0:
                        self.data[tmp_i][-1] = 0
                    c += 1
            if c == cf.SENSOR_AMOUNT:
                self.data.pop(tmp_i)
            else:
                tmp_i += 1

    def compute_relative_data(self, maxes_list_: list = None) -> None:
        maxes_list = None
        if maxes_list_ is None:
            maxes_list = self.maxes_list
        else:
            maxes_list = maxes_list_
        print(self.name, "\nMAXES", maxes_list)
        for tmp_i in range(len(self.data)):
            self.relative_data.append(np.array([0.] * (cf.SENSOR_AMOUNT + 1)))
            for i in range(cf.SENSOR_AMOUNT):
                self.relative_data[tmp_i][i] = self.data[tmp_i][i] / maxes_list[i]
            self.relative_data[tmp_i][-1] = self.relative_data[tmp_i][0]


class Max1SensorDataFrame(AbstractDataFrame):
    def __init__(self, name_: str, filename_list_: list, widget_owner_: QWidget):
        super().__init__(name_, widget_owner_)
        self.data = {'x': [], 'y': []}
        self.relative_data = {'x': [], 'y': []}
        self.filename_list = filename_list_

        if not self.data_init():
            self.clear()
        print(self.data)
        print(self.relative_data)

    def clear(self):
        self.active = False
        self.data = self.relative_data = self.header = None

    def data_init(self) -> bool:
        self_number = None
        for filename in self.filename_list:
            if os.path.exists(filename) and os.path.isfile(filename):
                base_name = os.path.basename(filename)
                measurement_num, sensor_num = get_num_file_by_default(base_name, cf.SENSOR_AMOUNT)
                if self_number is None:
                    self_number = sensor_num
                elif self_number != sensor_num:
                    measurement_num, sensor_num = -1, -1
                if measurement_num == -1 or sensor_num == -1:
                    QMessageBox.warning(self.widget_owner, cf.WRONG_FILENAME_WARNING_TITLE,
                                        f"{filename} - имеет не соответстующее требованиям название!", QMessageBox.Ok)
                    return False
                self.data['x'].append(measurement_num)
                self.data['y'].append(XYDataFrame(filename, self.widget_owner).data['y'].max())
            else:
                QMessageBox.warning(self.widget_owner, cf.FILE_NOT_EXIST_WARNING_TITLE,
                                    f"{filename} - не существует или не является файлом!", QMessageBox.Ok)
                return False
        self.compute_relative_data()
        return True

    def compute_relative_data(self, max_value_: float = None) -> None:
        if len(self.data['y']) < 1 or len(self.data['x']) < 1:
            return
        max_value = None
        if max_value_ is None:
            max_value = float(max(self.data['y']))
        else:
            max_value = max_value_
        print(self.name, "\nMAX", max_value)
        self.relative_data['x'] = self.data['x']
        for i in range(len(self.data['y'])):
            self.relative_data['y'].append(self.data['y'][i] / max_value)


class AbstractQtGraphWidget(PlotWidget):
    def __init__(self, data_frame_list_: list, parent_: QWidget = None):
        super().__init__(parent_)
        self.data_frame_list = data_frame_list_
        self.init_base()
        self.lines = []
        self.legend = self.addLegend()

    def init_base(self):
        self.setBackground('w')
        self.showGrid(x=True, y=True)

    def recreate(self, data_frame_list_: list) -> None:
        for line in self.lines:
            line.clear()
        self.data_frame_list = data_frame_list_
        self.init_base()
        self.init_graph()

    def init_graph(self) -> None:
        self.legend.clear()
        if len(self.data_frame_list) < 1:
            return
        c = 0
        for i in range(len(self.data_frame_list)):
            if c >= len(self.lines):
                self.lines.append(self.plot(self.data_frame_list[i].data["x"], self.data_frame_list[i].data["y"],
                                            pen=mkPen(cf.COLOR_NAMES[i], width=2)))
            else:
                if self.data_frame_list[i].active:
                    self.lines[c].setData(self.data_frame_list[i].data["x"], self.data_frame_list[i].data["y"])
            self.legend.addItem(self.lines[c], self.data_frame_list[i].name)
            c += 1


class OscilloscopeGraphWidget(AbstractQtGraphWidget):
    def __init__(self, data_frame_list_: list, parent_: QWidget = None):
        super().__init__(data_frame_list_, parent_)
        self.init_graph()
        self.setTitle("Данные осциллографа")
        self.setLabel('left', 'Напряжение (мВ)')
        self.setLabel('bottom', 'Время (с)')


class AmplitudeTimeGraphWidget(AbstractQtGraphWidget):
    def __init__(self, data_frame_list_: list, parent_: QWidget = None):
        super().__init__(data_frame_list_, parent_)
        self.init_graph()
        self.setTitle("Зависимость амплитуды во времени")
        self.setLabel('left', 'Значение')
        self.setLabel('bottom', 'Шаг')


class FrequencyResponseGraphWidget(AbstractQtGraphWidget):
    def __init__(self, data_frame_list_: list, parent_: QWidget = None):
        super().__init__(data_frame_list_, parent_)
        self.init_graph()
        self.setTitle("Частотная характеристика")
        self.setLabel('left', 'U, В')
        self.setLabel('bottom', 'f, кГц')


class PipeCrack:
    def __init__(self, side_: str, depth_: int, position_m_: float):
        self.side = side_
        self.depth = depth_
        self.position_m = position_m_


class PainterPipeCrack(PipeCrack):
    def __init__(self, side_: str, depth_: int, position_m_: float):
        super().__init__(side_, depth_, position_m_)
        self.line = None
        self.depth_text_point = None
        self.position_text_point = None

    def compute_line(self, inner_pipe_d_: float, wall_width_: float, pipe_length_: float,
                     paint_pipe_size_: QSize, paint_pipe_position_: QPoint) -> QLine:
        side_addition = 0
        if self.side == cf.BOTTOM_SIDE:
            side_addition = inner_pipe_d_ + wall_width_
        absolute_x = int(paint_pipe_size_.width() * self.position_m / pipe_length_)
        self.line = QLine(QPoint(paint_pipe_position_.x() + absolute_x, paint_pipe_position_.y() + side_addition),
                          QPoint(paint_pipe_position_.x() + absolute_x,
                                 int(paint_pipe_position_.y() + wall_width_ + side_addition)))
        return self.line

    def compute_depth_text_point(self, inner_pipe_d_: float, wall_width_: float, pipe_length_: float,
                                 paint_pipe_size_: QSize, paint_pipe_position_: QPoint, font_size_: int) -> QPoint:
        side_addition = 0
        if self.side == cf.BOTTOM_SIDE:
            side_addition = inner_pipe_d_ + wall_width_
        absolute_x = int(paint_pipe_size_.width() * self.position_m / pipe_length_)
        self.depth_text_point = QPoint(int(paint_pipe_position_.x() + absolute_x + paint_pipe_size_.width() / 50),
                                       int(paint_pipe_position_.y() + side_addition
                                           + font_size_ * paint_pipe_size_.height() / 80))
        return self.depth_text_point

    def compute_position_text_point(self, inner_pipe_d_: float, wall_width_: float, pipe_length_: float,
                                    paint_pipe_size_: QSize, paint_pipe_position_: QPoint, font_size_: int,) -> QPoint:
        side_addition = 0
        if self.side == cf.BOTTOM_SIDE:
            side_addition = inner_pipe_d_ + wall_width_
        absolute_x = int(paint_pipe_size_.width() * self.position_m / pipe_length_)
        self.position_text_point = QPoint(int(paint_pipe_position_.x() + absolute_x - paint_pipe_size_.width() / 50),
                                          int(paint_pipe_position_.y() + side_addition
                                              - font_size_ * paint_pipe_size_.height() / 200))
        return self.position_text_point


class PipeRectangle:
    def __init__(self, position_: QPoint, pipe_length_: float = cf.DEFAULT_PIPE_LENGTH_IN_METERS,):
        self.length = pipe_length_
        self.position = position_
        self.sensor_names = []

        self.cracks = []

    def clear(self) -> None:
        self.cracks.clear()

    def add_crack(self, side_: str, depth_: int, position_m_: float) -> bool:
        if side_ != cf.BOTTOM_SIDE and side_ != cf.UPPER_SIDE:
            return False
        self.cracks.append(PainterPipeCrack(side_, depth_, position_m_))
        return True


class PipePainter(QPainter):
    def __init__(self, parent_: QWidget, pipe_rect_: PipeRectangle):
        super().__init__(parent_)
        self.pipe_rect = pipe_rect_

        self.draw_base()

    def draw_base(self):
        pen = QPen()
        pen.setColor(cf.COLOR_NAMES[-1])
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(cf.SOLID_PIPE_LINE_WIDTH)
        self.setPen(pen)
        self.drawRect(QRect(self.pipe_rect.position, cf.SOLID_PIPE_SIZE))

        pen.setColor(cf.COLOR_NAMES[-1])
        pen.setStyle(Qt.DashLine)
        pen.setWidth(cf.DASH_PIPE_LINE_WIDTH)
        self.setPen(pen)
        self.drawRect(QRect(QPoint(self.pipe_rect.position.x() + cf.RELATIVE_DASH_PIPE_POSITION.x(),
                                   self.pipe_rect.position.y() + cf.RELATIVE_DASH_PIPE_POSITION.y()), cf.DASH_PIPE_SIZE))

    def __draw_crack(self, crack_: PainterPipeCrack) -> None:
        pen = QPen(QColor(cf.COLOR_NAMES[-1]))
        pen.setWidth(cf.CRACK_LINE_FOR_PIPE_WIDTH)
        self.setPen(pen)

        self.drawLine(crack_.compute_line(cf.DASH_PIPE_SIZE.height(), cf.RELATIVE_DASH_PIPE_POSITION.y(),
                                          self.pipe_rect.length, cf.SOLID_PIPE_SIZE, self.pipe_rect.position))

        font = self.font()
        font.setPixelSize(cf.CRACK_PIPE_FONT_SIZE)
        self.setFont(font)

        self.drawText(crack_.compute_depth_text_point(cf.DASH_PIPE_SIZE.height(), cf.RELATIVE_DASH_PIPE_POSITION.y(),
                                                      self.pipe_rect.length, cf.SOLID_PIPE_SIZE,
                                                      self.pipe_rect.position, cf.CRACK_PIPE_FONT_SIZE),
                      str(crack_.depth) + ' ' + cf.PIPE_CRACK_DEPTH_UNIT)

        self.drawText(crack_.compute_position_text_point(cf.DASH_PIPE_SIZE.height(), cf.RELATIVE_DASH_PIPE_POSITION.y(),
                                                         self.pipe_rect.length, cf.SOLID_PIPE_SIZE,
                                                         self.pipe_rect.position, cf.CRACK_PIPE_FONT_SIZE),
                      str(crack_.position_m) + ' ' + cf.PIPE_CRACK_POSITION_UNIT)

    def draw_all_cracks(self) -> None:
        for crack in self.pipe_rect.cracks:
            self.__draw_crack(crack)

    def draw_sensor_names(self) -> None:
        for i in range(len(self.pipe_rect.sensor_names)):
            self.__draw_sensor_name(i, str(self.pipe_rect.sensor_names[i]))

    def __draw_sensor_name(self, number_: int, name_: str) -> None:
        font = self.font()
        font.setPixelSize(cf.SENSOR_PIPE_FONT_SIZE)
        self.setFont(font)
        x_addition, y_addition = 0, 0
        if number_ == 2 or number_ == 3:
            y_addition = cf.DASH_PIPE_SIZE.height() + cf.RELATIVE_DASH_PIPE_POSITION.y()
        if number_ == 0 or number_ == 2:
            x_addition = cf.SOLID_PIPE_SIZE.width() + cf.SOLID_PIPE_SIZE.width() / 25
        position = QPoint(self.pipe_rect.position.x() - cf.SOLID_PIPE_SIZE.width() / 30 + x_addition,
                          self.pipe_rect.position.y() + cf.SENSOR_PIPE_FONT_SIZE * cf.SOLID_PIPE_SIZE.height() / 100 + y_addition)
        self.drawText(position, name_)


# MATPLOTLIB GRAPH
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.sensor_name_list = ['A', '', 'B', '', 'C', '', 'D', '']
        self.axes_init()
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def axes_init(self) -> None:
        self.ax.set_title("Label", va='bottom')
        angle_and_name_list = self.sensor_name_list.copy()
        for i in range(len(angle_and_name_list)):
            angle_and_name_list[i] = str(45 * i) + '° ' + angle_and_name_list[i]
        self.ax.set_xticklabels(angle_and_name_list)


class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

        self.theta = np.array([0, 90, 180, 270, 360]) / 180 * np.pi

    def set_data(self, data_frames_: list, index_: int = 0, is_relative_: bool = False):
        if len(data_frames_) < 1:
            return
        for i in range(len(data_frames_)):
            if not data_frames_[i].is_correct_read() or\
                    len(data_frames_[i].data) <= index_ or len(data_frames_[i].relative_data) <= index_:
                continue
            if is_relative_:
                self.canvas.ax.plot(self.theta, data_frames_[i].relative_data[index_])
            else:
                self.canvas.ax.plot(self.theta, data_frames_[i].data[index_])
            self.canvas.draw()

    def clear(self):
        self.canvas.ax.clear()
        self.canvas.axes_init()
