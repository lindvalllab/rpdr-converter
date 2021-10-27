import multiprocessing
from typing import Callable

from convert_rpdr import convert_rpdr
from ui import UserInterface


def process(input_file: str,
            output_file: str,
            append_error: Callable[[str], None],
            progress_queue: 'multiprocessing.Queue[float]') -> None:
    try:
        convert_rpdr(input_file, output_file, append_error, progress_queue)
    except Exception as e:
        append_error('An unknown error occurred. The following information may be useful.\n'
                     f'{type(e).__name__}: {e}')


if __name__ == '__main__':
    # Required for building on Windows
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    multiprocessing.freeze_support()

    ui = UserInterface(process)
    ui.run()
