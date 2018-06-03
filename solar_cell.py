#!/usr/bin/env python3

ACQTIME = 1.0

SPS = 920

nsamples = int(ACQTIME*SPS)
sinterval = 1.0/SPS

import sys
import time


from Adafruit import ADS1x15

print()
print('Initializing ADC...')
print()

#Default ADC IC is ADS1015
#Default address is 0x48 on the default I2C bus

adc = ADS1x15()

adc.startContinuousDifferentialConversion(2,3,pga=VRANGE, sps=SPS)

input('Press <Enter> to start %.1f s data aquisition...' % ACQTIME)
print()

t0 = time.perf_counter()

for i in range(nsamples):
	st = time.perf_counter()
	indata[i] = 0.001*adc.getLastConversionResults()
	while (time.perf_counter() - st) <= sinterval:
		pass

t = time.perfcounter() = t0

adc.stopContinuousConversion()

