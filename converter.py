import os
import sys
import pathlib
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QVBoxLayout, QPushButton, QWidget, QFormLayout, QLineEdit, QMessageBox
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt


def is_float(s_: str) -> bool:
    try:
        float(s_)
        return True
    except ValueError:
        return False


class FileConverter:
    def __init__(self, filename_: str, sensor_num_: int, crash_deep_: int, measurement_num_: int):
        self.old_filename = filename_
        self.old_basename = os.path.basename(self.old_filename)
        self.new_basename = f'DEFAULT_{self.get_sensor_num(sensor_num_)}_{crash_deep_}mm_{self.get_measurement_num(measurement_num_)}.csv'
        self.new_filename = str(pathlib.Path(self.old_filename).parent / self.new_basename)

    def get_measurement_num(self, measurement_num_: int) -> str:
        return chr(ord('A') + measurement_num_ - 10) if measurement_num_ > 9 else str(measurement_num_)

    def get_sensor_num(self, sensor_num_: int) -> str:
        return chr(ord('A') + sensor_num_)

    def convert(self) -> bool:
        if not pathlib.Path(self.old_filename).is_file():
            return False
        old_file = open(self.old_filename, 'r')
        new_file = open(self.new_filename, 'w')
        if not self.__header_line_convert(old_file, new_file, 'Time Base') or \
                not self.__header_line_convert(old_file, new_file, 'Sampling Rate') or \
                not self.__header_line_convert(old_file, new_file, 'Amplitude') or \
                not self.__header_line_convert(old_file, new_file, 'Amplitude resolution') or \
                not self.__header_line_convert(old_file, new_file, 'Data Uint') or \
                not self.__header_line_convert(old_file, new_file, 'Data points') or \
                not self.__data_convert(old_file, new_file):
            os.remove(self.new_filename)
            return False
        return True

    def __header_line_convert(self, old_file_, new_file_, header_name_: str) -> bool:
        time_base = self.__get_clear_header_line(old_file_.readline(), header_name_)
        if time_base is not None:
            new_file_.write(time_base)
            return True
        return False

    def __get_clear_header_line(self, line_: str, header_name_: str) -> str:
        index = line_.find(header_name_ + ':')
        if index == -1:
            return None
        return f'{header_name_}:{line_[index + len(header_name_ + ":"):]}'

    def __data_convert(self, old_file_, new_file_) -> bool:
        for line in old_file_:
            index = line.find(',')
            new_line = line if index == -1 else line[:index]
            if not is_float(new_line):
                return False
            if new_line[-1] != '\n':
                new_line += '\n'
            new_file_.write(new_line)
        return True


class FileDirector:
    def __init__(self, filename_list_: list, sensor_num_: int, crash_deep_: int, start_measurement_num_: int):
        self.filename_list = filename_list_
        self.sensor_num = sensor_num_
        self.crash_deep = crash_deep_
        self.start_measurement_num = start_measurement_num_

    def convert(self) -> bool:
        measurement_num = self.start_measurement_num
        for filename in self.filename_list:
            if measurement_num > 36:
                return True
            file_converter = FileConverter(filename, self.sensor_num, self.crash_deep, measurement_num)
            if not file_converter.convert():
                return False
            measurement_num += 1
        return True


class MainWindow(QMainWindow):
    def __init__(self, app_: QApplication):
        super().__init__()
        self.app = app_
        self.setWindowTitle('Data Converter')
        self.setCentralWidget(MenuWidget(self))


class MenuWidget(QWidget):
    def __init__(self, main_window_):
        super().__init__(main_window_)
        self.main_window = main_window_
        self.sensor_num = 0
        self.crash_deep = 0
        self.start_measurement_num = 0

        self.sensor_editor = QLineEdit(self)
        self.crash_deep_editor = QLineEdit(self)
        self.measurement_editor = QLineEdit(self)
        self.__editor_init()
        self.__values_to_editors()

        self.files_button = QPushButton('Выбрать Файлы', self)
        self.exit_button = QPushButton('Выход', self)
        self.__button_init()

        self.__all_widgets_to_layout()

    def __editor_init(self) -> None:
        self.sensor_editor.setAlignment(Qt.AlignRight)
        self.sensor_editor.textChanged.connect(self.sensor_num_edit_action)

        self.crash_deep_editor.setAlignment(Qt.AlignRight)
        self.crash_deep_editor.setValidator(QIntValidator())
        self.crash_deep_editor.textChanged.connect(self.crash_deep_edit_action)

        self.measurement_editor.setAlignment(Qt.AlignRight)
        self.measurement_editor.setValidator(QIntValidator())
        self.measurement_editor.textChanged.connect(self.measurement_num_edit_action)

    def __values_to_editors(self) -> None:
        self.sensor_num_edit_action(str(self.sensor_num))
        self.crash_deep_editor.setText(str(self.crash_deep))
        self.measurement_editor.setText(str(self.start_measurement_num))

    def __button_init(self) -> None:
        self.files_button.clicked.connect(self.files_action)
        self.exit_button.clicked.connect(self.exit_action)
        self.exit_button.setShortcut("Shift+Esc")

    def __all_widgets_to_layout(self) -> None:
        flo = QFormLayout()
        flo.addRow('Номер датчика', self.sensor_editor)
        flo.addRow('Глубина трещины', self.crash_deep_editor)
        flo.addRow('Номер первого измерения', self.measurement_editor)

        core_layout = QVBoxLayout()
        core_layout.addLayout(flo)
        core_layout.addWidget(self.files_button)
        core_layout.addWidget(self.exit_button)
        self.setLayout(core_layout)

    def sensor_num_edit_action(self, text_: str) -> None:
        len_text = len(text_)
        if len_text < 1:
            self.sensor_num = 0
            return
        elif len_text > 1 or not (text_.isalpha() or text_.isdigit()) or ord(text_) > ord('H'):
            self.sensor_num = ord('H') - ord('A')
        elif text_.isdigit():
            self.sensor_num = int(float(text_))
        else:
            self.sensor_num = ord(text_) - ord('A')
        self.sensor_editor.setText(chr(ord('A') + self.sensor_num))

    def crash_deep_edit_action(self, text_: str) -> None:
        if text_.find('-') != -1:
            text_ = '0'
            self.crash_deep_editor.setText(text_)
        self.crash_deep = 0 if len(text_) < 1 else int(float(text_))

    def measurement_num_edit_action(self, text_: str) -> None:
        if text_.find('-') != -1:
            text_ = '0'
            self.crash_deep_editor.setText(text_)
        self.start_measurement_num = 0 if len(text_) < 1 else int(float(text_))

    def files_action(self) -> None:
        filename_list, useless_filter = QFileDialog.getOpenFileNames(self, dir=str(pathlib.Path().resolve()), filter="CSV files (*.csv)")
        print(filename_list)
        print(self.sensor_num, self.crash_deep, self.start_measurement_num)

        file_director = FileDirector(filename_list, self.sensor_num, self.crash_deep, self.start_measurement_num)
        if file_director.convert():
            QMessageBox.information(self, "Convert Complete", "Конвертирование успешно завершенно", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Convert Warning", "Ошибка конвертирования", QMessageBox.Ok)

    def exit_action(self) -> None:
        self.main_window.app.exit()


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
