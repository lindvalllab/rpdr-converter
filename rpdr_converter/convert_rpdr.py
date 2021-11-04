import csv
import os
from multiprocessing import Queue
from typing import Callable, Iterator, List, Optional, Tuple


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
            reader = csv.reader(rpdr_file, delimiter='|', quoting=csv.QUOTE_NONE)
            writer = csv.writer(out_file, lineterminator=os.linesep)
            ignore_count = 0
            for row in reader:
                progress += len('|'.join(row).encode('utf-8')) / filesize
                if not progress_queue.full():
                    progress_queue.put(progress * 100)
                if line_length is None:
                    # Processing header row
                    line_length = len(row)
                    if row[-1] == 'Report_Text':
                        convert_rpdr_with_report_text(
                            rpdr_filename, out_filename, append_error, progress_queue
                        )
                        break
                if len(row) != line_length:
                    ignore_count += 1
                else:
                    writer.writerow(row)

            if ignore_count > 0:
                append_error(
                    f'WARNING: Found {ignore_count} badly formatted lines which were skipped.\n'
                    'The output file will be missing data from the original file.'
                )


def read_line_with_report_text(
    reader: Iterator[List[str]],
    expected_length: int
) -> Tuple[Optional[List[str]], int, int]:
    ignored = 0
    row: List[str] = []
    bytes_processed = 0
    while len(row) != expected_length:
        if len(row) != 0:  # don't worry about empty lines between entries
            ignored += 1
        try:
            row = next(reader)
            bytes_processed += len('|'.join(row).encode('utf-8'))
        except StopIteration:
            return None, ignored, bytes_processed

    if row[-1].endswith('[report_end]'):
        return row, ignored, bytes_processed

    try:
        next_row = next(reader)
        bytes_processed += len('|'.join(next_row).encode('utf-8'))
    except StopIteration:
        return None, ignored, bytes_processed

    # now row contains a full-length row, time to try to read the entire report text
    possibly_ignored = 0
    while not (len(next_row) > 0 and next_row[-1].endswith('[report_end]')):
        row[-1] += '\n'
        row[-1] += '|'.join(next_row)
        possibly_ignored += 1  # If we fail to find a '[report_end]', these lines have been ignored
        try:
            next_row = next(reader)
            bytes_processed += len('|'.join(next_row).encode('utf-8'))
        except StopIteration:
            return None, ignored + possibly_ignored, bytes_processed

    row[-1] += '\n'
    row[-1] += '|'.join(next_row)[:-len('[report_end]')]  # strip [report_end] from text

    row[-1] = row[-1].strip('\n')

    return row, ignored, bytes_processed


def convert_rpdr_with_report_text(rpdr_filename: str,
                                  out_filename: str,
                                  append_error: Callable[[str], None],
                                  progress_queue: 'Queue[float]') -> None:
    filesize = os.path.getsize(rpdr_filename)
    ignore_count = 0
    progress = 0.
    with open(rpdr_filename, 'r', newline='') as rpdr_file:
        with open(out_filename, 'w', newline='') as out_file:
            line_length = None
            reader = csv.reader(rpdr_file, delimiter='|', quoting=csv.QUOTE_NONE)
            writer = csv.writer(out_file, lineterminator=os.linesep)
            ignore_count = 0
            while True:
                if line_length is None:
                    # Processing header row
                    header = next(reader)
                    progress += len('|'.join(header).encode('utf-8')) / filesize
                    line_length = len(header)

                row, ignored, bytes_processed = read_line_with_report_text(reader, line_length)
                ignore_count += ignored

                progress += bytes_processed / filesize
                if not progress_queue.full():
                    progress_queue.put(progress * 100)

                if row is None:
                    # This signals that the file has been completely read
                    break

                writer.writerow(row)

            if ignore_count > 0:
                append_error(
                    f'WARNING: Found {ignore_count} badly formatted lines which were skipped.\n'
                    'The output file will be missing data from the original file.'
                )
