"""Задание 2: писатель и два читателя (приоритет писателя), алгоритм Петерсона."""
import time

from .worker import Worker

WRITER_ID, READER1_ID, READER2_ID = 0, 1, 2  # номера потоков для PetersonLock


class PetersonLock:
    """Алгоритм Петерсона, обобщённый на N потоков (filter lock): flag→level, turn→victim."""

    def __init__(self, threads_count):
        self.threads_count = threads_count
        self.level = [0] * threads_count  # level[поток] — до какой ступени он дошёл (0 — не хочет входить)
        self.victim = [0] * threads_count  # victim[ступень] — кто на этой ступени уступает

    def lock(self, me):
        # Чтобы войти в критическую секцию, поток проходит N-1 «ступеней».
        # На каждой ступени выполняется обычный алгоритм Петерсона для двух сторон:
        # «я» против всех остальных потоков.
        for step in range(1, self.threads_count):
            self.level[me] = step  # flag[me] = true: «я хочу пройти ступень step»
            self.victim[step] = me  # turn: «на этой ступени уступаю я»

            # Ждём, пока выполняются оба условия: уступаю я и кто-то другой на той же ступени или выше.
            # Иначе проходим дальше.
            while True:
                i_give_way = self.victim[step] == me
                someone_ahead = any(self.level[other] >= step
                                    for other in range(self.threads_count) if other != me)
                if not (i_give_way and someone_ahead):
                    break
                time.sleep(0)  # активное ожидание: отдаём процессор и проверяем снова

    def unlock(self, me):
        self.level[me] = 0


class Task2:
    """Писатель и два читателя, приоритет писателя; общие переменные защищены алгоритмом Петерсона."""

    RECORD_CELLS = 5  # запись из нескольких ячеек; писатель заполняет их по одной, чтобы был виден разрыв

    def __init__(self):
        self.record = [0] * self.RECORD_CELLS  # общие данные
        # Переменные состояния, их меняют только под self.lock:
        self.active_readers = 0  # сколько читателей сейчас читают
        self.writers_waiting = 0  # пока > 0, новые читатели не входят (приоритет писателя)
        self.writing = False
        self.errors = 0  # прочитано полузаписанных записей (должно остаться 0)
        self.lock = PetersonLock(3)
        self.writer = Worker("Писатель", self._write)
        self.reader1 = Worker("Читатель 1", lambda worker: self._read(worker, READER1_ID))
        self.reader2 = Worker("Читатель 2", lambda worker: self._read(worker, READER2_ID))

    def _write(self, worker):
        while not worker.stopped():
            worker.state = "готовит данные"
            worker.sleep()
            new_value = self.record[0] + 1

            worker.state = "ждёт доступа"
            self.lock.lock(WRITER_ID)
            self.writers_waiting += 1  # с этого момента новые читатели не входят
            self.lock.unlock(WRITER_ID)
            if not self._wait_until_can_write(worker):
                return

            worker.state = "пишет"
            for cell in range(self.RECORD_CELLS):
                self.record[cell] = new_value
                worker.sleep(1 / self.RECORD_CELLS)

            self.lock.lock(WRITER_ID)
            self.writing = False
            self.lock.unlock(WRITER_ID)

    def _wait_until_can_write(self, worker):
        """Ждёт, пока все читатели выйдут, и занимает данные. False — поток остановили."""
        while True:
            self.lock.lock(WRITER_ID)
            can_write = self.active_readers == 0 and not self.writing
            if can_write:
                self.writing = True
            if can_write or worker.stopped():
                self.writers_waiting -= 1  # больше не ждём: либо пишем, либо уходим
            self.lock.unlock(WRITER_ID)
            if can_write:
                return True
            if worker.stopped():
                return False
            time.sleep(0.005)

    def _read(self, worker, reader_id):
        while not worker.stopped():
            worker.state = "ждёт доступа"
            if not self._wait_until_can_read(worker, reader_id):
                return

            worker.state = "читает"
            values_read = []
            for cell in range(self.RECORD_CELLS):
                values_read.append(self.record[cell])
                worker.sleep(1 / self.RECORD_CELLS)

            self.lock.lock(reader_id)
            self.active_readers -= 1
            self.lock.unlock(reader_id)

            if len(set(values_read)) != 1:  # ячейки разные — прочитали полузаписанные данные
                self.errors += 1
            worker.state = "обрабатывает"
            worker.sleep()

    def _wait_until_can_read(self, worker, reader_id):
        """Ждёт, пока никто не пишет и писатель не ждёт, и входит. False — поток остановили."""
        while True:
            self.lock.lock(reader_id)
            can_read = self.writers_waiting == 0 and not self.writing
            if can_read:
                self.active_readers += 1
            self.lock.unlock(reader_id)
            if can_read:
                return True
            if worker.stopped():
                return False
            time.sleep(0.005)
