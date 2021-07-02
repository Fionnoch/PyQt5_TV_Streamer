import pickle
import socket 
import threading

import queue
from collections import deque

import numpy
import time

import OPi.GPIO as GPIO 

PWM_CHIP = 0
PWM_PIN = 0
FREQUENCY_HZ = 3800
DUTY_CYCLE_PERCENT = 50
p = GPIO.PWM(PWM_CHIP, PWM_PIN, FREQUENCY_HZ, DUTY_CYCLE_PERCENT)    # new PWM on channel=LED_gpio frequency=38KHz


PORT = 5050
SERVER_IP = "192.168.8.190" # "192.168.0.37" # "192.168.8.164"
#SERVER_IP = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER_IP, PORT)
HEADER = 10 # 64
FORMAT = 'utf-8'
DISCONNECT_MSG = "!DISCONNECT"
DISCONNECT_MSG_ENCODED = DISCONNECT_MSG.encode(FORMAT)
KILL_MSG = "!CLOSE"
KILL_MSG_ENCODED = KILL_MSG.encode(FORMAT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

class socket_ir:
    
    def __init__(self):
        
        PWM_CHIP = 0
        PWM_PIN = 0
        FREQUENCY_HZ = 3800
        DUTY_CYCLE_PERCENT = 50
        self.pwm = GPIO.PWM(PWM_CHIP, PWM_PIN, FREQUENCY_HZ, DUTY_CYCLE_PERCENT) 
        self.thread_queue = deque() #set a queue that will be used to make sure that IR commands are finished before another one is sent


    def handle_client(self, conn, addr):
        print("new connection", addr, "connected")
        connected = True
        while connected: 
            msg_length = conn.recv(HEADER).decode(FORMAT) #wait until we know how long the message will be
            if msg_length : 
                msg_length = int(msg_length)
                msg = conn.recv(msg_length) #wait until we have recieved the message 
                
                if msg == DISCONNECT_MSG or msg == DISCONNECT_MSG_ENCODED: #check if the message is a disconnect message 
                    print("disconnecting and closing socket ")
                    connected = False 
                    
                #elif msg == KILL_MSG or msg == KILL_MSG_ENCODED:
                #    thread_queue.put("end")
                #    connected = False
                #    print("killing loop")
                    
                else: 
                    command = numpy.array(pickle.loads(msg))
                    #print(command)
                    gpio_command = threading.Thread(target=self.flash_led, args=(command, )) #the , after the command is really important!! needed to tell the thread module that the command is an array and not a series of seperate inputs 
                    self.thread_queue.join() #wait until the queue is empty. important incase a command is being processed while this is recieved.
                    gpio_command.start() # start command
        
                conn.send("Msg recieved".encode(FORMAT))
        conn.close()

    def flash_led(self, command):
        self.thread_queue.append('1') # add something to the queue as an indicator to show the process is running. This is to stop overlaps
        alternator = True
        for i in command:
            if alternator is True:
                self.pwm.start()
                time.sleep(i)
            else:
                self.pwm.stop()
                time.sleep(i)
    
        self.pwm.stop()
        self.thread_queue.popleft() # remove item from queue to allow something to be inputted

    def start(self): # issue where the code waits on the server.listen() line even when the function has been stopped in the main function. when its stopped it waits on the server.listen line and then when it excecutes it then kills the message midway causeing an error on the client side  
        server.listen() #wait for input 
        print("listening on ", SERVER_IP)
        
        while True : #thread_queue.empty():
            con, addr = server.accept() #wait for connection 
            thread = threading.Thread(target = self.handle_client, args=(con, addr))
            thread.start()
            print("active connections = ", threading.active_count() -1)


if __name__ == "__main__":
    try:
        print("starting server")
        socket_ir = socket_ir()
        socket_ir.start()

    except KeyboardInterrupt:
        print("")
        print("program stopping")
