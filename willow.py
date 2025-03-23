from interface.window import Window
from emulator.terminal import TerminalEmulator
from pygame import *
from interface.terminal import TerminalInterface
from interface.actions import *
from emulator.ansi import *
import typing


escape_to_action = {
    ControlSequenceIntroducerType.CUU: MoveCursorAction.up,
    ControlSequenceIntroducerType.CUD: MoveCursorAction.down,
    ControlSequenceIntroducerType.CUF: MoveCursorAction.forward,
    ControlSequenceIntroducerType.CUB: MoveCursorAction.back,
    ControlSequenceIntroducerType.CNL: MoveCursorAction.next_line,
    ControlSequenceIntroducerType.CPL: MoveCursorAction.previous_line,
    ControlSequenceIntroducerType.CHA: MoveCursorAction.horizontal_absolute,
    ControlSequenceIntroducerType.CUP: MoveCursorAction.to_position,
}


class Willow:
    def __init__(self):
        self.window = Window()
        self.terminal = TerminalEmulator()
        self.terminal_interface = TerminalInterface(
            self.window.screen.get_size(), (80, 24)
        )

        self.register_update()
        self.register_draw()
        self.register_exit()

        self.terminal_output = []

        self.window.run()

    def register_update(self) -> None:
        self.window.on_update.extend(
            [
                self.send_input_to_terminal,
                self.read_terminal_output,
                self.send_actions_to_interface,
                self.terminal_interface.update,
            ]
        )

    def register_draw(self) -> None:
        self.window.on_draw.extend([self.terminal_interface.draw])

    def register_exit(self) -> None:
        self.window.on_exit.append(self.terminal.exit)

    def read_terminal_output(self, dt: int, _: typing.List[event.Event]) -> None:
        self.terminal_output.extend(self.terminal.read_all())

    def send_input_to_terminal(self, _: int, events: typing.List[event.Event]) -> None:
        for event in events:
            if event.type == KEYDOWN:
                self.terminal.write(event.unicode)

    def send_actions_to_interface(self, dt: int, _: typing.List[event.Event]) -> None:
        actions = self._convert_bytes_to_actions(self.terminal_output)
        self.terminal_interface.change_history.extend(actions)
        # Clear buffer once written
        self.terminal_output = []

    def _convert_bytes_to_actions(self, bytes: bytes) -> typing.List[InterfaceAction]:
        actions = []
        current_escape: typing.Optional[AnsiEscape] = None
        for char in bytes:
            if should_ignore_escape(char):
                continue
            if not current_escape and should_start_escape(char):
                current_escape = parse_escape(AnsiEscape(), char)
            elif current_escape:
                current_escape = parse_escape(current_escape, char)
                if current_escape.finished:
                    action_type = escape_to_action.get(current_escape.name)
                    if action_type:
                        actions.append(
                            action_type(self.terminal_interface, current_escape.parameters)
                        )
                    current_escape = None
            else:
                # Handle new lines
                if char == b"\n":
                    actions.append(
                        MoveCursorAction.next_line(self.terminal_interface, (1,))
                    )
                actions.append(InsertCharacterAction(self.terminal_interface, (char,)))
        return actions


if __name__ == "__main__":
    willow = Willow()


# terminal_interface has Action classes
# ansi has EscapeSequence classes
# willow has mapping of EscapeSequence to Action
