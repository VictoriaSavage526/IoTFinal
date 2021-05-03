import serial
from serial.tools.list_ports import comports

for p in comports():
    if "u-blox" in p.description:
        break

ser=serial.Serial(p.device,9600)

try:
    while True:
        readedText = ser.readline()
        print(readedText)
        

except KeyboardInterrupt:
    ser.close()
