"""Вкладка «Задание 1»."""
from tkinter import ttk

from .task1 import Task1
from .widgets import group_controls, task_text, worker_panel

TASK_TEXT = (
    "Задание 1. С помощью семафорных примитивов организовать работу параллельных вычислительных потоков. "
    "Первый поток записывает в файл подсчитанные значения функции Y=(ln x)/3 на интервале [1; 15] "
    "с шагом h=1. Второй поток считывает из файла очередное значение и подсчитывает сумму всех "
    "считанных значений в переменной Z."
)


def tab1(notebook):
    task = Task1()
    workers = (task.producer, task.consumer)
    tab = ttk.Frame(notebook, padding=8)
    notebook.add(tab, text="Задание 1")
    task_text(tab, TASK_TEXT, 2)

    buffer_frame = ttk.LabelFrame(tab, text=f"Буфер — файл {task.path.resolve()}", padding=6)
    buffer_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4)
    table = ttk.Treeview(buffer_frame, columns=("line", "x", "y", "status"), show="headings", height=8)
    for column, title, width in (("line", "№ строки", 80), ("x", "x", 60),
                                 ("y", "Y = (ln x)/3", 140), ("status", "Состояние", 160)):
        table.heading(column, text=title)
        table.column(column, width=width, anchor="center")
    table.tag_configure("read", foreground="gray")
    scrollbar = ttk.Scrollbar(buffer_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    buffer_frame.columnconfigure(0, weight=1)
    buffer_frame.rowconfigure(0, weight=1)

    bottom = ttk.Frame(buffer_frame)
    bottom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
    info_label = ttk.Label(bottom, font=("Consolas", 11))
    info_label.pack(side="left")

    def clear_table():
        # очищаем сам буфер (файл), а не только картинку; для этого потоки нужно остановить
        for worker in workers:
            worker.stop()
        for worker in workers:
            worker.join(1)
        task.reset()

    ttk.Button(bottom, text="Очистить таблицу", command=clear_table).pack(side="right")

    state_updaters = [worker_panel(tab, worker, 2, column) for column, worker in enumerate(workers)]
    group_controls(tab, workers, 3, 2)
    for column in range(2):
        tab.columnconfigure(column, weight=1)
    tab.rowconfigure(1, weight=1)

    def refresh():
        values = task.file_values()
        for index, y in enumerate(values):
            already_read = index < task.read_count
            row = (index + 1, task.X_START + index, y, "прочитано" if already_read else "не прочитано")
            row_id = str(index)
            tags = ("read",) if already_read else ()
            if table.exists(row_id):
                table.item(row_id, values=row, tags=tags)
            else:
                table.insert("", "end", iid=row_id, values=row, tags=tags)
                table.see(row_id)
        for row_id in table.get_children()[len(values):]:  # после очистки файл короче таблицы
            table.delete(row_id)
        info_label.config(text=f"в файле {len(values)} знач.   прочитано {task.read_count}/{task.values_total}"
                               f"   Z = {task.z:.6f}")
        for update_state in state_updaters:
            update_state()
        tab.after(100, refresh)

    refresh()
