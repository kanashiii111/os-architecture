"""Общие элементы интерфейса: текст задания, панель потока, общее управление."""
import tkinter as tk
from tkinter import ttk


def task_text(parent, text, columns):
    label = ttk.Label(parent, text=text, wraplength=860, justify="left", font=("Segoe UI", 10, "bold"))
    label.grid(row=0, column=0, columnspan=columns, sticky="w", padx=4, pady=(0, 6))


def worker_panel(parent, worker, row, column):
    """Панель потока: состояние, ползунок задержки, «Запуск» / «Пауза» / «Останов».
    Возвращает функцию, которая обновляет надпись состояния."""
    frame = ttk.LabelFrame(parent, text=worker.name, padding=6)
    frame.grid(row=row, column=column, sticky="nsew", padx=4, pady=4)
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
        ttk.Button(buttons, text=text, command=action, width=8).pack(side="left", padx=2)

    def update_state():
        state_label.config(text="Состояние: " + state_text(worker))

    return update_state


def state_text(worker):
    return "пауза" if worker.paused() else worker.state


def group_controls(parent, workers, row, columns):
    """Общее управление всеми потоками вкладки и выход из приложения."""
    frame = ttk.LabelFrame(parent, text="Все потоки", padding=6)
    frame.grid(row=row, column=0, columnspan=columns, sticky="ew", padx=4, pady=4)

    def start_all():
        for worker in workers:
            worker.start()

    def pause_all():
        # если хоть один работает — ставим всех на паузу, иначе снимаем паузу со всех
        running = [worker for worker in workers if worker.alive()]
        pause = not all(worker.paused() for worker in running)
        for worker in running:
            worker.set_paused(pause)

    def stop_all():
        for worker in workers:
            worker.stop()

    for text, action in (("Запустить все", start_all), ("Пауза всех", pause_all), ("Остановить все", stop_all)):
        ttk.Button(frame, text=text, command=action).pack(side="left", padx=2)
    ttk.Button(frame, text="Выход", command=parent.winfo_toplevel().destroy).pack(side="right", padx=2)
