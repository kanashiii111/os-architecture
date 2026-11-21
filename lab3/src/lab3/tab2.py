"""Вкладка «Задание 2»: схема как на рис. 13 методички — писатель → общая память → читатели."""
import tkinter as tk
from tkinter import ttk

from .task2 import Task2
from .widgets import PAUSE_COLOR, group_controls, task_text, worker_panel

TASK_TEXT = ("Задание 2. Задачу о писателе и читателе решить с помощью алгоритма Петерсона "
             "(два читателя, приоритет писателя).")

WRITING_COLOR = "#f4c7c3"
READING_COLOR = "#c8e6c9"
WAITING_COLOR = "#fff3c4"
IDLE_COLOR = "white"
ARROW_IDLE = "#9e9e9e"
ARROW_WRITE = "#d32f2f"
ARROW_READ = "#2e7d32"

CANVAS_WIDTH, CANVAS_HEIGHT = 860, 260
MEMORY_LEFT, MEMORY_TOP, MEMORY_RIGHT, MEMORY_BOTTOM = 330, 80, 530, 170


def rounded_box(canvas, left, top, right, bottom, radius=22):
    """Прямоугольник со скруглёнными углами (как «облачка» процессов на рисунке)."""
    points = [left + radius, top, right - radius, top, right, top, right, top + radius,
              right, bottom - radius, right, bottom, right - radius, bottom, left + radius, bottom,
              left, bottom, left, bottom - radius, left, top + radius, left, top]
    return canvas.create_polygon(points, smooth=True, outline="black", width=2, fill=IDLE_COLOR)


def process_box(canvas, center_x, center_y, title):
    """Блок процесса: рамка, название, строка состояния и значок паузы над правым углом."""
    box = rounded_box(canvas, center_x - 110, center_y - 32, center_x + 110, center_y + 32)
    canvas.create_text(center_x, center_y - 10, text=title, font=("Times New Roman", 14))
    state = canvas.create_text(center_x, center_y + 14, font=("Segoe UI", 9))
    pause_badge = canvas.create_text(center_x + 108, center_y - 34, anchor="se", text="⏸ пауза",
                                     fill=PAUSE_COLOR, font=("Segoe UI", 9, "bold"), state="hidden")
    return box, state, pause_badge


def tab2(notebook):
    task = Task2()
    workers = (task.writer, task.reader1, task.reader2)
    tab = ttk.Frame(notebook, padding=8)
    notebook.add(tab, text="Задание 2")
    task_text(tab, TASK_TEXT, 3)

    canvas = tk.Canvas(tab, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", highlightthickness=0)
    canvas.grid(row=1, column=0, columnspan=3, padx=4)

    writer_items = process_box(canvas, 130, 125, "Процесс-писатель")
    reader1_items = process_box(canvas, 730, 55, "Процесс-читатель 1")
    reader2_items = process_box(canvas, 730, 195, "Процесс-читатель 2")

    canvas.create_text((MEMORY_LEFT + MEMORY_RIGHT) / 2, MEMORY_TOP - 22, text="Общая область памяти",
                       font=("Times New Roman", 14, "bold"))
    memory_box = canvas.create_rectangle(MEMORY_LEFT, MEMORY_TOP, MEMORY_RIGHT, MEMORY_BOTTOM, width=2)
    cell_width = (MEMORY_RIGHT - MEMORY_LEFT - 20) / task.RECORD_CELLS
    memory_cells = []
    for index in range(task.RECORD_CELLS):
        left = MEMORY_LEFT + 10 + index * cell_width
        canvas.create_rectangle(left + 2, MEMORY_TOP + 25, left + cell_width - 2, MEMORY_BOTTOM - 25)
        memory_cells.append(canvas.create_text(left + cell_width / 2, (MEMORY_TOP + MEMORY_BOTTOM) / 2,
                                               font=("Consolas", 13)))

    arrow_style = {"arrow": "last", "arrowshape": (14, 16, 6)}
    writer_arrow = canvas.create_line(240, 125, MEMORY_LEFT - 4, 125, **arrow_style)
    reader1_arrow = canvas.create_line(MEMORY_RIGHT + 4, 105, 618, 65, **arrow_style)
    reader2_arrow = canvas.create_line(MEMORY_RIGHT + 4, 145, 618, 185, **arrow_style)
    info_text = canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT - 12, font=("Consolas", 10))

    state_updaters = [worker_panel(tab, worker, 2, column) for column, worker in enumerate(workers)]
    group_controls(tab, workers, 3, 3)
    for column in range(3):
        tab.columnconfigure(column, weight=1)

    def show_process(worker, items, arrow, active_state, active_color, arrow_color):
        box, state, pause_badge = items
        if worker.state == active_state:
            fill = active_color
        elif worker.state == "ждёт доступа":
            fill = WAITING_COLOR
        else:
            fill = IDLE_COLOR
        is_active = worker.state == active_state
        paused = worker.paused()
        # на паузе цвет и состояние остаются (поток замер там, где был), рамка — пунктир + значок
        canvas.itemconfig(box, fill=fill, dash=(6, 4) if paused else (), outline=PAUSE_COLOR if paused else "black")
        canvas.itemconfig(state, text=worker.state)
        canvas.itemconfig(pause_badge, state="normal" if paused else "hidden")
        canvas.itemconfig(arrow, fill=arrow_color if is_active else ARROW_IDLE, width=4 if is_active else 2)

    def refresh():
        show_process(task.writer, writer_items, writer_arrow, "пишет", WRITING_COLOR, ARROW_WRITE)
        show_process(task.reader1, reader1_items, reader1_arrow, "читает", READING_COLOR, ARROW_READ)
        show_process(task.reader2, reader2_items, reader2_arrow, "читает", READING_COLOR, ARROW_READ)
        if task.writing:
            memory_color = WRITING_COLOR
        elif task.active_readers:
            memory_color = READING_COLOR
        else:
            memory_color = IDLE_COLOR
        canvas.itemconfig(memory_box, fill=memory_color)
        for cell, value in zip(memory_cells, task.record):
            canvas.itemconfig(cell, text=value)
        canvas.itemconfig(info_text, text=f"читают: {task.active_readers}   писателей ждёт: ")
                                          # f"{task.writers_waiting}   ошибок чтения: {task.errors}")
        for update_state in state_updaters:
            update_state()
        tab.after(100, refresh)

    refresh()
