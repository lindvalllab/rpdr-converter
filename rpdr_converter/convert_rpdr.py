import csv
import os
from multiprocessing import Queue
from typing import Callable


def convert_rpdr(rpdr_filename: str,
                 out_filename: str,
                 append_error: Callable[[str], None],
                 progress_queue: 'Queue[float]') -> None:
    filesize = os.path.getsize(rpdr_filename)
    ignore_count = 0
    progress = 0.
    with open(rpdr_filename, 'r', newline='') as rpdr_file:
        with open(out_filename, 'w', newline='') as out_file:
            line_length = None
            reader = csv.reader(rpdr_file, delimiter='|')
            writer = csv.writer(out_file, lineterminator=os.linesep)
            ignore_count = 0
            for row in reader:
                progress += len('|'.join(row).encode('utf-8')) / filesize
                if not progress_queue.full():
                    progress_queue.put(progress * 100)
                if line_length is None:
                    line_length = len(row)
                if len(row) != line_length:
                    ignore_count += 1
                else:
                    writer.writerow(row)

            if ignore_count > 0:
                append_error(
                    f'WARNING: Found {ignore_count} badly formatted lines which were skipped.\n'
                    'The output file will be missing data from the original file.'
                )
