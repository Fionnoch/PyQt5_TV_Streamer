from random import randint

import time

import OPi.GPIO as GPIO
from time import sleep
from time import perf_counter
import threading
import numpy
from queue import Queue as thread_queue

import socket

ir_gpio = 5 # pin name = SCL.0 wPi = 1 GPIO = 11

GPIO.setmode(GPIO.BOARD)  # set up BOARD BCM SUNXI numbering

GPIO.setup(ir_gpio, GPIO.IN)

# ===================================================================================================
# IR controls

#wait_time = 4523982e-9 * 1.5 # 60e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
wait_time = 1e-2 *30

class IR_reciever:
    
    def __init__(self, pin_num, delay_time):
        self.pin_num = pin_num
        self.delay_time = delay_time
        self.socket_class = Send_Command('192.168.8.21', 5050) #localhost, port)

    def wait_for_falling_edge(self):
        while thread_flag_event.is_set() : #uses threading event to dictate when the loop should be killed
            if GPIO.input(ir_gpio) == 0:
                self.read_command(0)
                
    def wait_for_rising_edge(self):
        while thread_flag_event.is_set() :
            if GPIO.input(ir_gpio) == 1:
                self.read_command(1)

    def read_command(self, start_val):
        #print("input detected")
        command = []
        start_of_event = perf_counter()
        IR_timer = start_of_event + wait_time #make it extra long to stop the loop exiting premiturely. value will be reset inside loop
        
        previousValue = bool(start_val)
        
        while perf_counter() < IR_timer: #waits until a timer expires. the timer refers to the time after a command has not been passed. this is readjusted instide the code to make sure the entire command is captured
            #print(GPIO.input(ir_gpio)) #dont debug with this, it slows everything down too much and it misses all the inputs
            if GPIO.input(ir_gpio) != previousValue:  # Waits until change in state occurs.
                # Records the current time              maybe change to just record microseconds
                end_of_event = perf_counter() #records the end time of a signal change. the first start_of_event is above the while loop so from here out we need to record just hte$
                # Calculate time in between pulses
                command_length = end_of_event - start_of_event
                #print(command_length)
                start_of_event = perf_counter() #Resets the start time

                command.append(command_length)

                IR_timer = perf_counter() + wait_time #resets counter

                previousValue = not previousValue #value #changes previous value to current value to see if there is a change
                
        #print("finished event detect, lengh of command = ", len(command), "  command recorded = ")
        #print(command)
        #print("")
        
        len_command = len(command)
        #print("length of command = ", len_command)
          
        if len_command > 6:
            print("command recieved")
            print(command)
            print("")
            self.send_ir_command(command)
        
    def send_ir_command(self, command_to_send):
        self.socket_class.SendIR(command_to_send)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in the server.
class Send_Command:
    
    def __init__(self, localhost, port):
        self.server_address = (localhost, port)

    def SendIR(self, on_off_array):  # this sends the data
        #array_size_bytes =  on_off_array.size * on_off_array.itemsize
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if(sock.connect_ex(self.server_address) == 111):
            print('Could not create connection to base unit. Check connection.')
            sock.close()
            return(1)
        else:
            try:
                print ('connecting to %s port %s' % self.server_address)
                # Send data
                
                message = on_off_array + ' e'
                sock.sendall(message.encode('utf-8'))

                #print('sent data')

                #buff_length = len(message)

                # not looking for a response yet. possible option for debugging
                # Look for the response
                amount_received = 0
                amount_expected = len('done')
                #amount_expected = len(message)

                #wait here until data is recieved. currently this is running before data and is causing the system to crash
                #print('waiting for response')
                while (amount_received < amount_expected): #need to wait until all data is recived by otherside before closing:
                    #print('waiting for return')
                    data = sock.recv(amount_expected)
                    #print('length of data = ', len(data))
                    amount_received += len(data)
                    print ( 'received "%s"' % data.decode('utf-8'))
                    #print ('amount recieved = ', amount_recieved)
            except:
                print("could not connect/send codes check connection")

            finally:
                print ('closing socket')
                sock.close()
                return (1)

               
if __name__ == "__main__":

    ir_gpio = 5

    #-------initialise IR remote
    gpio_input = IR_reciever(ir_gpio, wait_time)  #initialte the function by inputting the input pin number and the wait time (longest time between individual pulses
    thread_flag_event = threading.Event() 
    thread_flag_event.set()
    thread = threading.Thread(target = gpio_input.wait_for_falling_edge) #place this into a thread so that it can run in parallel with the 
    thread.start()     
    
    try:
        print("running loop")
        while True:
            pass
            #print("test")
            #sleep(1)
    except KeyboardInterrupt:
        print("pressed interupt")
        thread_flag_event.clear()
        print("")
        print("program stopping")        
    finally:
        GPIO.cleanup()