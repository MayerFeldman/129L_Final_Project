#!/usr/bin/env python3

import time
import Adafruit_LSM303

lsm303 = Adafruit_LSM303.LSM303()

print('Printing accelerometer X,Y,Z axis values, press Ctrl-C to quit...')

while True:
	accel,mag = lsm303.read()
	accel_x,accel_y,accel_z = accel
	print('Accel X={0}, Accel Y = {1}, Accel Z = {2}'.format(accel_x/100,accel_y/100,accel_z/100))
	time.sleep(0.5)
