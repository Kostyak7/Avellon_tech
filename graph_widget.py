import os
import pandas as pd
from PySide6.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QSizePolicy
from pyqtgraph import PlotWidget, mkPen
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from third_party import MyWarning
import config as cf


class MyDataFrame:
    def __init__(self, filename_: str, widget_owner_: QWidget):
        self.filename = filename_
        self.active = True
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
            self.active = False
            self.data = self.header = None
            return
        self.data_init()

    def is_correct_read(self) -> bool:
        return self.data is not None and self.header is not None

    def header_init(self) -> dict:
        res = dict()
        for i in range(cf.CSV_FILE_HEADER_SIZE):
            dot_index = self.data.iloc[i][0].find(':')
            if dot_index == -1 or\
                    self.data.iloc[i][0][:dot_index] not in cf.CSV_FILE_HEADER_CONTENT:
                raise MyWarning(cf.INCORRECT_FILE_CONTENT_WARNING_TITLE,
                                f"Выбранный файл: - {self.filename} - имеет неправильное наполнение в хедере!")
            header_name = self.data.iloc[i][0][:dot_index]
            res[header_name] = cf.CSV_FILE_HEADER_CONTENT[header_name]\
                .get(self.data.iloc[i][0][dot_index + 1:])
        return res

    def data_init(self) -> None:
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


class AbstractGraphWidget(PlotWidget):
    def __init__(self, data_frame_list_: list):
        super().__init__()
        self.data_frame_list = data_frame_list_
        self.init_base()
        self.lines = []
        self.legend = self.addLegend()

    def init_base(self):
        self.setBackground('w')
        self.showGrid(x=True, y=True)

    def init_graph(self) -> None: ...
    def recreate(self, data_frame_list_: list) -> None: ...


class OscilloscopeGraphWidget(AbstractGraphWidget):
    def __init__(self, data_frame_list_: list):
        super().__init__(data_frame_list_)
        self.init_graph()
        self.setTitle("Данные осциллографа")
        self.setLabel('left', 'Напряжение (мВ)')
        self.setLabel('bottom', 'Время (с)')

    def init_graph(self) -> None:
        self.legend.clear()
        if len(self.data_frame_list) < 1:
            return
        c = 0
        for i in range(len(self.data_frame_list)):
            if c >= len(self.lines):
                self.lines.append(self.plot(self.data_frame_list[i].data["x"], self.data_frame_list[i].data["y"],
                                            pen=mkPen(cf.COLOR_NAMES[i])))
            else:
                if self.data_frame_list[i].active:
                    self.lines[c].setData(self.data_frame_list[i].data["x"], self.data_frame_list[i].data["y"])
            self.legend.addItem(self.lines[c], os.path.basename(self.data_frame_list[i].filename))
            c += 1

    def recreate(self, data_frame_list_: list) -> None:
        for line in self.lines:
            line.clear()
        self.data_frame_list = data_frame_list_
        self.init_base()
        self.init_graph()


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
        QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
