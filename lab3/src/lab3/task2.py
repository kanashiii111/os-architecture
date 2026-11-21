import time

from .worker import Worker

WRITER_ID, READER1_ID, READER2_ID = 0, 1, 2

class PetersonLock:
    def __init__(self, threads_count):
        self.threads_count = threads_count
        self.flags = [0] * threads_count
        self.turn = [0] * threads_count

    def lock(self, me):
        for stage in range(1, self.threads_count):
            self.flags[me] = stage
            self.turn[stage] = me

            while True:
                i_give_way = self.turn[stage] == me
                someone_ahead = any(self.flags[other] >= stage
                                    for other in range(self.threads_count) if other != me)
                if not (i_give_way and someone_ahead):
                    break
                time.sleep(0)

    def unlock(self, me):
        self.flags[me] = 0


class Task2:
    RECORD_CELLS = 5

    def __init__(self):
        self.record = [0] * self.RECORD_CELLS
        self.active_readers = 0
        self.writers_waiting = 0
        self.writing = False
        # self.errors = 0
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
            self.writers_waiting += 1
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

            # if len(set(values_read)) != 1:  # ячейки разные — прочитали полузаписанные данные
            #     self.errors += 1
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
