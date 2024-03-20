from PySide6.QtCore import QSize, QPoint
from formatting import IntFormatting, FloatFormatting, StrFormatting


# Window titles
MAIN_WINDOW_TITLE = "Avellon tech"
CREATE_PROJECT_DIALOG_TITLE = "Create project"
HIDING_LINES_DIALOG_TITLE = "Hiding lines"
BOREHOLE_SETTINGS_DIALOG_TITLE = "Borehole settings"
CRACK_SETTINGS_DIALOG_TITLE = "Cracks Settings"
FILTER_SETTINGS_DIALOG_TITLE = "Filter Settings"
GRAPH_SETTINGS_DIALOG_TITLE = 'Graph settings'
HELP_INFO_DIALOG_TITLE = 'Help information'
SELECT_FOLDER_FILE_DIALOG_TITLE = "Select folder"
SELECT_FILE_FILE_DIALOG_TITLE = "Select file"
DATA_CONVERTER_DIALOG_TITLE = 'Data Converter'


# Folder names and project files names
DEFAULT_PROJECT_NAME = "Avellon_Project"
DEFAULT_PROJECT_INFO_FILENAME = 'info.txt'
BOREHOLE_INFO_SAVE_FILENAME = "info.txt"
DEFAULT_PROJECT_FOLDER = 'projects'
CACHE_DIR_PATH = '__avellon_cache__'
CACHE_FILE_INFO_PATH = CACHE_DIR_PATH + '/' + DEFAULT_PROJECT_INFO_FILENAME
DEFAULT_FOLDER_NAME_FOR_SELECT = "data"
DEFAULT_FOLDER_NAME_TO_SAVE = "save_data"
DEFAULT_FORMAT_OF_FILENAME = "%Y_%m_%d_%H_%M_%S"
EXE_FILENAME = 'app.bat'
DEFAULT_SECTION_NAME = 'name_'
DEFAULT_DATA_FOLDER = 'data'
DEFAULT_CONVERTED_DATA_FOLDER = "Converted data"

# Resources
ICON_WINDOW_PATH = "resource/img/favicon.ico"
MAIN_MENU_LOGO_PATH = "resource/img/logo.png"
LOAD_LABEL_PATH = 'resource/img/loading.gif'


# Default sizes
MAIN_WINDOW_MINIMUM_SIZE = QSize(800, 450)
DEFAULT_BUTTON_SIZE = QSize(200, 50)


# Modes
SEQUENCE_NUMBER_SHORTCUT_MODE = "SEQNUM"
NO_SHORTCUT_MODE = "NO"
ENCODING_UTF8 = 'UTF-8'
DEFAULT_ENCODING = ENCODING_UTF8


# Font settings
DEFAULT_BOREHOLE_NAME_FONT_SIZE = 40


# Borehole measurement settings
DEFAULT_SENSOR_AMOUNT = 4
DEFAULT_MEASUREMENT_NUMBER = 21
DEFAULT_SECTION_LENGTH = 8.


# File dialog settings
FILE_DIALOG_FOLDER_FILTER = "FOLDER_FILTER"
FILE_DIALOG_CSV_FILTER = "CSV files (*.csv)"
FILE_DIALOG_SAVE_FILTERS = ["JPG files (*.jpg; *.jpeg)", "PNG files (*.png)",
                            "JPG files (*.jpg; *.jpeg);; PNG files (*.png)"]


# Formats and types
ALLOWED_FILE_LOAD_FORMATS = ['csv']
TYPES_OF_SAVING_FILE = ['png', 'jpg', 'jpeg']


# Pipe crack settings
PIPE_SECTION_SIZE = QSize(600, 150)
SOLID_PIPE_SIZE = QSize(500, 100)
DEFAULT_PIPE_LENGTH_IN_METERS = 1
DASH_PIPE_SIZE = QSize(SOLID_PIPE_SIZE.width(), int(SOLID_PIPE_SIZE.height() / 2))
RELATIVE_DASH_PIPE_POSITION = QPoint(0, int(SOLID_PIPE_SIZE.height() / 4))
SOLID_PIPE_LINE_WIDTH = 3
DASH_PIPE_LINE_WIDTH = 1
CRACK_LINE_FOR_PIPE_WIDTH = 2
CRACK_PIPE_FONT_SIZE = 16
SENSOR_PIPE_FONT_SIZE = 24
UPPER_SIDE = 'upper'
BOTTOM_SIDE = 'bottom'
LEFT_RIGHT_DIRECTION = '->'
RIGHT_LEFT_DIRECTION = '<-'
MAX_CRACK_AMOUNT = 10
PIPE_CRACK_DEPTH_UNIT = "мм"
PIPE_CRACK_POSITION_UNIT = "м"


