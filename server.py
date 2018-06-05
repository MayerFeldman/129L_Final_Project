#!/usr/bin/env python3


USAGE = """
usage: server.py port 

	   Serve data from specified port.
"""

N_ARGUMENTS = (1,2)

import sys
import os
import socket
import time
from _thread import *
import threading
import requests
from bs4 import BeautifulSoup
import Adafruit_LSM303
import math
import Adafruit.MCP9808 as MCP9808

sensor = MCP9808()
lsm303 = Adafruit_LSM303.LSM303()
print_lock = threading.Lock()
connect = True
##################################################################################

def usage(message = ''):
    sys.stdout = sys.stderr
    if message != '':
       print()
       print(message)
    print(USAGE)

    sys.exit(1)

##################################################################################

def check_arguments():
    """Check command line args for proper usage
    """
    global nargs, prognam
    nargs = len(sys.argv) - 1
    progname = os.path.basename(sys.argv[0])
    flag = True
    if nargs != 0 and N_ARGUMENTS[-1] == '*':
       flag = False
    else: 
       for i in N_ARGUMENTS:
          if nargs == i:
             flag = False
    if flag: 
       usage()
    return(nargs)

##################################################################################

def bind_port(port):
    '''Create socket and bind to port
    '''
    print('binding to port ', str(port))
    host = ''
   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen(1)
    return(s)

##################################################################################

def threaded(connection):
    gravDat = avgGrav()
    gravity = gravDat[0]
    stdDev = gravDat[1]
    while True:
       data = connection.recv(4096)
       if not data:
          print('Goodbye')
          print_lock.release()
          global connect 
          connect = False
          print(connect)
          break
       if data.decode() == 'Weather':
          connection.send(weatherHandle().encode())
       elif data.decode() == 'Earthquake':
          connection.send(earthquakeHandle(gravity,stdDev).encode())
       elif data.decode() == 'Report':
          connection.send(reportHandle().encode())
       else:

          connection.send(data)
    connection.close()



################################################################################

def example():
    return('Call Function was a success!')
def cel2far(T):
    return(1.8*T + 32.0)

def weatherHandle():
    global sensor
    sensor.begin()
    Tc = sensor.readTempC()
    Tf = cel2far(Tc)
    page = requests.get('https://www.timeanddate.com/weather/usa/santa-barbara')
    soup = BeautifulSoup(page.text, 'html.parser')
    findOvercast = soup.find('p').text
    weather = findOvercast + ', ' + str(Tf) + ' degrees Farenheit'
    return weather 

#################################################################################
def avgGrav():
    global lsm303
    start = time.perf_counter()
    print('Gathering data for the average gravity reading, please do not shake the acclerometer')
    avgmag = 0
    for i in range(1000):
        accel,mag = lsm303.read()
        accel_x,accel_y,accel_z = accel
        addto = math.sqrt((accel_x/100)**2+(accel_y/100)**2+(accel_z/100)**2)
        avgmag += addto
    avgmag /= 1000
    stdDev = abs(avgmag - 9.81)
    end = time.perf_counter()
    print(end-start)
    print('Data collection finished, you may choose an option clientside')
    return((avgmag,stdDev))

################################################################################    

def earthquakeHandle(gravity, stdDev):
    print('Gathering Accelerometer data for 10 seconds')
    count = 0
    npoint = 10
    sleeptime = 1/10
    diffsum = 0
    gravvals = ''
    start = time.perf_counter()
    nettime = 0
    allvals = ''
    while nettime < 1.0:
        while count < npoint:
           accel,mag = lsm303.read()
           accel_x,accel_y,accel_z = accel
           mag = math.sqrt((accel_x/100)**2 + (accel_y/100)**2 + (accel_z/100)**2)
           diff = abs(mag-gravity)
           if(diff >= 0.4):
              return('EARTHQUAKE!')
           count += 1
           gravvals += ',' + str(mag)
           time.sleep(sleeptime)
        allvals += ',' + gravvals
        end = time.perf_counter()
        nettime = end - start
    return(allvals)

#################################################################################

def reportHandle():
    print('This is the Report Handler!')
    return('This is the Report Handler!')

##############################stdDev)##################################################

def inpHandler(recdat):
    
    if recdat.decode() == 'Weather':
       return(weatherHandle())

    elif recdat.decode() == 'Earthquake':
       return(earthquakeHandle())
 
    elif recdat.decode() == 'Report':
       return(reportHandle())

    else:
       return(recdat.decode())

################################################################################

if __name__ == '__main__':
    ipnum = '127.0.0.1'
    port = 55555
    count = 0
    thesocket = bind_port(port)
    closeVal = 'Shutting Down'
    closeVal = closeVal.encode()
    connect = True
    while connect:
       connection, peer = thesocket.accept()
       print_lock.acquire()
       thr = threading.Thread(target = threaded, args = (connection,))
       thr.start()
       
       
    #thesocket.shutdown(socket.SHUT_RDWR)
    #thesocket.close()   
    
