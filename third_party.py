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