# CSV file data
CSV_FILE_HEADER_SIZE = 7
TIME_BASE_HEADER = "Time Base"
SAMPLING_RATE_HEADER = "Sampling Rate"
AMPLITUDE_HEADER = 'Amplitude'
AMPLITUDE_RESOLUTION_HEADER = 'Amplitude resolution'
DATA_UINT_HEADER = 'Data Uint'
DATA_POINTS_HEADER = 'Data points'
ZERO_INDEX_HEADER = 'Zero index'
CSV_FILE_HEADER_CONTENT = {
    TIME_BASE_HEADER: FloatFormatting(['Ojs', 'μs', 'ms']),
    SAMPLING_RATE_HEADER: FloatFormatting(['MSa/s']),
    AMPLITUDE_HEADER:  FloatFormatting(['Ojs', 'mV', 'μV', 'V']),
    AMPLITUDE_RESOLUTION_HEADER: FloatFormatting(['Ojs', 'μV', 'mV', 'V']),
    DATA_UINT_HEADER: StrFormatting([]),
    DATA_POINTS_HEADER: IntFormatting([]),
    ZERO_INDEX_HEADER: IntFormatting([]),
}


# Borehole info file
BOREHOLE_NAME_BOREHOLE_INFO = "BOREHOLE_NAME"
START_SECTIONS_TAG_BOREHOLE_INFO = '#START SECTIONS\n'
START_SECTION_TAG_BOREHOLE_INFO = '#START SECTION\n'
END_SECTIONS_TAG_BOREHOLE_INFO = '#END SECTIONS\n'
END_SECTION_TAG_BOREHOLE_INFO = '#END SECTION\n'
SECTION_NAME_BOREHOLE_INFO = 'SECTION_NAME'
SECTION_DEPTH_BOREHOLE_INFO = 'SECTION_DEPTH'
SECTION_LENGTH_BOREHOLE_INFO = 'SECTION_LENGTH'
def BOREHOLE_NAME_BOREHOLE_INFO_F(name_: str) -> str:
    return f"{BOREHOLE_NAME_BOREHOLE_INFO}:{name_}\n"
def SECTION_NAME_BOREHOLE_INFO_F(name_: str) -> str:
    return f"{SECTION_NAME_BOREHOLE_INFO}:{name_}\n"
def SECTION_DEPTH_BOREHOLE_INFO_F(depth_: int) -> str:
    return f"{SECTION_DEPTH_BOREHOLE_INFO}:{depth_}\n"
def SECTION_LENGTH_BOREHOLE_INFO_F(length_: float) -> str:
    return f"{SECTION_LENGTH_BOREHOLE_INFO}:{length_}\n"


# WARNING TITLES
FILE_NOT_EXIST_WARNING_TITLE = "File not exist"
WRONG_TYPE_WARNING_TITLE = "Wrong type"
WRONG_FILENAME_WARNING_TITLE = "Wrong filename"
INCORRECT_FILE_CONTENT_WARNING_TITLE = "Incorrect file content"
NOT_EMPTY_FOLDER_WARNING_TITLE = "Not empty folder"
NOT_DIR_WARNING_TITTLE = 'Not a dir'
EMPTY_NAME_WARNING_TITTLE = 'Empty name'
INVALID_NAME_WARNING_TITTLE = 'Invalid name'
UNKNOWN_WARNING_TITLE = "Unknown warning"
CONVERT_WARNING_TITLE = "Convert Warning"


# WARNING MESSAGE
UNKNOWN_WARNING_MESSAGE = "Неизвестная ошибка при чтении файла."
NOT_DIR_WARNING_MESSAGE = "Выбранный объект не является папкой!"
NOT_EMPTY_FOLDER_WARNING_MESSAGE ="Выбранная папка содержит файлы!\nВыберете пустую или не существующую папку."
EMPTY_PROJECT_NAME_WARNING_MESSAGE = "Название проекта не может быть пустым."
INVALID_PROJECT_NAME_WARNING_MESSAGE = "Не корректное имя проекта."
WRONG_FILENAME_WARNING_MESSAGE = "Файл имеет не соответстующее требованиям название."
CONVERT_WARNING_MESSAGE = "Ошибка конвертирования!"
FILE_NOT_EXIST_WARNING_MESSAGE = "Файл не существует или не является файлом!"
def NOT_DIR_WARNING_MESSAGE_F(path_: str = "") -> str:
    return f"{path_} - не является папкой!"
