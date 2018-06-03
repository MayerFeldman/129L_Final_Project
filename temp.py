#!/usr/bin/env python3

'''
Read data from the temperature sensor and convert from Celcius to Farenheit
'''

import Adafruit.MCP9808 as MCP9808

def cel2far(T):
	"""Convert T from Celsius to Farenheit"""
	return(1.8*T + 32.0)

#Define the sensor
sensor = MCP9808()
#Begin taking data
sensor.begin()
#Read the temperature in Celsius
Tc = sensor.readTempC()
#Convert from C to F
Tf = cel2far(Tc)
