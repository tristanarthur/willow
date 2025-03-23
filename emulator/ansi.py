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

    def __init__(self, data: bytes=b""):
        self.data = data
        self._prefix = None
        self.parameters = []
        self.end = None
        self.finished = False

    def parse(self, data: bytes) -> "AnsiEscape":
        self.data += data


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

    def __init__(self, data: bytes=b""):
        super().__init__(data)

    def parse(self, char: bytes) -> typing.Optional[EscapeSequenceNames]:
        self.data += char
        try:
            decoded_char = char.decode("utf-8")
        except UnicodeDecodeError:
            return None
        if decoded_char == ";":
            # is param seperator
            pass
        if decoded_char.isdigit():
            self.parameters.append(decoded_char)
        if decoded_char.isalpha():
            self.name = ControlSequenceIntroducer.CODE_MAPPING.get(decoded_char)
            if self.name:
                self.finished = True

        return None


ESCAPES = [
    b"\x1b",
]

IGNORE_ESCAPES = [
    b"\x08",
    b"\x9c",
    b"\x9e",
    b"\x07",
    b"\x97",
]

ANSI_PREFIX = { 
    ESCAPES[0] + b"[": ControlSequenceIntroducer,
}

def should_start_escape(char: bytes) -> bool:
    return char in ESCAPES

def should_ignore_escape(char: bytes) -> bool:
    return char in IGNORE_ESCAPES


def parse_escape(escape: AnsiEscape, char: bytes) -> AnsiEscape:
    escape.parse(char)
    if escape._prefix is None:
        new_escape_type = ANSI_PREFIX.get(escape.data)
        if new_escape_type:
            return new_escape_type(escape.data)
    return escape
    
    