def NOT_EMPTY_FOLDER_WARNING_MESSAGE_F(path_: str = "") -> str:
    return f"Выбранная папка: - {path_} - содержит файлы!\nВыберете пустую или не существующую папку."
def WRONG_FILENAME_WARNING_MESSAGE_F(name_: str = "") -> str:
    return f"{name_} - имеет не соответстующее требованиям название!"
def FILE_NOT_EXIST_WARNING_MESSAGE_F(filename_: str = "") -> str:
    return f"{filename_} - не существует или не является файлом!"
def INCORRECT_FILE_HEADER_WARNING_MESSAGE_F(filename_: str = "") -> str:
    return f"Выбранный файл: - {filename_} - имеет неправильное наполнение в заголовке!"


def IS_FLOAT(s_: str) -> bool:
    try:
        float(s_)
        return True
    except ValueError:
        return False


# INFORMATION TITLES
CONVERT_COMPLETE_INFO_TITLE = "Convert Complete"


# INFORMATION MESSAGES
CONVERT_COMPLETE_INFO_MESSAGE = "Конвертирование успешно завершенно."


# Colors
COLOR_NAMES = ['red', 'blue', 'green', 'orange', 'burlywood',
               'darkcyan', 'darkgoldenrod', 'pink',
               'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
               'darksalmon', 'darkseagreen', 'darkslateblue', 'darkturquoise', 'darkviolet',
               'deeppink', 'deepskyblue', 'dodgerblue', 'firebrick', 'forestgreen', 'fuchsia',
               'gold', 'honeydew', 'indianred', 'lavender', 'lavenderblush', 'pink',
               'lawngreen', 'lemonchiffon', 'lightgoldenrodyellow', 'lightgreen',
               'lightsteelblue', 'lime', 'limegreen', 'magenta', 'maroon', 'mediumvioletred',
               'midnightblue', 'olive', 'orchid', 'palegoldenrod', 'plum',
               'purple', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen',
               'skyblue', 'slateblue', 'springgreen', 'steelblue', 'thistle', 'violet', 'black']


# Help info text
COMMON_HELP_INFO = '''
<p>Чтобы построить любой график необходимо загруить файлы и в окне желаемого графика нажать `▷ Построить`. </p>

<p>Каждый построенный график можно сохранить. Быстро с помощью пункта `Сохранить` в панеле сверху или сочетания клавиш `Ctrl+S`. 
Тогда файл автоматически сохраниться в папку `save_data` в дириктории проекта проекте.
Более детальное сохранение доступно при нажатии `Сохранить как` - `Ctrl+Shift+S`, тогда откроется диалоговое окно 
и появиться возможность выбрать место и имя сохраняемого файла.
В окне любого графика можно поднастроить скважину для всего проекта. Это делается через верхнюю панель `Скважина->Настроить скважину`.
Для получения справочной информации необходимо нажать на `Справка` на верхней панеле.
При нажатии кнопки `Назад` на верхней панеле пользователь вернется в главное меню.
У каждого графика можно убирать отдельные лини с помощью списка галочек.</p>
'''

BOREHOLE_HELP_INFO = '''
<p>Настройка скважины есть единое окружение для постройки любого графика.
Для постройки некоторых из них необходимо определенное количество исходных файлов с данными. </p>


<p> При открытии экрана настройки скважины изначально будут доступны 3 кнопки: </p>
<ul> 
<li> `+ Добавить секцию` - при нажатии которой в списке появляется секция с возможностью ее дальнейшего редактирования. </li>
<li>`Принять` - все внесенные изменения в настройку секции вступят в силу </li>
<li>`Отмена` -  все внесенные изменения в настройку секции отменяться, скважина вернется в настройку до открытия окна настройки скважины </li>
</ul>

<p> В соответсутвующий полях секции можно настроить `Имя` секции, `Глубину` ее месторасположения, `Длину`.
С помощью кнопок `+`, `▽`, `Х` можно добавить новый шаг в секцию,
открыть/закрыть список уже существующих шагов, полностью удалить секцию соответсвенно. У каждой секции должно быть свое уникальное имя 
(Написать два одинаковых программа ва не позволит)
Аналогично у шага можно редактировать его номер, добавлять файлы с данными, открывать/закрывать список добавленных файлов,
удалять шаг. Номер уникален для каждого шага. Добавленные файлы должны иметь разное базвое название по формату `DEFAULT_A_0mm_0.csv`,
В противном случае в проекте останется только последний добавленный файл с повторяющимся именем.
Файлы также можно удалять с помощь кнопки `Х`. 
Пока что изменение имени или номера шага соответсвенно для Секции или Шага сотрет все что есть внутри них.
Галочки у каждого раздела означает, необходимо ли учитывать файл в построении осциллограммы.</p>
'''

