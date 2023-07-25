import os
import pathlib
import numpy as np
import pandas as pd
from time import gmtime, strftime
from graph_widget import XYDataFrame, OscilloscopeGraphWidget, AmplitudeTimeGraphWidget,\
    FrequencyResponseGraphWidget, MplWidget, Max1SectionDataFrame, Max1SensorDataFrame, \
    select_files,PipeRectangle
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, \
    QTableWidget, QTableWidgetItem, QLabel, QSlider
from PySide6.QtGui import QScreen, QIcon, QPixmap
from PySide6.QtCore import Qt, QUrl, QPoint, QSize, QRect
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWebEngineWidgets import QWebEngineView
from third_party import AbstractFunctor, basename_decorator, AbstractCheckBoxList, \
    get_num_file_by_default
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
        self.create_in_button_list("Построить осциллограммы", self.plot_oscilloscope_action)
        self.create_in_button_list("Построить частотную характеристику", self.plot_frequency_resp_action, True)
        self.create_in_button_list("Построить зависимости амплитуды во времени", self.plot_amplitude_time_action, True)
        self.create_in_button_list("Построить розу ветров", self.plot_wind_rose_action)

        self.create_in_button_list("Выход", self.quit_app_action, shortcut_="Shift+Esc")

        self.all_widgets_to_layout()

    def create_in_button_list(self, text_: str, action_, is_word_wrap_: bool = False,
                              shortcut_: str = cf.SEQUENCE_NUMBER_SHORTCUT_MODE) -> None:
        button = QPushButton(text_)
        if is_word_wrap_:
            label = QLabel(text_, button)
            button.setText('')
            label.setWordWrap(True)
            layout = QHBoxLayout(button)
            layout.addWidget(label, 0, Qt.AlignCenter)
        if shortcut_ != cf.NO_SHORTCUT_MODE:
            if shortcut_ == cf.SEQUENCE_NUMBER_SHORTCUT_MODE:
                button.setShortcut("Ctrl+" + str(len(self.button_list) + 1))
            else:
                button.setShortcut(shortcut_)
        button.clicked.connect(action_)
        self.button_list.append(button)

    def all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        core_layout.addStretch()

        logo_layout = QVBoxLayout()
        logo_layout.addWidget(self.logo_label, Qt.AlignCenter)

        button_layout = QVBoxLayout()
        for button in self.button_list:
            button.setFixedSize(
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

    def plot_frequency_resp_action(self) -> None:
        self.main_window.setCentralWidget(FrequencyResponseGraphWindowWidget(self.main_window))
        pass

    def plot_amplitude_time_action(self) -> None:
        self.main_window.setCentralWidget(AmplitudeTimeGraphWindowWidget(self.main_window))

    def plot_wind_rose_action(self) -> None:
        self.main_window.setCentralWidget(WindRoseGraphWindowWidget(self.main_window))


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

        self.download_action = file_menu.addAction("&Сохранить", "Ctrl+s")
        self.download_action.setEnabled(False)
        self.download_action.triggered.connect(self.save_data_by_default_action)

        self.download_as_action = file_menu.addAction("&Сохранить как", "Ctrl+Shift+s")
        self.download_as_action.setEnabled(False)
        self.download_as_action.triggered.connect(self.save_data_by_select_action)

        self.data_frames = []
        self.filename_list = []
        self.widget_list = []
        self.plot_widget = None
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


class CheckBoxHideFunctor(AbstractFunctor):
    def __init__(self, name_: str, graph_window_widget_: AbstractGraphWindowWidget):
        self.name = name_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        for dataframe in self.graph_window_widget.data_frames:
            if dataframe.name == self.name:
                dataframe.active = state_ != 0
        self.graph_window_widget.replot_for_new_data()


class HideCheckBoxesList(AbstractCheckBoxList):
    def __init__(self, names_list_: list, graph_window_widget_: AbstractGraphWindowWidget):
        super().__init__(CheckBoxHideFunctor)
        self.set_data(names_list_, graph_window_widget_)


class OscilloscopeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.table_widget = QTableWidget(self)
        self.checkbox_list_widget = HideCheckBoxesList(list(), self)
        self.plot_widget = OscilloscopeGraphWidget(list())

    def help_window_action(self) -> None:
        QMessageBox.information(self, "Help info", "Какая-то справачная информация", QMessageBox.Ok)

    def save_data_for_path(self, path_: str, type_: str) -> None:
        if self.plot_widget is not None:
            QScreen.grabWindow(self.main_window.app.primaryScreen(), self.plot_widget.winId()).save(path_, type_)

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()
        for filename in self.filename_list:
            if os.path.exists(filename) and os.path.isfile(filename):
                self.data_frames.append(XYDataFrame(filename, self))
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
            lTWI = QTableWidgetItem(data_frames[i].name)
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
        plot_layout.addWidget(self.plot_widget)

        core_layout = QVBoxLayout()
        core_layout.addLayout(table_checkbox_layout)
        core_layout.addLayout(plot_layout)

        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if len(self.data_frames) < 1:
            return
        self.set_table(self.data_frames)

        self.plot_widget.recreate(self.data_frames)

        self.download_action.setEnabled(True)
        self.download_as_action.setEnabled(True)

        name_list = []
        for dataframe in self.data_frames:
            name_list.append(dataframe.name)
        self.checkbox_list_widget.set_data(name_list, self)

        self.all_widgets_to_layout()

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)
        self.all_widgets_to_layout()


class WindRoseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.plot_widget = MplWidget()
        self.is_relative = False

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
        section_dict = {1: self.filename_list}
        # determine sections list ...
        for section_num in section_dict.keys():
            self.data_frames.append(Max1SectionDataFrame("sensor=" + str(section_num),
                                                         section_dict[section_num], self))

    def replot_for_new_data(self) -> None:
        self.plot_widget.clear()
        if len(self.data_frames) < 1:
            return
        self.slider.setRange(1, len(self.data_frames[0].data))
        self.plot_widget.set_data(self.data_frames, self.slider.value() - 1, self.is_relative)

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if self.slider.value() != 1:
            self.slider.setValue(1)
        else:
            self.replot_for_new_data()


class CheckBoxAbsoluteValueWindRoseFunctor(AbstractFunctor):
    def __init__(self, name_: str, graph_window_widget_: WindRoseGraphWindowWidget):
        self.name = name_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        self.graph_window_widget.is_relative = state_ == 0
        self.graph_window_widget.replot_for_new_data()


class WindRoseCheckBoxesList(AbstractCheckBoxList):
    def __init__(self, names_list_: list, graph_window_widget_: WindRoseGraphWindowWidget):
        super().__init__(CheckBoxAbsoluteValueWindRoseFunctor)
        self.set_data(names_list_, graph_window_widget_)


class FrequencyResponseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.plot_widget = FrequencyResponseGraphWidget(list(), self)
        self.plot_widget.setGeometry(0, 0, self.main_window.size().width(), self.main_window.size().height() * 0.7)
        self.sensor_name_list = ['1', '1', '3', '3']

        self.all_widgets_to_layout()

    def paintEvent(self, event_) -> None:
        pipe_widget = PipeRectangle(cf.PIPE_RECTANGLE_POSITION, self.sensor_name_list, self)
        pipe_widget.add_crack_line(cf.UPPER_SIDE, 25, 0.3)
        pipe_widget.add_crack_line(cf.BOTTOM_SIDE, 25, 0.6)

    def all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        # core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)
        self.update()

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()
        self.data_frames.append([])

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if len(self.data_frames) < 1:
            return

        self.download_action.setEnabled(True)
        self.download_as_action.setEnabled(True)

        self.replot_for_new_data()

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)
        self.all_widgets_to_layout()


class CheckBoxHideFrequencyResponseGraphFunctor(AbstractFunctor):
    def __init__(self, name_: str, graph_window_widget_: FrequencyResponseGraphWindowWidget):
        self.name = name_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        for dataframe in self.graph_window_widget.data_frames:
            if dataframe.name == self.name:
                dataframe.active = state_ != 0
        self.graph_window_widget.replot_for_new_data()


class FrequencyResponseGraphCheckBoxesList(AbstractCheckBoxList):
    def __init__(self, names_list_: list, graph_window_widget_: FrequencyResponseGraphWindowWidget):
        super().__init__(CheckBoxHideFrequencyResponseGraphFunctor)
        self.set_data(names_list_, graph_window_widget_)


class AmplitudeTimeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.plot_widget = AmplitudeTimeGraphWidget(list())
        self.relative_data_frames = []
        self.checkbox_list_widget = HideCheckBoxesList(list(), self)

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()
        sensor_dict = dict()
        for filename in self.filename_list:
            measurement_num, sensor_num = get_num_file_by_default(filename, cf.SENSOR_AMOUNT)
            if sensor_num not in sensor_dict:
                sensor_dict[sensor_num] = []
            sensor_dict[sensor_num].append(filename)
        for sensor_num in sensor_dict.keys():
            self.data_frames.append(Max1SensorDataFrame("sensor=" + str(sensor_num),
                                                        sensor_dict[sensor_num], self))

    def all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.plot_widget)
        core_layout.addWidget(self.checkbox_list_widget)
        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if len(self.data_frames) < 1:
            return

        self.download_action.setEnabled(True)
        self.download_as_action.setEnabled(True)

        name_list = []
        for dataframe in self.data_frames:
            name_list.append(dataframe.name)
        self.checkbox_list_widget.set_data(name_list, self)

        self.replot_for_new_data()

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)
        self.all_widgets_to_layout()
