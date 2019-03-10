from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import datetime
import paho.mqtt.client as mqtt
import json
import calendar
from sqlalchemy.exc import SQLAlchemyError


SIGNALS=[
    ("/signal/ESP_Laengsbeschl",0), #acc_x
    ("/signal/ESP_Querbeschleinigung",0), # acc_y
    ("/signal/ESP_Bremsdruck",0), #stop throttle
    # ("/signal/ESP_v_Signal",0), # average speed
    # ("/signal/MO_Fahrpedalrohwert_01",0), #
    # ("/signal/NP_LatDegree",0), # latitude
    # ("/signal/NP_LongDegree",0) #
]

# POSTGRES = {
#     'user': 'pwdabvae',
#     'pass': 'Cx7URhLBWVT3y2LjPxZ_j6I-efdS2jri',
#     'db': 'pwdabvae',
#     'host': 'manny.db.elephantsql.com',
#     'port': '5432',
# }
POSTGRES = {
    'db': 'starthack',
    'host': 'localhost',
    'port': '5432',
}

db_string = 'postgresql://%(host)s:%(port)s/%(db)s' % POSTGRES

MQTT_SERVER = "82.165.25.152"
MQTT_PORT = 1884


db = create_engine(db_string)  
base = declarative_base()

class Signal(base):
    __tablename__ = 'signal'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    timestamp = Column(Date)
    value = Column(String)

    def __init__(self, key, timestamp, value):
        self.key = key
        self.timestamp = datetime.datetime.utcfromtimestamp(timestamp)
        self.value = value

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)

cached = {}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    print("Subscribing to topics: " + str(SIGNALS))
    client.subscribe(SIGNALS)
        
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    j = json.loads(msg.payload)
    # print("Value:{} UTC: {}".format(j['value'], str(j['utc'])[:10]))
    saveData(str(msg.topic),str(j['utc']),str(j['value']))


def saveData(signal,time,value):
    try:
        print("Saving... Signal: {} UTC: {} Value:{}".format(signal, time, value))
        signal = Signal(signal,int(time), value)
        session.add(signal)
        session.commit()
    except SQLAlchemyError as e:
        print(e)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
