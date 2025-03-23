import pty
import os
import threading
from select import select
from queue import Queue, Empty
import typing
import logging


shutdown_event = threading.Event()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())


class TerminalEmulator:
    # Heavily inspired by https://github.com/smstong/pyterm

    SHELL = os.environ.get("SHELL", "/bin/sh")

    def __init__(self):
        self.queue = Queue()
        self.pid, self.parent_fd = pty.fork()
        self.running = True
        if self.pid == 0:
            os.execvp(TerminalEmulator.SHELL, (TerminalEmulator.SHELL,))
        else:
            self.read_thread = threading.Thread(
                target=self._read_from_parent, args=(self.queue,)
            )
            self.read_thread.start()

    def write(self, data: str) -> None:
        encoded_data = data.encode("utf-8")
        os.write(self.parent_fd, encoded_data)

    def read(self) -> typing.Optional[bytes]:
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def read_all(self) -> typing.List[bytes]:
        data = []
        entry = self.read()
        while entry:
            data.append(entry)
            entry = self.read()
        return data

    def _read_from_parent(self, input_queue: Queue):
        while not shutdown_event.is_set():
            readables, _, exceptions = select(
                [self.parent_fd], [], [self.parent_fd], 0.1
            )
            for fd in readables:
                byte = os.read(fd, 1)
                input_queue.put(byte)

            for fd in exceptions:
                print("exception")
                return

    def exit(self):
        LOGGER.info("Terminal Emulator is exiting")
        shutdown_event.set()
        self.read_thread.join(timeout=1.0)


# terminal = TerminalEmulator()
# terminal.write("ls\n")

# while terminal.queue.qsize != 0:
#    print(terminal.queue.get())
