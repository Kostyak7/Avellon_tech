import os
import pathlib
import shutil
from uuid import uuid4
from time import gmtime, strftime
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, QFormLayout,\
    QTableWidget, QTableWidgetItem, QLabel, QSlider, QDialog, QLineEdit, QComboBox, \
    QLayout, QMenuBar
from PySide6.QtGui import QScreen, QIcon, QPixmap, QIntValidator, QDoubleValidator, QPainter, QColor, QPen
from PySide6.QtCore import Qt,  QPoint, QSize, QRect, QLine
from PySide6.QtWidgets import QAbstractItemView
from graph_widget import XYDataFrame, OscilloscopeGraphWidget, AmplitudeTimeGraphWidget,\
    FrequencyResponseGraphWidget, MplWidget,  \
    MaxesDataFrame
from third_party import AbstractFunctor, \
    get_num_file_by_default, SimpleItemListWidget, select_path_to_files, \
    select_path_to_dir, select_path_to_one_file, ListWidget, AbstractWindowWidget, \
    MyCheckBox
import config as cf


# DONE 0) get XYDataFrame in Borehole
# DONE 1) Amplitude time graph
# DONE 2) Оптимизация датафреймов ???
# DONE 3) Роза с несколькими секциями
# DONE 4) Трубу в виджет
# DONE 5) Настройки трубы
# DONE 6) Checkbox in ListWidget
# DONE 7) get Step maxes dataframe
# TODO 8) Selector by steps for frequency graph
# TODO 9) Relative data
# TODO 10) Save data for path
# TODO 11) Два раза открываются настройки скважины


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        self.__window_init()
        # self.main_menu_widget = MainMenuWidget(self)
        self.main_menu_widget = BoreholeWindowWidget("test_1", self)
        self.setCentralWidget(self.main_menu_widget)

    def __window_init(self) -> None:
        self.setWindowTitle(cf.MAIN_WINDOW_TITLE)
        self.setMinimumSize(cf.MAIN_WINDOW_MINIMUM_SIZE)
        self.setWindowIcon(QIcon(cf.ICON_WINDOW_PATH))


class MainMenuWidget(QWidget):
    def __init__(self, main_window_: MainWindow):
        super().__init__()
        self.id = uuid4()
        self.main_window = main_window_

        self.create_project_dialog = CreateProjectDialog(self)

        self.logo_label = QLabel(self)
        pixmap = QPixmap(cf.MAIN_MENU_LOGO_PATH)
        self.logo_label.setPixmap(pixmap)

        self.button_list = SimpleItemListWidget(ButtonWidget, self)
        self.button_list.add_item("Создать проект", action=self.create_project_action)
        self.button_list.add_item("Открыть проект", action=self.open_project_action)
        self.button_list.add_item("Выход", action=self.quit_action, shortcut="Shift+Esc")

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        tmp_layout = QVBoxLayout()
        tmp_layout.addWidget(self.logo_label)
        tmp_layout.addWidget(self.button_list)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(tmp_layout)
        center_layout.addStretch()

        core_layout = QVBoxLayout()
        core_layout.addStretch()
        core_layout.addLayout(center_layout)
        core_layout.addStretch()
        self.setLayout(core_layout)

    def create_project_action(self) -> None:
        self.create_project_dialog.run()

    def open_project_action(self) -> None:
        pass

    def quit_action(self) -> None:
        self.main_window.app.exit()


class ButtonWidget(QPushButton):
    def __init__(self, name_: str, parent_: QWidget = None, *args, **kwargs):
        super().__init__(name_, parent_)
        self.name = name_
        self.id = uuid4()

        self.recreate(self.name, **kwargs)

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def __set_visible(self, is_show_: bool = True) -> None:
        self.setVisible(is_show_)

    def __word_wrap(self) -> None:
        label = QLabel(self.name, self)
        self.setText('')
        label.setWordWrap(True)
        layout = QHBoxLayout(self)
        layout.addWidget(label, 0, Qt.AlignCenter)

    def __set_shortcut(self, shortcut_: str = cf.NO_SHORTCUT_MODE) -> None:
        if shortcut_ != cf.NO_SHORTCUT_MODE:
            self.setShortcut(shortcut_)

    def recreate(self, name_: str, *args, **kwargs) -> None:
        self.name = name_
        self.setText(name_)
        self.clicked.connect(kwargs['action'])

        if 'is_word_wrap' in kwargs and kwargs['is_word_wrap']:
            self.__word_wrap()

        if 'shortcut' in kwargs:
            self.__set_shortcut(kwargs['shortcut'])

        self.__set_visible('is_show' in kwargs and kwargs['is_show'] or 'is_show' not in kwargs)


class CreateProjectDialog(QDialog):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.project_name = str(pathlib.Path().resolve() / "projects" / (cf.DEFAULT_PROJECT_NAME + '1'))
        self.setWindowTitle("Create project")
        self.setWindowModality(Qt.ApplicationModal)

        self.name_editor = QLineEdit(self)
        self.some_editor = QLineEdit(self)
        self.path_editor = PathEdit(self.project_name, cf.FILE_DIALOG_FOLDER_FILTER,
                                    self.path_edit_action, self)
        self.__editors_init()

        self.accept_button = QPushButton("Создать", self)
        self.accept_button.clicked.connect(self.accept_action)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setShortcut("Shift+Esc")
        self.cancel_button.clicked.connect(self.cancel_action)

        self.__all_widgets_to_layout()

    def __editors_init(self) -> None:
        self.name_editor.setAlignment(Qt.AlignLeft)
        self.name_editor.setText(os.path.basename(self.project_name))
        self.name_editor.textChanged.connect(self.project_name_action)

        self.some_editor.setAlignment(Qt.AlignLeft)
        self.name_editor.textChanged.connect(self.some_edit_action)

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("Название", self.name_editor)
        flo.addRow("???", self.some_editor)
        flo.addRow("Путь", self.path_editor)

        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.accept_button)
        tmp_layout.addWidget(self.cancel_button)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        core_layout.addLayout(tmp_layout)
        self.setLayout(core_layout)

    def project_name_action(self, text_: str) -> None:
        self.project_name = self.project_name[:-len(os.path.basename(self.project_name)) - 1] + '/' + text_
        self.name_editor.setText(os.path.basename(self.project_name))
        self.path_editor.set_text(self.project_name)

    def some_edit_action(self, text_: str) -> None:
        pass

    def path_edit_action(self, text_: str) -> None:
        self.project_name = self.path_editor.path = text_
        self.name_editor.setText(os.path.basename(self.project_name))

    def accept_action(self) -> None:
        path = self.project_name
        is_exist = os.path.exists(path)
        if is_exist:
            if not os.path.isdir(path):
                QMessageBox.warning(self, cf.NOT_EMPTY_FOLDER_WARNING_TITLE,
                                    f"{path} - не является папкой!", QMessageBox.Ok)
                return
            if len([f for f in pathlib.Path(path).glob('*')]):
                QMessageBox.warning(self, cf.NOT_EMPTY_FOLDER_WARNING_TITLE,
                                    f"Выбранная папка: - {path} - содержит файлы!"
                                    f"\nВыберете пустую или не существующую папку", QMessageBox.Ok)
                return
        if not is_exist:
            os.mkdir(path)

        self.close()

    def cancel_action(self) -> None:
        self.close()

    def run(self) -> None:
        self.exec()


class PathEdit(QWidget):
    def __init__(self, text_: str, filter_: str, action_, parent_: QWidget = None):
        super(PathEdit, self).__init__(parent_)
        self.id = uuid4()
        self.path = text_
        self.filter = filter_

        self.path_editor = QLineEdit(self.path, self)
        self.path_editor.setAlignment(Qt.AlignLeft)
        self.path_editor.setText(self.path)
        self.path_editor.textChanged.connect(action_)

        self.select_path_button = QPushButton("...", self)
        self.select_path_button.setMaximumWidth(30)
        self.select_path_button.clicked.connect(self.select_path_action)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.path_editor)
        core_layout.addWidget(self.select_path_button)
        self.setLayout(core_layout)

    def select_path_action(self) -> None:
        if self.filter == cf.FILE_DIALOG_FOLDER_FILTER:
            self.path = select_path_to_dir(self.parent(), dir=self.path)
        else:
            self.path = select_path_to_one_file(self.filter, self.parent())
        self.path_editor.setText(self.path)

    def set_text(self, text_: str) -> None:
        self.path = text_
        self.path_editor.setText(self.path)


