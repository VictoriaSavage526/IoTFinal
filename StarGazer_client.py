# import time
# import paho.mqtt.client as paho
# from cryptography.fernet import Fernet
# import json
# from queue import Queue

# # BROKER = 'BROKER.emqx.io'
# # BROKER="BROKER.hivemq.com"
# BROKER = "test.mosquitto.org"
# SERVER_TOPIC = "ECSE4660/StarGazer/Server"
# CLIENT_TOPIC = "ECSE4660/StarGazer/Client"

from StarGazer_common import *
import GPS_reading as GPS



url_received = ""
messageQ = Queue()
cipher = Fernet(CIPHER_KEY)
init_globals(cipher, messageQ)

#define callback
# def on_log(client, userdata, level, buf):
#     print("log: ",buf)

# def on_message(client, userdata, message):
#     #time.sleep(1)
#     print("Receive Payload: ",message.payload)
#     decrypted_message = cipher.decrypt(message.payload)   #decrypted_message = cipher.decrypt(encrypted_message)
#     decoded_message = str(decrypted_message.decode("utf-8"))
#     print("\nreceived message =",decoded_message)
#     messageQ.put(decoded_message)
#     # time.sleep(2)
#     # if decoded_message == "Send Coordinates":
#     #     lat = 41
#     #     longi = -73
#     #     msg = f'{lat} {longi}'.encode()
#     #     encrypted_message = cipher.encrypt(msg)
#     #     out_message=encrypted_message.decode()
#     #     client.publish(CLIENT_TOPIC, out_message)

# def on_subscribe(client, userdata, mid, granted_qos):   #create function for callback
#     print("subscribed with qos",granted_qos," ",mid, "\n")
#     pass

# def on_disconnect(client, userdata, rc):
#     print("client disconnected ok")
#     print("disconnecting reason  " + str(rc))
#     client.connected_flag=False
#     client.disconnect_flag=True
#     client.subscribe_flag=False

# def on_connect(client, userdata, flags, rc):
#     m="Connected flags"+str(flags)+"result code "+str(rc)

# def on_publish(client, userdata, mid):
#     print("pub ack "+ str(mid))
#     client.puback_flag=True

# def handle_message(msg):
#     if msg == "Send coordinates":


def Publish(client, msg, qos=0):
    encrypted_message = cipher.encrypt(msg.encode())
    out_message=encrypted_message.decode()
    client.publish(CLIENT_TOPIC, out_message, qos)


def init_connection():
    pass


def request_info(client):
    # msg = {"send": "sky"}
    msg = "send sky "



def main():
    last_gps = None
    gps = GPS.GPS_read()

    client_id = "StarGazer_Client"
    client= paho.Client(client_id)  #create client object client1.on_publish = on_publish                          #assign function to callback client1.connect(broker,port)                                 #establish connection client1.publish("house/bulb1","on")  
    client.on_log=on_log
    client.on_publish=on_publish
    client.on_subscribe = on_subscribe   #assign function to callback
    client.on_disconnect = on_disconnect #assign function to callback
    client.on_connect = on_connect #assign function to callback
    ######
    client.on_message=on_message
    #####encryption
    # cipher_key =b'cb99hQ96hEpCxRO9O5_pHtaxJhtFEXaOhd4tcd_ak6s='
    # cipher = Fernet(cipher_key)

    print("connecting to BROKER ",BROKER)
    client.connect(BROKER)#connect
    # client.loop_start() #start loop to process received messages
    print("subscribing ")
    client.subscribe(SERVER_TOPIC)#subscribe
    time.sleep(5)

    Publish(client, "send url", 1)
    time.sleep(1)
    
    # client.loop_start()
    try:
        while True:
            client.loop() # client_loop()
            if not messageQ.empty():
                msg = messageQ.get()
                if msg == "send coordinates and timezone":
                    print("getting gps info")
                    gps.read_cycle()
                    print(gps.position)
                    Publish(client, "coordinates " + gps.position +" {:03}".format(gps.utc_offset))

                elif 'URL' in msg:
                    url_received = msg.split()[1]
                    time.sleep(1)
                    print()
                    action = input("Do you want to open the URL? (y/n): ")
                    if action.lower() == 'y':
                        webbrowser.open(url_received)
                        time.sleep(10)

            

    except KeyboardInterrupt:
        client.disconnect()
    # count=0
    # while count <30:
    #     time.sleep(1)
    #     count+=1

    # client.disconnect() #disconnect
        # client.loop_stop() #stop loop


if __name__ == "__main__":
	main()