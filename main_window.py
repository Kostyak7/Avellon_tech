import os
import pathlib
import shutil
from uuid import uuid4
from time import gmtime, strftime
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QCheckBox, \
    QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFormLayout, QLayout, QMenuBar, \
    QTableWidget, QTableWidgetItem, QLabel, QSlider, QLineEdit, QComboBox
from PySide6.QtGui import QScreen, QIcon, QPixmap, QIntValidator, QDoubleValidator, QPainter, QPen
from PySide6.QtCore import Qt, QPoint, QSize, QRect, QLine
from PySide6.QtWidgets import QAbstractItemView
from graph_widget import OscilloscopeGraphWidget, AmplitudeTimeGraphWidget,\
    FrequencyResponseGraphWidget, WindRoseGraphWidget, DepthResponseGraphWidget
from third_party import AbstractFunctor, HelpInfoDialog, SimpleItemListWidget, \
    select_path_to_files, select_path_to_dir, ListWidget, AbstractWindowWidget, \
    MyCheckBox, ButtonWidget, MessageBox, get_last_project_path, AbstractToolDialog
from loadlabel import loading
from borehole_logic import *
from data_filter import *
from converter import ConverterDialog
import config as cf


# DONE 0) get XYDataFrame in Borehole
# DONE 1) Amplitude time graph
# DONE 2) Оптимизация датафреймов ???
# DONE 3) Роза с несколькими секциями
# DONE 4) Трубу в виджет
# DONE 5) Настройки трубы
# DONE 6) Checkbox in ListWidget
# DONE 7) get Step maxes dataframe
# DONE 8) Selector by steps for frequency graph
# DONE 9) Relative data
# DONE 10) Save data for path
# DONE 11) Два раза открываются настройки скважины
# DONE 12) project logic
# DONE 13) cache
# DONE 14) глубинный
# DONE 15) амплитудный для нескольких
# DONE 16) разные средние
# DONE 17) отслеживание варнинтов
# DONE 18) git update
# DONE 18) рестуктурирование окна скважины
# DONE 19) edit pathedit
# DONE 20) load dialog
# DONE 21) tools for graphs
# TODO 22) settings and information of borehole
# DONE 23) check minimum possible name for borehole and sections
# DONE 24) Help window for each graph
# TODO 25) Change oscilloscope graph size
# TODO 26) Rewrite README
# TODO 27) close event
# TODO 28) pyinstaller for .exe
# TODO 29) Предупреждение о неполности данных
# DONE 30) try catch for other thread
# DONE 31) New modes for conversion
# DONE 32) slider for depth
# DONE 33) hide update button
# DONE 34) update config
# TODO 35) Implement Qt Designer
# TODO 36) View on graph
# TODO 37) амлитудный в онтносительных
# TODO 38) txt to json
# TODO 39)
# TODO 40)


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        mb = MessageBox()
        self.__window_init()
        self.__cache_init()

    def __window_init(self) -> None:
        self.setWindowTitle(cf.MAIN_WINDOW_TITLE)
        self.setMinimumSize(cf.MAIN_WINDOW_MINIMUM_SIZE)
        self.setWindowIcon(QIcon(cf.ICON_WINDOW_PATH))
    
    def __cache_init(self) -> None:
        last_project_path = get_last_project_path()
        if last_project_path is None:
            self.run_main_menu()
            return
        self.run_borehole_menu(last_project_path)
    
    def __cache_save(self, project_name_: str) -> None:
        if project_name_ is None:
            return
        if not os.path.isdir(cf.CACHE_DIR_PATH):
            os.mkdir(cf.CACHE_DIR_PATH)
        file = open(cf.CACHE_FILE_INFO_PATH, 'w', encoding=cf.DEFAULT_ENCODING)
        file.write('' if project_name_ is None else project_name_)
        file.close()

    def run_main_menu(self) -> None:
        self.setWindowTitle(cf.MAIN_WINDOW_TITLE)
        self.setCentralWidget(MainMenuWidget(self))

    def run_borehole_menu(self, project_path: str) -> None:
        self.__cache_save(project_path)
        self.setCentralWidget(BoreholeMenuWindowWidget(project_path, self))
    
    def exit(self) -> None:
        self.app.exit()


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
        self.button_list.add_item("Открыть последний проект", action=self.open_last_project_action)
        self.button_list.add_item("Открыть проект", action=self.open_project_action)
        self.button_list.add_item("Выход", action=self.quit_action, shortcut="Shift+Esc")

        # self.update_button = QPushButton('Update', self, Qt.AlignLeft)
        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_action)
        self.update_button.setMaximumWidth(160)

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
        # core_layout.addWidget(self.update_button, Qt.AlignLeft | Qt.AlignBottom)
        self.setLayout(core_layout)

    def create_project_action(self) -> None:
        self.create_project_dialog.run()

    def open_last_project_action(self) -> None:
        self.main_window.run_borehole_menu(get_last_project_path())

    def open_project_action(self) -> None:
        project_path = select_path_to_dir(self)
        if len(project_path) < 1:
            return
        if not os.path.isdir(project_path):
            MessageBox().warning(cf.NOT_DIR_WARNING_TITTLE, cf.NOT_DIR_WARNING_MESSAGE_F(project_path))
            return
        self.main_window.run_borehole_menu(project_path)
    
    def update_action(self) -> None:
        if pathlib.Path(cf.EXE_FILENAME).is_file():
            os.system(f'start {cf.EXE_FILENAME} update')
            self.main_window.exit()

    def quit_action(self) -> None:
        self.main_window.exit()


