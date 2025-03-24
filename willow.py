import stransi.instruction
from interface.window import Window
from emulator.terminal import TerminalEmulator
from pygame import *
from interface.terminal import TerminalInterface
from interface.actions import *
from emulator.ansi import *
import typing
import stransi


instruction_to_action = {
    stransi.cursor.SetCursor: MoveCursorAction,
    stransi.color.SetColor: SetColorAction,
    stransi.attribute.SetAttribute: SetAttributeAction,
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
                if event.key == K_RETURN:
                    self.terminal.write("\n")
                elif event.key == K_BACKSPACE:
                    self.terminal.write("\b")
                else:
                    self.terminal.write(event.unicode)

    def send_actions_to_interface(self, dt: int, _: typing.List[event.Event]) -> None:
        if self.terminal_output:
            actions = self._convert_bytes_to_actions(self.terminal_output)
            self.terminal_interface.change_history.extend(actions)
            # Clear buffer once written
            self.terminal_output = []

    def _convert_bytes_to_actions(
        self, data: typing.List[bytes]
    ) -> typing.List[InterfaceAction]:
        actions = []

        byte_str = bytes.join(b"", data)
        # print("byte_str", byte_str)
        # print("byte_str", byte_str.decode("unicode_escape"))

        ansi = stransi.Ansi(byte_str.decode("unicode_escape"))
        for instruction in ansi.instructions():
            print("instruction", instruction)
            if type(instruction) is str:
                instructions = [
                    InsertCharacterInstruction(character) for character in instruction
                ]
                actions.extend(
                    [
                        InsertCharacterAction(self.terminal_interface, instruction)
                        for instruction in instructions
                    ]
                )
            else:
                action = instruction_to_action.get(type(instruction))
                if action:
                    actions.append(action(self.terminal_interface, instruction))

        return actions


if __name__ == "__main__":
    willow = Willow()
