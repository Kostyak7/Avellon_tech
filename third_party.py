import os
from PySide6.QtWidgets import QWidget, QCheckBox, QVBoxLayout


class MyWarning(Warning):
    def __init__(self, exception_title_: str, message_: str):
        self.message = message_
        self.exception_title = exception_title_
        super().__init__(self.message)


class AbstractFormatting:
    def __init__(self, unit_: str = ''):
        self.content = ''
        self.unit = unit_
        self.unit_index = -1

    def unit_separator(self, content_: str) -> None:
        if len(self.unit) == 0:
            self.unit_index = len(content_)
            return
        self.unit_index = content_.find(self.unit)
        if self.unit_index == -1:
            raise MyWarning('', '')

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
    def action(self, state_: int): ...


class MyCheckBox(QCheckBox):
    def __init__(self, text_: str, functor_: AbstractFunctor, checked_: bool = True):
        super().__init__(text_)
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


class AbstractCheckBoxList(QWidget):
    def __init__(self, functor_class_, name_decorator_=empty_name_decorator):
        super().__init__()
        self.check_boxes = []
        self.functor_class = functor_class_
        self.name_decorator = name_decorator_
        self.setLayout(QVBoxLayout())

    def set_data(self, names_list: list, *args, **kwargs) -> None:
        for checkbox in self.check_boxes:
            checkbox.setVisible(False)
        for i in range(len(names_list)):
            if i >= len(self.check_boxes):
                check_box = MyCheckBox(self.name_decorator(names_list[i]),
                                       self.functor_class(names_list[i], *args, **kwargs))
                self.layout().addWidget(check_box)
                self.check_boxes.append(check_box)
            else:
                self.check_boxes[i].recreate(names_list[i], self.functor_class(names_list[i], *args, **kwargs))
