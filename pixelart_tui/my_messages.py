from textual.events import Message
from textual.widget import Widget


class DebugStatus(Message):
    def __init__(self, sender: Widget, mes: str):
        super().__init__(sender)
        self.mes = mes


class ColorStatus(Message):
    def __init__(self, sender: Widget, color: dict):
        super().__init__(sender)
        self.color = color


class LoadSaveStatus(Message):
    def __init__(self, sender: Widget, loadsave: str):
        super().__init__(sender)
        self.loadsave = loadsave
