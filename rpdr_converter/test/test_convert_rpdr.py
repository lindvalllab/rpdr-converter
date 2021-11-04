import filecmp
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
    convert_rpdr(in_file, test_out, lambda x: errors.append(x), Queue(maxsize=1))

    print(errors)
    assert filecmp.cmp(expected_out, test_out)