class CreateProjectDialog(AbstractToolDialog):
    @staticmethod
    def get_project_name(parent_path_: str, name_: str, num_: int = 0) -> str:
        tmp_name = f'{name_}_{num_}'
        for filename in pathlib.Path(parent_path_).glob('*'):
            if os.path.basename(filename) == tmp_name:
                return CreateProjectDialog.get_project_name(parent_path_, name_, num_ + 1)
        return tmp_name
        
    def __init__(self, main_menu_widget_: MainMenuWidget):
        super().__init__(cf.CREATE_PROJECT_DIALOG_TITLE, main_menu_widget_)
        self.main_menu_widget = main_menu_widget_
        self.parent_path = str(pathlib.Path().resolve() / cf.DEFAULT_PROJECT_FOLDER)
        self.project_name = CreateProjectDialog.get_project_name(self.parent_path, cf.DEFAULT_PROJECT_NAME)
        self.setMinimumWidth(800)
        self.setWindowModality(Qt.ApplicationModal)

        self.name_editor = QLineEdit(self)
        self.some_editor = QLineEdit(self)
        self.path_editor = DirPathEdit(self.parent_path, self.project_name, self.path_edit_action, self)
        self.__editors_init()

        self.accept_button = QPushButton("Создать", self)
        self.accept_button.clicked.connect(self.accept_action)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.setShortcut("Shift+Esc")
        self.cancel_button.clicked.connect(self.cancel_action)

        self.__all_widgets_to_layout()

    def __editors_init(self) -> None:
        self.name_editor.setAlignment(Qt.AlignLeft)
        self.name_editor.setText(self.project_name)
        self.name_editor.textChanged.connect(self.project_name_edit_action)

        self.some_editor.setAlignment(Qt.AlignLeft)
        self.some_editor.textChanged.connect(self.some_edit_action)

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

    def project_name_edit_action(self, text_: str) -> None:
        self.project_name = self.path_editor.name = os.path.basename(text_)
        if len(self.project_name):
            self.parent_path = self.path_editor.parent_path = str((pathlib.Path(self.parent_path) / text_).parent)
        else:
            self.parent_path = self.path_editor.parent_path = str(pathlib.Path(self.parent_path) / text_)
        if self.name_editor.text() != self.project_name:
            self.name_editor.setText(self.project_name)
        self.path_editor.path_editor.setText(self.parent_path + '/' + self.project_name)

    def some_edit_action(self, text_: str) -> None:
        pass

    def path_edit_action(self, text_: str) -> None:
        self.project_name = self.path_editor.name = os.path.basename(text_)
        if len(self.project_name):
            self.parent_path = self.path_editor.parent_path = str(pathlib.Path(text_).parent)
        else:
            self.parent_path = self.path_editor.parent_path = str(pathlib.Path(text_))
        if self.name_editor.text() != self.project_name:
            self.name_editor.setText(self.project_name)

    def accept_action(self) -> None:
        if len(self.project_name) < 1:
            MessageBox().warning(cf.EMPTY_NAME_WARNING_TITTLE, cf.EMPTY_PROJECT_NAME_WARNING_MESSAGE)
            return
        if self.project_name.find(' ') != -1:
            MessageBox().warning(cf.INVALID_NAME_WARNING_TITTLE, cf.INVALID_PROJECT_NAME_WARNING_MESSAGE)
            return
        path = str(pathlib.Path(self.parent_path) / self.project_name)
        is_exist = os.path.exists(path)
        if is_exist:
            if not os.path.isdir(path):
                MessageBox().warning(cf.NOT_DIR_WARNING_TITTLE, cf.NOT_DIR_WARNING_MESSAGE_F(path))
                return
            if len([f for f in pathlib.Path(path).glob('*')]):
                MessageBox().warning(cf.NOT_EMPTY_FOLDER_WARNING_TITLE, cf.NOT_EMPTY_FOLDER_WARNING_MESSAGE_F(path))
                return
        else:
            os.mkdir(path)
        self.main_menu_widget.main_window.run_borehole_menu(path)
        self.close()

    def run(self) -> None:
        self.parent_path = str(pathlib.Path().resolve() / cf.DEFAULT_PROJECT_FOLDER)
        self.project_name = CreateProjectDialog.get_project_name(self.parent_path, cf.DEFAULT_PROJECT_NAME)
        self.path_editor.path_editor.setText(self.parent_path + '/' + self.project_name)
        self.exec()


class DirPathEdit(QWidget):
    def __init__(self, parent_path_: str, name_: str, action_, parent_: QWidget = None):
        super().__init__(parent_)
        self.id = uuid4()
        self.parent_path = parent_path_
        self.name = name_

        self.path_editor = QLineEdit(self)
        self.path_editor.setAlignment(Qt.AlignLeft)
        self.path_editor.setText(str(pathlib.Path(self.parent_path) / self.name))
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
        self.path_editor.setText(str(pathlib.Path(select_path_to_dir(self.parent(), dir=self.parent_path)) / self.name))


