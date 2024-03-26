import cherrypy
import random
import string
import json
import math
import redis

from kafka import KafkaConsumer
from kafka.structs import TopicPartition

r1 = redis.Redis(host='localhost', port=6379, db=1)
r2 = redis.Redis(host='localhost', port=6379, db=2)

cherrypy.config.update({
    'server.socket_host':'127.0.0.1',
    'server.socket_port':8000,  #Change the port if 8000 is occupied
    })

consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id="Testgroup",
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

partition = TopicPartition('bchain',0)
consumer.assign([partition])

@cherrypy.expose
class show_transactions(object):
    def GET(self):
        txlist = []
        consumer.seek_to_end(partition)
        t = consumer.position(partition)
        consumer.seek(partition,(max(0,t-100)))
        for message in consumer:
            if consumer.position(partition)<t:
                txlist.append(message.value)
            elif consumer.position(partition)==t:
                txlist.append(message.value)
                break
        htmlstring = "<h1>Latest 100 Transactions</h1>\n<ol>\n"
        for s in txlist:
            htmlstring += "<li>" + json.dumps(s, sort_keys=True, indent=4) + "</br></br></li>\n"
        htmlstring += "</ol>\n"
        return htmlstring 

@cherrypy.expose
class transactions_count_per_minute(object):
    def GET(self,min_value):
        out=r2.get(str(min_value)[:-1])
        htmlstring = "<p>No of Transactions during "+str(min_value)[:-1]+" = "+str(out)[2:-1]+"</p>"
        return htmlstring

@cherrypy.expose
class high_value_addr(object):
    def GET(self):
        complist = []
        highlist = []
        final = []
        keys = r1.keys(pattern='*')
        for w in keys:
            complist.append([str(w)[2:-1],int(r1.get(w))])
        for w in complist:
            highlist.append(w[1])
        highlist.sort(reverse=True)
        i = 0
        rst = True
        while rst and i<5:
            rst = False
            for w in complist:
                if int(w[1]) == highlist[i]:
                    final.append(w)
                    i =i+1
                    rst = True
                    break
        htmlstring = "<h1>Addresses with Highest Transactions (Top 5)</h1>\n<ul>\n"
        for s in final:
            htmlstring += "<li>" + str(s)[1:-1] + "</li>\n"
        htmlstring += "</ul>"
        return htmlstring 
           
cherrypy.tree.mount(show_transactions(),'/show_transactions',
    {'/':
	{'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
	}
    )

cherrypy.tree.mount(transactions_count_per_minute(),'/transactions_count_per_minute',
    {'/':
	{'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
	}
    )

cherrypy.tree.mount(high_value_addr(),'/high_value_addr',
    {'/':
	{'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
	}
    )



cherrypy.engine.start()
