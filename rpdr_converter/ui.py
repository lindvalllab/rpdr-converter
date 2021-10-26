import multiprocessing
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from convert_rpdr import convert_rpdr


class UserInterface:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("RPDR converter")

        # Set up interface
        content = ttk.Frame(self.root)
        content.grid(column=0, row=0, sticky='nsew')
        frame = ttk.Frame(content, borderwidth=5, relief="ridge")
        frame.grid(column=0, row=0, columnspan=1, rowspan=1, sticky='nsew')

        button = ttk.Button(content,
                            text="Start",
                            command=self.process_files)
        button.grid(column=0, row=0, sticky='nsew', padx=50, pady=50)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        button.focus()

    def run(self) -> None:
        self.root.mainloop()

    def process_files(self) -> None:
        input_file = filedialog.askopenfilename(
            title='Please select an RPDR input file',
            filetypes=[("Text files", "*.txt")]
        )
        if len(input_file) == 0:
            return
        output_file = filedialog.asksaveasfilename(
            title='Please choose where to save the processed file',
            filetypes=[("Comma-separated files", "*.csv")],
            defaultextension=".csv"
        )
        if len(output_file) == 0:
            return

        errors: multiprocessing.Queue[str] = multiprocessing.Queue()

        thread = multiprocessing.Process(
            target=convert_rpdr,
            args=(input_file, output_file, errors.put)
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

        create_loading_window(self.root, thread, on_finish)
        # convert_rpdr(input_file, output_file)


def create_loading_window(root: tk.Tk,
                          thread: multiprocessing.Process,
                          on_finish: Callable[[], None]) -> None:
    loading_window = tk.Toplevel(root)
    loading_window.attributes('-type', 'dialog')
    loading_window.title('Processing')
    progress = ttk.Progressbar(loading_window, orient='horizontal', mode='indeterminate')
    progress.pack()
    progress.start(10)

    def check_if_running() -> None:
        if thread.is_alive():
            loading_window.after(10, check_if_running)
        else:
            loading_window.destroy()
            on_finish()

    loading_window.after(50, check_if_running)
    loading_window.mainloop()


if __name__ == '__main__':
    ui = UserInterface()
    ui.run()
