'''
For NMEA message formats:
    https://www.rfwireless-world.com/Terminology/GPS-sentences-or-NMEA-sentences.html
    https://www.trimble.com/OEM_ReceiverHelp/V4.44/en/NMEA-0183messages_MessageOverview.html
'''
import serial               #import serial pacakge
from serial.tools.list_ports import comports
import time
import sys                  #import system package
import re
import webbrowser
# import threading


class GPS_read:
    class Satellite:
        def __init__(self, prn, elv, az, snr):
            self.PRN = prn
            self.elevation = elv
            self.azimuth = az
            self.SNR = snr



    def __init__(self):
        #find GPS module's serial port, assuming a USB cable is being used
        port = ""
        for p in comports():
            if "u-blox" in p.description:
                port = p.device
                break
        if not port:
            print("Could not find the device on a serial port")
            sys.exit(0)

        self.port = port
        self.info_dict = dict()
        self.lat_degrees = 0
        self.long_degrees = 0
        self.latitude = 0
        self.longitude = 0
        self.position = ""
        self.lat_direction = ""
        self.long_direction = ""
        self.nmea_time = ""
        self.local_time = ""
        self.knots = 0
        self.kph = 0
        self.mph = 0
        self.nmea_date = ""
        self.mode = ""
        self.course = 0
        self.num_satellites = 0
        self.altitude = 0
        self.satellites = dict()

    
    def read_cycle(self):
        # try:
        ser = serial.Serial(self.port, 9600)
        got=0
        self.info_dict = dict()
        self.lines = ""
        while True:
            #strip out the leading '$' and don't include the checksum or newline
            line = re.findall("\$(.*?)\*",ser.readline().decode())[0]
            if 'GPRMC' in line:
                if got:
                    break
                else:
                    got+=1
            if got and 'GPTXT' not in line:
                self.lines += line +'\n'
                line_list = line.split(',')
                header = line_list[0] #.pop(0)
                if header not in self.info_dict:
                    if header == "GPGSV":
                        self.info_dict[header] = [line_list]
                    else:
                        self.info_dict[header] = line_list
                elif header == "GPGSV":
                    self.info_dict[header].append(line_list)

        ser.close()
        self.update()
        # except KeyboardInterrupt:
            # raise()

    def print_cycle(self):
        print(self.lines)
        # for line in self.info_dict:
        #     print(line, self.info_dict[line])

    def update(self):
        if 'GPGGA' in self.info_dict:
            gpgga = self.info_dict['GPGGA']
            self.nmea_time = get_str(gpgga[1])
            self.local_time = nmea_time_string(self.nmea_time)
            self.latitude = get_float(gpgga[2])
            self.lat_direction = get_str(gpgga[3])
            self.longitude = get_float(gpgga[4])
            self.long_direction = get_str(gpgga[5])
            lat = self.latitude * (-1 if self.lat_direction == "S" else 1)
            longi = self.longitude * (-1 if self.long_direction == "W" else 1)
            self.lat_degrees = convert_to_degrees(lat)
            self.long_degrees = convert_to_degrees(longi)
            self.position = self.lat_degrees +" "+ self.long_degrees
            self.num_satellites = get_int(gpgga[7])
            self.altitude = get_float(gpgga[9])
        if 'GPRMC' in self.info_dict:
            gprmc = self.info_dict['GPRMC']
            self.knots = get_float(gprmc[7])
            self.mph = self.knots * 1.15077945
            if gprmc[8]:
                self.course = float(gprmc[8]) #course/direction over ground in degrees
            else:
                self.course = "?"
            self.nmea_date = get_str(gprmc[9])
        if 'GPGSV' in self.info_dict:
            gpgsv = self.info_dict['GPGSV']
            for msg in gpgsv:
                # parse info, create satellite, add to dictionart
                pass



#HELPER FUNCTIONS
def get_str(string):
    if string:
        return string
    else:
        return "?"


def get_int(string):
    try:
        return int(string)
    except:
        return 0

def get_float(string):
    try:
        return float(string)
    except:
        return 0


def nmea_time_string(nmea_time, h24=0):
    """takes in NMEA time value, converts it to local time, returns in nice format.
    The second parameter is optinal and takes 1 or True for 24-hour format, 
    and 0 or False for 12-hour. Default/blank is 12-hour.
    """
    utc_offset = int(time.localtime().tm_gmtoff/60/60)
    timezone = time.localtime().tm_zone
    #NMEA time string is in format 	hhmmss.sss and timezone is UTC
    hour = int(nmea_time[:2]) + utc_offset
    minute = nmea_time[2:4]
    seconds = nmea_time[4:]
    if h24:
        return str(hour) +':'+ minute +':'+ seconds +' '+ timezone
    else:
        if hour < 0 or hour >= 12:
            meridiem = ' PM'
            hour %= 12
        else:
            meridiem = ' AM'
        if hour==0:
            hour==12
        return str(hour) +':'+ minute +':'+ seconds + meridiem +' ('+ timezone +')'

    
def convert_to_degrees(raw_value):
    """convert raw NMEA float into degree decimal format.
    The raw value i in the format dddmm.mmmm, where d is degrees
    and m is minutes. There are 60 minutes in one degree.
    """
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position
    

def clear_terminal():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      out = os.system('clear')
   else:
      # for windows
      out = os.system('cls')


def clear_output():
    """This uses ANSI escape sequences to clear only the output
    of this program, and leaves the rest of the terminal alone
    """
    print('\33[u',end='') #restores the saved cursor position
    print('\33[J', end='') #clears the from cursor to end of screen



def main():
    print('\33[s',end='') #saves the beginning cursor position
    
    #initialize GPS object
    gps = GPS_read()

    try:
        while True:
            clear_output()  #print on top of the previous print, so the terminal doesn't scroll
            gps.read_cycle()

            lat = gps.lat_degrees
            longi = gps.long_degrees
            print("Current GPS reading:")
            
            print("Time", gps.local_time, " Satellites seen:", gps.num_satellites)
            print("Latitude in degrees:", lat," Longitude in degree:", longi, " Altitude in meters:", gps.altitude)
            print("Speed over ground:",gps.knots,"knots","Course over ground:",gps.course,"degrees")
            map_link = 'http://maps.google.com/?q=' + lat + ',' + longi  #create link to plot location on Google map
            print("\n<<<<<<<<press ctrl+c for link to plot location on google maps>>>>>>")               #press ctrl+c to plot on map and exit 
            print("------------------------------------------------------------\n")
            gps.print_cycle()
            time.sleep(5)
                            
    except KeyboardInterrupt:
        # ser.close()
        if map_link:
            print("\nLink to Google Maps", map_link)
            # webbrowser.open(map_link)
        sys.exit(0)

   
if __name__ == "__main__":
	main()
