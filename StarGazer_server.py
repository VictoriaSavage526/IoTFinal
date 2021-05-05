from StarGazer_common import *

messageQ = Queue()
cipher = Fernet(CIPHER_KEY)
init_globals(cipher, messageQ)


def send_url(client, msg):
    msg = msg.split()
    if len(msg) == 4:
        # lat, longi, tz = msg[1], msg[2], msg[3]
        url = "URL https://in-the-sky.org/index.php?latitude={0[1]}&longitude={0[2]}&timezone={0[3]}%3A00".format(msg)
        print(f"Sending `{url}` to `{CLIENT_TOPIC}` topic")
        # print("opening webbrowser now....")
        # webbrowser.open(url)
        Publish(client, url, SERVER_TOPIC)
    else:
        #TODO: handle invalid msg
        pass


def main():

    client_id = "StarGazer_Server"
    client= paho.Client(client_id)  #create client object 
    client.on_log=on_log
    client.on_publish=on_publish
    client.on_subscribe = on_subscribe   #assign function to callback
    client.on_disconnect = on_disconnect #assign function to callback
    client.on_connect = on_connect #assign function to callback
    client.on_message=on_message

    print("connecting to BROKER ",BROKER)
    client.connect(BROKER)#connect
    print("subcribing to", CLIENT_TOPIC)
    client.subscribe(CLIENT_TOPIC)

    time.sleep(1)

    while True:
        try:
            client.loop()
            if not messageQ.empty():
                msg = messageQ.get()
                if msg == "send url":
                    Publish(client, "send coordinates and timezone", SERVER_TOPIC)

                elif msg.split()[0] == "coordinates":
                    send_url(client, msg)

        except KeyboardInterrupt:
            break        
    client.disconnect() #disconnect
    # client.loop_stop() #stop loop

if __name__ == "__main__":
	main()