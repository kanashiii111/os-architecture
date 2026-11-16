"""Вкладка «Задание 2»."""
import tkinter as tk
from tkinter import ttk

from .task2 import Task2
from .widgets import log_box, show_new_log_messages, worker_panel

WRITING_COLOR = "#f4c7c3"
READING_COLOR = "#c8e6c9"
IDLE_COLOR = "SystemButtonFace"


def tab2(notebook):
    task = Task2()
    tab = ttk.Frame(notebook, padding=8)
    notebook.add(tab, text="Задание 2")

    record_frame = ttk.LabelFrame(
        tab, text="Общие данные (запись из ячеек; писатель заполняет их по одной)", padding=6)
    record_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=4)
    record_cells = [tk.Label(record_frame, width=6, relief="sunken", font=("Consolas", 14))
                    for _ in range(task.RECORD_CELLS)]
    for column, cell in enumerate(record_cells):
        cell.grid(row=0, column=column, padx=3)
    info_label = ttk.Label(record_frame, font=("Consolas", 11))
    info_label.grid(row=1, column=0, columnspan=task.RECORD_CELLS, sticky="w", pady=(6, 0))

    workers = (task.writer, task.reader1, task.reader2)
    state_updaters = [worker_panel(tab, worker, column) for column, worker in enumerate(workers)]
    log_list = log_box(tab, 3)
    for column in range(3):
        tab.columnconfigure(column, weight=1)

    def refresh():
        if task.writing:
            color = WRITING_COLOR
        elif task.active_readers:
            color = READING_COLOR
        else:
            color = IDLE_COLOR
        for cell, value in zip(record_cells, task.record):
            cell.config(text=value, bg=color)
        info_label.config(text=f"пишет: {'да' if task.writing else 'нет'}   читают: {task.active_readers}   "
                               f"писателей ждёт: {task.writers_waiting}   ошибок: {task.errors}")
        for update_state in state_updaters:
            update_state()
        show_new_log_messages(task.log, log_list)
        tab.after(100, refresh)

    refresh()
