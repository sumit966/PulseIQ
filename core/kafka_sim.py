"""Kafka simulation without a real broker."""
import json
import queue
import threading
import time
from collections import defaultdict

from core.data_generator import generate_event


class FakeKafkaBroker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.topics = defaultdict(queue.Queue)
            cls._instance.messages_sent = 0
            cls._instance.messages_consumed = 0
            cls._instance.lock = threading.Lock()
        return cls._instance


class FakeKafkaProducer:
    def __init__(self, topic: str):
        self.topic = topic
        self.broker = FakeKafkaBroker()

    def send(self, value: dict):
        self.broker.topics[self.topic].put(json.dumps(value))
        with self.broker.lock:
            self.broker.messages_sent += 1


class FakeKafkaConsumer:
    def __init__(self, topic: str, group_id: str = "default"):
        self.topic = topic
        self.group_id = group_id
        self.broker = FakeKafkaBroker()

    def poll(self, max_records=1):
        out = []
        q = self.broker.topics[self.topic]
        for _ in range(max_records):
            try:
                out.append(json.loads(q.get_nowait()))
                with self.broker.lock:
                    self.broker.messages_consumed += 1
            except queue.Empty:
                break
        return out

    def lag(self) -> int:
        return self.broker.topics[self.topic].qsize()


_producer_thread = None
_stop_flag = threading.Event()


def _producer_loop(topic: str, interval: float = 0.4):
    producer = FakeKafkaProducer(topic)
    while not _stop_flag.is_set():
        producer.send(generate_event())
        time.sleep(interval)


def start_producer(topic: str, interval: float = 0.4):
    global _producer_thread
    if _producer_thread is None or not _producer_thread.is_alive():
        _stop_flag.clear()
        _producer_thread = threading.Thread(
            target=_producer_loop, args=(topic, interval), daemon=True
        )
        _producer_thread.start()


def stop_producer():
    _stop_flag.set()


def broker_stats():
    b = FakeKafkaBroker()
    return {
        "topics": list(b.topics.keys()),
        "messages_sent": b.messages_sent,
        "messages_consumed": b.messages_consumed,
        "lag": max(0, b.messages_sent - b.messages_consumed),
    }