class DataFile:
    def __init__(self, name_: str, step_path_: str, id_: str = None):
        self.name = name_
        self.step_path = step_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.measurement_num, self.sensor_num = get_num_file_by_default(os.path.basename(self.name),
                                                                        cf.DEFAULT_SENSOR_AMOUNT)
        self.max_value = None
        self.is_select = False

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.step_path + '/' + self.name

    def change_path(self, new_step_path_: str) -> None:
        self.step_path = new_step_path_

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            if self.get_xy_dataframe() is None:
                return float('-inf')
        return self.max_value

    def get_xy_dataframe(self) -> XYDataFrame:
        self.measurement_num, self.sensor_num = get_num_file_by_default(os.path.basename(self.name),
                                                                        cf.DEFAULT_SENSOR_AMOUNT)
        if self.measurement_num == -1 or self.sensor_num == -1:
            QMessageBox.warning(QWidget(), cf.WRONG_FILENAME_WARNING_TITLE,
                                f"{self.name} - имеет не соответстующее требованиям название!", QMessageBox.Ok)
            self.max_value = None
            return None
        xy_dataframe = XYDataFrame(self.path())
        self.max_value = xy_dataframe.max_y
        return xy_dataframe

    def exist(self, step_path_: str = None) -> bool:
        if step_path_ is not None:
            self.change_path(step_path_)
        path = self.path()
        return os.path.isfile(path)


class Step:
    def __init__(self, number_: int, section_path_: str, id_: str = None):
        self.number = number_
        self.section_path = section_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.max_value = None
        self.data_list = []
        self.is_select = False

        if len([f for f in pathlib.Path(self.path()).glob('*')]):
            self.correlate_data()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.section_path + '/' + str(self.number)

    def change_path(self, new_section_path_: str) -> None:
        self.section_path = new_section_path_
        path = self.path()
        for data_file in self.data_list:
            data_file.change_path(path)

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_
        for data_file in self.data_list:
            data_file.select(is_select_)

    def add_file(self, file_name_: str, id_: str = None) -> None:
        if id_ is not None:
            for data_file in self.data_list:
                if data_file.id == id_:
                    return
        if os.path.exists(self.path() + '/' + file_name_):
            self.data_list.append(DataFile(file_name_, self.path(), id_))

    def __remove_file_by_index(self, i_: int) -> None:
        if self.data_list[i_].exist():
            os.remove(self.data_list[i_].path())
        self.data_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.data_list) - 1
        while i >= 0:
            self.__remove_file_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_file(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.data_list)):
                if self.data_list[i].id == id_:
                    self.__remove_file_by_index(i)
                    return
        elif 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.data_list)):
                if self.data_list[i].name == name_:
                    self.__remove_file_by_index(i)
                    return

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            self.max_value = float('-inf')
            for data_file in self.data_list:
                data_file_max = data_file.max(is_reload_)
                if self.max_value < data_file_max:
                    self.max_value = data_file_max
        return self.max_value

    def get_xy_dataframes_list(self) -> list:
        xy_dataframes_list = list()
        for data_file in self.data_list:
            xy_dataframe = data_file.get_xy_dataframe()
            if xy_dataframe is not None and xy_dataframe.is_correct_read() and data_file.is_select:
                xy_dataframes_list.append(xy_dataframe)
        return xy_dataframes_list

    def get_sensor_maxes_dict(self) -> dict:
        sensor_dict = dict()
        for data_file in self.data_list:
            if data_file.sensor_num == -1 and data_file.get_xy_dataframe() is None:
                self.remove_file(id=data_file.id)
            if data_file.sensor_num not in sensor_dict:
                sensor_dict[data_file.sensor_num] = [None] * cf.DEFAULT_MEASUREMENT_NUMBER
            sensor_dict[data_file.sensor_num][data_file.measurement_num] = data_file.max()
        dataframes_list = []
        for sensor_num in sensor_dict.keys():
            i = 0
            while i < len(sensor_dict[sensor_num]):
                if sensor_dict[sensor_num][i] is None:
                    sensor_dict[sensor_num].pop(i)
                else:
                    i += 1
        return sensor_dict

    def get_sensor_dataframe_list(self) -> list:
        sensor_dict = self.get_sensor_maxes_dict()
        dataframes_list = []
        for sensor_num in sensor_dict.keys():
            if len(sensor_dict[sensor_num]):
                dataframes_list.append(MaxesDataFrame(str(sensor_num), sensor_dict[sensor_num]))
        return dataframes_list

    def get_maxes_dataframe(self) -> MaxesDataFrame:
        maxes = []
        for data_file in self.data_list:
            if data_file.is_select:
                if data_file.max() != float('-inf'):
                    maxes.append(data_file.max())
        return MaxesDataFrame('step=' + str(self.number), maxes)

    def exist(self, section_path_: str = None) -> bool:
        if section_path_ is not None:
            self.change_path(section_path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, section_path_: str = None) -> None:
        if not self.exist(section_path_):
            return
        path = pathlib.Path(self.path())
        files_dict = dict()

        for file_name in pathlib.Path(path).glob('*'):
            if file_name.is_file():
                files_dict[file_name] = False

        i = 0
        while i < len(self.data_list):
            self_file_path = pathlib.Path(self.data_list[i].path())
            if self_file_path not in files_dict:
                self.__remove_file_by_index(i)
                continue
            files_dict[self_file_path] = True
            i += 1

        for file_name in files_dict.keys():
            if not files_dict[file_name]:
                self.add_file(os.path.basename(file_name))


class Section:
    def __init__(self, name_: str, borehole_path_: str, depth_: int = 0, length_: float = 0., id_: str = None):
        self.name = name_
        self.depth = depth_
        self.length = length_
        self.borehole_path = borehole_path_

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.max_value = None
        self.step_list = []
        self.is_select = False

        if len([f for f in pathlib.Path(self.path()).glob('*')]):
            self.correlate_data()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.borehole_path + '/' + self.name

    def change_path(self, new_borehole_path_: str) -> None:
        self.borehole_path = new_borehole_path_
        path = self.path()
        for step in self.step_list:
            step.change_path(path)

    def select(self, is_select_: bool = True) -> None:
        self.is_select = is_select_
        for step in self.step_list:
            step.select(is_select_)

    def max(self, is_reload_: bool = False) -> float:
        if is_reload_ or self.max_value is None:
            self.max_value = float('-inf')
            for step in self.step_list:
                step_max = step.max(is_reload_)
                if self.max_value < step_max:
                    self.max_value = step_max
        return self.max_value

    def add_step(self, number_: int, id_: str = None):
        if id_ is not None:
            for step in self.step_list:
                if step.id == id_:
                    return
        path_to_new = self.path() + '/' + str(number_)
        if not os.path.isdir(path_to_new):
            os.mkdir(path_to_new)
        new_step = Step(number_, self.path(), id_)
        new_step.correlate_data()
        self.step_list.append(new_step)

    def __remove_step_by_index(self, i_: int) -> None:
        if self.step_list[i_].exist():
            shutil.rmtree(self.step_list[i_].path())
        self.step_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.step_list) - 1
        while i >= 0:
            self.__remove_step_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_step(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.step_list)):
                if self.step_list[i].id == id_:
                    self.__remove_step_by_index(i)
                    return
        elif 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.step_list)):
                if self.step_list[i].name == name_:
                    self.__remove_step_by_index(i)
                    return

    def exist(self, borehole_path_: str = None) -> bool:
        if borehole_path_ is not None:
            self.change_path(borehole_path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, borehole_path_: str = None) -> None:
        if not self.exist(borehole_path_):
            return
        path = pathlib.Path(self.path())
        step_dict = dict()

        for step_name in pathlib.Path(path).glob('*'):
            if step_name.is_dir() and os.path.basename(step_name).isdigit():
                step_dict[step_name] = False

        i = 0
        while i < len(self.step_list):
            self_step_path = pathlib.Path(self.step_list[i].path())
            if self_step_path not in step_dict:
                self.__remove_step_by_index(i)
                continue
            step_dict[self_step_path] = True
            self.step_list[i].correlate_data()
            i += 1

        for step_name in step_dict.keys():
            if not step_dict[step_name]:
                self.add_step(int(os.path.basename(step_name)))

    def get_xy_dataframes_list(self) -> list:
        xy_dataframes_list = []
        for step in self.step_list:
            xy_dataframes_list += step.get_xy_dataframes_list()
        return xy_dataframes_list

    def get_sensor_21_dataframe_list(self) -> list:
        dataframes_list = []
        for step in self.step_list:
            step_df_list = step.get_sensor_dataframe_list()
            for dataframe in step_df_list:
                if len(dataframe.data['y']) == 21:
                    dataframes_list.append(dataframe)
        return dataframes_list

    def get_sensor_dataframe_list(self) -> list:
        dataframes_list = []
        tmp_list = [None] * cf.DEFAULT_SENSOR_AMOUNT
        for step in self.step_list:
            step_df_dict = step.get_sensor_maxes_dict()
            for key in step_df_dict.keys():
                ikey = int(key)
                if tmp_list[ikey] is None:
                    tmp_list[ikey] = []
                tmp_list[ikey] += step_df_dict[key]
        for i in range(len(tmp_list)):
            dataframes_list.append(MaxesDataFrame(str(i), [] if tmp_list[i] is None else tmp_list[i]))
        return dataframes_list

    def get_maxes_dataframe_list(self) -> list:
        dataframes_list = list()
        for step in self.step_list:
            dataframes_list.append(step.get_maxes_dataframe())
        return dataframes_list

    def get_step_maxes_dataframe_list(self) -> list:
        dataframes_list = []
        maxes_steps_dict = dict()
        for step in self.step_list:
            step_df_list = step.get_sensor_dataframe_list()
            for dataframe in step_df_list:
                if dataframe.name not in maxes_steps_dict:
                    maxes_steps_dict[dataframe.name] = []
                maxes_steps_dict[dataframe.name].append([dataframe.max(), int(step.number)])
        for sensor_num in maxes_steps_dict.keys():
            maxes_steps_dict[sensor_num].sort(key=lambda ms_: ms_[1])
            maxes, tmp_dict = [], {'x': []}
            for ms_ in maxes_steps_dict[sensor_num]:
                maxes.append(ms_[0])
                tmp_dict['x'].append(ms_[1])
            maxes_dataframe = MaxesDataFrame(str(sensor_num), maxes)
            maxes_dataframe.tmp_value = tmp_dict
            dataframes_list.append(maxes_dataframe)
        return dataframes_list


