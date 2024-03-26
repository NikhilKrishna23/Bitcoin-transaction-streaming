import json
import time
import math
import redis

from threading import Thread
from datetime import datetime
from kafka import KafkaConsumer
from kafka.structs import TopicPartition

r1 = redis.Redis(host='localhost', port=6379, db=1)
r2 = redis.Redis(host='localhost', port=6379, db=2)

consumer = KafkaConsumer(
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id="Testgroup",
     value_deserializer=lambda x: json.loads(x.decode('utf-8')))

count = 0
ttl = 10800

def counter():    #Function to Count No of Transactions per minute
    global count
    while True:
        time.sleep(60)
        now = datetime.now()
        r2.set((str(now.hour)+':'+str(now.minute)),count)
        r2.expire(name=(str(now.hour)+':'+str(now.minute)),time=3540) 
        count = 0

partition = TopicPartition('bchain',0)
consumer.assign([partition])

consumer.seek_to_beginning(partition)

bg = Thread(target=counter)
bg.start()

for message in consumer:
    count = count + 1
    if message.value['x']['inputs']:
        for w in message.value['x']['inputs']:
            if str(r1.exists(str(w['prev_out']['addr']))) == "0":
                r1.set(str(w['prev_out']['addr']),(int(w['prev_out']['value'])*-1))
                r1.expire(name=str(w['prev_out']['addr']),time=ttl)
            else:
                r1.decrby(str(w['prev_out']['addr']),int(w['prev_out']['value']))
                r1.expire(name=str(w['prev_out']['addr']),time=ttl)
    
    if message.value['x']['out']:
        for w in message.value['x']['out']:
            if str(w['spent']) == "False":
                if str(r1.exists(str(w['addr']))) == "0":
                    r1.set(str(w['addr']),int(w['value']))
                    r1.expire(name=str(w['addr']),time=ttl)
                else:
                    r1.incrby(str(w['addr']),int(w['value']))
                    r1.expire(name=str(w['addr']),time=ttl)
            else:
                if str(r1.exists(str(w['addr']))) == "0":
                    r1.set(str(w['addr']),int(0))
                    r1.expire(name=str(w['addr']),time=ttl)   
