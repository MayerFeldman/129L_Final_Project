#!/usr/bin/env python3

USAGE = """
usage: server.py port [file]

	   Serve data from specified port.
	   Default message is sent if no file is specified.
"""

N_ARGUMENTS = (1,2)

import sys
import os
import socket
import time

###############################################################################

def usage(mesage = ''):
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

###############################################################################

def bind_port(prt):
    """Create socket and bind to port prt.
    """
    print('binding to port' +str(prt))	
    host = '' #bind to all available interfaces

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reuse port
    s.bind((host,prt))
    s.listen(1)
    return(s)

###############################################################################

if __name__ == '__main__':
    nargs = check_arguments()
    port = int(sys.argv[1])
	
    if nargs == 1 and port == 55555:
        outdata = b'\n\nHello from the server.py program!\n\n'
    else:
        filename = sys.argv[2]
        with open(filename, 'rb') as datafile:
            outdata = datafile.read()
	
    count = 0
    connect = True
    thesocket = bind_port(port)
    closeVal = 'Shutting Down'
    closeVal = closeVal.encode()
    
    connection, peer = thesocket.accept()
    while connect:
        thesocket.listen(1)
        data = connection.recv(1024)
        if(data == '\n'):
            outdata = b'Thanks for talking to me!\n ' + str(count)
            connection.sendall(outdata)
        if(count == 20):
            connection.sendall(closeVal)
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        count += 1

            
    '''while connect:
        connection, peer = thesocket.accept()
        if(count == 0):
            outdata = b'\nWelcome to the MC weather station!\n'
            connection.sendall(outdata)
        elif(count == 20):
            connect = False
            connection.sendall(closeVal)
        else:
            moddat = str(count)
            moddat = moddat +'\n'
            outdata = moddat.encode()
            connection.sendall(outdata)
        count += 1
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
    '''
