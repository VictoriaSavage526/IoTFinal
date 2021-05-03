#!/usr/bin/env python3

import RPi.GPIO as GPIO
from dht11 import DHT11
import time
import datetime
import argparse
import os


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

def parseArgs():
	# set up command line argument parser
    parser = argparse.ArgumentParser(description="DHT11 Temperature and Humidity Sensor Access")
    parser.add_argument("-t", "--temp", action="store_true", help="include this flag to print temperature")
    parser.add_argument("-m", "--humidity", action='store_true', help="include this flag to print humidity")
    parser.add_argument("-c", "--clear", action='store_true', 
		help="include this flag to clear the terminal after each read. Default behavior is to keep printed output on the terminal.")
    parser.add_argument("-d", "--delay", action='store', default=0.0, const=1.0, type=float, nargs='?',
		help="include this flag to start an infinte loop. Provide a float value after the flag to specify the delay in seconds between reads. \
			If flag is present but no value is provided, the default delay is 1.0 seconds. \
			Exluding this flag or giving a value of zero means only one reading will be taken.")
    return parser.parse_args()


def main():
	args = parseArgs()
	delay = args.delay
	temp = args.temp
	hum = args.humidity
	clear = args.clear

	if temp is False and hum is False:
		temp = True
		hum = True

	# initialize GPIO
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.cleanup()

	# read data using pin 11
	instance = DHT11(pin=17)  # BCM17 / Pin 11 change accordingly
	print('\33[s',end='') #set the beginning cursor mark
	try:
		while True:
			result = instance.read()
			valid = result.is_valid()
			if valid:
				if clear:
					clear_output()
					
				print("Last valid input: " + str(datetime.datetime.now()))
				if temp:
					print("Temperature: %-3.2f C" % result.temperature)
					print("Temperature: %-3.2f F" % (result.temperature*1.8 + 32))
				if hum:
					print("Humidity: %-3.2f %%" % result.humidity)
			elif result.error_code == 1:
				print("\nERROR: Missing Data " + str(datetime.datetime.now()))
			elif result.error_code == 2:
				print("\nERROR: Invalid Checksum " + str(datetime.datetime.now()))

			if delay:
				time.sleep(delay)
			else:
				break

	except KeyboardInterrupt:
		print("Cleanup")
		GPIO.cleanup()


if __name__ == "__main__":
	main()
