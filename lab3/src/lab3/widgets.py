"""Общие элементы интерфейса: панель потока и лог."""
import tkinter as tk
from tkinter import ttk

LOG_MAX_LINES = 1000  # при задержке 0 мс потоки пишут ~100 тыс. сообщений/с — показываем только хвост


def worker_panel(parent, worker, column):
    """Панель потока: состояние, ползунок задержки, «Запуск» / «Пауза» / «Останов».
    Возвращает функцию, которая обновляет надпись состояния."""
    frame = ttk.LabelFrame(parent, text=worker.name, padding=6)
    frame.grid(row=1, column=column, sticky="nsew", padx=4, pady=4)
    state_label = ttk.Label(frame, width=24)
    state_label.pack(anchor="w")

    ttk.Label(frame, text="Задержка, мс:").pack(anchor="w")
    delay_slider = tk.Scale(frame, from_=0, to=3000, resolution=50, orient="horizontal", length=200,
                            command=lambda ms: setattr(worker, "delay_seconds", int(ms) / 1000))
    delay_slider.set(int(worker.delay_seconds * 1000))
    delay_slider.pack(fill="x")

    buttons = ttk.Frame(frame)
    buttons.pack(pady=(4, 0))
    for text, action in (("Запуск", worker.start), ("Пауза", worker.pause), ("Останов", worker.stop)):
        ttk.Button(buttons, text=text, command=action).pack(side="left", padx=2)

    def update_state():
        state_label.config(text="Состояние: " + ("пауза" if worker.paused() else worker.state))

    return update_state


class LogList(tk.Listbox):
    """Список сообщений лога, который помнит, сколько их пришло за всё время (для нумерации)."""

    def __init__(self, parent):
        super().__init__(parent, height=12)
        self.total_messages = 0


def log_box(parent, columns):
    log_list = LogList(parent)
    log_list.grid(row=2, column=0, columnspan=columns, sticky="nsew", padx=4, pady=4)
    parent.rowconfigure(2, weight=1)
    return log_list


def show_new_log_messages(messages_queue, log_list: LogList):
    """Переносит новые сообщения из очереди потоков в лог, с номерами."""
    new_count = messages_queue.qsize()  # только то, что уже есть, иначе при быстрых потоках цикл не кончится
    new_messages = [messages_queue.get() for _ in range(new_count)]
    shown_messages = new_messages[-LOG_MAX_LINES:]
    first_number = log_list.total_messages + new_count - len(shown_messages) + 1
    log_list.total_messages += new_count

    for number, message in enumerate(shown_messages, start=first_number):
        log_list.insert("end", f"{number}. {message}")
    if log_list.size() > LOG_MAX_LINES:
        log_list.delete(0, log_list.size() - LOG_MAX_LINES - 1)
    if new_count:
        log_list.see("end")
