import os
import pathlib
from uuid import uuid4
from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QMessageBox, \
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QLabel, QDialog, QTextEdit, QTabWidget
from PySide6.QtCore import Qt, QUrl, QPoint, QSize, QRect, QRunnable, QThreadPool, Signal, QObject
from PySide6.QtGui import QMovie
import config as cf


class MyWarning(Warning):
    def __init__(self, exception_title_: str, message_: str):
        self.message = message_
        self.exception_title = exception_title_
        super().__init__(self.message)


class MessageSignalHandler(QObject):
    information = Signal(str, str)
    warning = Signal(str, str)
    

class MessageBox:
    def __init__(self) -> None:
        self.signal_handler = MessageSignalHandler()
        self.signal_handler.information.connect(self.wrapper_information_message)
        self.signal_handler.warning.connect(self.wrapper_warning_message)
    
    def information(self, title_: str, message_: str) -> None:
        self.signal_handler.information.emit(title_, message_)
    
    def warning(self, title_: str, message_: str) -> None:
        self.signal_handler.warning.emit(title_, message_)
    
    def wrapper_information_message(self, title_: str, message_: str) -> None:
        QMessageBox.information(None, title_, message_, QMessageBox.Ok)
    
    def wrapper_warning_message(self, title_: str, message_: str) -> None:
        QMessageBox.warning(None, title_, message_, QMessageBox.Ok)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MessageBox, cls).__new__(cls)
        return cls.instance


def get_num_file_by_default(base_name_: str, sensor_amount_: int) -> list:
    if len(base_name_) < 19:
        return [-1, -1]
    measurement_num = -1
    if base_name_[-5].isalpha():
        measurement_num = ord(base_name_[-5].lower()) - ord('a') + 10
    elif base_name_[-5].isdigit():
        measurement_num = int(base_name_[-5])
    else:
        return [-1, -1]
    sensor_num = -1
    if base_name_[8].isalpha() and ord(base_name_[8].lower()) - ord('a') < sensor_amount_:
        sensor_num = ord(base_name_[8].lower()) - ord('a')
    else:
        return [-1, -1]
    return [measurement_num, sensor_num]


class AbstractFunctor:
    def action(self, state_: int) -> None: ...


class MyCheckBox(QCheckBox):
    def __init__(self, text_: str, functor_: AbstractFunctor, checked_: bool = True, parent_: QWidget = None):
        super().__init__(text_, parent_)
        self.functor = functor_

        self.setChecked(checked_)
        self.stateChanged.connect(self.click_checkbox_action)

    def recreate(self, text_: str, functor_: AbstractFunctor, checked_: bool = True) -> None:
        self.functor = functor_
        self.setVisible(True)
        self.setChecked(checked_)
        self.setText(text_)

    def click_checkbox_action(self, state_) -> None:
        self.functor.action(state_)


def empty_name_decorator(name_: str) -> str:
    return name_


def basename_decorator(name_: str) -> str:
    return os.path.basename(name_)


class SimpleAbstractItemWidget:
    def __init__(self, name_: str = None, parent_: QWidget = None, *args, **kwargs): ...
    def __eq__(self, other_) -> bool: ...
    def __set_visible(self, is_show_: bool) -> None: ...
    def recreate(self, name_: str, *args, **kwargs) -> None: ...
    def __all_widgets_to_layout(self) -> None: ...
    def delete_action(self) -> None: ...


class SimpleItemListWidget(QWidget):
    def __init__(self, item_class_, parent_: QWidget = None, **kwargs):
        super().__init__(parent_)
        self.item_class = item_class_
        self.layout_type = QVBoxLayout
        if 'layout_t' in kwargs:
            self.layout_type = kwargs['layout_t']

        self.item_list = []

        self.__layout_init()

    def __layout_init(self) -> None:
        self.setLayout(self.layout_type())

    def length(self) -> int:
        length = 0
        for item in self.item_list:
            if item.name is not None:
                length += 1
        return length

    def add_item(self, name_: str, *args, **kwargs) -> None:
        for item in self.item_list:
            if item.name is not None and item.name == name_:
                return
        for item in self.item_list:
            if item.name is None:
                item.recreate(name_, *args, **kwargs)
                return
        new_item = self.item_class(name_, self, *args, **kwargs)
        self.item_list.append(new_item)
        self.layout().addWidget(new_item)

    def remove_item(self, name_: str) -> None:
        for i in range(len(self.item_list)):
            if self.item_list[i].name is not None and self.item_list[i].name == name_:
                self.item_list[i].delete_action()
                return

    def remove_all(self) -> None:
        for i in range(len(self.item_list)):
            self.item_list[i].delete_action()


def select_path_to_dir(parent_: QWidget = None, **kwargs) -> str:
    if 'dir' in kwargs:
        return QFileDialog.getExistingDirectory(parent_, cf.SELECT_FOLDER_FILE_DIALOG_TITLE, dir=kwargs['dir'])
    return QFileDialog.getExistingDirectory(parent_, cf.SELECT_FOLDER_FILE_DIALOG_TITLE)


