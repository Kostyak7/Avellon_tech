import os
import pathlib
import numpy as np
import pandas as pd
from time import gmtime, strftime
from graph_widget import MyDataFrame, OscilloscopeGraphWidget, MplWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, \
    QTableWidget, QTableWidgetItem, QLabel, QSlider
from PySide6.QtGui import QScreen, QIcon, QPixmap
from PySide6.QtCore import Qt, QUrl, QPoint, QSize, QRect
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWebEngineWidgets import QWebEngineView
from third_party import AbstractFunctor, basename_decorator, AbstractCheckBoxList
import config as cf


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        self.main_menu_widget = MainMenuWidget(self)
        self.setCentralWidget(self.main_menu_widget)


class MainMenuWidget(QWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__()
        self.main_window = main_window_
        self.main_window.setWindowTitle(cf.MAIN_WINDOW_TITLE)
        self.main_window.setMinimumSize(cf.MAIN_WINDOW_MINIMUM_SIZE)
        self.main_window.setWindowIcon(QIcon(cf.ICON_WINDOW_PATH))

        self.logo_label = QLabel(self)
        pixmap = QPixmap(cf.MAIN_MENU_LOGO_PATH)
        self.logo_label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        self.button_list = list()

        button = QPushButton("Построить осциллограммы")
        button.setShortcut("Ctrl+" + str(len(self.button_list) + 1))
        button.clicked.connect(self.plot_oscilloscope_action)
        self.button_list.append(button)

        button = QPushButton("Построить частотную характеристику")
        button.setShortcut("Ctrl+" + str(len(self.button_list) + 1))
        button.clicked.connect(self.quit_app_action)
        self.button_list.append(button)

        button = QPushButton("Построить розу ветров")
        button.setShortcut("Ctrl+" + str(len(self.button_list) + 1))
        button.clicked.connect(self.plot_wind_rose_action)
        self.button_list.append(button)

        button = QPushButton("Выход")
        button.setShortcut("Shift+Esc")
        button.clicked.connect(self.quit_app_action)
        self.button_list.append(button)

        self.all_widgets_to_layout()

    def all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        core_layout.addStretch()

        logo_layout = QVBoxLayout()
        logo_layout.addWidget(self.logo_label, Qt.AlignCenter)

        button_layout = QVBoxLayout()
        for button in self.button_list:
            button.setMaximumSize(
                QSize(int(self.main_window.size().width() / 4), int(self.main_window.size().height() / 10)))
            button.setMinimumSize(
                QSize(int(self.main_window.size().width() / 4), int(self.main_window.size().height() / 10)))
            button_layout.addWidget(button, Qt.AlignCenter)

        button_wrapper_layout = QHBoxLayout()
        button_wrapper_layout.addStretch()
        button_wrapper_layout.addLayout(button_layout)
        button_wrapper_layout.addStretch()

        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(logo_layout)
        center_layout.addLayout(button_wrapper_layout)
        center_layout.addStretch()

        core_layout.addLayout(center_layout)
        core_layout.addStretch()
        self.setLayout(core_layout)

    def quit_app_action(self) -> None:
        self.main_window.app.exit()

    def plot_oscilloscope_action(self) -> None:
        self.main_window.setCentralWidget(OscilloscopeGraphWindowWidget(self.main_window))

    def plot_wind_rose_action(self) -> None:
        self.main_window.setCentralWidget(WindRoseGraphWindowWidget(self.main_window))


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
            QMessageBox.warning(self_widget_, "Wrong type",
                                f"Выбранный файл: - {filenames[i]} - имеет неправильный формат!", QMessageBox.Ok)
    return filenames


def get_num_file_by_default(base_name_: str) -> list:
    measurement_num = 0
    if base_name_[-5].isalpha():
        measurement_num = ord(base_name_[-5].lower()) - ord('a') + 10
    elif base_name_[-5].isdigit():
        measurement_num = int(base_name_[-5])
    else:
        return [-1, -1]
    sensor_num = 0
    if base_name_[-11].isalpha() and ord(base_name_[-11].lower()) - ord('a') < cf.SENSOR_AMOUNT:
        sensor_num = ord(base_name_[-11].lower()) - ord('a')
    else:
        return [-1, -1]
    return [measurement_num, sensor_num]


class AbstractGraphWindowWidget(QWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__()
        self.main_window = main_window_

        menu_bar = self.main_window.menuBar()
        file_menu = menu_bar.addMenu("Файл")

        self.plot_action = menu_bar.addAction("&Построить", "Ctrl+p")
        self.plot_action.setEnabled(False)
        self.plot_action.triggered.connect(self.plot_graph_action)

        help_action = menu_bar.addAction("&Справка", "Ctrl+i")
        help_action.triggered.connect(self.help_window_action)

        back_menu_action = menu_bar.addAction("&Назад", "Shift+Esc")
        back_menu_action.triggered.connect(self.back_main_menu_action)

        self.select_action = file_menu.addAction("&Выбрать Файл", "Ctrl+o")
        self.select_action.triggered.connect(self.select_csv_files_action)

        old_version_action = file_menu.addAction("&Старая Версия", "Ctrl+p+1")
        old_version_action.triggered.connect(self.open_old_version_action)

        self.download_action = file_menu.addAction("&Сохранить", "Ctrl+s")
        self.download_action.setEnabled(False)
        self.download_action.triggered.connect(self.save_data_by_default_action)

        self.download_as_action = file_menu.addAction("&Сохранить как", "Ctrl+Shift+s")
        self.download_as_action.setEnabled(False)
        self.download_as_action.triggered.connect(self.save_data_by_select_action)

        self.data_frames = []
        self.filename_list = []
        self.widget_list = []
        self.graph_widget = None
        self.webV = QWebEngineView()

    def all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        plot_layout = QVBoxLayout()
        for i in range(len(self.widget_list)):
            plot_layout.addWidget(self.widget_list[i])
        core_layout.addLayout(plot_layout)
        self.setLayout(core_layout)
        self.layout().update()

    def select_csv_files_action(self) -> None:
        self.filename_list = select_files(self, cf.FILE_DIALOG_CSV_FILTER)
        if len(self.filename_list):
            self.plot_action.setEnabled(True)

    def back_main_menu_action(self) -> None:
        self.main_window.menuBar().clear()
        self.main_window.setCentralWidget(MainMenuWidget(self.main_window))

    def save_data_by_default_action(self) -> None:
        filename = strftime(cf.DEFAULT_FORMAT_OF_FILENAME, gmtime()) + '.' + cf.TYPES_OF_SAVING_FILE[0]
        if not os.path.exists(cf.DEFAULT_FOLDER_NAME_TO_SAVE):
            os.mkdir(cf.DEFAULT_FOLDER_NAME_TO_SAVE)
        self.save_data_for_path(cf.DEFAULT_FOLDER_NAME_TO_SAVE + '/' + filename, cf.TYPES_OF_SAVING_FILE[0])

    def save_data_by_select_action(self) -> None:
        filename = QFileDialog.getSaveFileName(self, dir=str(pathlib.Path().resolve() / cf.DEFAULT_FOLDER_NAME_TO_SAVE),
                                               filter=cf.FILE_DIALOG_SAVE_FILTERS[2])
        self.save_data_for_path(filename[0], filename[0].split('.')[-1].lower())

    def plot_graph_action(self) -> None: ...
    def replot_for_new_data(self) -> None: ...
    def help_window_action(self) -> None: ...
    def save_data_for_path(self, path_: str, type_: str) -> None: ...
    def read_csv_into_data_frame(self) -> None: ...

    def open_old_version_action(self) -> None:
        self.webV.load(QUrl.fromLocalFile(
            pathlib.Path().resolve() / 'resource/oscilloscope_data.html'))
        self.select_action.setEnabled(False)
        self.plot_action.setEnabled(False)
        self.download_action.setEnabled(False)
        self.download_as_action.setEnabled(False)
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.webV)
        self.setLayout(core_layout)


class OscilloscopeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.table_widget = QTableWidget(self)
        self.checkbox_list_widget = OscilloscopeGraphCheckBoxesList(list(), self)
        self.graph_widget = OscilloscopeGraphWidget(list())

    def help_window_action(self) -> None:
        QMessageBox.information(self, "Help info", "Какая-то справачная информация", QMessageBox.Ok)

    def save_data_for_path(self, path_: str, type_: str) -> None:
        if self.graph_widget is not None:
            QScreen.grabWindow(self.main_window.app.primaryScreen(), self.graph_widget.winId()).save(path_, type_)

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()
        for filename in self.filename_list:
            if os.path.exists(filename) and os.path.isfile(filename):
                self.data_frames.append(MyDataFrame(filename, self))
            else:
                QMessageBox.warning(self, cf.FILE_NOT_EXIST_WARNING_TITLE,
                                    f"{filename} - не существует или не является файлом!", QMessageBox.Ok)

    def set_table(self, data_frames: list) -> None:
        self.table_widget.clear()
        self.table_widget.setColumnCount(2)
        self.table_widget.setRowCount(len(data_frames))
        self.table_widget.setHorizontalHeaderLabels(["Файл", "Максимум, " + data_frames[0].header['Data Uint']])
        self.table_widget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.table_widget.horizontalHeaderItem(1).setTextAlignment(Qt.AlignLeft)
        self.table_widget.horizontalHeader() \
            .setStyleSheet("QHeaderView::section {background-color: rgb(128, 255, 192);}")
        for i in range(len(data_frames)):
            lTWI = QTableWidgetItem(os.path.basename(data_frames[i].filename))
            rTWI = QTableWidgetItem(str(data_frames[i].data['y'].max()))
            lTWI.setTextAlignment(Qt.AlignRight)
            rTWI.setTextAlignment(Qt.AlignRight)
            self.table_widget.setItem(i, 0, lTWI)
            self.table_widget.setItem(i, 1, rTWI)
        self.table_widget.setColumnWidth(0, int(self.main_window.size().width() / 3))
        self.table_widget.setColumnWidth(1, int(self.main_window.size().width() / 4))
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def all_widgets_to_layout(self) -> None:
        table_checkbox_layout = QHBoxLayout()
        table_checkbox_layout.addWidget(self.table_widget)
        table_checkbox_layout.addWidget(self.checkbox_list_widget)

        plot_layout = QHBoxLayout()
        plot_layout.addWidget(self.graph_widget)

        core_layout = QVBoxLayout()
        core_layout.addLayout(table_checkbox_layout)
        core_layout.addLayout(plot_layout)

        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if len(self.data_frames) < 1:
            return
        self.set_table(self.data_frames)

        self.graph_widget.recreate(self.data_frames)

        self.download_action.setEnabled(True)
        self.download_as_action.setEnabled(True)

        self.checkbox_list_widget.set_data(self.filename_list, self)

        self.all_widgets_to_layout()

    def replot_for_new_data(self) -> None:
        self.graph_widget.recreate(self.data_frames)
        self.all_widgets_to_layout()


class CheckBoxOscilloscopeGraphFunctor(AbstractFunctor):
    def __init__(self, filename_: str, graph_window_widget_: OscilloscopeGraphWindowWidget):
        self.filename = filename_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        for dataframe in self.graph_window_widget.data_frames:
            if dataframe.filename == self.filename:
                dataframe.active = state_ != 0
        self.graph_window_widget.replot_for_new_data()


class OscilloscopeGraphCheckBoxesList(AbstractCheckBoxList):
    def __init__(self, names_list_: list, graph_window_widget_: OscilloscopeGraphWindowWidget):
        super().__init__(CheckBoxOscilloscopeGraphFunctor, basename_decorator)
        self.set_data(names_list_, graph_window_widget_)


class WindRoseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.plot_widget = MplWidget()
        self.relative_data_frames = []
        self.is_relative = False
        self.theta = np.array([0, 90, 180, 270, 360]) / 180 * np.pi

        self.checkbox_list_widget = WindRoseCheckBoxesList(['Абсолютные значения'], self)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setMinimumWidth(int(self.main_window.size().width() / 4 * 3))
        self.slider.valueChanged.connect(self.replot_for_new_data)

        self.all_widgets_to_layout()
        self.plot_graph_action()

    def all_widgets_to_layout(self) -> None:
        slider_checkbox_layout = QHBoxLayout()
        slider_checkbox_layout.addWidget(self.slider)
        slider_checkbox_layout.addWidget(self.checkbox_list_widget)

        core_layout = QVBoxLayout()
        core_layout.addLayout(slider_checkbox_layout)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()
        self.relative_data_frames.clear()
        for filename in self.filename_list:
            if os.path.exists(filename) and os.path.isfile(filename):
                tmp_value = MyDataFrame(filename, self).data['y'].max()
                base_name = os.path.basename(filename)
                measurement_num, sensor_num = get_num_file_by_default(base_name)
                if measurement_num == -1 or sensor_num == -1:
                    QMessageBox.warning(self, cf.WRONG_FILENAME_WARNING_TITLE,
                                        f"{filename} - имеет не соответстующее требованиям название!", QMessageBox.Ok)
                    self.data_frames.clear()
                    return
                for i in range(max(0, 1 + measurement_num - len(self.data_frames))):
                    self.data_frames.append(np.array([None] * (cf.SENSOR_AMOUNT + 1)))
                self.data_frames[measurement_num][sensor_num] = tmp_value
                if sensor_num == 0:
                    self.data_frames[measurement_num][-1] = tmp_value
            else:
                QMessageBox.warning(self, cf.FILE_NOT_EXIST_WARNING_TITLE,
                                    f"{filename} - не существует или не является файлом!", QMessageBox.Ok)
                self.data_frames.clear()
                return
        self.compute_dataframes_list()

    def compute_dataframes_list(self) -> None:
        tmp_i = 0
        maxs = [-1] * cf.SENSOR_AMOUNT
        while tmp_i < len(self.data_frames):
            c = 0
            for i in range(cf.SENSOR_AMOUNT):
                if self.data_frames[tmp_i][i] is None:
                    self.data_frames[tmp_i][i] = 0
                    if i == 0:
                        self.data_frames[tmp_i][-1] = 0
                    c += 1
                elif self.data_frames[tmp_i][i] > maxs[i]:
                    maxs[i] = self.data_frames[tmp_i][i]
            if c == cf.SENSOR_AMOUNT:
                self.data_frames.pop(tmp_i)
            else:
                tmp_i += 1
        for tmp_i in range(len(self.data_frames)):
            self.relative_data_frames.append(np.array([0.] * (cf.SENSOR_AMOUNT + 1)))
            for i in range(cf.SENSOR_AMOUNT):
                self.relative_data_frames[tmp_i][i] = self.data_frames[tmp_i][i] / maxs[i]
                if i == 0:
                    self.relative_data_frames[tmp_i][-1] = self.data_frames[tmp_i][i] / maxs[i]

    def replot_for_new_data(self) -> None:
        self.plot_widget.canvas.ax.clear()
        self.plot_widget.canvas.axes_init()
        self.slider.setRange(1, len(self.data_frames))
        if len(self.data_frames) == 0:
            return
        print("RelDATA", len(self.relative_data_frames), self.relative_data_frames)
        print("DATA", len(self.data_frames), self.data_frames)
        if self.is_relative:
            self.plot_widget.canvas.ax.plot(self.theta, self.relative_data_frames[self.slider.value() - 1])
        else:
            self.plot_widget.canvas.ax.plot(self.theta, self.data_frames[self.slider.value() - 1])
        self.plot_widget.canvas.draw()

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        self.slider.setValue(1)


class CheckBoxWindRoseFunctor(AbstractFunctor):
    def __init__(self, name_: str, graph_window_widget_: WindRoseGraphWindowWidget):
        self.name = name_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        self.graph_window_widget.is_relative = state_ == 0
        self.graph_window_widget.replot_for_new_data()


class WindRoseCheckBoxesList(AbstractCheckBoxList):
    def __init__(self, names_list_: list, graph_window_widget_: WindRoseGraphWindowWidget):
        super().__init__(CheckBoxWindRoseFunctor)
        self.set_data(names_list_, graph_window_widget_)