class Borehole:
    def __init__(self, name_: str, path_: str, id_: str = None):
        self.name = name_
        self.up_path = path_
        if not os.path.isdir(self.path()):
            os.mkdir(self.path())

        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.section_list = []

        self.load_info_from_file()

    def __del__(self):
        self.save_info_to_file()

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def path(self) -> str:
        return self.up_path + '/' + self.name

    def change_path(self, new_path_: str) -> None:
        self.up_path = new_path_
        path = self.path()
        for section in self.section_list:
            section.change_path(path)

    def add_section(self, name_: str, depth_: int = 0, length_: float = 0., id_: str = None) -> None:
        if id_ is not None:
            for step in self.section_list:
                if step.id == id_:
                    return
        path_to_new = self.path() + '/' + name_
        if not os.path.isdir(path_to_new):
            os.mkdir(path_to_new)
        self.section_list.append(Section(name_, self.path(), depth_, length_, id_))

    def __remove_section_by_index(self, i_: int) -> None:
        if self.section_list[i_].exist():
            shutil.rmtree(self.section_list[i_].path())
        self.section_list.pop(i_)

    def remove_all(self, full_clean_: bool = False) -> None:
        i = len(self.section_list) - 1
        while i >= 0:
            self.__remove_section_by_index(i)
            i -= 1
        if full_clean_:
            shutil.rmtree(self.path())
            os.mkdir(self.path())

    def remove_section(self, **kwargs) -> None:
        if 'id' in kwargs:
            id_ = kwargs['id']
            for i in range(len(self.section_list)):
                if self.section_list[i].id == id_:
                    self.__remove_section_by_index(i)
                    return
        if 'name' in kwargs:
            name_ = kwargs['name']
            for i in range(len(self.section_list)):
                if self.section_list[i].name == name_:
                    self.__remove_section_by_index(i)
                    return

    def exist(self, path_: str = None) -> bool:
        if path_ is not None:
            self.change_path(path_)
        path = self.path()
        return os.path.isdir(path)

    def correlate_data(self, path_: str = None) -> None:
        if not self.exist(path_):
            return
        path = pathlib.Path(self.path())
        section_dict = dict()

        for section_name in pathlib.Path(path).glob('*'):
            if section_name.is_dir():
                section_dict[section_name] = False

        i = 0
        while i < len(self.section_list):
            self_section_path = pathlib.Path(self.section_list[i].path())
            if self_section_path not in section_dict:
                self.__remove_section_by_index(i)
                continue
            section_dict[self_section_path] = True
            self.section_list[i].correlate_data()
            i += 1

        for section_name in section_dict.keys():
            if not section_dict[section_name]:
                self.add_section(os.path.basename(section_name))

    def get_xy_dataframes_dict(self) -> dict:
        xy_dataframes_dict = dict()
        for section in self.section_list:
            xy_dataframes_dict[section.name] = section.get_xy_dataframes_list()
        return xy_dataframes_dict

    def get_sensor_21_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            section_df_list = section.get_sensor_21_dataframe_list()
            if len(section_df_list):
                dataframes_dict[section.name] = section_df_list
        return dataframes_dict

    def get_sensor_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            section_df_list = section.get_sensor_dataframe_list()
            if len(section_df_list):
                dataframes_dict[section.name] = section_df_list
        return dataframes_dict

    def get_maxes_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            dataframes_dict[section.name] = section.get_maxes_dataframe_list()
        return dataframes_dict

    def get_step_maxes_dataframe_dict(self) -> dict:
        dataframes_dict = dict()
        for section in self.section_list:
            dataframes_dict[section.name] = section.get_step_maxes_dataframe_list()
        return dataframes_dict

    def save_info_to_file(self, filename_: str = cf.BOREHOLE_INFO_SAVE_FILENAME) -> None:
        path_filename = self.path() + '/' + filename_
        if os.path.isfile(path_filename):
            os.remove(path_filename)
        file = open(path_filename, "w")
        file.write(f"BOREHOLE_NAME:{self.name}\n")

        file.write("#START SECTIONS\n")
        for section in self.section_list:
            file.write("#START SECTION\n")
            file.write(f"SECTION_NAME:{section.name}\n")
            file.write(f"SECTION_DEPTH:{section.depth}\n")
            file.write(f"SECTION_LENGTH:{section.length}\n")
            file.write("#END SECTION\n")
        file.write("#END SECTIONS\n")

    def load_info_from_file(self, filename_: str = cf.BOREHOLE_INFO_SAVE_FILENAME) -> None:
        path = self.path() + '/' + filename_
        if not os.path.isfile(path):
            return
        file = open(path, "r")

        is_start = True
        is_in_section = False
        tmp_name, tmp_depth, tmp_length = '', -1, -1.
        for line in file:
            if is_start:
                if line[:len("BOREHOLE_NAME")] != 'BOREHOLE_NAME':
                    return
                self.name = line[len("BOREHOLE_NAME") + 1:-1]
                is_start = False
            else:
                if is_in_section:
                    if line[:len("SECTION_NAME")] == 'SECTION_NAME':
                        tmp_name = line[len("SECTION_NAME") + 1:-1]
                    elif line[:len("SECTION_DEPTH")] == 'SECTION_DEPTH':
                        tmp_depth = int(float(line[len("SECTION_DEPTH") + 1:]))
                    elif line[:len("SECTION_LENGTH")] == 'SECTION_LENGTH':
                        tmp_length = float(line[len("SECTION_LENGTH") + 1:])
                    elif line == "#END SECTION\n":
                        self.add_section(tmp_name, tmp_depth, tmp_length)
                        is_in_section = False
                elif line == "#START SECTION\n":
                    is_in_section = True
                    tmp_name, tmp_depth, tmp_length = '', -1, -1.


class BoreholeWindowWidget(QWidget):
    def __init__(self, name_: str, main_window_: MainWindow):
        super().__init__()
        self.id = uuid4()
        self.name = name_
        self.main_window = main_window_

        self.borehole = Borehole(self.name, str(pathlib.Path().resolve() / cf.DEFAULT_PROJECT_FOLDER))
        self.borehole_dialog = BoreHoleDialog(self.borehole, self)

        self.borehole_menu_widget = BoreHoleMenuWidget(self.name, self)
        self.oscilloscope_window_widget = OscilloscopeGraphWindowWidget(self)
        self.frequency_window_widget = FrequencyResponseGraphWindowWidget(self)
        self.amplitude_window_widget = AmplitudeTimeGraphWindowWidget(self)
        self.windrose_window_widget = WindRoseGraphWindowWidget(self)

        menu_bar = QMenuBar(self.main_window)
        file_menu = menu_bar.addMenu("Скважина")

        self.plot_bar_action = menu_bar.addAction("&▷ Построить", "Ctrl+p")
        self.help_bar_action = menu_bar.addAction("&Справка", "Ctrl+i")
        self.back_menu_bar_action = menu_bar.addAction("&Назад", "Shift+Esc")
        self.sections_bar_action = file_menu.addAction("&Настроить секции", "Ctrl+a")
        self.download_bar_action = file_menu.addAction("&Сохранить", "Ctrl+s")
        self.download_as_bar_action = file_menu.addAction("&Сохранить как", "Ctrl+Shift+s")
        self.main_window.setMenuBar(menu_bar)

        self.__all_widgets_to_layout()
        self.borehole_menu_action()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.borehole_menu_widget)
        core_layout.addWidget(self.oscilloscope_window_widget)
        core_layout.addWidget(self.frequency_window_widget)
        core_layout.addWidget(self.amplitude_window_widget)
        core_layout.addWidget(self.windrose_window_widget)
        self.setLayout(core_layout)

    def __deactivate_all(self, is_active_: bool = False) -> None:
        self.main_window.menuBar().setVisible(is_active_)
        self.borehole_menu_widget.activate(is_active_)
        self.oscilloscope_window_widget.activate(is_active_)
        self.frequency_window_widget.activate(is_active_)
        self.amplitude_window_widget.activate(is_active_)
        self.windrose_window_widget.activate(is_active_)

    def borehole_menu_action(self) -> None:
        self.__deactivate_all()
        self.borehole_menu_widget.activate()

    def set_borehole_action(self) -> None:
        self.borehole_dialog.run()

    def plot_oscilloscope_action(self) -> None:
        self.__deactivate_all()
        self.oscilloscope_window_widget.activate()

    def plot_frequency_resp_action(self) -> None:
        pass
        self.__deactivate_all()
        self.frequency_window_widget.activate()

    def plot_amplitude_time_action(self) -> None:
        pass
        self.__deactivate_all()
        self.amplitude_window_widget.activate()

    def plot_depth_response_action(self) -> None:
        pass

    def plot_wind_rose_action(self) -> None:
        pass
        self.__deactivate_all()
        self.windrose_window_widget.activate()