class BoreholeMenuWindowWidget(QWidget):
    class TopMenuBarInit:
        def __init__(self, borehole_menu_window_widget_):
            self.borehole_window = borehole_menu_window_widget_
            self.menu_bar = QMenuBar(self.borehole_window)
            self.menu_bar.addSeparator()
            self.menu_bar.setNativeMenuBar(False)
            self.borehole_window.main_window.setMenuBar(self.menu_bar)

            self.set_bore_action_btn = self.menu_bar.addAction('&Настроить скважину', 'Ctrl+a')
            self.select_graph_menu_btn = self.menu_bar.addMenu('Выбрать график')
            self.converter_action_btn = self.menu_bar.addAction('&Конвертер', 'Ctrl+k')
            self.response_action_btn = self.menu_bar.addAction('&Выгрузить отчет', 'Ctrl+r')
            self.view_menu_btn = self.menu_bar.addMenu('Вид')
            self.back_main_menu_action_btn = self.menu_bar.addAction('В главное меню')
            self.__menu_bar_init()
        
        def __menu_bar_init(self) -> None:
            self.set_bore_action_btn.triggered.connect(self.borehole_window.set_borehole_action)
            self.__select_graph_menu_init()
            self.converter_action_btn.triggered.connect(self.borehole_window.converter_action)
            self.response_action_btn.triggered.connect(self.borehole_window.response_action)
            self.__view_menu_init()
            self.back_main_menu_action_btn.triggered.connect(self.borehole_window.back_main_menu_action)
        
        def __select_graph_menu_init(self) -> None:
            oscilloscope_action_btn = self.select_graph_menu_btn.addAction('&Осциллограмма', 'Ctrl+g+1')
            oscilloscope_action_btn.triggered.connect(self.borehole_window.plot_oscilloscope_action)
            freq_resp_action_btn = self.select_graph_menu_btn.addAction('&Частотная характеристика', 'Ctrl+g+2')
            freq_resp_action_btn.triggered.connect(self.borehole_window.plot_frequency_resp_action)
            wind_rose_action_btn = self.select_graph_menu_btn.addAction('&Круговая диаграмма', 'Ctrl+g+3')
            wind_rose_action_btn.triggered.connect(self.borehole_window.plot_wind_rose_action)
            amplitude_action_btn = self.select_graph_menu_btn.addAction('&Зависимость амплитуды во времени', 'Ctrl+g+4')
            amplitude_action_btn.triggered.connect(self.borehole_window.plot_amplitude_time_action)
            depth_resp_action_btn = self.select_graph_menu_btn.addAction('&Глубинная характеристика', 'Ctrl+g+5')
            depth_resp_action_btn.triggered.connect(self.borehole_window.plot_depth_response_action)

        def __view_menu_init(self) -> None:
            pass

    def __init__(self, path_: str, main_window_: MainWindow):
        super().__init__(main_window_)
        self.id = uuid4()
        if path_ is None or len(os.path.basename(path_)) < 1:
            MessageBox().warning(cf.EMPTY_NAME_WARNING_TITTLE, cf.EMPTY_PROJECT_NAME_WARNING_MESSAGE)
            main_window_.run_main_menu()
            return
        self.name = os.path.basename(path_)
        self.main_window = main_window_
        self.main_window.setWindowTitle(self.name + " - скважина")

        self.borehole = Borehole(self.name, str(pathlib.Path(path_).parent))
        self.borehole_dialog = BoreHoleDialog(self.borehole, self)
        self.converter_dialog = ConverterDialog(self)

        self.borehole_menu_widget = BoreHoleMenuWidget(self.name, self)
        self.graph_window_widgets = {
            'oscilloscope': OscilloscopeGraphWindowWidget(self),
            'frequency': FrequencyResponseGraphWindowWidget(self),
            'amplitude': AmplitudeTimeGraphWindowWidget(self),
            'depth': DepthResponseGraphWindowWidget(self),
            'windrose': WindRoseGraphWindowWidget(self),
        }

        top_menu_bar_init = self.TopMenuBarInit(self)
        self.__all_widgets_to_layout()
        self.borehole_menu_action()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.borehole_menu_widget)
        for key in self.graph_window_widgets.keys():
            core_layout.addWidget(self.graph_window_widgets[key])
        self.setLayout(core_layout)

    def __deactivate_all(self, is_deactivate_: bool = True) -> None:
        self.borehole_menu_widget.activate(not is_deactivate_)
        for key in self.graph_window_widgets.keys():
            self.graph_window_widgets[key].activate(not is_deactivate_)
    
    def set_borehole_action(self) -> None:
        self.borehole_dialog.run()
    
    def converter_action(self) -> None:
        self.converter_dialog.run()

    def response_action(self) -> None:
        pass

    def back_main_menu_action(self) -> None:
        self.main_window.menuBar().clear()
        self.main_window.run_main_menu()

    def borehole_menu_action(self) -> None:
        self.__deactivate_all()
        self.borehole_menu_widget.activate()

    def __plot_graph_action_interface(self, name_: str) -> None:
        self.__deactivate_all()
        if name_ in self.graph_window_widgets:
            self.graph_window_widgets[name_].activate()

    def plot_oscilloscope_action(self) -> None:
        self.__plot_graph_action_interface('oscilloscope')

    def plot_frequency_resp_action(self) -> None:
        self.__plot_graph_action_interface('frequency')

    def plot_amplitude_time_action(self) -> None:
        self.__plot_graph_action_interface('amplitude')

    def plot_depth_response_action(self) -> None:
        self.__plot_graph_action_interface('depth')

    def plot_wind_rose_action(self) -> None:
        self.__plot_graph_action_interface('windrose')


