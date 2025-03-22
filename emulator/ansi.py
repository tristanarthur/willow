from enum import Enum
import typing


class EscapeSequenceNames(Enum):
    pass


class ControlSequenceIntroducerType(EscapeSequenceNames):
    CUU = "Cursor Up"
    CUD = "Cursor Down"
    CUF = "Cursor Forward"
    CUB = "Cursor Back"
    CNL = "Cursor Next Line"
    CPL = "Cursor Previous Line"
    CHA = "Cursor Horizontal Absolute"
    CUP = "Cursor Position"
    ED = "Erase in Display"
    EL = "Erase in Line"
    SU = "Scroll Up"
    SD = "Scroll Down"
    HVP = "Horizontal Vertical Position"
    SGR = "Select Graphic Rendition"
    DSR = "Device Status Report"


class AnsiEscape:
    def __init__(self):
        self.data = b""
        self.escape_type = None
        self.parameters = []

    def process(self, char: bytes) -> typing.Optional[EscapeSequenceNames]:
        raise NotImplementedError("This method should be overridden by subclasses")


class ControlSequenceIntroducer(AnsiEscape):
    CODE_MAPPING = {
        "A": ControlSequenceIntroducerType.CUU,
        "B": ControlSequenceIntroducerType.CUD,
        "C": ControlSequenceIntroducerType.CUF,
        "D": ControlSequenceIntroducerType.CUB,
        "E": ControlSequenceIntroducerType.CNL,
        "F": ControlSequenceIntroducerType.CPL,
        "G": ControlSequenceIntroducerType.CHA,
        "H": ControlSequenceIntroducerType.CUP,
        "J": ControlSequenceIntroducerType.ED,
    }

    def __init__(self):
        super().__init__()

    def process(self, char: bytes) -> typing.Optional[EscapeSequenceNames]:
        self.data += char
