import paho.mqtt.client as paho
from queue import Queue
import time
import json
from cryptography.fernet import Fernet
import webbrowser, urllib


# broker = 'broker.emqx.io'
# broker="broker.hivemq.com"
BROKER = "test.mosquitto.org"
PORT = 1883
SERVER_TOPIC = "ECSE4660/StarGazer/Server"
CLIENT_TOPIC = "ECSE4660/StarGazer/Client"

CIPHER_KEY =b'cb99hQ96hEpCxRO9O5_pHtaxJhtFEXaOhd4tcd_ak6s='
# cipher = Fernet(cipher_key)


def on_log(client, userdata, level, buf):
    print("log: ",buf)


def on_subscribe(client, userdata, mid, granted_qos):   #create function for callback
    print("subscribed with qos",granted_qos," ",mid, "\n")
    pass


def on_message(client, userdata, message):
    #time.sleep(1)
    global cipher, messageQ
    print("Receive Payload: ",message.payload)
    decrypted_message = cipher.decrypt(message.payload)   #decrypted_message = cipher.decrypt(encrypted_message)
    decoded_message = str(decrypted_message.decode("utf-8"))
    print("\nreceived message =",decoded_message)
    messageQ.put(decoded_message)


def on_disconnect(client, userdata, rc):
    print("client disconnected ok")
    print("disconnecting reason  " + str(rc))
    client.connected_flag=False
    client.disconnect_flag=True
    client.subscribe_flag=False

def on_connect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "+str(rc)

def on_publish(client, userdata, mid):
    print("pub ack "+ str(mid))
    client.puback_flag=True


def init_globals(cipher_, mQ):
    global cipher, messageQ
    cipher = cipher_
    messageQ = mQ

# def Publish(client, msg, topic):
#     encrypted_message = cipher.encrypt(msg)
#     out_message=encrypted_message.decode()
#     client.publish(topic, out_message)


def client_loop(client, cipher):
    pass