class BoreHoleMenuWidget(AbstractWindowWidget):
    def __init__(self, name_: str, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.borehole_window = borehole_window_
        self.name = name_
        self.label = QLabel("Скважина: " + self.name, self)
        self.__label_init()

        self.button_list = SimpleItemListWidget(ButtonWidget, self)
        self.button_list.add_item("Настроить скважину", action=self.borehole_window.set_borehole_action)
        self.button_list.add_item("Построить график", action=self.goto_graph_list)
        self.button_list.add_item("Конвертер", action=self.borehole_window.converter_action)
        self.button_list.add_item("В главное меню", action=self.borehole_window.back_main_menu_action)

        self.graph_button_list = SimpleItemListWidget(ButtonWidget, self)
        self.graph_button_list.add_item("Построить осциллограммы", action=self.borehole_window.plot_oscilloscope_action)
        self.graph_button_list.add_item("Построить частотную характеристику", action=self.borehole_window.plot_frequency_resp_action)
        self.graph_button_list.add_item("Построить круговую диаграмму", action=self.borehole_window.plot_wind_rose_action)
        self.graph_button_list.add_item("Построить зависимости амплитуды во времени", action=self.borehole_window.plot_amplitude_time_action)
        self.graph_button_list.add_item("Построить глубинную характеристику", action=self.borehole_window.plot_depth_response_action)
        self.graph_button_list.add_item("Назад", action=self.back_from_graph_list)
        self.graph_button_list.setVisible(False)

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
        center_layout.addWidget(self.graph_button_list)
        center_layout.addStretch()

        core_layout = QHBoxLayout()
        core_layout.addStretch()
        core_layout.addLayout(center_layout)
        core_layout.addStretch()
        self.setLayout(core_layout)
    
    def goto_graph_list(self) -> None:
        self.button_list.setVisible(False)
        self.graph_button_list.setVisible(True)

    def back_from_graph_list(self) -> None:
        self.button_list.setVisible(True)
        self.graph_button_list.setVisible(False)


class BoreHoleDialog(AbstractToolDialog):
    def __init__(self, borehole_: Borehole, parent_: QWidget = None):
        super().__init__(cf.BOREHOLE_SETTINGS_DIALOG_TITLE, parent_)
        self.borehole = borehole_
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
        len_default_name = len(cf.DEFAULT_SECTION_NAME)
        max_section_number = -1
        for section in self.section_list_widget.widget_list:
            if section.name[:len_default_name] == cf.DEFAULT_SECTION_NAME and section.name[len_default_name:].isdigit():
                max_section_number = max(int(section.name[len_default_name:]), max_section_number)
        self.add_section(cf.DEFAULT_SECTION_NAME + str(max_section_number + 1))

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

    @loading('cancel_action')
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
        self.borehole.save_info_to_file()

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
        got_file_list = select_path_to_files(cf.FILE_DIALOG_CSV_FILTER, self, dir=cf.DEFAULT_DATA_FOLDER)
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


class HideLineToolDialog(AbstractToolDialog):
    def __init__(self, parent_: QWidget = None):
        super().__init__(cf.HIDING_LINES_DIALOG_TITLE, parent_)
        self.checkbox_list_widget = CheckBoxList(self)
        self.checkbox_list_widget.setMaximumSize(300, 300)
        self.__all_widgets_to_layout()
    
    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.checkbox_list_widget)
        self.setLayout(core_layout)
    
    def remove_all(self, *args, **kwargs) -> None:
        self.checkbox_list_widget.remove_all(*args, **kwargs)

    def add_checkbox(self, *args, **kwargs) -> None:
        self.checkbox_list_widget.add_checkbox(*args, **kwargs)


class AbstractGraphWindowWidget(AbstractWindowWidget):
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.borehole_window = borehole_window_
        self.plot_widget = None
        self.data_frames = dict()

        self.hide_line_dialog = HideLineToolDialog(self)
        self.help_info_dialog = HelpInfoDialog(self)

        self.menu_bar = QMenuBar(self)
        self.menu_bar.addSeparator()
        self.menu_bar.setNativeMenuBar(False)
        self.save_action_btn = self.menu_bar.addAction('&💾Сохранить', "Ctrl+s")
        self.plot_action_btn =  self.menu_bar.addAction("&▷ Построить", "Ctrl+p")
        self.tools_menu_btn = self.menu_bar.addMenu('Инструменты')
        self.help_action_btn = self.menu_bar.addAction('&Справка', "Ctrl+i")
        self.back_action_btn = self.menu_bar.addAction('&Назад', "Shift+Esc")
        self.__actions_init()

    def __actions_init(self) -> None:
        self.save_action_btn.triggered.connect(self.save_data_by_default_action)
        self.plot_action_btn.triggered.connect(self.plot_graph_action)
        self.__tools_menu_init()
        self.help_action_btn.triggered.connect(self.help_window_action)
        self.back_action_btn.triggered.connect(self.back_action)

    def __tools_menu_init(self) -> None:
        tools_save_action_btn = self.tools_menu_btn.addAction('Сохранить')
        tools_save_as_action_btn = self.tools_menu_btn.addAction('Сохранить как')
        hide_lines_action_btn = self.tools_menu_btn.addAction('Отображение линий')

        tools_save_action_btn.triggered.connect(self.save_data_by_default_action)
        tools_save_as_action_btn.triggered.connect(self.save_data_by_select_action)
        hide_lines_action_btn.triggered.connect(self.run_hide_line_dialog_action)

    def activate(self, is_active_: bool = True) -> None:
        self.hide_line_dialog.close()
        self.setVisible(is_active_)

    def plot_graph_action(self) -> None: ...

    def replot_for_new_data(self) -> None:
        self.plot_widget.recreate(self.data_frames)
    
    def checkbox_activate(self) -> None: ...

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
    
    def help_window_action(self) -> None:
        self.help_info_dialog.run()

    def back_action(self) -> None:
        self.borehole_window.borehole_menu_action()

    def run_hide_line_dialog_action(self) -> None:
        self.hide_line_dialog.run()


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


