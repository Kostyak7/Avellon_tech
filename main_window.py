import os
import pathlib
import numpy as np
import pandas as pd
from time import gmtime, strftime
from graph_widget import XYDataFrame, OscilloscopeGraphWidget, AmplitudeTimeGraphWidget,\
    FrequencyResponseGraphWidget, MplWidget, Max1SectionDataFrame, Max1SensorDataFrame, \
    select_files, PipeRectangle, PipePainter, PipeCrack
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, QFormLayout,\
    QTableWidget, QTableWidgetItem, QLabel, QSlider, QDialog, QLineEdit, QComboBox
from PySide6.QtGui import QScreen, QIcon, QPixmap, QIntValidator, QDoubleValidator
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


class ChangerPipeCrack(PipeCrack, QWidget):
    def __init__(self, num_: int, list_owner_, side_: str = cf.UPPER_SIDE, depth_: int = 0, position_m_: float = 0):
        PipeCrack.__init__(self, side_, depth_, position_m_)
        QWidget.__init__(self)

        self.num = num_
        self.list_owner = list_owner_

        self.side_editor = QComboBox()
        self.depth_editor = QLineEdit()
        self.position_editor = QLineEdit()
        self.delete_button = QPushButton("X")

        self.__editors_init()
        self.__set_values_to_editors()
        self.setVisible(self.num != -1)

    def __eq__(self, other_) -> bool:
        return self.side == other_.side and self.depth == other_.depth and self.position_m == other_.position_m

    def __editors_init(self) -> None:
        core_layout = QHBoxLayout()

        flo = QFormLayout()
        self.side_editor.addItems(["Верхняя", "Нижняя"])
        self.side_editor.currentIndexChanged.connect(self.side_changed_action)
        flo.addRow("Сторона", self.side_editor)
        core_layout.addLayout(flo)

        flo = QFormLayout()
        self.depth_editor.setValidator(QIntValidator())
        self.depth_editor.setAlignment(Qt.AlignRight)
        self.depth_editor.textChanged.connect(self.depth_edit_action)
        flo.addRow("Глубина (мм)", self.depth_editor)
        core_layout.addLayout(flo)

        flo = QFormLayout()
        self.position_editor.setValidator(QDoubleValidator(0., 8., 2))
        self.position_editor.textChanged.connect(self.position_edit_action)
        self.position_editor.setAlignment(Qt.AlignRight)
        flo.addRow("Позиция (м)", self.position_editor)
        core_layout.addLayout(flo)

        self.delete_button.setMaximumWidth(25)
        self.delete_button.clicked.connect(self.delete_action)
        core_layout.addWidget(self.delete_button)

        self.setLayout(core_layout)

    def __set_values_to_editors(self) -> None:
        self.side_editor.setCurrentIndex(int(self.side == cf.BOTTOM_SIDE))
        self.depth_editor.setText(str(self.depth))
        self.position_editor.setText(str(self.position_m))

    def side_changed_action(self, index_: int) -> None:
        self.side = cf.UPPER_SIDE if index_ == 0 else cf.BOTTOM_SIDE

    def depth_edit_action(self, text_: str) -> None:
        self.depth = 0 if len(text_) < 1 else int(text_)

    def position_edit_action(self, text_: str) -> None:
        self.position_m = 0. if len(text_) < 1 else float(text_.replace(',', '.'))

    def delete_action(self) -> None:
        self.num = -1
        self.setVisible(False)

    def recreate(self, num_: int, list_owner_, side_: str = cf.UPPER_SIDE, depth_: int = 0, position_m_: float = 0) -> None:
        self.num = num_
        self.list_owner = list_owner_
        self.side = side_
        self.depth = depth_
        self.position_m = position_m_
        self.setVisible(self.num != -1)
        self.__set_values_to_editors()
        self.update()


class CrackListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.cracks = []

        core_layout = QVBoxLayout()
        for i in range(cf.MAX_CRACK_AMOUNT):
            self.cracks.append(ChangerPipeCrack(-1, self))
            core_layout.addWidget(self.cracks[i])

        self.setLayout(core_layout)

    def add_crack(self, side_: str = cf.UPPER_SIDE, depth_: int = 0, position_m_: float = 0) -> bool:
        for i in range(len(self.cracks)):
            if self.cracks[i].num == -1:
                self.cracks[i].recreate(i, self, side_, depth_, position_m_)
                return True
        return False

    def length(self) -> int:
        c = 0
        for i in range(len(self.cracks)):
            if self.cracks[i] != -1:
                c += 1
        return c


class CrackSettingsDialog(QDialog):
    def __init__(self, pipe_rect_: PipeRectangle):
        super().__init__()
        self.pipe_rect = pipe_rect_
        self.cracks = CrackListWidget()

        self.setWindowTitle("Settings")
        self.setWindowModality(Qt.ApplicationModal)

        self.add_button = QPushButton("+ Добавить")
        self.add_button.clicked.connect(self.add_crack_action)

        self.accept_button = QPushButton("Применить")
        self.accept_button.clicked.connect(self.accept_action)

        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.setShortcut("Shift+Esc")
        self.cancel_button.clicked.connect(self.cancel_action)

        for crack in self.pipe_rect.cracks:
            self.cracks.add_crack(crack.side, crack.depth, crack.position_m)

        self.all_widgets_to_layout()

    def all_widgets_to_layout(self) -> None:
        accept_cancel_layout = QHBoxLayout()
        accept_cancel_layout.addWidget(self.accept_button)
        accept_cancel_layout.addWidget(self.cancel_button)

        core_layout = QVBoxLayout()
        core_layout.addWidget(self.cracks)
        core_layout.addWidget(self.add_button)
        core_layout.addLayout(accept_cancel_layout)

        self.setLayout(core_layout)

    def add_crack_action(self):
        self.cracks.add_crack()
        self.update()

    def accept_action(self):
        self.pipe_rect.clear()
        for crack in self.cracks.cracks:
            if crack.num == -1:
                continue
            is_copy = False
            for added_crack in self.pipe_rect.cracks:
                if added_crack == crack:
                    is_copy = True
                    crack.delete_action()
                    break
            if not is_copy:
                self.pipe_rect.add_crack(crack.side, crack.depth, crack.position_m)
        self.close()

    def cancel_action(self):
        self.close()

    def run(self):
        self.exec()


class FrequencyResponseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__(main_window_)
        self.plot_widget = FrequencyResponseGraphWidget(list(), self)
        self.plot_widget.setGeometry(0, 0, self.main_window.size().width(), self.main_window.size().height() * 0.7)

        self.pipe_rect = PipeRectangle(cf.PIPE_RECTANGLE_POSITION)
        self.pipe_rect.sensor_names = ['1', '1', '3', '3']
        self.pipe_rect.add_crack(cf.UPPER_SIDE, 25, 0.3)
        self.pipe_rect.add_crack(cf.BOTTOM_SIDE, 25, 0.6)

        self.cracks_dialog = CrackSettingsDialog(self.pipe_rect)

        self.crack_button = QPushButton("Задать трещены", self)
        self.crack_button.setGeometry(50, 550, 200, 60)
        self.crack_button.clicked.connect(self.run_dialog)

    def run_dialog(self):
        self.cracks_dialog.run()
        self.update()

    def paintEvent(self, event_) -> None:
        pipe_painter = PipePainter(self, self.pipe_rect)
        pipe_painter.draw_sensor_names()
        pipe_painter.draw_all_cracks()

    def read_csv_into_data_frame(self) -> None:
        self.data_frames.clear()

    def plot_graph_action(self) -> None:
        self.read_csv_into_data_frame()
        if len(self.data_frames) < 1:
            return

        self.download_action.setEnabled(True)
        self.download_as_action.setEnabled(True)

        self.replot_for_new_data()

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)
        self.update()


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
