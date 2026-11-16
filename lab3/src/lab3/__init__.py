import tkinter as tk
from tkinter import ttk

from .tab1 import tab1
from .tab2 import tab2


def main() -> None:
    root = tk.Tk()
    root.title("Лабораторная 3 — синхронизация потоков (вариант 34)")
    root.geometry("820x560")
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)
    tab1(notebook)
    tab2(notebook)
    root.mainloop()