class AbstractFilterSettings(QWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = None
        self.setVisible(False)

    def get_filtered_data(self, init_data_: list) -> list:
        self.filter.set_data(init_data_)
        return self.filter.get_data()


class ArithFilterSettings(AbstractFilterSettings):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = ArithmeticMeanFilter([])

        self.buffer_editor = QLineEdit(self)
        self.buffer_editor.setValidator(QIntValidator())
        self.buffer_editor.setText(str(self.filter.buffer_size))
        self.buffer_editor.textChanged.connect(self.buffer_edit_action)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("Размер буффера", self.buffer_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        self.setLayout(core_layout)

    def buffer_edit_action(self, text_: str) -> None:
        if len(text_) == 0 or not (0 < int(text_) < 100):
            self.buffer_editor.setText(str(self.filter.buffer_size))
            return
        self.filter.set_params(int(text_))


class MedianFilterSettings(AbstractFilterSettings):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = MedianFilter([])

        self.buffer_editor = QLineEdit(self)
        self.buffer_editor.setValidator(QIntValidator())
        self.buffer_editor.setText(str(self.filter.buffer_size))
        self.buffer_editor.textChanged.connect(self.buffer_edit_action)

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("Размер буффера", self.buffer_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        self.setLayout(core_layout)

    def buffer_edit_action(self, text_: str) -> None:
        if len(text_) == 0 or not (0 < int(text_) < 100):
            self.buffer_editor.setText(str(self.filter.buffer_size))
            return
        self.filter.set_params(int(text_))


class ExpMeanFilterSettings(AbstractFilterSettings):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = ExpEasyMeanFilter([])

        self.s_k_editor = QLineEdit(self)
        self.max_k_editor = QLineEdit(self)
        self.d_editor = QLineEdit(self)
        self.__editors_init()

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("S_k", self.s_k_editor)
        flo.addRow("Max_k", self.max_k_editor)
        flo.addRow("D", self.d_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        self.setLayout(core_layout)

    def __editors_init(self) -> None:
        self.s_k_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.s_k_editor.setText(str(self.filter.s_k))
        self.s_k_editor.textChanged.connect(self.s_k_edit_action)

        self.max_k_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.max_k_editor.setText(str(self.filter.max_k))
        self.max_k_editor.textChanged.connect(self.max_k_edit_action)

        self.d_editor.setValidator(QDoubleValidator(0.3, 10., 4))
        self.d_editor.setText(str(self.filter.d))
        self.d_editor.textChanged.connect(self.d_edit_action)

    def s_k_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.s_k = float(text_)

    def max_k_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.max_k = float(text_)

    def d_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.d = float(text_)


class NormFilterSettings(AbstractFilterSettings):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = NormaliseFilter([])

        self.buffer_editor = QLineEdit(self)
        self.s_k_editor = QLineEdit(self)
        self.max_k_editor = QLineEdit(self)
        self.d_editor = QLineEdit(self)
        self.__editors_init()

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("Размер буффера", self.buffer_editor)
        flo.addRow("S_k", self.s_k_editor)
        flo.addRow("Max_k", self.max_k_editor)
        flo.addRow("D", self.d_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        self.setLayout(core_layout)

    def __editors_init(self) -> None:
        self.buffer_editor.setValidator(QIntValidator())
        self.buffer_editor.setText(str(self.filter.buffer_size))
        self.buffer_editor.textChanged.connect(self.buffer_edit_action)

        self.s_k_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.s_k_editor.setText(str(self.filter.s_k))
        self.s_k_editor.textChanged.connect(self.s_k_edit_action)

        self.max_k_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.max_k_editor.setText(str(self.filter.max_k))
        self.max_k_editor.textChanged.connect(self.max_k_edit_action)

        self.d_editor.setValidator(QDoubleValidator(0.3, 10., 4))
        self.d_editor.setText(str(self.filter.d))
        self.d_editor.textChanged.connect(self.d_edit_action)

    def s_k_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.s_k = float(text_)

    def max_k_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.max_k = float(text_)

    def d_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.d = float(text_)

    def buffer_edit_action(self, text_: str) -> None:
        if len(text_) == 0 or not (0 < int(text_) < 100):
            self.buffer_editor.setText(str(self.filter.buffer_size))
            return
        self.filter.buffer_size = int(text_)


class KalmanFilterSettings(AbstractFilterSettings):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.filter = KalmanFilter([])

        self.q_editor = QLineEdit(self)
        self.r_editor = QLineEdit(self)
        self.__editors_init()

        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow("Q", self.q_editor)
        flo.addRow("R", self.r_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        self.setLayout(core_layout)

    def __editors_init(self) -> None:
        self.q_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.q_editor.setText(str(self.filter.q))
        self.q_editor.textChanged.connect(self.q_edit_action)

        self.r_editor.setValidator(QDoubleValidator(0., 0.999, 4))
        self.r_editor.setText(str(self.filter.r))
        self.r_editor.textChanged.connect(self.r_edit_action)

    def q_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.q = float(text_)

    def r_edit_action(self, text_: str) -> None:
        if len(text_) != 0:
            self.filter.r = float(text_)


class FilterSettingsDialog(AbstractToolDialog):
    def __init__(self, window_widget_):
        super().__init__(cf.FILTER_SETTINGS_DIALOG_TITLE, window_widget_)
        self.window_widget = window_widget_
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(800, 500)
        self.is_filtering = False
        self.is_filter_checkbox = QCheckBox(self)
        self.is_filter_checkbox.setChecked(self.is_filtering)
        self.is_filter_checkbox.clicked.connect(self.is_filter_action)

        self.filter_widgets_dict = {
            "Среднее арифметическое":  ArithFilterSettings(self),
            "Медиана": MedianFilterSettings(self),
            "Экспонициальное среднее": ExpMeanFilterSettings(self),
            "Нормализованное": NormFilterSettings(self),
            "Фильтр Калмана": KalmanFilterSettings(self)
        }
        self.filter_editor = QComboBox(self)
        self.filter_editor.addItems(self.filter_widgets_dict.keys())
        self.filter_editor.currentIndexChanged.connect(self.filter_changed_action)
        self.filter_editor.setCurrentIndex(0)
        self.filter_widgets_dict[self.filter_editor.currentText()].setVisible(True)

        self.accept_button = QPushButton("Применить")
        self.__button_init()
        self.__all_widgets_to_layout()

    def __button_init(self) -> None:
        self.accept_button.clicked.connect(self.accept_action)
        self.accept_button.setShortcut("Shift+Esc")

    def __all_widgets_to_layout(self) -> None:
        accept_cancel_layout = QHBoxLayout()
        accept_cancel_layout.addWidget(self.accept_button)

        flo = QFormLayout()
        flo.addRow("Применить фильтр к данным", self.is_filter_checkbox)
        flo.addRow("Способ фильтрации", self.filter_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        for key in self.filter_widgets_dict.keys():
            core_layout.addWidget(self.filter_widgets_dict[key])
        core_layout.addLayout(accept_cancel_layout)
        self.setLayout(core_layout)

    def filter_changed_action(self, index_: int) -> None:
        for key in self.filter_widgets_dict.keys():
            self.filter_widgets_dict[key].setVisible(False)
        self.filter_widgets_dict[self.filter_editor.currentText()].setVisible(True)

    def set_filter(self, state_: bool) -> None:
        self.is_filtering = state_
        self.is_filter_checkbox.setChecked(state_)

    def is_filter_action(self, state_: bool) -> None:
        self.is_filtering = state_

    def get_data(self, init_data_: list) -> dict:
        return {"y": self.filter_widgets_dict[self.filter_editor.currentText()].get_filtered_data(init_data_)}

    def accept_action(self) -> None:
        self.window_widget.filter_action_btn.setChecked(self.is_filtering)
        self.window_widget.plot_graph_action()
        self.close()

    def run(self):
        self.show()


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
        self.__table_init(row_count, 2, ["Файл", "Максимум, " + data_frames_[fkey][0].header[cf.DATA_UINT_HEADER]])
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
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.table_widget = OscilloscopeTableWidget(self)
        self.plot_widget = OscilloscopeGraphWidget(dict(), self)

        self.filter_settings_dialog = FilterSettingsDialog(self)
        self.filter_action_btn = self.tools_menu_btn.addAction('Фильтрация данных')
        self.filter_action_btn.setCheckable(True)
        self.filter_action_btn.setChecked(self.filter_settings_dialog.is_filtering)
        self.filter_action_btn.triggered.connect(self.filter_data_action)
        filter_dialog_action_btn = self.tools_menu_btn.addAction('Настройка фильтров данных')
        filter_dialog_action_btn.triggered.connect(self.filter_settings_dialog.run)

        self.__all_widgets_to_layout()
        self.activate(False)

    def __all_widgets_to_layout(self) -> None:
        table_checkbox_layout = QHBoxLayout()
        table_checkbox_layout.addWidget(self.table_widget)

        core_layout = QVBoxLayout()
        core_layout.addWidget(self.menu_bar)
        core_layout.addLayout(table_checkbox_layout)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def filter_data_action(self, state_: bool) -> None:
        self.filter_settings_dialog.set_filter(state_)
        self.plot_graph_action()

    @loading('checkbox_activate')
    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_xy_dataframes_dict()
        if len(self.data_frames) < 1:
            return
        if self.filter_settings_dialog.is_filtering:
            for key in self.data_frames.keys():
                for dataframe in self.data_frames[key]:
                    if dataframe.filt_data is None:
                        dataframe.filt_data = self.filter_settings_dialog.get_data(dataframe.origin_data["y"])
                    dataframe.data = dataframe.filt_data
        else:
            for key in self.data_frames.keys():
                for dataframe in self.data_frames[key]:
                    dataframe.data = dataframe.origin_data

        self.table_widget.set_data(self.data_frames, self.borehole_window.main_window.size())
        self.replot_for_new_data()
    
    def checkbox_activate(self) -> None:
        self.hide_line_dialog.remove_all()
        for key in self.data_frames.keys():
            for dataframe in self.data_frames[key]:
                self.hide_line_dialog.add_checkbox(dataframe.name,
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


class CrackSettingsDialog(AbstractToolDialog):
    def __init__(self, pipe_: Pipe, parent_: QWidget = None):
        super().__init__(cf.CRACK_SETTINGS_DIALOG_TITLE, parent_)
        self.pipe = pipe_
        self.pipe_settings_widget = ChangerPipeWidget(self, self.pipe.length, self.pipe.inner_d,
                                                      self.pipe.wall_thickness, self.pipe.sensors, self.pipe.direction)
        self.cracks_list_widget = ListWidget(self)

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

    def run(self):
        self.cracks_list_widget.remove_all()
        for crack in self.pipe.cracks:
            self.__add_crack(crack.side, crack.depth, crack.position_m)
        self.show()


class FrequencyResponseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = FrequencyResponseGraphWidget(dict(), self)
        self.pipe_widget = PipeWidget(self)
        self.cracks_dialog = CrackSettingsDialog(self.pipe_widget.pipe, self)
        crack_action_btn = self.tools_menu_btn.addAction('Задать параметры трубы')
        crack_action_btn.triggered.connect(self.run_crack_dialog_action)

        # self.filter_settings_dialog = FilterSettingsDialog(self)
        # self.filter_action_btn = self.tools_menu_btn.addAction('Фильтрация данных')
        # self.filter_action_btn.setCheckable(True)
        # self.filter_action_btn.setChecked(self.filter_settings_dialog.is_filtering)
        # self.filter_action_btn.triggered.connect(self.filter_data_action)
        # filter_dialog_action_btn = self.tools_menu_btn.addAction('Настройка фильтров данных')
        # filter_dialog_action_btn.triggered.connect(self.filter_settings_dialog.run)

        self.__all_widgets_to_layout()
        self.activate(False)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.menu_bar)
        core_layout.addWidget(self.plot_widget)
        core_layout.addWidget(self.pipe_widget)
        self.setLayout(core_layout)
    
    def activate(self, is_active_: bool = True) -> None:
        self.cracks_dialog.close()
        super().activate(is_active_)

    # def filter_data_action(self, state_: bool) -> None:
    #     self.filter_settings_dialog.set_filter(state_)
    #     self.plot_graph_action()

    @loading('checkbox_activate')
    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_sensor_21_dataframe_dict()
    
    def checkbox_activate(self) -> None:
        if len(self.data_frames.keys()) < 1:
            return
        self.hide_line_dialog.remove_all()
        for section_name in self.data_frames.keys():
            for dataframe in self.data_frames[section_name]:
                self.hide_line_dialog.add_checkbox(section_name + '=' + dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)
        self.replot_for_new_data()

    def run_crack_dialog_action(self) -> None:
        self.cracks_dialog.run()
        self.pipe_widget.update()


# ---------------- AmplitudeTime ----------------
class GraphSettingsDialog(AbstractToolDialog):
    def __init__(self, window_graph_):
        super().__init__(cf.GRAPH_SETTINGS_DIALOG_TITLE, window_graph_)
        self.window_graph = window_graph_
        self.is_relative = False
        self.relative_checkbox = QCheckBox("Абсолютное значение", self)
        self.mean_mode = -1 # -1 means ARITHMETIC
        self.sensor_num = -1 # -1 means all sensors
        self.mean_editor = QComboBox(self)
        self.sensors_editor = QComboBox(self)
        self.accept_btn = ButtonWidget('Ок', self, action=self.accept_action)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        flo = QFormLayout()
        flo.addRow('Cпособо среднего', self.mean_editor)
        flo.addRow('Выбрать датчики', self.sensors_editor)
        core_layout.addLayout(flo)
        core_layout.addWidget(self.accept_btn)
        self.setLayout(core_layout)

    def _editors_init(self) -> None:
        self.relative_checkbox.setChecked(not self.is_relative)
        self.relative_checkbox.stateChanged.connect(self.relative_checkbox_action)

        self.mean_editor.addItems(["Среднее арифметическое", "Медиана", "Среднее геометрическое",
                                   "Среднее гармоническое", "Сгруппированная медиана"])
        self.mean_editor.currentIndexChanged.connect(self.mean_changed_action)
        self.mean_editor.setCurrentIndex(0)

        choice_list = ["Все датчики"]
        for i in range(cf.DEFAULT_SENSOR_AMOUNT):
            choice_list.append("Датчик " + chr(ord('A') + i))
        self.sensors_editor.addItems(choice_list)
        self.sensors_editor.currentIndexChanged.connect(self.sensors_changed_action)
        self.sensors_editor.setCurrentIndex(0)

    def relative_checkbox_action(self, state_) -> None:
        self.is_relative = state_ == 0

    def mean_changed_action(self, index_: int) -> None:
        self.mean_mode = - index_ -1

    def sensors_changed_action(self, index_: int) -> None:
        self.sensor_num = index_ - 1
        self.mean_editor.setVisible(self.sensor_num < 0)

    def accept_action(self) -> None:
        self.window_graph.replot_for_new_data()
        self.close()


class AmplitudeGraphSettingsDialog(GraphSettingsDialog):
    def __init__(self, window_graph_):
        super().__init__(window_graph_)
        self.section_mode = 0
        self.section_list = []
        self.section_mode_editor = QComboBox(self)
        self.current_section_editor = QComboBox(self)
        self._editors_init()
        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.relative_checkbox)
        flo = QFormLayout()
        flo.addRow('Отображение секций', self.section_mode_editor)
        flo.addRow('Выбор секции', self.current_section_editor)
        flo.addRow('Выбрать датчики', self.sensors_editor)
        flo.addRow('Cпособо среднего', self.mean_editor)
        core_layout.addLayout(flo)
        core_layout.addWidget(self.accept_btn)
        self.setLayout(core_layout)

    def _editors_init(self) -> None:
        super()._editors_init()
        self.section_mode_editor.addItems(["Одна секция", "Все доступные секции"])
        self.section_mode_editor.currentIndexChanged.connect(self.section_mode_changed_action)
        self.section_mode_editor.setCurrentIndex(self.section_mode)

        self.current_section_editor.currentIndexChanged.connect(self.current_section_changed_action)
        self.init_current_section_editor()

        self.section_mode_changed_action(self.section_mode)

    def init_current_section_editor(self) -> None:
        self.current_section_editor.clear()
        self.section_list.clear()
        for section in self.window_graph.borehole_window.borehole.section_list:
            self.section_list.append(section.name)
        if len(self.section_list) < 1:
            return
        self.current_section_editor.addItems(self.section_list)
        self.current_section_editor.setCurrentIndex(0)

    def section_mode_changed_action(self, index_: int) -> None:
        self.section_mode = index_
        self.current_section_editor.setVisible(self.section_mode == 0)
        self.sensors_editor.setVisible(self.section_mode != 0)
        self.mean_editor.setVisible(self.section_mode != 0 and self.sensor_num < 0)

    def current_section_changed_action(self, index_: int) -> None:
        pass

    def get_current_section(self) -> str:
        if len(self.section_list) < 1:
            return None
        return self.section_list[self.current_section_editor.currentIndex() \
            if len(self.section_list) > self.current_section_editor.currentIndex() else 0]

    def accept_action(self) -> None:
        self.window_graph.checkbox_activate()
        self.close()


class AmplitudeTimeGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = AmplitudeTimeGraphWidget(dict(), self)
        
        self.graph_settings_dialog = AmplitudeGraphSettingsDialog(self)
        self.settings_menu_action_btn = self.tools_menu_btn.addAction('Настройки графика')
        self.settings_menu_action_btn.triggered.connect(self.graph_settings_dialog.run)

        self.__all_widgets_to_layout()
        self.activate(False)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.menu_bar)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def activate(self, is_active_: bool = True) -> None:
        self.graph_settings_dialog.close()
        super().activate(is_active_)
        self.graph_settings_dialog.init_current_section_editor()

    @loading('checkbox_activate')
    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_step_maxes_dataframe_dict()
    
    def checkbox_activate(self) -> None:
        print(self.data_frames)
        if len(self.data_frames) < 1:
            return
        self.hide_line_dialog.remove_all()
        if self.graph_settings_dialog.section_mode == 0:
            section_name = self.graph_settings_dialog.get_current_section()
            if section_name is None or section_name not in self.data_frames:
                return
            for k_ in self.data_frames[section_name].keys():
                if k_ >= 0:
                    dataframe = self.data_frames[section_name][k_]
                    self.plot_widget.dict_data_x[section_name] = dataframe.tmp_value['x']
                    self.hide_line_dialog.add_checkbox(section_name + '=sensor=' + dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)
        else:
            for section_name in self.data_frames.keys():
                if self.graph_settings_dialog.sensor_num > -1:
                    if self.graph_settings_dialog.sensor_num not in self.data_frames[section_name]:
                        continue
                    dataframe = self.data_frames[section_name][self.graph_settings_dialog.sensor_num]
                    self.plot_widget.dict_data_x[section_name] = dataframe.tmp_value['x']
                    self.hide_line_dialog.add_checkbox(section_name + '=sensor=' + dataframe.name,
                                                       CheckBoxHideFunctor(dataframe, self), True)
                else:
                    dataframe = self.data_frames[section_name][self.graph_settings_dialog.mean_mode]
                    self.plot_widget.dict_data_x[section_name] = dataframe.tmp_value
                    self.hide_line_dialog.add_checkbox(dataframe.name, CheckBoxHideFunctor(dataframe, self), True)
        self.replot_for_new_data()

    # для одной секции - для всех
    # выбор секции       выбор датчика - для всех
    # 		   	  	                     выбор среднего

    def replot_for_new_data(self) -> None:
        if self.graph_settings_dialog.section_mode == 0:
            section_name = self.graph_settings_dialog.get_current_section()
            if section_name is None:
                return
            self.plot_widget.recreate(self.data_frames, section_name=section_name, is_relative=self.graph_settings_dialog.is_relative)
        elif self.graph_settings_dialog.sensor_num == -1:
            self.plot_widget.recreate(self.data_frames, sensor_num=-1, mean_mode=self.graph_settings_dialog.mean_mode, is_relative=self.graph_settings_dialog.is_relative)
        else:
            self.plot_widget.recreate(self.data_frames, sensor_num=self.graph_settings_dialog.sensor_num, is_relative=self.graph_settings_dialog.is_relative)


# ---------------- DepthResponseTime ----------------
class DepthGraphSettingsDialog(GraphSettingsDialog):
    def __init__(self, window_graph_):
        super().__init__(window_graph_)
        self._editors_init()
        self.__all_widgets_to_layout()

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.relative_checkbox)
        flo = QFormLayout()
        flo.addRow('Cпособо среднего', self.mean_editor)
        flo.addRow('Выбрать датчики', self.sensors_editor)
        core_layout.addLayout(flo)
        core_layout.addWidget(self.accept_btn)
        self.setLayout(core_layout)

    def sensors_changed_action(self, index_: int) -> None:
        self.sensor_num = index_ - 1
        self.mean_editor.setVisible(self.sensor_num < 0)


class DepthResponseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = DepthResponseGraphWidget(dict(), self)

        self.graph_settings_dialog = DepthGraphSettingsDialog(self)
        self.settings_menu_action_btn = self.tools_menu_btn.addAction('Настройки графика')
        self.settings_menu_action_btn.triggered.connect(self.graph_settings_dialog.run)

        self.step_nums_list = list()
        self.slider = QSlider(Qt.Horizontal, self)
        self.__slider_init()
        self.__all_widgets_to_layout()
        self.activate(False)

    def __slider_init(self) -> None:
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setMinimumWidth(int(self.borehole_window.main_window.size().width() / 4 * 3))
        self.slider.valueChanged.connect(self.replot_for_new_data)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.menu_bar)
        core_layout.addWidget(self.slider)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    def activate(self, is_active_: bool = True) -> None:
        self.graph_settings_dialog.close()
        super().activate(is_active_)

    @loading()
    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_step_depth_dataframe_dict()
        if len(self.data_frames) < 1:
            return

        self.step_nums_list.clear()
        for step_num in self.data_frames.keys():
            self.step_nums_list.append(step_num)
        self.step_nums_list.sort()
        self.slider.setRange(1, len(self.step_nums_list))
        self.slider.setValue(1)

        self.replot_for_new_data()

    # @loading()
    def replot_for_new_data(self) -> None:
        if len(self.step_nums_list) < 1:
            return
        if self.graph_settings_dialog.sensor_num == -1:
            self.plot_widget.recreate(self.data_frames, sensor_num=-1,
                                      step_num=self.step_nums_list[self.slider.value() - 1],
                                      mean_mode=self.graph_settings_dialog.mean_mode,
                                      is_relative=self.graph_settings_dialog.is_relative)
        else:
            self.plot_widget.recreate(self.data_frames, sensor_num=self.graph_settings_dialog.sensor_num,
                                      step_num=self.step_nums_list[self.slider.value() - 1],
                                      is_relative=self.graph_settings_dialog.is_relative)

    def checkbox_activate(self) -> None:
        pass


# ---------------- WindRose ----------------
class WindRoseGraphWindowWidget(AbstractGraphWindowWidget):
    def __init__(self, borehole_window_: BoreholeMenuWindowWidget):
        super().__init__(borehole_window_)
        self.plot_widget = WindRoseGraphWidget(self)

        self.is_relative = False
        relative_action_btn = self.tools_menu_btn.addAction('Абсолютное значение')
        relative_action_btn.setCheckable(True)
        relative_action_btn.setChecked(True)
        relative_action_btn.triggered.connect(self.change_relative_mode_action)

        self.slider = QSlider(Qt.Horizontal, self)
        self.__slider_init()
        self.__all_widgets_to_layout()
        self.activate(False)

    def __slider_init(self) -> None:
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setMinimumWidth(int(self.borehole_window.main_window.size().width() / 4 * 3))
        self.slider.valueChanged.connect(self.replot_for_new_data)

    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.menu_bar)
        core_layout.addWidget(self.slider)
        core_layout.addWidget(self.plot_widget)
        self.setLayout(core_layout)

    @loading('checkbox_activate')
    def plot_graph_action(self) -> None:
        self.data_frames = self.borehole_window.borehole.get_sensor_dataframe_dict()
        
    def checkbox_activate(self) -> None:
        self.hide_line_dialog.remove_all()
        for section_name in self.data_frames:
            self.hide_line_dialog.add_checkbox(section_name, CheckBoxHideWindRoseFunctor(section_name, self), True)
        if self.slider.value() != 1:
            self.slider.setValue(1)
        else:
            self.replot_for_new_data()

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
    
    def change_relative_mode_action(self, state_: bool) -> None:
        CheckBoxAbsoluteValueWindRoseFunctor(self).action(state_)


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
