import json
import psycopg2
from confluent_kafka import Consumer

# 1. Connect to our new Postgres container
conn = psycopg2.connect(
    dbname="iot_data",
    user="admin",
    password="adminpassword",
    host="localhost",
    port="5432"
)
# Autocommit ensures data saves instantly
conn.autocommit = True
cursor = conn.cursor()

# 2. Build the table if it is the first time running
cursor.execute("""
    CREATE TABLE IF NOT EXISTS temperatures (
        id SERIAL PRIMARY KEY,
        classroom VARCHAR(50),
        temperature_f NUMERIC(5,1),
        humidity NUMERIC(5,1),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 3. Connect to Redpanda
conf = {
    'bootstrap.servers': 'localhost:19092',
    'group.id': 'db-writer-group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': 'Sasha',
    'sasl.password': 'sashapassword'
}
consumer = Consumer(conf)
consumer.subscribe(['classroom-temperatures'])

print("Database writer started... Saving data to Postgres. Press Ctrl+C to stop.")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue
        
        data = json.loads(msg.value().decode('utf-8'))
        
        # 4. Insert the data row into Postgres
        cursor.execute(
            "INSERT INTO temperatures (classroom, temperature_f, humidity) VALUES (%s, %s, %s)",
            (data['classroom'], data['temperature_f'], data['humidity'])
        )
        print(f"💾 Saved to database: {data['classroom']} at {data['temperature_f']}°F")

except KeyboardInterrupt:
    print("Stopping database writer...")
finally:
    consumer.close()
    cursor.close()
    conn.close()