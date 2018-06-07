#!/usr/bin/env python3

#
# client.py - Connect to TCP socket
#
USAGE="""
usage: client.py port

       ipnum defaults to 127.0.0.1
"""
N_ARGUMENTS = (1,2)

import sys
import os
import socket
import select
import time
import matplotlib.pyplot as plt
import numpy as np


###############################################################################

def open_connection(ipn, prt):
   """Open TCP connection to ipnum:port.
   """
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
   connect_error = s.connect_ex((ipn, prt))

   if connect_error:
      if connect_error == 111:
         usage('Connection refused.  Check address and try again.')
      else:
         usage('Error %d connecting to %s:%d' % (connect_error,ipn,prt))

   return(s)
###############################################################################

def receive_data(thesock, nbytes):
   """Attempt to receive nbytes of data from open socket thesock.
   """
   dstring = b''
   rcount = 0  # number of bytes received
   thesock.settimeout(5.1)
   while rcount < nbytes:
      try:
         somebytes = thesock.recv(min(nbytes - rcount, 2048))
      except socket.timeout:
         print('Connection timed out.', file = sys.stderr)
         break
      if somebytes == b'':
         print('Connection closed.', file = sys.stderr)
         break
      rcount = rcount + len(somebytes)
      dstring = dstring + somebytes
      
   print('\n%d bytes received.\n' % rcount)

   return(dstring)
##############################################################################

def earthquakeHandle(data):
   moddat = data.split(',')
   earth = []   
   for i in range(len(moddat)-1):
       earth.append(float(moddat[i]))
   if(int(moddat[len(moddat)-1]) == 1):
       print()
       print()
       print('          EARTHQUAKE!!!!!       ')
       print('          TAKE COVER!!!!!       ')
       print()
       print()
       
   timeArr = np.arange(0,10,10/(len(moddat)-1))
   f1 = plt.figure(1)
   plt.plot(timeArr,earth,'g', label = 'Gravity Data')
   plt.xlabel('Time elapsed (seconds)')
   plt.ylabel('Local value of gravity m/s^2')
   plt.title('Local value of gravity vs time')
   f1.show()


##############################################################################
def reportHandle(data):
   moddat = data.split(',')
   weather = moddat[0]
   isQuake = int(moddat[len(moddat) - 1])
   earth = []
   temp = []
   for i in range(1,len(moddat) - 1):
       if(i%2 == 1):
           earth.append(float(moddat[i]))
       else:
           temp.append(float(moddat[i]))
   timeArr = np.arange(0,10,0.2)
   print()
   print()
   print()
   print('The current weather in Santa Barbara is:',weather)
   print()
   print()
   print()
   if(isQuake == 1):
       print('               EARTHQUAKE!!!!!          ')
       print('                 Take Cover!            ')

       print()
       print()

   f1 = plt.figure(1)
   plt.plot(timeArr,earth,'g', label = 'Gravity Data')
   plt.xlabel('Time elapsed (seconds)')
   plt.ylabel('Local value of gravity m/s^2')
   plt.title('Local value of gravity vs time')
   f1.show()

   f2 = plt.figure(2)
   plt.plot(timeArr,temp,'b', label = 'Temperature Data')
   plt.xlabel('Time elapsed (seconds)')
   plt.ylabel('Ambient Temperature in Farenheit')
   plt.title('Ambient Temperature vs time')
   f2.show()

   input('\nPress <Enter> to exit...\n')
   return 0        

###############################################################################

def preCheck():
    inp = input('Please enter Weather, Earthquake, or Report: ')
    while(inp.lower() != 'weather' and inp.lower() != 'earthquake' and inp.lower() != 'report'):
       inp = input('Invalid entry, please enter Weather, Earthquake or Report:')
    return inp  

###############################################################################
if __name__ == '__main__':
   ipnum = '127.0.0.1'
   port = 55555

   print()
   print('Connecting to %s, port %d...\n' % (ipnum, port))
   connected = True
   thesocket = open_connection(ipnum,port)
   print('Please wait, the server is collecting some data, it should take ~3 seconds')
   time.sleep(3)
   print('Server should be complete! Continue!')

   while connected:
       #thesocket = open_connection(ipnum, port)
       message = input('Please enter Weather, Earthquake, or Report: ')
       while(message.lower() != 'weather' and message.lower() != 'earthquake' and message.lower() != 'report'):
          message = input('Invalid entry, please enter Weather, Earthquake or Report:')
 

       
       thesocket.send(message.encode())
       data = thesocket.recv(4096).decode()
    
       if(message.lower() == 'report'):
          reportHandle(data)
       elif(message.lower() == 'earthquake'):
          earthquakeHandle(data)
       elif(message.lower() == 'weather'):
          print()
          print()
          print(data)
          print()
          print()
       ans = input('Continue? (y/n) ')
    
       if ans == 'y':
          continue
       else:
    
          break

   thesocket.shutdown(socket.SHUT_RDWR)
   thesocket.close()   

