
class AbstractFormatting:
    def __init__(self, unit_list_: list):
        self.content = ''
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
            raise Warning('')
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
        