class ListWidget(QListWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.id = uuid4()
        self.widget_list = []

    def add_widget(self, widget_) -> None:
        itemN = QListWidgetItem(self)
        itemN.setSizeHint(widget_.sizeHint())
        self.setItemWidget(itemN, widget_)
        self.widget_list.append(widget_)

    def resize_item(self, widget_):
        for i in range(len(self.widget_list)):
            if widget_ == self.widget_list[i]:
                self.item(i).setSizeHint(widget_.sizeHint())
                return

    def remove_item(self, widget_) -> None:
        for i in range(len(self.widget_list)):
            if widget_ == self.widget_list[i]:
                self.takeItem(i)
                self.widget_list.pop(i)
                return

    def remove_all(self) -> None:
        while len(self.widget_list) > 0:
            self.takeItem(0)
            self.widget_list.pop(0)


class AbstractWindowWidget(QWidget):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.id = uuid4()

    def activate(self, is_active_: bool = True) -> None:
        self.setVisible(is_active_)


class AbstractListWidgetItem(QWidget):
    def __init__(self, name_: str = "", parent_list_: ListWidget = None, id_: str = None):
        super().__init__(parent_list_)
        self.id = id_
        if self.id is None:
            self.id = uuid4()
        self.parent_list = parent_list_
        self.name = name_

    def __eq__(self, other_) -> bool:
        return self.id == other_.id

    def __all_widgets_to_layout(self) -> None: ...

    def delete_action(self) -> None:
        self.parent_list.remove_item(self)
        self.name = None
        self.id = None


def select_path_to_files(filter_str_: str, parent_: QWidget = None, **kwargs) -> list:
    file_dialog = QFileDialog(parent_)
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    file_dialog.setNameFilter(filter_str_)
    if 'dir' in kwargs:
        file_dialog.setDirectory(kwargs['dir'])
    if not file_dialog.exec():
        return list()
    return file_dialog.selectedFiles()


def select_path_to_one_file(filter_str_: str, parent_: QWidget = None, **kwargs) -> str:
    if 'dir' in kwargs:
        return QFileDialog.getOpenFileName(parent_, cf.SELECT_FILE_FILE_DIALOG_TITLE, dir=kwargs['dir'], filter=filter_str_)[0]
    return QFileDialog.getOpenFileName(parent_, cf.SELECT_FILE_FILE_DIALOG_TITLE, filter=filter_str_)[0]


def get_last_project_path() -> str:
    is_break = False
    if not os.path.isdir(cf.CACHE_DIR_PATH):
        os.mkdir(cf.CACHE_DIR_PATH)
        is_break = True
    if not os.path.isfile(cf.CACHE_FILE_INFO_PATH):
        file = open(cf.CACHE_FILE_INFO_PATH, 'w', encoding=cf.DEFAULT_ENCODING)
        file.close()
        is_break = True
    if is_break:
        return None
    file = open(cf.CACHE_FILE_INFO_PATH, 'r', encoding=cf.DEFAULT_ENCODING)
    project_path = file.readline().replace('/n', '')
    file.close()
    if len(project_path) < 1 or not os.path.isdir(project_path):
        os.remove(cf.CACHE_FILE_INFO_PATH)
        return None
    return project_path


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


class HelpInfoPageWidget(QWidget):
    def __init__(self, text_: str, parent_: QWidget = None):
        super().__init__(parent_)
        self.setMinimumSize(700, 600)
        self.text_widget = QTextEdit(self)
        self.text_widget.setText(text_)
        self.text_widget.setReadOnly(True)
        self.__all_widgets_to_layout()
    
    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.text_widget)
        self.setLayout(core_layout)


class AbstractToolDialog(QDialog):
    def __init__(self, name_: str, parent_: QWidget = None):
        super().__init__(parent_)
        self.id = uuid4()
        self.name = name_
        self.setWindowTitle(self.name)

    def __all_widgets_to_layout(self) -> None: ...

    def close(self) -> None:
        super().close()

    def cancel_action(self) -> None:
        self.close()

    def run(self) -> None:
        self.show()


class HelpInfoDialog(AbstractToolDialog):
    def __init__(self, parent_: QWidget = None):
        super().__init__(cf.HELP_INFO_DIALOG_TITLE, parent_)
        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(HelpInfoPageWidget(cf.COMMON_HELP_INFO, self), 'Общее')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.BOREHOLE_HELP_INFO, self), 'Настройка скважины')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.OSCILLOSCOPE_HELP_INFO, self), 'Осциллограмма')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.FREQUENCY_HELP_INFO, self), 'Частотная характеристика')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.WINDROSE_HELP_INFO, self), 'Роза ветров')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.AMPLITUDE_HELP_INFO, self), 'Амлитудный')
        self.tab_widget.addTab(HelpInfoPageWidget(cf.DEPTH_HELP_INFO, self), 'Глубинный')
        self.__all_widgets_to_layout()
    
    def __all_widgets_to_layout(self) -> None:
        core_layout = QVBoxLayout()
        core_layout.addWidget(self.tab_widget)
        self.setLayout(core_layout)
