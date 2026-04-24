import json
import time
from kafka import KafkaProducer
from app.config import KAFKA_BOOTSTRAP_SERVERS


def get_producer(retries=12, delay=5):
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Connected to Kafka")
            return producer
        except Exception as e:
            print(f"Kafka not ready, retry {i + 1}/{retries}: {e}")
            time.sleep(delay)

    raise Exception("Could not connect to Kafka")


try:
    producer = get_producer()
except Exception as e:
    print("Kafka not available:", e)
    producer = None


def send_event_to_kafka(event_data: dict, topic: str):
    if producer:
        producer.send(topic, event_data)
        producer.flush()
    else:
        print("Kafka is not available. Event was not sent to Kafka.")