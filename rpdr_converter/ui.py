import multiprocessing
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

import _version


class UserInterface:
    def __init__(
        self,
        convert: Callable[[str, str, Callable[[str], None], 'multiprocessing.Queue[float]'], None]
    ) -> None:
        self.convert = convert

        self.root = tk.Tk()
        self.root.title('RPDR converter')

        # Set up interface
        content = ttk.Frame(self.root)
        content.grid(column=0, row=0, sticky='nsew')
        frame = ttk.Frame(content, borderwidth=5, relief='ridge')
        frame.grid(column=0, row=0, columnspan=1, rowspan=2, sticky='nsew')

        self.button = ttk.Button(content,
                                 text='Start',
                                 command=self.process_files)
        self.about = ttk.Button(
            content,
            text='About',
            command=lambda: messagebox.showinfo('RPDR Converter',
                                                f'RPDR Converter v{_version.__version__}')
        )
        self.button.grid(column=0, row=0, sticky='nsew', padx=50, pady=(25, 10))
        self.about.grid(column=0, row=1, sticky='nsew', padx=50, pady=(10, 25))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self.button.focus()

    def run(self) -> None:
        self.root.mainloop()

    def process_files(self) -> None:
        input_file = filedialog.askopenfilename(
            title='Please select an RPDR input file',
            filetypes=[("Text files", "*.txt")]
        )
        if len(input_file) == 0:
            return
        directory, filename = os.path.split(input_file)
        output_file = filedialog.asksaveasfilename(
            title='Please choose where to save the processed file',
            filetypes=[("Comma-separated files", "*.csv")],
            initialdir=directory,
            initialfile=filename[:-3] + 'csv',
            defaultextension=".csv"
        )
        if len(output_file) == 0:
            return

        self.button['state'] = tk.DISABLED

        errors: multiprocessing.Queue[str] = multiprocessing.Queue()
        progress: multiprocessing.Queue[float] = multiprocessing.Queue(maxsize=1)

        thread = multiprocessing.Process(
            target=self.convert,
            args=(input_file, output_file, errors.put, progress)
        )
        thread.start()

        def on_finish() -> None:
            if errors.empty():
                messagebox.showinfo('Done!', message='Finished converting!')
            else:
                error_list = []
                while not errors.empty():
                    error_list.append(errors.get())
                messagebox.showwarning('A problem occurred', message='\n\n'.join(error_list))
            self.button['state'] = tk.NORMAL

        create_loading_window(self.root, thread, progress, on_finish)


def create_loading_window(root: tk.Tk,
                          thread: multiprocessing.Process,
                          progress: 'multiprocessing.Queue[float]',
                          on_finish: Callable[[], None]) -> None:
    loading_window = tk.Toplevel(root)
    if sys.platform.startswith('linux'):
        loading_window.attributes('-type', 'dialog')
    elif sys.platform.startswith('windows'):
        loading_window.attributes('-toolwindow', True)
    loading_window.title('Processing')

    progress_var = tk.StringVar(value='0%')

    progress_label = ttk.Label(loading_window, textvariable=progress_var)
    progress_label.pack()
    progress_bar = ttk.Progressbar(loading_window, orient='horizontal')
    progress_bar.pack()

    def check_if_running() -> None:
        if thread.is_alive():
            if not progress.empty():
                pr = progress.get()
                progress_var.set(f'{pr:.2f}%')
                progress_bar['value'] = pr
            loading_window.after(50, check_if_running)
        else:
            loading_window.destroy()
            on_finish()

    loading_window.after(50, check_if_running)
    loading_window.mainloop()