OSCILLOSCOPE_HELP_INFO = '''
<h2> Смысл графика </h2>
<p> Что-то ... </p>
<h2> Построение </h2>
<p>Если в скважину добавлены файлы, то с помощью кнопки в верхней панеле
можно построить осциллограмму выбранных файлов (поставлена голчка напротив).</p>
'''

FREQUENCY_HELP_INFO = '''
<h2> Смысл графика </h2>
<p> Что-то ... </p>

<h2> Построение </h2>
<p>Для построения частотной характеристики для одного датчика необходим 21 файл с данными в одном шаге.</p>

<h2> Визуализация участка </h2>
<p> Также в окне доступна возможность настройки визуализации участка скважины с трещинами.
Настройка производиться в окне называемом кнопкой `Задать параметры трубы`. 
В данном окне есть возможность настроить в соответствующих полях `Длину`, `Диаметр внутренности`, `Толщину стенок`,
`Направление прозвучки`, `Имена датчиков`. А также добавить трещены - `+ Добавить`. `Принять` - все внесенные изменения в настройку секции вступят в силу.
`Отмена` -  все внесенные изменения в настройку секция отменяться, все вернется в настройку до открытия окна.
У каждой трещины можно настроить `Cторону` ее расположения - Верхняя/Нижняя, `Глубину` трещены, `Позицию` на трубе.</p>
'''

WINDROSE_HELP_INFO = '''
<h2> Смысл графика </h2>
<p> Что-то ... </p>
<h2> Построение </h2>
<p>Круговая диаграмма строиться по датчикам секции по номерам измерений для абсолютных значений или для относительных.
Чтобы выбрать способ отображение есть галочка `Абсолютное значение`.
С помощью слайдера можно выбирать номер измерения для отображения соответствующей диаграммы.</p>
'''

AMPLITUDE_HELP_INFO = '''
<h2> Смысл графика </h2>
<p> Что-то ... </p>
<h2> Построение </h2>
<p>График можно построить для каждого датчика секции по отдельности, он строиться по имеющимся шагам.
То есть для построения необходимо иметь минимум два шага для датчика, заполненные файлами.</p>
'''

DEPTH_HELP_INFO = '''
<h2> Смысл графика </h2>
<p> Что-то ... </p>
<h2> Построение </h2>
<p> Что-то ... </p>
'''


'''
"All Files (*.*)|*.*" +
        "|All Pictures (*.emf;*.wmf;*.jpg;*.jpeg;*.jfif;*.jpe;*.png;*.bmp;*.dib;*.rle;*.gif;*.emz;*.wmz;*.tif;*.tiff;*.svg;*.ico)" +
            "|*.emf;*.wmf;*.jpg;*.jpeg;*.jfif;*.jpe;*.png;*.bmp;*.dib;*.rle;*.gif;*.emz;*.wmz;*.tif;*.tiff;*.svg;*.ico" +
        "|Windows Enhanced Metafile (*.emf)|*.emf" +
        "|Windows Metafile (*.wmf)|*.wmf" +
        "|JPEG File Interchange Format (*.jpg;*.jpeg;*.jfif;*.jpe)|*.jpg;*.jpeg;*.jfif;*.jpe" +
        "|Portable Network Graphics (*.png)|*.png" +
        "|Bitmap Image File (*.bmp;*.dib;*.rle)|*.bmp;*.dib;*.rle" +
        "|Compressed Windows Enhanced Metafile (*.emz)|*.emz" +
        "|Compressed Windows MetaFile (*.wmz)|*.wmz" +
        "|Tag Image File Format (*.tif;*.tiff)|*.tif;*.tiff" +
        "|Scalable Vector Graphics (*.svg)|*.svg" +
        "|Icon (*.ico)|*.ico";
'''