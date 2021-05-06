from StarGazer_common import *
import GPS_reading as GPS


# url_received = ""
messageQ = Queue()
cipher = Fernet(CIPHER_KEY)
init_globals(cipher, messageQ)


def main():
    url_received = ""
    last_gps = None
    gps = GPS.GPS_read()

    client_id = "StarGazer_Client"
    client= paho.Client(client_id)  #create client object client1.on_publish = on_publish                          #assign function to callback client1.connect(broker,port)                                 #establish connection client1.publish("house/bulb1","on")  
    client.on_log=on_log
    client.on_publish=on_publish
    client.on_subscribe = on_subscribe   #assign function to callback
    client.on_disconnect = on_disconnect #assign function to callback
    client.on_connect = on_connect #assign function to callback
    client.on_message=on_message


    print("connecting to BROKER ",BROKER)
    client.connect(BROKER)#connect
    print("subscribing to", SERVER_TOPIC)
    client.subscribe(SERVER_TOPIC)#subscribe
    time.sleep(5)

    Publish(client, "send url", CLIENT_TOPIC, 1)
    time.sleep(1)
    
    # client.loop_start()
    try:
        count=0
        while True:
            client.loop()
            if not messageQ.empty():
                msg = messageQ.get()
                if msg == "send coordinates and timezone":
                    print("getting gps info")
                    gps.read_cycle()
                    print(gps.position)
                    Publish(client, "coordinates " + gps.position +" {:03}".format(gps.utc_offset), CLIENT_TOPIC)

                elif 'URL' in msg:
                    url_received = msg.split()[1]
                    time.sleep(1)
                    print()
                    action = input("Do you want to open the URL? (y/n): ")
                    if action.lower() == 'y':
                        webbrowser.open(url_received)
                        time.sleep(5)

            else:
                if count % 10 ==0:
                    gps.read_cycle()

                    lat = gps.lat_degrees
                    longi = gps.long_degrees
                    print("Current GPS reading:")
                    
                    print("Time", gps.local_time, " Satellites seen:", gps.num_satellites)
                    print("Latitude in degrees:", lat," Longitude in degree:", longi, " Altitude in meters:", gps.altitude)
                    print("Speed over ground:",gps.knots,"knots","Course over ground:",gps.course,"degrees")
                    print("------------------------------------------------------------\n")
                
                    if not url_received:
                        Publish(client, "send url", CLIENT_TOPIC, 1)
                # elif count %
                count+=1
                time.sleep(1)
            
    except KeyboardInterrupt:
        client.disconnect()
        # client.loop_stop() #stop loop


if __name__ == "__main__":
	main()