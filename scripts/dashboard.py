import json
from confluent_kafka import Consumer, KafkaError, KafkaException

# 1. Connect to Redpanda with Sasha's credentials
conf = {
    'bootstrap.servers': 'localhost:19092',
    'group.id': 'iot-dashboard-group',      # The group we just authorized
    'auto.offset.reset': 'earliest',        # 'earliest' reads all missed messages from the beginning
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': 'Sasha',
    'sasl.password': 'sashapassword'
}

consumer = Consumer(conf)

# 2. Subscribe to our topic
consumer.subscribe(['classroom-temperatures'])
print("Starting dashboard... Waiting for sensor data. Press Ctrl+C to stop.")

try:
    while True:
        # 3. Poll for new messages every 1 second
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Reached the end of the topic, just keep waiting
                continue
            else:
                raise KafkaException(msg.error())
        
        # 4. Decode the bytes back into a Python dictionary
        raw_data = msg.value().decode('utf-8')
        data = json.loads(raw_data)
        
        # 5. Display the data nicely
        print(f"🌡️ Dashboard Received: {data['classroom']} is currently {data['temperature_f']}°F with {data['humidity']}% humidity.")

except KeyboardInterrupt:
    print("Stopping dashboard...")
finally:
    # 6. Always cleanly close the consumer connection
    consumer.close()
