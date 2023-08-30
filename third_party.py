import os
import pathlib
from uuid import uuid4
from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout, QHBoxLayout, QLineEdit, \
    QPushButton, QFileDialog, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, QUrl, QPoint, QSize, QRect


class MyWarning(Warning):
    def __init__(self, exception_title_: str, message_: str):
        self.message = message_
        self.exception_title = exception_title_
        super().__init__(self.message)


class AbstractFormatting:
    def __init__(self, unit_list_: list):
        self.content = ''
        # self.unit = None
        self.unit_list = unit_list_
        self.unit_index = -1

    def unit_separator(self, content_: str) -> str:
        if len(self.unit_list) == 0:
            self.unit_index = len(content_)
            return None
        self.unit_index = -1
        for unit in self.unit_list:
            if len(unit) == 0:
                self.unit_index = len(content_)
                return None
            self.unit_index = content_.find(unit)
            if self.unit_index != -1:
                return unit
        if self.unit_index == -1:
            raise MyWarning('', '')
        return None

    def get(self, content_: str): ...


class IntFormatting(AbstractFormatting):
    def get(self, content_: str) -> int:
        self.unit_separator(content_)
        return int(content_[:self.unit_index])


class FloatFormatting(AbstractFormatting):
    def get(self, content_: str) -> float:
        self.unit_separator(content_)
        return float(content_[:self.unit_index])


class StrFormatting(AbstractFormatting):
    def get(self, content_: str) -> str:
        self.unit_separator(content_)
        return str(content_[:self.unit_index])


def get_num_file_by_default(base_name_: str, sensor_amount_: int) -> list:
    measurement_num = -1
    if base_name_[-5].isalpha():
        measurement_num = ord(base_name_[-5].lower()) - ord('a') + 10
    elif base_name_[-5].isdigit():
        measurement_num = int(base_name_[-5])
    else:
        return [-1, -1]
    sensor_num = -1
    if base_name_[-11].isalpha() and ord(base_name_[-11].lower()) - ord('a') < sensor_amount_:
        sensor_num = ord(base_name_[-11].lower()) - ord('a')
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
        return QFileDialog.getExistingDirectory(parent_, 'Select Folder', dir=kwargs['dir'])
    return QFileDialog.getExistingDirectory(parent_, 'Select Folder')


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
        return QFileDialog.getOpenFileName(parent_, 'Select File', dir=kwargs['dir'], filter=filter_str_)[0]
    return QFileDialog.getOpenFileName(parent_, 'Select File', filter=filter_str_)[0]
