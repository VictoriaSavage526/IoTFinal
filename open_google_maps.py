'''
GPS Interfacing with Raspberry Pi using Pyhton
adapted from example on http://www.electronicwings.com
'''
import serial               #import serial pacakge
from serial.tools.list_ports import comports
# from time import sleep
import time
import webbrowser           #import package for opening link in browser
import sys                  #import system package


def GPGGA_Info(NMEA_buff):
    # global NMEA_buff
    # global lat_in_degrees
    # global long_in_degrees

    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string

    lat_hemisphere = NMEA_buff[2]  #N/S
    long_hemisphere = NMEA_buff[4] #E/W

    # if lat_hemisphere == "S":
    #     nmea_latitude = "-" + nmea_latitude
    # if long_hemisphere == "W":
    #     nmea_longitude = "-" + nmea_longitude
    utc_offset = int(time.localtime().tm_gmtoff/60/60)
    timezone = time.localtime().tm_zone

    time_12h = str((int(nmea_time[:2]) + utc_offset)%12) +':'+ nmea_time[2:4] +':'+ nmea_time[4:] +' '+timezone
    
    print("NMEA Time: ", time_12h,'\n')
    print ("NMEA Latitude:", nmea_latitude,lat_hemisphere,"NMEA Longitude:", nmea_longitude,long_hemisphere,'\n')
    
    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation
    
    lat_in_degrees = convert_to_degrees(lat) +lat_hemisphere   #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) +long_hemisphere #get longitude in degree decimal format

    return lat_in_degrees, long_in_degrees
    
#convert raw NMEA string into degree decimal format   
def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.6f" %(position)
    return position
    

def clear_terminal():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      out = os.system('clear')
   else:
      # for windows
      out = os.system('cls')


def clear_output():
	# print('\33[H', end='')
	print('\33[u',end='')
	print('\33[J', end='')



def main():
    print('\33[s',end='') #set the beginning cursor mark

    gpgga_info = "$GPGGA,"

    for p in comports():
        if "u-blox" in p.description:
            break
    try:
        ser = serial.Serial (p.device, 9600)              #Open port with baud rate
    except:
        print("Serial port couldn't be opened. Make sure the device is plugged in to USB.")
        exit()

    # global NMEA_buff
    # global lat_in_degrees
    # global long_in_degrees

    # GPGGA_buffer = 0
    # NMEA_buff = 0
    # lat_in_degrees = 0
    # long_in_degrees = 0

    try:
        while True:
            clear_output()  #print on top of the previous print, so the terminal doesn't scroll
            received_data = (str)(ser.readline())                   #read NMEA string received
            GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                 
            if (GPGGA_data_available>0):
                GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
                NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
                lat_in_degrees, long_in_degrees = GPGGA_Info(NMEA_buff)                                          #get time, latitude, longitude
    
                print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
                map_link = 'http://maps.google.com/?q=' + lat_in_degrees + ',' + long_in_degrees  #create link to plot location on Google map
                print("<<<<<<<<press ctrl+c to plot location on google maps>>>>>>\n")               #press ctrl+c to plot on map and exit 
                print("------------------------------------------------------------\n")
                            
    except KeyboardInterrupt:
        ser.close()
        print("\nOpening", map_link)
        webbrowser.open(map_link)        #open current position information in google map
        sys.exit(0)

   
if __name__ == "__main__":
	main()