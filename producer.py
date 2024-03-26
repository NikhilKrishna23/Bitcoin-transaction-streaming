import json
import time
import math

from kafka import KafkaProducer
from websocket import create_connection

ws = create_connection("wss://ws.blockchain.info/inv")
ws.send('{"op":"unconfirmed_sub"}')

producer = KafkaProducer( bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))


while True:
    result = json.loads(ws.recv())
    producer.send('bchain', value=result)   
ws.close()
