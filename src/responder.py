from kafka import KafkaConsumer, KafkaProducer
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
import httplib
import urllib
import json
from collections import namedtuple
import io
import yaml
import os
import sys
import time
#host = '172.69.0.4:9092'
host = 'kafka:9092'
webHost = "responder:8099"

print ('responder bridge')

#only allow one 
def pid():
    pid = str(os.getpid())
    pidfile = "responder.pid"

    if os.path.isfile(pidfile):
        print "%s already exists, exiting" % pidfile
        sys.exit()

    file(pidfile, 'w').write(pid)

#listen to kafka
def run():
    print(host)
    consumer = KafkaConsumer('ServiceRequest',bootstrap_servers=host)
    print("consumer running")
    for record in consumer:
        read(record)

def read(record):
    try:
        #with open('service_response1.yaml', 'r') as stream:
        #    j = yaml.load(stream)
        bytes_reader = io.BytesIO(record.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(req_schema)
        request = reader.read(decoder)
        print('got',record.key)
        response = call(request)
        reply(record.key, response)
    except Exception as e:
        print ('*',e)

def reply(key,res):
    try:
        response=json.loads(res)#, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        response['serviceResult']['chargingSessionId']=key

        #print(response)

        producer = KafkaProducer(bootstrap_servers=host) #(value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        writer = avro.io.DatumWriter(res_schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(response,encoder)
        producer.send('ServiceResponse', bytes_writer.getvalue(),key)
        print('sent ', key)
        producer.flush()
    except Exception as e:
        print ('**',e)

#forward request to web service
def call(req):
    try:
        conn = httplib.HTTPConnection(webHost)

        #args=
        #headers={'Authorization' : 'Basic %s' % base64.b64encode("username:password")}

        headers={
            'content-type':'application/json',
            'accept':'application/json',
            'X-sessionId': req['header']['subscriberId'],
        }

        #request = urllib.urlencode(json.dumps(req))

        request = json.dumps(req)
        r1 = conn.request("post", "/", request, headers)
        r2 = conn.getresponse()
        res = r2.read()
        conn.close()
        print ('-->',r1,r2.status,r2.reason,'===',headers,'-->',req,'<--',res,'!!!')
        return res
    except Exception as e:
        print ('***',e)


pid()

print ('starting')

req_schema = avro.schema.parse(open("service-request.avcs", "rb").read())
res_schema = avro.schema.parse(open("service-response.avcs", "rb").read())

global consumer
global producer

while 1:
    try:
        print ('run')
        run()
    except Exception as e:
        print ('-',e)
        time.sleep(5)

    try:
    finally:
        os.unlink(pidfile)
