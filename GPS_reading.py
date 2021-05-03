'''
For NMEA message formats:
    https://www.rfwireless-world.com/Terminology/GPS-sentences-or-NMEA-sentences.html
    https://www.trimble.com/OEM_ReceiverHelp/V4.44/en/NMEA-0183messages_MessageOverview.html
'''
import serial               #import serial pacakge
from serial.tools.list_ports import comports
# from time import sleep
import time
import webbrowser           #import package for opening link in browser
import sys                  #import system package
# import threading


class GPS:
    def __init__(self, port):
        # self.ser = serial.Serial(port, 9600)
        self.port = port
        self.reading = dict()
        self.latitude_deg = 0
        self.longitude_deg = 0
        self.latitude = 0
        self.longitude = 0
        self.lat_direction = ""
        self.long_direction = ""
        self.nmea_time = ""
        self.local_time = ""
        self.knots = 0
        self.kph = 0
        self.nmea_date = ""
        self.mode = ""
        self.course = 0
        self.num_satellites = 0
        self.altitude = 0

    
    def read_cycle(self):
        # try:
        ser = serial.Serial(self.port, 9600)
        got=0
        self.reading = dict()
        while True:
            line = ser.readline().decode()[1:].strip()
            if 'GPRMC' in line:
                if got:
                    break
                else:
                    got+=1
            if got:
                line_list = line.split(',')
                header = line_list[0] #.pop(0)
                if header not in self.reading:
                    if header == "GPGSV":
                        self.reading[header] = [line_list]
                    else:
                        self.reading[header] = line_list
                elif header == "GPGSV":
                    self.reading[header].append(line_list)

        # for line in self.reading:
        #     print(line, self.reading[line])
        ser.close()
        self.update()

        # except KeyboardInterrupt:
            # raise()


    def update(self):
        if 'GPGGA' in self.reading:
            gpgga = self.reading['GPGGA']
            self.nmea_time = gpgga[1]
            self.local_time = nmea_time_string(self.nmea_time)
            self.latitude = float(gpgga[2])
            self.lat_direction = gpgga[3]
            self.longitude = float(gpgga[4])
            self.long_direction = gpgga[5]
            lat = self.latitude * (-1 if self.lat_direction == "S" else 1)
            longi = self.longitude * (-1 if self.long_direction == "W" else 1)
            self.latitude_deg = convert_to_degrees(lat)
            self.longitude_deg = convert_to_degrees(longi)
            self.num_satellites = int(gpgga[7])
            self.altitude = float(gpgga[9])
        if 'GPRMC' in self.reading:
            gprmc = self.reading['GPRMC']
            self.knots = float(gprmc[7])
            self.nmea_date = gprmc[9]


    # def GPGGA_Info(self):
    #     NMEA_buff = self.reading['GPGGA']
    #     nmea_time = NMEA_buff[1]                    #extract time from GPGGA string
    #     nmea_latitude = NMEA_buff[2]                #extract latitude from GPGGA string
    #     nmea_longitude = NMEA_buff[4]               #extract longitude from GPGGA string

    #     lat_direction = NMEA_buff[3]  #N/S
    #     long_direction = NMEA_buff[5] #E/W
        
    #     time_12h = nmea_time_string(nmea_time)
        
    #     print("NMEA Time: ", time_12h,'\n')
    #     print ("NMEA_Latitude:", nmea_latitude, lat_direction,"NMEA_Longitude:", nmea_longitude, long_direction,'\n')
        
    #     lat = float(nmea_latitude) * (-1 if lat_direction == "S" else 1)                 #convert string into float for calculation
    #     longi = float(nmea_longitude) * (-1 if long_direction == "W" else 1)              #convertr string into float for calculation
        
    #     lat_in_degrees = convert_to_degrees(lat) #+lat_direction   #get latitude in degree decimal format
    #     long_in_degrees = convert_to_degrees(longi) #+long_direction #get longitude in degree decimal format

    #     return time_12h, lat_in_degrees, long_in_degrees



def nmea_time_string(nmea_time, h24=0):
    utc_offset = int(time.localtime().tm_gmtoff/60/60)
    timezone = time.localtime().tm_zone
    h = int(nmea_time[:2]) + utc_offset
    minute = nmea_time[2:4]
    seconds = nmea_time[4:]
    if h24:
        return str(h) +':'+ minute +':'+ seconds +' '+ timezone
    else:
        if h < 0 or h >= 12:
            meridiem = ' PM'
            h %= 12
        else:
            meridiem = ' AM'
        if h==0:
            h=12
        return str(h) +':'+ nmea_time[2:4] +':'+ nmea_time[4:] + meridiem +' ('+ timezone +')'


    
#convert raw NMEA float into degree decimal format   
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

    for p in comports():
        if "u-blox" in p.description:
            break
    
    gps = GPS(p.device)

    try:
        while True:
            clear_output()  #print on top of the previous print, so the terminal doesn't scroll
            gps.read_cycle()

            lat = gps.latitude_deg
            longi = gps.longitude_deg
            print("Time", gps.local_time, " Satellites used:", gps.num_satellites)
            print("lat in degrees:", lat," long in degree: ", longi, " altitude in meters: ", gps.altitude, '\n')
            map_link = 'http://maps.google.com/?q=' + lat + ',' + longi  #create link to plot location on Google map
            print("<<<<<<<<press ctrl+c to plot location on google maps>>>>>>\n")               #press ctrl+c to plot on map and exit 
            print("------------------------------------------------------------\n")
                            
    except KeyboardInterrupt:
        # ser.close()
        print("\nLink to Google Maps", map_link)
        # webbrowser.open(map_link)        #open current position information in google map
        sys.exit(0)

   
if __name__ == "__main__":
	main()