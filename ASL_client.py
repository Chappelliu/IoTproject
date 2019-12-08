#modified from lesson2 socket
#mimics the ebedded system on the assembly line
from tkinter import *
import sys
import random
import socket
import datetime, time


#function list
false_list = [10,15,18]
false_node = random.choice(false_list)
i = 0
sleep_list = [1,2,3,4,5,6,7]
part_list = ['chassis','body']
part = random.choice(part_list)
model_list = ['SVW', 'BMW', 'Benz']
model = random.choice(model_list)
HOST = '192.168.1.215'        # The remote host IP address
PORT = 50007              # The same port as used by the server
while 1:
    sleep_time = random.choice(sleep_list)
    if i == false_node:
        part = random.choice(part_list)
        model = random.choice(model_list)
        false_node = false_node + 3
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #simulate the signal from the sensor.
    #the node will read the exact information from the things on the assembly line
    Node_list = ['Node1', 'Node2', 'Node3']
    node = random.choice(Node_list)
    data = '{0}, {1}, {2}, {3}.'.format(model,part,node,datetime.datetime.now())
        #send the read data to the server
    s.sendall(data.encode())
    data = s.recv(1024).decode()
    s.close()
    print('Sended', repr(data))
    i = i + 1
    time.sleep(sleep_time)