class BoreHoleMenuWidget(AbstractWindowWidget):
    def __init__(self, name_: str, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.borehole_window = borehole_window_
        self.name = name_
        self.label = QLabel("Скважина: " + self.name, self)
        self.__label_init()

        self.button_list = SimpleItemListWidget(ButtonWidget, self)
        self.button_list.add_item("Настроить Скважину", action=self.borehole_window.set_borehole_action)
        self.button_list.add_item("Построить осциллограммы", action=self.borehole_window.plot_oscilloscope_action)
        self.button_list.add_item("Построить частотную характеристику",
                                  action=self.borehole_window.plot_frequency_resp_action)
        self.button_list.add_item("Построить зависимости амплитуды во времени",
                                  action=self.borehole_window.plot_amplitude_time_action)
        self.button_list.add_item("Построить глубинную характеристику",
                                  action=self.borehole_window.plot_depth_response_action)
        self.button_list.add_item("Построить розу ветров", action=self.borehole_window.plot_wind_rose_action)

        self.button_list.add_item("Назад", action=self.quit_action, shortcut="Shift+Esc")

        self.__all_widgets_to_layout()
        self.activate(False)

    def __label_init(self) -> None:
        font = self.label.font()
        font.setPointSize(cf.DEFAULT_BOREHOLE_NAME_FONT_SIZE)
        font.setBold(True)
        self.label.setFont(font)

    def __all_widgets_to_layout(self) -> None:
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(self.label)
        center_layout.addWidget(self.button_list)
        center_layout.addStretch()

        core_layout = QHBoxLayout()
        core_layout.addStretch()
        core_layout.addLayout(center_layout)
        core_layout.addStretch()
        self.setLayout(core_layout)

    def quit_action(self) -> None:
        self.borehole_window.main_window.app.exit()
        # TODO save the project
        self.borehole_window.borehole.save_info_to_file()


class BoreHoleDialog(QDialog):
    def __init__(self, borehole_: Borehole, parent_: QWidget = None):
        super().__init__(parent_)
        self.borehole = borehole_
        # TODO check minimum possible name

        self.setWindowTitle("Borehole settings")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(800, 500)

        self.section_list_widget = ListWidget(self)

        self.add_button = QPushButton("+ Добавить секцию", self)
        self.add_button.clicked.connect(self.add_section_action)

        self.accept_button = QPushButton("Принять", self)
        self.accept_button.clicked.connect(self.accept_action)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setShortcut("Shift+Esc")
        self.cancel_button.clicked.connect(self.cancel_action)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.accept_button)
        tmp_layout.addWidget(self.cancel_button)

        core_layout = QVBoxLayout()
        core_layout.addWidget(self.section_list_widget)
        core_layout.addWidget(self.add_button)
        core_layout.addLayout(tmp_layout)
        self.setLayout(core_layout)

    def add_section(self, name_: str, depth_: int = 0, length_: float = 0., id_: str = None) -> None:
        self.section_list_widget.add_widget(SectionWidget(name_, self.section_list_widget, depth_, length_, id_))

    def add_section_action(self) -> None:
        len_default_name = len('name_')
        max_section_number = -1
        for section in self.section_list_widget.widget_list:
            if section.name[:len_default_name] == 'name_' and section.name[len_default_name:].isdigit():
                max_section_number = max(int(section.name[len_default_name:]), max_section_number)
        self.add_section('name_' + str(max_section_number + 1))

    def save_all_sections(self, up_path_: str) -> None:
        borehole_path = self.borehole.path()
        for filename in pathlib.Path(borehole_path).glob('*'):
            is_inside_widget_list = False
            file_base_name = os.path.basename(filename)
            if os.path.isdir(filename):
                for section in self.section_list_widget.widget_list:
                    if section.name == file_base_name:
                        is_inside_widget_list = True
                        break
            if os.path.isfile(filename) and file_base_name == cf.BOREHOLE_INFO_SAVE_FILENAME:
                is_inside_widget_list = True
            if not is_inside_widget_list:
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
        for section in self.section_list_widget.widget_list:
            section.save_all(borehole_path)

    def accept_action(self) -> None:
        self.save_all_sections(self.borehole.up_path)
        print('______________________________')
        print("Widget")
        for section in self.section_list_widget.widget_list:
            print('sec\t', section.name)
            for step in section.step_list.widget_list:
                print('\tstep\t', step.number)
                for file in step.file_list.widget_list:
                    print('\t\tf\t', file.path)

        # time.sleep(10)

        self.borehole.correlate_data()
        print('______________________________')
        print("OUT:", self.borehole.path())
        for section in self.borehole.section_list:
            for section_w in self.section_list_widget.widget_list:
                if section.name == section_w.name:
                    section.select(section_w.is_selected())
                    for step in section.step_list:
                        for step_w in section_w.step_list.widget_list:
                            if step_w.number == step.number:
                                step.select(step_w.is_selected())
                                for file in step.data_list:
                                    for file_w in step_w.file_list.widget_list:
                                        if file.name == os.path.basename(file_w.path):
                                            file.select(file_w.is_selected())
                                            ifs = True
                                            break
                                break
                    break


            print('sec\t', section.path())
            for step in section.step_list:
                print('\tstep\t', step.path())
                for file in step.data_list:
                    print('\t\tf\t', file.path())
            for section_w in self.section_list_widget.widget_list:
                if section.name == section_w.name:
                    section.depth = section_w.depth
                    section.length = section_w.length
        print('______________________________')
        self.close()

    def cancel_action(self) -> None:
        self.close()

    def run(self) -> None:
        self.section_list_widget.remove_all()
        for section in self.borehole.section_list:
            self.add_section(section.name, section.depth, section.length, section.id)
            section_w = self.section_list_widget.widget_list[len(self.section_list_widget.widget_list) - 1]
            section_w.checkbox.setChecked(section.is_select)
            for step in section.step_list:
                section_w.add_step(step.number, step.id)
                step_w = section_w.step_list.widget_list[len(section_w.step_list.widget_list) - 1]
                step_w.checkbox.setChecked(step.is_select)
                for file in step.data_list:
                    step_w.add_file(file.name, file.id)
                    step_w.file_list.widget_list[len(step_w.file_list.widget_list) - 1]\
                        .checkbox.setChecked(file.is_select)
        print('______________________________')
        print("IN:", self.borehole.path())
        for section in self.borehole.section_list:
            print('sec\t', section.path())
            for step in section.step_list:
                print('\tstep\t', step.path())
                for file in step.data_list:
                    print('\t\tf\t', file.path())
        print('______________________________')

        self.exec()


class AbstractBoreholeDialogItemWidget(QWidget):
    def __init__(self, parent_list_: ListWidget, id_: str = None, is_show_: bool = True):
        super().__init__(parent_list_)
        self.parent_list = parent_list_
        self.id = id_
        if self.id is None:
            self.id = uuid4()

        self.checkbox = QCheckBox(self)
        self.checkbox.setChecked(True)

        self.delete_button = QPushButton("X", self)
        self.delete_button.setMaximumWidth(20)
        self.delete_button.clicked.connect(self.delete_action)

        self.setVisible(is_show_)

    def __all_widgets_to_layout(self) -> None: ...

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def delete_action(self) -> None:
        self.parent_list.remove_item(self)


class FileWidget(AbstractBoreholeDialogItemWidget):
    def __init__(self, path_: str, parent_list_: ListWidget, id_: str = None, is_show_: bool = False):
        super().__init__(parent_list_, id_, is_show_)
        self.path = path_
        self.basename = os.path.basename(self.path)
        self.checkbox.setText(self.basename)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.checkbox)
        core_layout.addWidget(self.delete_button)
        core_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(core_layout)

    def copy_to(self, step_dir_path_: str):
        if os.path.isfile(self.path):
            shutil.copy2(self.path, step_dir_path_)


