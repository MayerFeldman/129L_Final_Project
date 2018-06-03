#!/usr/bin/env python3

#
# client.py - Connect to TCP socket
#
# 17May17  Added call to socket.shutdown()
# 16May17  Updated to use more sophisticated recv behavior
# 10May16  Everett Lipman
#
USAGE="""
usage: client.py [ipnum] port

       Open TCP connection to ipnum:port and print the output.
       ipnum defaults to 127.0.0.1
"""
N_ARGUMENTS = (1,2)

import sys
import os
import socket

###############################################################################

def usage(message = ''):
   sys.stdout = sys.stderr
   if message != '':
      print()
      print(message)
   print(USAGE)

   sys.exit(1)
###############################################################################

def check_arguments():
   """Check command line arguments for proper usage.
   """
   global nargs, progname
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
   thesock.settimeout(5)
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
###############################################################################

if __name__ == '__main__':
   nargs = check_arguments()

   if nargs == 1:
      ipnum = '127.0.0.1'
      port = int(sys.argv[1])
   else:
      ipnum = sys.argv[1]
      port = int(sys.argv[2])

   print()
   print('Connecting to %s, port %d...\n' % (ipnum, port))
   connected = True
   thesocket = open_connection(ipnum,port)
   while connected:
       #thesocket = open_connection(ipnum, port)
       indata = receive_data(thesocket, 4096)
       datastring = indata.decode()
       
       print()
       print()
       print(datastring)
       print()
       if(datastring == 'Shutting Down'):
           connected = False
           thesocket.shutdown(socket.SHUT_RDWR)
           thesocket.close()
   
