"""Управляемый поток: запуск / пауза / останов и регулируемая задержка."""
import threading
import time


class Worker:
    """Поток с управлением: запуск / пауза / останов и регулируемой задержкой."""

    def __init__(self, name, work_function):
        self.name = name
        self.work_function = work_function  # что делает поток; получает этот Worker аргументом
        self.delay_seconds = 0.5  # задаётся ползунком
        self.state = "остановлен"
        self.thread: threading.Thread | None = None
        self._is_running = threading.Event()  # поднят — работает, опущен — на паузе
        self._stop_requested = threading.Event()  # поднят — потоку пора завершиться

    def alive(self):
        return self.thread is not None and self.thread.is_alive()

    def paused(self):
        return self.alive() and not self._is_running.is_set()

    def start(self):
        self._is_running.set()  # заодно снимает паузу
        if not self.alive():
            self._stop_requested.clear()
            self.thread = threading.Thread(target=self._thread_main, daemon=True)
            self.thread.start()

    def set_paused(self, paused):
        if paused:
            self._is_running.clear()
        else:
            self._is_running.set()

    def pause(self):
        if self._is_running.is_set():
            self._is_running.clear()
        else:
            self._is_running.set()

    def join(self, timeout=None):
        """Дождаться завершения потока (если он был запущен)."""
        if self.thread is not None:
            self.thread.join(timeout)

    def stop(self):
        self._stop_requested.set()

    def stopped(self):
        return self._stop_requested.is_set()

    def sleep(self, fraction_of_delay=1.0):
        """Задержка, моделирующая скорость; на паузе стоит здесь. Останов прерывает задержку,
        а выход из потока делает само тело в безопасной точке (вне критической секции)."""
        remaining_seconds = self.delay_seconds * fraction_of_delay
        time.sleep(0.001)  # даже при 0 мс отдаём процессор, иначе поток душит GUI через GIL
        while not self.stopped():
            if not self._is_running.is_set():
                time.sleep(0.02)
                continue
            if remaining_seconds <= 0:
                return
            # спим короткими кусками, чтобы быстро реагировать на паузу и останов
            chunk = min(0.02, remaining_seconds)
            time.sleep(chunk)
            remaining_seconds -= chunk

    def _thread_main(self):
        try:
            self.work_function(self)
        finally:
            self.state = "остановлен" if self.stopped() else "завершён"
