import json
import time
from kafka import KafkaConsumer

time.sleep(10)

consumer = KafkaConsumer(
    "user_events",
    bootstrap_servers="kafka:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="event-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Consumer started...", flush=True)

for message in consumer:
    print("Received event:", message.value, flush=True)