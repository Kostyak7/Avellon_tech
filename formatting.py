
class AbstractFormatting:
    def __init__(self, unit_list_: list):
        self.unit_list = unit_list_
        self.unit_index = -1

    def unit_separator(self, content_: str) -> str:
        if len(self.unit_list) == 0:
            self.unit_index = len(content_)
            return None
        self.unit_index = -1
        success_find = False
        unit = ''
        for i in range(len(content_)):
            tmp_unit = content_[len(content_) - i: len(content_)]
            for un in self.unit_list:
                # print(len(content_) - i, un.lower(), tmp_unit.lower(), un.lower() == tmp_unit.lower())
                if un.lower() == tmp_unit.lower():
                    success_find = True
                    unit = tmp_unit
                    self.unit_index = len(content_) - i
                    break
        # print(unit, success_find)
        if not success_find:
            raise Warning('')
        return unit

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
        self.unit_index = len(content_)
        return content_[:self.unit_index]
        