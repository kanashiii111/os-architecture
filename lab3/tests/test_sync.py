"""Самопроверка: uv run python tests/test_sync.py"""
import math
import tempfile
import time
from pathlib import Path

from lab3.task1 import Task1
from lab3.task2 import Task2

# Задание 1: при разных скоростях Z = сумма (ln x)/3 по x=1..15
expected_z = sum(round(math.log(x) / 3, 6) for x in range(1, 16))  # в файл пишем 6 знаков
for producer_delay, consumer_delay in ((0, 0.02), (0.02, 0), (0.01, 0.01)):
    task1 = Task1(Path(tempfile.gettempdir()) / "lab3_test_buffer.txt")
    task1.producer.delay_seconds = producer_delay
    task1.consumer.delay_seconds = consumer_delay
    task1.producer.start()
    task1.consumer.start()
    task1.producer.join(10)
    task1.consumer.join(10)
    assert abs(task1.z - expected_z) < 1e-9, (producer_delay, consumer_delay, task1.z, expected_z)

# Задание 2: ни один читатель не прочитал полузаписанные данные, писатель не голодает
task2 = Task2()
workers = (task2.writer, task2.reader1, task2.reader2)
for worker, delay in zip(workers, (0.05, 0.03, 0.04)):
    worker.delay_seconds = delay
    worker.start()
time.sleep(3)
for worker in workers:
    worker.stop()
for worker in workers:
    worker.join(5)
    assert not worker.alive(), worker.name
assert task2.errors == 0, task2.errors
assert task2.record[0] > 5, task2.record
assert task2.active_readers == 0 and task2.writers_waiting == 0 and not task2.writing
print("ok")
