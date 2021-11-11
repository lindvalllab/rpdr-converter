import filecmp
import math
import os
from multiprocessing import Queue

import pytest
from convert_rpdr import convert_rpdr


@pytest.mark.parametrize('file_path', [
    'files/sample_Prc',
    'files/sample_Vis',
    'files/bad_Prc',
    'files/bad_Vis'
])
def test_convert_rpdr_no_report(file_path: str) -> None:
    file_prefix = os.path.join(
        os.path.dirname(__file__),
        file_path
    )
    in_file = file_prefix + '.txt'
    expected_out = file_prefix + '.csv'
    test_out = file_prefix + '_test_output.csv'
    errors = []
    progress_queue: 'Queue[float]' = Queue()
    convert_rpdr(in_file, test_out, lambda x: errors.append(x), progress_queue)

    assert filecmp.cmp(expected_out, test_out)

    # The last reported progress value should be 100%
    last_progress = 0.
    while not progress_queue.empty():
        last_progress = progress_queue.get()

    assert math.isclose(last_progress, 100.0)
    print(last_progress)


def test_progress() -> None:
    file_prefix = os.path.join(
        os.path.dirname(__file__),
        'files/progress'
    )
    in_file = file_prefix + '.txt'
    test_out = file_prefix + '_test_output.csv'

    errors = []
    progress_queue: 'Queue[float]' = Queue(maxsize=5)
    convert_rpdr(in_file, test_out, lambda x: errors.append(x), progress_queue)

    # The input file has four lines, each 12 bytes long.
    assert progress_queue.get() == 25.0
    assert progress_queue.get() == 50.0
    assert progress_queue.get() == 75.0
    assert progress_queue.get() == 100.0
    assert progress_queue.empty()
