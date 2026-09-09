import json
import time
import random
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:19092',
    'client.id': 'classroom-sensor',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': 'Sasha',
    'sasl.password': 'sashapassword'
}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")

topic_name = "classroom-temperatures"

# 1. Define our list of classrooms
classrooms = ["Room 101", "Room 102", "Room 205", "Science Lab"]

print("Starting multi-room sensors... Press Ctrl+C to stop.")

try:
    while True:
        # 2. Loop through every classroom and generate unique data for each
        for room in classrooms:
            data = {
                "classroom": room,
                # Give the science lab a slightly different temp range so it stands out on the chart
                "temperature_f": round(random.uniform(66.0, 70.0) if room == "Science Lab" else random.uniform(70.0, 75.0), 1),
                "humidity": round(random.uniform(35.0, 50.0), 1)
            }
            
            json_data = json.dumps(data).encode('utf-8')
            producer.produce(topic_name, value=json_data, callback=delivery_report)
            print(f"Sent: {data}")
        
        # 3. Push the batch of messages and wait 2 seconds
        producer.poll(0)
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping sensors...")

producer.flush()