class StepWidget(AbstractBoreholeDialogItemWidget):
    def __init__(self, number_: int, parent_list_: ListWidget, id_: str = None, is_show_: bool = False):
        super().__init__(parent_list_, id_, is_show_)
        self.number = number_
        self.file_list = ListWidget(self)
        self.setMaximumHeight(150)
        self.setMinimumWidth(400)

        self.checkbox.stateChanged.connect(self.click_checkbox_action)

        self.number_editor = QLineEdit(self)
        self.__editor_init()
        self.__values_to_editors()

        self.add_button = QPushButton('+', self)
        self.drop_button = QPushButton('▽', self)
        self.__button_init()
        self.is_dropped = True
        self.drop_list_action()

        self.__all_widgets_to_layout()

    def __editor_init(self) -> None:
        self.number_editor.setAlignment(Qt.AlignLeft)
        self.number_editor.setValidator(QIntValidator())
        self.number_editor.textChanged.connect(self.number_edit_action)

    def __values_to_editors(self) -> None:
        self.number_editor.setText(str(self.number))

    def __button_init(self) -> None:
        self.add_button.setMaximumWidth(20)
        self.add_button.clicked.connect(self.add_files_action)

        self.drop_button.setMaximumWidth(20)
        self.drop_button.clicked.connect(self.drop_list_action)

    def __all_widgets_to_layout(self) -> None:
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(self.checkbox)
        flo = QFormLayout()
        flo.addRow("Шаг №", self.number_editor)
        tmp_layout.addLayout(flo)
        tmp_layout.addWidget(self.add_button)
        tmp_layout.addWidget(self.drop_button)
        tmp_layout.addWidget(self.delete_button)

        core_layout = QVBoxLayout()
        core_layout.addLayout(tmp_layout)
        core_layout.addWidget(self.file_list)
        core_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(core_layout)

    def add_file(self, path_: str, id_: str = None, is_select: bool = True) -> None:
        for file in self.file_list.widget_list:
            if file.id == id_ or file.path == path_:
                return
        file_widget = FileWidget(path_, self.file_list, id_)
        self.file_list.add_widget(file_widget)
        file_widget.checkbox.setChecked(is_select)

    def remove_file(self, **kwargs):
        if 'id' in kwargs:
            id_ = kwargs['id']
            for file in self.file_list.widget_list:
                if file.id == id_:
                    file.delete_action()
        elif 'name' in kwargs:
            name_ = kwargs['name']
            for file in self.file_list.widget_list:
                if file.name == name_:
                    file.delete_action()

    def remove_all(self) -> None:
        for file in self.file_list.widget_list:
            file.delete_action()

    def add_files_action(self) -> None:
        got_file_list = select_path_to_files(cf.FILE_DIALOG_CSV_FILTER, self, dir="data")
        for filename in got_file_list:
            self.add_file(filename)

    def click_checkbox_action(self, state_: bool) -> None:
        for file in self.file_list.widget_list:
            file.checkbox.setChecked(state_)

    def number_edit_action(self, text_: str) -> None:
        for step in self.parent_list.widget_list:
            if len(text_) and int(text_) == step.number:
                self.number_editor.setText(str(self.number))
                return
        if len(text_):
            self.number = int(text_)

    def __drop_list(self, is_drop: bool) -> None:
        self.is_dropped = is_drop
        self.drop_button.setText("△" if self.is_dropped else "▽")
        self.file_list.setVisible(self.is_dropped)
        self.parent_list.resize_item(self)

    def drop_list_action(self) -> None:
        self.__drop_list(not self.is_dropped)

    def save_all(self, section_path_: str) -> None:
        step_path = section_path_ + '/' + str(self.number)
        if not os.path.isdir(step_path):
            os.mkdir(step_path)
        for filename in pathlib.Path(step_path).glob('*'):
            is_inside_widget_list = False
            file_base_name = os.path.basename(filename)
            for file in self.file_list.widget_list:
                if file.basename == file_base_name:
                    is_inside_widget_list = True
                    break
            if not is_inside_widget_list:
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
        for file in self.file_list.widget_list:
            file.copy_to(step_path)


class SectionWidget(AbstractBoreholeDialogItemWidget):
    def __init__(self, name_: str, parent_list_: ListWidget, depth_: int = 0, length_: float = 0.,
                 id_: str = None, is_show_: bool = False):
        super().__init__(parent_list_, id_, is_show_)
        self.name = name_
        self.depth = depth_
        self.length = length_
        self.step_list = ListWidget(self)

        self.checkbox.stateChanged.connect(self.click_checkbox_action)

        self.name_editor = QLineEdit(self)
        self.depth_editor = QLineEdit(self)
        self.length_editor = QLineEdit(self)
        self.__editor_init()
        self.__values_to_editors()

        self.add_button = QPushButton('+', self)
        self.drop_button = QPushButton('▽', self)
        self.__button_init()

        self.is_dropped = True
        self.drop_list_action()
        self.__all_widgets_to_layout()

    def __editor_init(self) -> None:
        self.name_editor.setAlignment(Qt.AlignRight)
        self.name_editor.textChanged.connect(self.name_edit_action)

        self.depth_editor.setAlignment(Qt.AlignRight)
        self.depth_editor.setValidator(QIntValidator())
        self.depth_editor.textChanged.connect(self.depth_edit_action)

        self.length_editor.setAlignment(Qt.AlignRight)
        self.length_editor.setValidator(QDoubleValidator(0., 20., 1))
        self.length_editor.textChanged.connect(self.length_edit_action)

    def __values_to_editors(self) -> None:
        self.name_editor.setText(self.name)
        self.depth_editor.setText(str(self.depth))
        self.length_editor.setText(str(self.length))

    def __button_init(self) -> None:
        self.add_button.setMaximumWidth(20)
        self.add_button.clicked.connect(self.add_step_action)

        self.drop_button.setMaximumWidth(20)
        self.drop_button.clicked.connect(self.drop_list_action)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.checkbox)
        base_layout = QHBoxLayout()
        flo = QFormLayout()
        flo.addRow("Имя", self.name_editor)
        base_layout.addLayout(flo)
        flo = QFormLayout()
        flo.addRow("Глубина (м)", self.depth_editor)
        base_layout.addLayout(flo)
        flo = QFormLayout()
        flo.addRow("Длина (м)", self.length_editor)
        base_layout.addLayout(flo)
        base_layout.addWidget(self.add_button)
        base_layout.addWidget(self.drop_button)
        base_layout.addWidget(self.delete_button)
        core_layout.addLayout(base_layout)
        core_layout.addWidget(self.step_list)
        self.setLayout(core_layout)

    def add_step(self, number_: int, id_: str = None, is_select: bool = True) -> None:
        for step in self.step_list.widget_list:
            if step.id == id_ or step.number == number_:
                return
        step_widget = StepWidget(number_, self.step_list, id_)
        self.step_list.add_widget(step_widget)
        step_widget.checkbox.setChecked(is_select)

    def remove_step(self, **kwargs):
        if 'id' in kwargs:
            id_ = kwargs['id']
            for step in self.step_list.widget_list:
                if step.id == id_:
                    step.delete_action()
        elif 'number' in kwargs:
            number_ = kwargs['number']
            for step in self.step_list.widget_list:
                if step.number == number_:
                    step.delete_action()

    def remove_all(self) -> None:
        for step in self.step_list.widget_list:
            step.delete_action()

    def add_step_action(self) -> None:
        max_number = -1
        for step in self.step_list.widget_list:
            if max_number < step.number:
                max_number = step.number
        self.add_step(max_number + 1)
        if not self.is_dropped:
            self.__drop_list(not self.is_dropped)

    def click_checkbox_action(self, state_) -> None:
        for step in self.step_list.widget_list:
            step.checkbox.setChecked(state_)

    def name_edit_action(self, text_: str) -> None:
        for section in self.parent_list.widget_list:
            if section.name == text_:
                self.name_editor.setText(self.name)
                return
        self.name = text_

    def depth_edit_action(self, text_: str) -> None:
        if len(text_):
            self.depth = int(float(text_))

    def length_edit_action(self, text_: str) -> None:
        if len(text_):
            self.length = float(text_.replace(',', '.'))

    def __drop_list(self, is_drop: bool) -> None:
        self.is_dropped = is_drop
        self.drop_button.setText("△" if self.is_dropped else "▽")
        self.step_list.setVisible(self.is_dropped)
        self.parent_list.resize_item(self)

    def drop_list_action(self) -> None:
        self.__drop_list(not self.is_dropped)

    def save_all(self, borehole_path_: str) -> None:
        section_path = borehole_path_ + '/' + self.name
        if not os.path.isdir(section_path):
            os.mkdir(section_path)
        for filename in pathlib.Path(section_path).glob('*'):
            is_inside_widget_list = False
            if os.path.isdir(filename) and str(os.path.basename(filename)).isdigit():
                file_num = int(os.path.basename(filename))
                for step in self.step_list.widget_list:
                    if step.number == file_num:
                        is_inside_widget_list = True
                        break
            if not is_inside_widget_list:
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
        for step in self.step_list.widget_list:
            step.save_all(section_path)


