import serial
from serial.tools.list_ports import comports
import time

for p in comports():
    if "u-blox" in p.description:
        break
try:
    ser = serial.Serial (p.device, 9600)              #Open port with baud rate
except:
    print("Serial port couldn't be opened. Make sure the device is plugged in to USB.")
    exit()


# try:
#     while True:
#         readedText = ser.readline()
#         print(readedText)
try:
    while True:
        ser = serial.Serial (p.device, 9600) 
        got=0
        lines = dict()
        while True:
            line = ser.readline().decode()[1:].strip()
            print(line)
            if 'GPRMC' in line:
                if got:
                    break
                else:
                    got+=1
            if got:
                line_list = line.split(',')
                header = line_list[0] #.pop(0)
                if header not in lines:
                    if header == "GPGSV":
                        lines[header] = [line_list]
                    else:
                        lines[header] = line_list
                elif header == "GPGSV":
                    lines[header].append(line_list)

        for line in lines:
            print(line, lines[line])
        ser.close()
        time.sleep(10)
        print()

except KeyboardInterrupt:
    ser.close()
