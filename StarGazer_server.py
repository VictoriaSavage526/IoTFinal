# import time
# import paho.mqtt.client as paho
# from cryptography.fernet import Fernet
# import json

# # broker = 'broker.emqx.io'
# # broker="broker.hivemq.com"
# broker = "test.mosquitto.org"
# port = 1883
# server_topic = "ECSE4660/StarGazer/Server"
# client_topic = "ECSE4660/StarGazer/Client"

from StarGazer_common import *

#define callback
def on_log(client, userdata, level, buf):
    print("log: ",buf)
def on_message(client, userdata, message):
    #time.sleep(1)
    print("receive payload ",message.payload)
    decrypted_message = cipher.decrypt(message.payload)   #decrypted_message = cipher.decrypt(encrypted_message)
    print("\nreceived message =",str(decrypted_message.decode("utf-8")))

def on_subscribe(client, userdata, mid, granted_qos):   #create function for callback
    print("subscribed with qos",granted_qos," ",mid, "\n")
    pass

def on_disconnect(client, userdata, rc):
    print("client disconnected ok")

def on_connect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)

def on_publish(client, userdata, mid):
    print("pub ack "+ str(mid))
    client.puback_flag=True

def Message(client, count):
    message = f'message from Mark: {count}'.encode()
    #message = b'the quick brown fox jumps over the lazy dog'
    encrypted_message = cipher.encrypt(message)
    out_message=encrypted_message.decode()# turn it into a string to send
    ##t
    print("publishing encrypted message ",encrypted_message)
    #out_message="on"
    client.publish(server_topic,out_message)#publish

client_id = "StarGazer_Server"
client= paho.Client(client_id)  #create client object 
client.on_log=on_log
client.on_publish=on_publish
client.on_subscribe = on_subscribe   #assign function to callback
client.on_disconnect = on_disconnect #assign function to callback
client.on_connect = on_connect #assign function to callback
######
client.on_message=on_message
#####encryption
#cipher_key = Fernet.generate_key()
cipher_key=b'cb99hQ96hEpCxRO9O5_pHtaxJhtFEXaOhd4tcd_ak6s='
cipher = Fernet(cipher_key)
message = b'Send Coordinates'
#message = b'the quick brown fox jumps over the lazy dog'
encrypted_message = cipher.encrypt(message)
out_message=encrypted_message.decode()# turn it into a string to send
##
print("connecting to broker ",broker)
client.connect(broker)#connect
print("publishing encrypted message ",encrypted_message)
#out_message="on"
client.subscribe(client_topic)
client.publish(server_topic,out_message)#publish
time.sleep(10)
count=0
while True:
    try:
        time.sleep(1)
        client.loop()
        if count%10 ==0:
            Message(client, count)
        count = (count+1)%10000

        # client_loop(client, cipher, messageQ)
    except KeyboardInterrupt:
        break        
client.disconnect() #disconnect
client.loop_stop() #stop loop