class AbstractGraphWindowWidget(AbstractWindowWidget):
    def __init__(self, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.borehole_window = borehole_window_
        self.plot_widget = None
        self.data_frames = dict()

        self.activate(False)

    def __all_widgets_to_layout(self) -> None: ...

    def __connect_bar_menu(self) -> None:
        self.borehole_window.plot_bar_action.triggered.connect(self.plot_graph_action)
        self.borehole_window.help_bar_action.triggered.connect(self.help_window_action)
        self.borehole_window.back_menu_bar_action.triggered.connect(self.back_borehole_menu_action)
        self.borehole_window.sections_bar_action.triggered.connect(self.set_sections_action)
        self.borehole_window.download_bar_action.setEnabled(False)
        self.borehole_window.download_bar_action.triggered.connect(self.save_data_by_default_action)
        self.borehole_window.download_as_bar_action.setEnabled(False)
        self.borehole_window.download_as_bar_action.triggered.connect(self.save_data_by_select_action)

    def activate(self, is_active_: bool = True) -> None:
        self.setVisible(is_active_)
        self.borehole_window.main_window.menuBar().setVisible(is_active_)
        if is_active_:
            self.__connect_bar_menu()

    def plot_graph_action(self) -> None: ...

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)

    def help_window_action(self) -> None:
        qmb = QMessageBox.information(self, "Help info", cf.HELP_INFO, QMessageBox.Ok)

    def back_borehole_menu_action(self) -> None:
        self.activate(False)
        self.borehole_window.borehole_menu_action()

    def set_sections_action(self) -> None:
        self.borehole_window.set_borehole_action()

    def save_data_by_default_action(self) -> None:
        filename = strftime(cf.DEFAULT_FORMAT_OF_FILENAME, gmtime()) + '.' + cf.TYPES_OF_SAVING_FILE[0]
        if not os.path.exists(cf.DEFAULT_FOLDER_NAME_TO_SAVE):
            os.mkdir(cf.DEFAULT_FOLDER_NAME_TO_SAVE)
        self.save_data_for_path(cf.DEFAULT_FOLDER_NAME_TO_SAVE + '/' + filename, cf.TYPES_OF_SAVING_FILE[0])

    def save_data_by_select_action(self) -> None:
        filename = QFileDialog.getSaveFileName(self, dir=str(pathlib.Path().resolve() / cf.DEFAULT_FOLDER_NAME_TO_SAVE),
                                               filter=cf.FILE_DIALOG_SAVE_FILTERS[2])
        self.save_data_for_path(filename[0], filename[0].split('.')[-1].lower())

    def save_data_for_path(self, path_: str, type_: str) -> None:
        if self.plot_widget is not None:
            QScreen.grabWindow(self.borehole_window.main_window.app.primaryScreen(),
                               self.plot_widget.winId()).save(path_, type_)


class CheckBoxHideFunctor(AbstractFunctor):
    def __init__(self, dataframe_, graph_window_widget_: AbstractGraphWindowWidget):
        self.dataframe = dataframe_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        self.dataframe.active = state_ != 0
        self.graph_window_widget.replot_for_new_data()


class CheckBoxList(ListWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.setMaximumWidth(200)

    def add_checkbox(self, text_: str, functor_: AbstractFunctor, checked_: bool):
        checkbox = MyCheckBox(text_, functor_, checked_, self)
        self.add_widget(checkbox)


# ---------------- Oscilloscope ----------------
class OscilloscopeTableWidget(QTableWidget):
    def __init__(self, parent_: QWidget):
        super().__init__(parent_)

    def __table_init(self, row_count_: int, column_count_: int, labels_: list) -> None:
        self.setRowCount(row_count_)
        self.setColumnCount(column_count_)
        self.setHorizontalHeaderLabels(labels_)
        for i in range(len(labels_)):
            self.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)
        self.horizontalHeader().setStyleSheet("QHeaderView::section {background-color: rgb(128, 255, 192);}")

    def __default_size_set(self, window_size_: QSize) -> None:
        self.setColumnWidth(0, int(window_size_.width() / 3))
        self.setColumnWidth(1, int(window_size_.width() / 4))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def set_data(self, data_frames_: dict, window_size_: QSize) -> None:
        self.clear()
        row_count, fkey = 0, None
        for key in data_frames_:
            dfl = len(data_frames_[key])
            row_count += dfl
            if dfl:
                fkey = key
        if fkey is None:
            return
        self.__table_init(row_count, 2, ["Файл", "Максимум, " + data_frames_[fkey][0].header['Data Uint']])
        for key in data_frames_:
            for i in range(len(data_frames_[key])):
                lTWI = QTableWidgetItem(data_frames_[key][i].name)
                rTWI = QTableWidgetItem(str(data_frames_[key][i].max_y))
                lTWI.setTextAlignment(Qt.AlignRight)
                rTWI.setTextAlignment(Qt.AlignRight)
                self.setItem(i, 0, lTWI)
                self.setItem(i, 1, rTWI)
        self.__default_size_set(window_size_)


class OscilloscopeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.table_widget = OscilloscopeTableWidget(self)
        self.checkbox_list_widget = CheckBoxList(self)
        self.checkbox_list_widget.setMaximumSize(300, 300)
        self.plot_widget = OscilloscopeGraphWidget(dict(), self)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        table_checkbox_layout = QHBoxLayout()
        table_checkbox_layout.addWidget(self.table_widget)
        table_checkbox_layout.addWidget(self.checkbox_list_widget)

        core_layout = QVBoxLayout()
        core_layout.addLayout(table_checkbox_layout)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_xy_dataframes_dict()
        if len(self.data_frames) < 1:
            return
        self.table_widget.set_data(self.data_frames, self.borehole_window.main_window.size())

        self.replot_for_new_data()
        self.borehole_window.download_bar_action.setEnabled(True)
        self.borehole_window.download_as_bar_action.setEnabled(True)

        self.checkbox_list_widget.remove_all()
        for key in self.data_frames.keys():
            for dataframe in self.data_frames[key]:
                self.checkbox_list_widget.add_checkbox(dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)


# ---------------- FrequencyResponse ----------------
class PipeCrack:
    def __init__(self, side_: str, depth_: int, position_m_: float):
        self.side = side_
        self.depth = depth_
        self.position_m = position_m_

    def __eq__(self, other_) -> bool:
        return self.side == other_.side and self.depth == other_.depth and self.position_m == other_.position_m


class Pipe:
    def __init__(self, length_: float, inner_d_: float, wall_thickness_: float, sensors_: list, direction_: str):
        self.length = length_
        self.inner_d = inner_d_
        self.wall_thickness = wall_thickness_
        self.sensors = sensors_
        self.direction = direction_
        self.cracks = []

    def add_crack(self, side_: str, depth_: int, position_m_: float) -> None:
        new_crack = PipeCrack(side_, depth_, position_m_)
        for crack in self.cracks:
            if crack == new_crack:
                return
        self.cracks.append(new_crack)


