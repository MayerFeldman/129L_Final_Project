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

#Initialize sensors/lock statements for threaded server.
sensor = MCP9808()
lsm303 = Adafruit_LSM303.LSM303()
print_lock = threading.Lock()
connect = True

##################################################################################

def bind_port(port):
    """Create socket and bind to port
    """
    print('binding to port ', str(port))
    host = ''
	#creating the socket for the server   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#binding the socket to the port on the pi.
    s.bind((host,port))
	#listen to incoming connection, blocks the port until a connection is established.
    s.listen(1)
    return(s)

##################################################################################

def threaded(connection):
    """Thread that handles client/server communication closes connection and thread
       when client sends no data
    """
    gravDat = avgGrav()
    gravity = gravDat[0]
    stdDev = gravDat[1]
    while True:
#data will be anything that is recieved from the connection that's established.
       data = connection.recv(4096)
       if not data:
#if theres no data, connection and thread needs to be closed.
          print('Goodbye')
#release the print lock, thread will be closed
          print_lock.release()
          global connect 
          connect = False
          print(connect)
          break
#handle the different messages we receive
       if data.decode().lower() == 'weather':
          connection.send(weatherHandle().encode())
       elif data.decode().lower() == 'earthquake':
          connection.send(earthquakeHandle(gravity,stdDev).encode())
       elif data.decode().lower() == 'report':
          connection.send(reportHandle(gravity).encode())
       else:
#dummy send value.
          connection.send(data)
#close the connection after while loop is broken
    connection.close()



################################################################################

def cel2far(T):
    return(1.8*T + 32.0)

def weatherHandle():
    """Function reads a temperature from the temp sensor, grabs forecast from online,
    and return both the temp and forecast.
    """
    global sensor


    sensor.begin()
    Tc = sensor.readTempC()
    Tf = cel2far(Tc)

    page = requests.get('https://www.timeanddate.com/weather/usa/santa-barbara')
    soup = BeautifulSoup(page.text, 'html.parser')
#use beautiful soup to find the forecast from the html file.
    findOvercast = soup.find('p').text
    weather = 'It is ' + str(Tf) + ' degrees Farenheit and ' + findOvercast
    return weather 

#################################################################################
def avgGrav():
    """Gather data from accelerometer and average the data to find the acceleration
       due to gravity at the location the user is at
    """
    global lsm303
    start = time.perf_counter()
    print('Gathering data for the average gravity reading, please do not shake the accelerometer')
    avgmag = 0
#gather 1000 data points from the accelerometer to get the average value for the gravity
    for i in range(1000):
        accel,mag = lsm303.read()
        accel_x,accel_y,accel_z = accel
#find the magnitude of the acceleration in all 3 dimensions
        addto = math.sqrt((accel_x/100)**2+(accel_y/100)**2+(accel_z/100)**2)
#have a running sum of the magnitudes to average later
        avgmag += addto
    avgmag /= 1000
    stdDev = abs(avgmag - 9.81)
    end = time.perf_counter()
    print(end-start)
    print('Data collection finished, you may choose an option clientside')
    return((avgmag,stdDev))

################################################################################    

def earthquakeHandle(gravity, stdDev):
    """Gather data for 5 seconds and return all the data in a string.
    """
    print('Gathering Accelerometer data for 10 seconds')
    count = 0
    npoint = 10
    sleeptime = 1/10
    diffsum = 0
    gravvals = ''
    start = time.perf_counter()
    nettime = 0
    flag = False
    while nettime < 10:
        while count < npoint and nettime < 10:
           accel,magn = lsm303.read()
           accel_x,accel_y,accel_z = accel
           mag = math.sqrt((accel_x/100)**2 + (accel_y/100)**2 + (accel_z/100)**2)
           diff = abs(mag-gravity)
           if(diff >= 0.4):
              flag = True
           count += 1
           gravvals += str(mag) + ','
           time.sleep(0.1)
        count = 0
        end = time.perf_counter()
        nettime = end - start
    if(flag == True):
        gravvals += '1'
        return(gravvals)
    gravvals += '0'
    return(gravvals)

#################################################################################

def reportHandle(gravity):
    """Gathering eathquake data for 10 seconds, plot it on a graph client side, and print out the
    forecast.
    """
    print('Gathering Accelerometer and Temperature data for 10 seconds')
    global sensor
#begin the sensor initialized earlier and acquire temperature data.
    sensor.begin()
#use requests to grab html data from website below
    page = requests.get('https://www.timeanddate.com/weather/usa/santa-barbara')
    soup = BeautifulSoup(page.text, 'html.parser')
#use beautiful soup to find the forecast from the html file.
    findOvercast = soup.find('p').text
    
    count = 0
    npoint = 10
    sleeptime = 1/10
    diffsum = 0 
    alldata = str(findOvercast) + ',' 
    start = time.perf_counter()
    nettime = 0
    flag = False
    while nettime <= 10:
        while (count < npoint or nettime <=10):
            accel, magn = lsm303.read()
            accel_x,accel_y,accel_z = accel
            mag = math.sqrt((accel_x/100)**2 + (accel_y/100)**2 + (accel_z/100)**2)
           
            if(abs(mag - gravity) >= 0.4):
                flag = True

            count += 1
            alldata += str(mag)
            
            Tc = sensor.readTempC()
            Tf = cel2far(Tc)

            alldata += ',' + str(Tf) + ','
            end = time.perf_counter()
            nettime = end - start
            time.sleep(0.2)
        end2 = time.perf_counter()
        nettime = end2 - start

    if flag:
        alldata += '1'
        return alldata
    alldata += '0'
    return alldata

##############################stdDev)##################################################

def inpHandler(recdat):
    npoint = 10
    sleeptime = 1/10
    diffsum = 0
    gravvals = []
    tempvals = []
    alldata = []
    start = time.perf_counter()
    nettime = 0
    flag = False
    while nettime <= 10:
        while (count < npoint or nettime <=10):
            accel, magn = lsm303.read()
            accel_x,accel_y,accel_z = accel
            mag = math.sqrt((accel_x/100)**2 + (accel_y/100)**2 + (accel_z/100)**2)

            if(abs(mag - gravity) >= 0.4):
                flag = True
            count += 1

    """Handle all the inputs from the client
    """
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
    
