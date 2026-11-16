"""Вкладка «Задание 1»."""
import tkinter as tk
from tkinter import ttk

from .task1 import Task1
from .widgets import log_box, show_new_log_messages, worker_panel


def tab1(notebook):
    task = Task1()
    tab = ttk.Frame(notebook, padding=8)
    notebook.add(tab, text="Задание 1")

    buffer_frame = ttk.LabelFrame(
        tab, text=f"Буфер — файл {task.path.resolve()} (серым — уже прочитанные)", padding=6)
    buffer_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4)
    # по ячейке на каждую строку файла: 3 ряда по 5, весь файл виден сразу
    file_cells = [tk.Label(buffer_frame, width=16, relief="sunken", font=("Consolas", 11))
                  for _ in range(task.values_total)]
    for index, cell in enumerate(file_cells):
        cell.grid(row=index // 5, column=index % 5, padx=3, pady=2)
    info_label = ttk.Label(buffer_frame, font=("Consolas", 11))
    info_label.grid(row=3, column=0, columnspan=5, sticky="w", pady=(6, 0))

    state_updaters = [worker_panel(tab, task.producer, 0), worker_panel(tab, task.consumer, 1)]
    log_list = log_box(tab, 2)
    for column in range(2):
        tab.columnconfigure(column, weight=1)

    def refresh():
        values = task.file_values()
        for index, cell in enumerate(file_cells):
            if index < len(values):
                x = task.X_START + index
                already_read = index < task.read_count
                cell.config(text=f"x={x}: {values[index]}", fg="gray" if already_read else "black")
            else:
                cell.config(text="—", fg="black")
        next_x = min(task.next_x, task.X_END + 1)
        info_label.config(text=f"следующий x = {next_x}   прочитано {task.read_count}/{task.values_total}"
                               f"   Z = {task.z:.6f}")
        for update_state in state_updaters:
            update_state()
        show_new_log_messages(task.log, log_list)
        tab.after(100, refresh)

    refresh()
