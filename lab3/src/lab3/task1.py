"""Задание 1: поставщик и потребитель через файл, синхронизация семафорами."""
import math
import threading
from pathlib import Path

from .worker import Worker


def wait_semaphore(semaphore, worker):
    """P(семафор), но ожидание можно прервать остановом потока. False — поток остановили."""
    while not semaphore.acquire(timeout=0.05):
        if worker.stopped():
            return False
    return True


class Task1:
    """Поставщик пишет в файл Y=(ln x)/3, x=1..15; потребитель читает и суммирует в Z."""

    X_START = 1
    X_END = 15

    def __init__(self, path: str | Path = "task1_buffer.txt"):
        self.path = Path(path)
        self.reset()
        self.producer = Worker("Поток 1: считает Y=(ln x)/3 и пишет в файл", self._produce)
        self.consumer = Worker("Поток 2: читает из файла и суммирует в Z", self._consume)

    def reset(self):
        self.path.write_text("", encoding="utf-8")
        self.next_x = self.X_START
        self.read_count = 0  # сколько значений потребитель уже прочитал из файла
        self.z = 0.0  # сумма прочитанных значений
        self.filled_slots = threading.Semaphore(0)  # сколько записанных, но ещё не прочитанных значений
        self.file_access = threading.Semaphore(1)  # мьютекс на файл

    @property
    def values_total(self):
        return self.X_END - self.X_START + 1

    def _read_file_values(self):
        return self.path.read_text(encoding="utf-8").split()

    def file_values(self):
        """Всё содержимое файла-буфера; первые read_count значений уже прочитаны."""
        self.file_access.acquire()
        try:
            return self._read_file_values()
        finally:
            self.file_access.release()

    def _produce(self, worker):
        if self.read_count == self.values_total:  # прошлый прогон закончен — начинаем заново
            self.reset()
        while self.next_x <= self.X_END and not worker.stopped():
            worker.state = "вычисляет"
            y = math.log(self.next_x) / 3
            worker.sleep()

            worker.state = "ждёт доступа к файлу"
            self.file_access.acquire()
            with self.path.open("a", encoding="utf-8") as file:
                file.write(f"{y:.6f}\n")
            self.next_x += 1
            self.file_access.release()
            self.filled_slots.release()

    def _consume(self, worker):
        while self.read_count < self.values_total and not worker.stopped():
            worker.state = "ждёт данные"
            if not wait_semaphore(self.filled_slots, worker):
                return
            self.file_access.acquire()
            y = float(self._read_file_values()[self.read_count])
            self.read_count += 1
            self.file_access.release()

            worker.state = "суммирует"
            self.z += y
            worker.sleep()
