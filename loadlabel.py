import sys
import time
import functools
from PySide6.QtWidgets import QWidget, QLabel, QMenuBar
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize, QObject, QThread, Signal
from third_party import MyWarning, MessageBox
import config as cf


class LoadLabel(QLabel):
    def __init__(self, parent_: QWidget = None):
        super().__init__(parent_)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setScaledContents(True)
        self.setMaximumWidth(200)
        
        self.movie = QMovie(cf.LOAD_LABEL_PATH)
        self.setMovie(self.movie)
    
    def __set_actual_size(self, image_size_: QSize):
        actual_size = QSize(200, 0)
        actual_size.setHeight(image_size_.height() * actual_size.width() // image_size_.width())
        self.setFixedSize(actual_size)
    
    def run(self) -> None:
        self.movie.start()
        self.__set_actual_size(self.movie.currentImage().size())
        self.show()
    
    def stop(self) -> None:
        self.movie.stop()
        self.close()
        
class LoadWorker(QObject):
    exception_signal = Signal(str, str)
    complete = Signal(list)
    def run(self, func_: classmethod, args: tuple, kwargs: dict) -> None:
        print("Start Work in other Thread")
        try:
            result = func_(*args, **kwargs)
            self.complete.emit([result])
        except MyWarning as mw:
            self.exception_signal.emit(mw.exception_title, mw.message)
        except BaseException:
            self.exception_signal.emit(cf.UNKNOWN_WARNING_TITLE, cf.UNKNOWN_WARNING_MESSAGE)
        
        
class LoadDirector(QObject):
    work_inition = Signal(classmethod, tuple, dict)


class LoadThread:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_busy = False
        self.worker = LoadWorker()
        self.director = LoadDirector()
        self.load_label = LoadLabel()
        self.work_thread = QThread()

        self.worker.exception_signal.connect(self.exception)
        self.worker.complete.connect(self.complete_work)
        self.director.work_inition.connect(self.worker.run)
        self.worker.moveToThread(self.work_thread)
        
        self.after_func = None
        self.is_result_to_after = False
        self.after_args = tuple()
        self.after_kwargs = dict()

    def start_worker(self, func_, *args, **kwargs) -> bool:
        if self.is_busy:
            return False
        self.is_busy = True
        self.work_thread.start()
        self.load_label.run()
        self.director.work_inition.emit(func_, args, kwargs)        
        return True
    
    def after_work(self, other_, after_func_: str, is_result_to_after_: bool = False, *args, **kwargs) -> None:
        self.after_func = None if after_func_ is None else getattr(other_, after_func_)
        self.is_result_to_after = is_result_to_after_
        self.after_args = args
        self.after_kwargs = kwargs

    def exception(self, title_: str, message_: str) -> None:
        MessageBox().warning(title_, message_)
        self.is_busy = False
        self.load_label.stop()
        self.work_thread.terminate()
    
    def complete_work(self, list_result_: list) -> None:
        work_result = list_result_[0]
        self.is_busy = False
        self.load_label.stop()
        self.work_thread.terminate()
        if self.after_func is not None:
            if self.is_result_to_after:
                self.after_func(work_result, *self.after_args, **self.after_kwargs)
            else:
                self.after_func(*self.after_args, **self.after_kwargs)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(LoadThread, cls).__new__(cls)
        return cls.instance
    

def loading(after_func_: str = None, is_result_to_it_: bool = False, *after_args, **after_kwargs):
    def loading_decorator(func_):
        @functools.wraps(func_)
        def wrapper(self, *args, **kwargs):
            threads = LoadThread()
            threads.after_work(self, after_func_, is_result_to_it_, *after_args, **after_kwargs)
            threads.start_worker(func_, self, *args, **kwargs)
        return wrapper
    return loading_decorator