class ComputePipeCrack:
    def __init__(self, crack_: PipeCrack, pipe_: Pipe, position_: QPoint):
        self.crack = crack_
        self.pipe = pipe_
        self.position = position_

        self.side_addition = 0
        if self.crack.side == cf.BOTTOM_SIDE:
            self.side_addition = cf.DASH_PIPE_SIZE.height() + cf.RELATIVE_DASH_PIPE_POSITION.y()
        self.absolute_x = cf.SOLID_PIPE_SIZE.width() * self.crack.position_m // self.pipe.length

        self.line = self.compute_line()
        self.position_text_position = self.compute_position_text_position()
        self.depth_text_position = self.compute_depth_text_position()

    def compute_line(self) -> QLine:
        return QLine(QPoint(self.position.x() + self.absolute_x, self.position.y() + self.side_addition),
                     QPoint(self.position.x() + self.absolute_x,
                            int(self.position.y() + cf.RELATIVE_DASH_PIPE_POSITION.y() + self.side_addition)))

    def compute_position_text_position(self) -> QPoint:
        return QPoint(self.position.x() + self.absolute_x - cf.SOLID_PIPE_SIZE.width() // 50,
                      self.position.y() + self.side_addition
                      - cf.CRACK_PIPE_FONT_SIZE * cf.SOLID_PIPE_SIZE.height() / 200)

    def compute_depth_text_position(self) -> QPoint:
        return QPoint(self.position.x() + self.absolute_x + cf.SOLID_PIPE_SIZE.width() // 50,
                      self.position.y() + self.side_addition
                      + cf.CRACK_PIPE_FONT_SIZE * cf.SOLID_PIPE_SIZE.height() // 80)


class PipePainterResources:
    def __init__(self):
        self.solid_pen = QPen()
        self.thin_solid_pen = QPen()
        self.dash_pen = QPen()
        self.__pen_init()

    def __pen_init(self) -> None:
        self.solid_pen.setColor(cf.COLOR_NAMES[-1])
        self.solid_pen.setStyle(Qt.SolidLine)
        self.solid_pen.setWidth(cf.SOLID_PIPE_LINE_WIDTH)

        self.thin_solid_pen.setColor(cf.COLOR_NAMES[-1])
        self.thin_solid_pen.setStyle(Qt.SolidLine)
        self.thin_solid_pen.setWidth(cf.CRACK_LINE_FOR_PIPE_WIDTH)

        self.dash_pen.setColor(cf.COLOR_NAMES[-1])
        self.dash_pen.setStyle(Qt.DashLine)
        self.dash_pen.setWidth(cf.DASH_PIPE_LINE_WIDTH)


class PipePainter(QPainter):
    def __init__(self, pipe_: Pipe, paint_resources_: PipePainterResources, pipe_widget_size_: QSize, parent_: QWidget):
        super().__init__(parent_)
        self.pipe = pipe_
        self.paint_resources = paint_resources_

        self.position = QPoint((pipe_widget_size_.width() - cf.SOLID_PIPE_SIZE.width()) // 2,
                               (pipe_widget_size_.height() - cf.SOLID_PIPE_SIZE.height()) // 2)

        self.inner_position = self.position + cf.RELATIVE_DASH_PIPE_POSITION

    def draw_all(self) -> None:
        self.draw_pipe()
        self.draw_sensors()
        self.draw_cracks()

    def draw_pipe(self) -> None:
        self.setPen(self.paint_resources.solid_pen)
        self.drawRect(QRect(self.position, cf.SOLID_PIPE_SIZE))

        self.setPen(self.paint_resources.dash_pen)
        self.drawRect(QRect(self.inner_position, cf.DASH_PIPE_SIZE))

    def draw_sensors(self) -> None:
        for i in range(len(self.pipe.sensors)):
            self.__draw_sensor_name(i, self.pipe.sensors[i])

    def __draw_sensor_name(self, index_: int, name_: str) -> None:
        font = self.font()
        font.setPixelSize(cf.SENSOR_PIPE_FONT_SIZE)
        self.setFont(font)
        x_addition, y_addition = 0, 0
        if index_ == 2 or index_ == 3:
            y_addition = cf.DASH_PIPE_SIZE.height() + cf.RELATIVE_DASH_PIPE_POSITION.y()
        if index_ == 0 or index_ == 2:
            x_addition = cf.SOLID_PIPE_SIZE.width() + cf.SOLID_PIPE_SIZE.width() / 25
        position = QPoint(self.position.x() - cf.SOLID_PIPE_SIZE.width() / 30 + x_addition,
                          self.position.y() + cf.SENSOR_PIPE_FONT_SIZE * cf.SOLID_PIPE_SIZE.height() / 100 + y_addition)
        self.drawText(position, name_)

    def draw_cracks(self) -> None:
        for crack in self.pipe.cracks:
            self.__draw_crack(crack)

    def __draw_crack(self, crack_: PipeCrack) -> None:
        compute_crack = ComputePipeCrack(crack_, self.pipe, self.position)

        self.setPen(self.paint_resources.thin_solid_pen)
        self.drawLine(compute_crack.line)

        font = self.font()
        font.setPixelSize(cf.CRACK_PIPE_FONT_SIZE)
        self.setFont(font)
        self.drawText(compute_crack.depth_text_position, str(crack_.depth) + ' ' + cf.PIPE_CRACK_DEPTH_UNIT)
        self.drawText(compute_crack.position_text_position, str(crack_.position_m) + ' ' + cf.PIPE_CRACK_POSITION_UNIT)


class PipeWidget(QWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.setMinimumSize(cf.PIPE_SECTION_SIZE)
        self.pipe = Pipe(1, 0.3, 0.2, ['1', '1', '3', '3'], cf.LEFT_RIGHT_DIRECTION)

        self.paint_resources = PipePainterResources()

    def paintEvent(self, event_) -> None:
        painter = PipePainter(self.pipe, self.paint_resources, self.size(), self)
        painter.draw_all()


class ChangerPipeCrackWidget(PipeCrack, QWidget):
    def __init__(self, parent_list_: ListWidget, pipe_length_: float,
                 side_: str = cf.UPPER_SIDE, depth_: int = 0, position_m_: float = 0):
        PipeCrack.__init__(self, side_, depth_, position_m_)
        QWidget.__init__(self)
        self.pipe_length = pipe_length_
        if self.position_m > self.pipe_length:
            self.position_m = self.pipe_length
        self.parent_list = parent_list_

        self.side_editor = QComboBox(self)
        self.depth_editor = QLineEdit(self)
        self.position_editor = QLineEdit(self)
        self.__editors_init()
        self.__set_values_to_editors()

        self.delete_button = QPushButton("X", self)
        self.__button_init()

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QHBoxLayout()
        flo = QFormLayout()
        flo.addRow("Сторона", self.side_editor)
        core_layout.addLayout(flo)
        flo = QFormLayout()
        flo.addRow("Глубина (мм)", self.depth_editor)
        core_layout.addLayout(flo)
        flo = QFormLayout()
        flo.addRow("Позиция (м)", self.position_editor)
        core_layout.addLayout(flo)
        core_layout.addWidget(self.delete_button)
        self.setLayout(core_layout)

    def __editors_init(self) -> None:
        self.side_editor.addItems(["Верхняя", "Нижняя"])
        self.side_editor.currentIndexChanged.connect(self.side_changed_action)

        self.depth_editor.setValidator(QIntValidator())
        self.depth_editor.setAlignment(Qt.AlignRight)
        self.depth_editor.textChanged.connect(self.depth_edit_action)

        self.position_editor.setValidator(QDoubleValidator(0., 8., 2))
        self.position_editor.textChanged.connect(self.position_edit_action)
        self.position_editor.setAlignment(Qt.AlignRight)

    def __button_init(self) -> None:
        self.delete_button.setMaximumWidth(25)
        self.delete_button.clicked.connect(self.delete_action)

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
        if self.position_m > self.pipe_length:
            self.position_m = self.pipe_length
            self.position_editor.setText(str(self.position_m))

    def delete_action(self) -> None:
        self.parent_list.remove_item(self)


class ChangerPipeWidget(Pipe, QWidget):
    def __init__(self, parent_: QWidget, length_: float, inner_d_: float, wall_thickness_: float,
                 sensors_: list, direction_: str):
        Pipe.__init__(self, length_, inner_d_, wall_thickness_, sensors_, direction_)
        QWidget.__init__(self)

        self.length_editor = QLineEdit(self)
        self.inner_d_editor = QLineEdit(self)
        self.wall_thickness_editor = QLineEdit(self)
        self.direction_editor = QComboBox(self)
        self.sensor_editors = [QLineEdit(self), QLineEdit(self), QLineEdit(self), QLineEdit(self)]
        self.__editors_init()
        self.__set_values_to_editors()

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        form_layout = QFormLayout()
        form_layout.addRow("Длина (м)", self.length_editor)
        form_layout.addRow("Диаметр внутренней трубы (м)", self.inner_d_editor)
        form_layout.addRow("Толщина стенки (м)", self.wall_thickness_editor)
        form_layout.addRow("Направление прозвучки", self.direction_editor)

        up_layout = QHBoxLayout()
        for i in range(2):
            flo = QFormLayout()
            flo.addRow("Датчик №" + str(i + 1), self.sensor_editors[i])
            up_layout.addLayout(flo)

        low_layout = QHBoxLayout()
        for i in range(2, 4):
            flo = QFormLayout()
            flo.addRow("Датчик №" + str(i + 1), self.sensor_editors[i])
            low_layout.addLayout(flo)

        core_layout = QVBoxLayout()
        core_layout.addLayout(form_layout)
        core_layout.addLayout(up_layout)
        core_layout.addLayout(low_layout)
        self.setLayout(core_layout)

    def __editors_init(self) -> None:
        self.length_editor.setValidator(QDoubleValidator(0., 8., 2))
        self.length_editor.textChanged.connect(self.length_edit_action)
        self.length_editor.setAlignment(Qt.AlignRight)

        self.inner_d_editor.setValidator(QDoubleValidator(0., 2., 2))
        self.inner_d_editor.textChanged.connect(self.inner_d_edit_action)
        self.inner_d_editor.setAlignment(Qt.AlignRight)

        self.wall_thickness_editor.setValidator(QDoubleValidator(0., 2., 2))
        self.wall_thickness_editor.textChanged.connect(self.wall_thickness_edit_action)
        self.wall_thickness_editor.setAlignment(Qt.AlignRight)

        self.direction_editor.addItems(["->", "<-"])
        self.direction_editor.currentIndexChanged.connect(self.direction_changed_action)

        self.sensor_editors[0].textChanged.connect(self.sensor_0_edit_action)
        self.sensor_editors[1].textChanged.connect(self.sensor_1_edit_action)
        self.sensor_editors[2].textChanged.connect(self.sensor_2_edit_action)
        self.sensor_editors[3].textChanged.connect(self.sensor_3_edit_action)

    def __set_values_to_editors(self) -> None:
        self.length_editor.setText(str(self.length))
        self.inner_d_editor.setText(str(self.inner_d))
        self.wall_thickness_editor.setText(str(self.wall_thickness))
        self.direction_editor.setCurrentIndex(int(self.direction == cf.RIGHT_LEFT_DIRECTION))
        for i in range(len(self.sensor_editors)):
            self.sensor_editors[i].setText(self.sensors[i])

    def length_edit_action(self, text_) -> None:
        self.length = 0. if len(text_) < 1 else float(text_.replace(',', '.'))

    def inner_d_edit_action(self, text_) -> None:
        self.inner_d = 0. if len(text_) < 1 else float(text_.replace(',', '.'))

    def wall_thickness_edit_action(self, text_) -> None:
        self.wall_thickness = 0. if len(text_) < 1 else float(text_.replace(',', '.'))

    def direction_changed_action(self, index_: int) -> None:
        self.direction = cf.LEFT_RIGHT_DIRECTION if index_ == 0 else cf.RIGHT_LEFT_DIRECTION

    def sensor_0_edit_action(self, text_) -> None:
        self.sensors[0] = text_

    def sensor_1_edit_action(self, text_) -> None:
        self.sensors[1] = text_

    def sensor_2_edit_action(self, text_) -> None:
        self.sensors[2] = text_

    def sensor_3_edit_action(self, text_) -> None:
        self.sensors[3] = text_


class CrackSettingsDialog(QDialog):
    def __init__(self, pipe_: Pipe, parent_: QWidget = None):
        super().__init__(parent_)
        self.pipe = pipe_
        self.pipe_settings_widget = ChangerPipeWidget(self, self.pipe.length, self.pipe.inner_d,
                                                      self.pipe.wall_thickness, self.pipe.sensors, self.pipe.direction)
        self.cracks_list_widget = ListWidget(self)

        self.setWindowTitle("Cracks Settings")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(800, 500)

        self.add_button = QPushButton("+ Добавить")
        self.accept_button = QPushButton("Применить")
        self.cancel_button = QPushButton("Отменить")
        self.__button_init()

        for crack in self.pipe.cracks:
            self.cracks_list_widget.add_widget(ChangerPipeCrackWidget(self.cracks_list_widget, self.pipe.length,
                                                                      crack.side, crack.depth, crack.position_m))
        self.__all_widgets_to_layout()

    def __button_init(self) -> None:
        self.add_button.clicked.connect(self.add_crack_action)
        self.accept_button.clicked.connect(self.accept_action)
        self.cancel_button.setShortcut("Shift+Esc")
        self.cancel_button.clicked.connect(self.cancel_action)

    def __all_widgets_to_layout(self) -> None:
        accept_cancel_layout = QHBoxLayout()
        accept_cancel_layout.addWidget(self.accept_button)
        accept_cancel_layout.addWidget(self.cancel_button)

        core_layout = QVBoxLayout()
        core_layout.addWidget(self.pipe_settings_widget)
        core_layout.addWidget(self.cracks_list_widget)
        core_layout.addWidget(self.add_button)
        core_layout.addLayout(accept_cancel_layout)

        self.setLayout(core_layout)

    def __add_crack(self, side_: str = cf.UPPER_SIDE, depth_: int = 0, position_m_: float = 0) -> None:
        self.cracks_list_widget.add_widget(ChangerPipeCrackWidget(self.cracks_list_widget, self.pipe.length,
                                                                  side_, depth_, position_m_))
        self.update()

    def add_crack_action(self) -> None:
        self.__add_crack()

    def accept_action(self) -> None:
        self.pipe.cracks.clear()
        for crack in self.cracks_list_widget.widget_list:
            self.pipe.add_crack(crack.side, crack.depth, crack.position_m)
        self.close()
        self.pipe.length = self.pipe_settings_widget.length
        self.pipe.inner_d = self.pipe_settings_widget.inner_d
        self.pipe.wall_thickness = self.pipe_settings_widget.wall_thickness
        self.pipe.sensors = self.pipe_settings_widget.sensors
        self.pipe.direction = self.pipe_settings_widget.direction

    def cancel_action(self):
        self.close()

    def run(self):
        self.cracks_list_widget.remove_all()
        for crack in self.pipe.cracks:
            self.__add_crack(crack.side, crack.depth, crack.position_m)
        self.exec()


class FrequencyResponseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = FrequencyResponseGraphWidget(dict(), self)
        self.pipe_widget = PipeWidget(self)
        self.cracks_dialog = CrackSettingsDialog(self.pipe_widget.pipe, self)
        self.checkbox_list_widget = CheckBoxList(self)
        self.checkbox_list_widget.setMaximumSize(300, 300)

        self.crack_button = QPushButton("Задать параметры трубы", self)
        self.__button_init()

        self.__all_widgets_to_layout()

    def __button_init(self) -> None:
        self.crack_button.clicked.connect(self.run_crack_dialog)
        self.crack_button.setMaximumWidth(200)
        self.crack_button.setMinimumHeight(60)

    def __all_widgets_to_layout(self) -> None:
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.crack_button)

        tmp_layout = QHBoxLayout()
        tmp_layout.addLayout(btn_layout)
        tmp_layout.addWidget(self.pipe_widget)
        tmp_layout.addWidget(self.checkbox_list_widget)

        core_layout = QVBoxLayout()
        core_layout.addWidget(self.plot_widget)
        core_layout.addLayout(tmp_layout)
        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_sensor_21_dataframe_dict()
        if len(self.data_frames.keys()) < 1:
            return

        self.borehole_window.download_bar_action.setEnabled(True)
        self.borehole_window.download_as_bar_action.setEnabled(True)

        self.checkbox_list_widget.remove_all()
        for section_name in self.data_frames.keys():
            for dataframe in self.data_frames[section_name]:
                self.checkbox_list_widget.add_checkbox(section_name + '=' + dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)
        self.replot_for_new_data()

    def run_crack_dialog(self) -> None:
        self.cracks_dialog.run()
        self.pipe_widget.update()


# ---------------- AmplitudeTime ----------------
class AmplitudeTimeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = AmplitudeTimeGraphWidget(dict(), self)
        self.checkbox_list_widget = CheckBoxList(self)
        self.checkbox_list_widget.setMaximumSize(300, 300)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.plot_widget)
        core_layout.addWidget(self.checkbox_list_widget)
        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_step_maxes_dataframe_dict()
        if len(self.data_frames) < 1:
            return

        self.borehole_window.download_bar_action.setEnabled(True)
        self.borehole_window.download_as_bar_action.setEnabled(True)

        self.checkbox_list_widget.remove_all()
        for section_name in self.data_frames.keys():
            for dataframe in self.data_frames[section_name]:
                self.plot_widget.dict_data_x[section_name] = dataframe.tmp_value
                self.checkbox_list_widget.add_checkbox(section_name + '=sensor=' + dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)
        self.replot_for_new_data()


# ---------------- WindRose ----------------
class WindRoseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = MplWidget(self)
        self.checkbox_list_widget = CheckBoxList(self)
        self.checkbox_list_widget.setMaximumSize(300, 300)
        self.checkbox_list_widget.add_checkbox('Абсолютное значение',
                                               CheckBoxAbsoluteValueWindRoseFunctor(self), True)

        self.is_relative = False

        self.slider = QSlider(Qt.Horizontal, self)
        self.__slider_init()

        self.__all_widgets_to_layout()

    def __slider_init(self) -> None:
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setMinimumWidth(int(self.borehole_window.main_window.size().width() / 4 * 3))
        self.slider.valueChanged.connect(self.replot_for_new_data)

    def __all_widgets_to_layout(self) -> None:
        slider_checkbox_layout = QHBoxLayout()
        slider_checkbox_layout.addWidget(self.slider)
        slider_checkbox_layout.addWidget(self.checkbox_list_widget)

        core_layout = QVBoxLayout()
        core_layout.addLayout(slider_checkbox_layout)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_sensor_dataframe_dict()
        self.checkbox_list_widget.remove_all()
        self.checkbox_list_widget.add_checkbox('Абсолютное значение',
                                               CheckBoxAbsoluteValueWindRoseFunctor(self), not self.is_relative)
        if len(self.data_frames.keys()) > 1:
            for section_name in self.data_frames:
                self.checkbox_list_widget.add_checkbox(section_name,
                                                       CheckBoxHideWindRoseFunctor(section_name, self), True)
        if self.slider.value() != 1:
            self.slider.setValue(1)
        else:
            self.replot_for_new_data()

        self.borehole_window.download_bar_action.setEnabled(True)
        self.borehole_window.download_as_bar_action.setEnabled(True)

    def replot_for_new_data(self) -> None:
        self.plot_widget.clear()
        if len(self.data_frames.keys()) < 1:
            return
        max_range = 1
        for key in self.data_frames.keys():
            for dataframe in self.data_frames[key]:
                max_range = max(max_range, len(dataframe.data['y']))
        self.slider.setRange(1, max_range)
        self.plot_widget.set_data(self.data_frames, self.slider.value() - 1, self.is_relative)


class CheckBoxAbsoluteValueWindRoseFunctor(AbstractFunctor):
    def __init__(self, graph_window_widget_: WindRoseGraphWindowWidget):
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        self.graph_window_widget.is_relative = state_ == 0
        self.graph_window_widget.replot_for_new_data()


class CheckBoxHideWindRoseFunctor(AbstractFunctor):
    def __init__(self, section_name_: str, graph_window_widget_: WindRoseGraphWindowWidget):
        self.section_name = section_name_
        self.graph_window_widget = graph_window_widget_

    def action(self, state_: int) -> None:
        if self.section_name in self.graph_window_widget.data_frames:
            for dataframe in self.graph_window_widget.data_frames[self.section_name]:
                dataframe.active = state_
        self.graph_window_widget.replot_for_new_data()
