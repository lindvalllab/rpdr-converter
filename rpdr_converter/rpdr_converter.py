from typing import Callable

from convert_rpdr import convert_rpdr


def process(input_file: str,
            output_file: str,
            append_error: Callable[[str], None]) -> None:
    try:
        convert_rpdr(input_file, output_file, append_error)
    except Exception as e:
        append_error('An unknown error occurred. The following information may be useful.\n'
                     f'{type(e).__name__}: {e}')
