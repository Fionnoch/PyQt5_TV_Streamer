
from time import sleep
from time import perf_counter
import threading

import socket

# ===================================================================================================
# IR controls

class IR_reciever:
    #core funtionality in ir-test
    #Differences are: 
    #   1. sends commands over socket to base unit
 
    def __init__(self, pin_num, delay_time):
        self.pin_num = pin_num
        self.delay_time = delay_time
        
        import OPi.GPIO as GPIO
        import threading
        from time import perf_counter
        self.GPIO = GPIO
        self.GPIO.setmode(GPIO.BOARD) 
        self.GPIO.setup(ir_gpio, GPIO.IN)
        
        self.thread_flag_event = threading.Event()
        self.socket_class = Send_Command('192.168.8.21', 5050) #localhost, port)

    def wait_for_falling_edge(self):
        self.thread_flag_event.set()
        while self.thread_flag_event.is_set() : #uses threading event to dictate when the loop should be killed
            if self.GPIO.input(ir_gpio) == 0:
                self.read_command(0)
                
    def wait_for_rising_edge(self):
        self.thread_flag_event.set()
        while self.thread_flag_event.is_set() :
            if self.GPIO.input(ir_gpio) == 1:
                self.read_command(1)
            
    def stop_detection(self, clean_GPIO):
        self.socket_class.send_disconnect()
        self.thread_flag_event.clear()
        if clean_GPIO is True:
            self.GPIO.cleanup()

    def read_command(self, start_val):
        #print("input detected")
        command = []
        start_of_event = perf_counter()
        IR_timer = start_of_event + wait_time #make it extra long to stop the loop exiting premiturely. value will be reset inside loop
        
        previousValue = bool(start_val)
        
        while perf_counter() < IR_timer: #waits until a timer expires. the timer refers to the time after a command has not been passed. this is readjusted instide the code to make sure the entire command is captured
            #print(GPIO.input(ir_gpio)) #dont debug with this, it slows everything down too much and it misses all the inputs
            if self.GPIO.input(ir_gpio) != previousValue:  # Waits until change in state occurs.
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
            self.send_ir_command(command) #compare value
        
    def send_ir_command(self, command_to_send):
        self.socket_class.SendIR(command_to_send)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in the server.
class Send_Command:
    
    def __init__(self, localhost, port): 
        
        import pickle 
        
        self.pickle = pickle
        
        self.HEADER = 10 # 64
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MSG = "!DISCONNECT"
        self.KILL_MSG = "!CLOSE"  
        self.server_address = (localhost, port)
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client_sock.send(send_length)
        self.client_sock.send(message) 
        print(self.client.recv(50).decode(self.FORMAT))

    def send_disconnect(self):
        message = self.DISCONNECT_MSG.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client_sock.send(send_length)
        self.client_sock.send(message) 
        self.client_sock.shutdown(socket.SHUT_RDWR)
        self.client_sock.close()
        print("disconnect sent and socket closed")

    def SendIR(self, on_off_array):  # this sends the data
        #self.client_sock.connect(self.server_address)

        if(self.client_sock.connect_ex(self.server_address) == 0 or 106): # 0 means the connection was successful 
            try:
                #----- send data ------
                message = self.pickle.dumps(on_off_array) #pickle converts to byte
                #message = on_off_array.encode(self.FORMAT)
                msg_length = len(message)
                send_length = str(msg_length).encode(self.FORMAT)
                send_length += b' ' * (self.HEADER - len(send_length))
                
                print ('connecting to %s port %s' % self.server_address)
                
                self.client_sock.send(send_length) #send the length of the command 
                self.client_sock.send(message)               
                print(self.client_sock.recv(50).decode(self.FORMAT))
                
            except:
                print("could not connect/send codes check connection")
                #sock.close()
                #return (1)
            finally:
                print ('finished socket')
                #self.client_sock.close()
                #return (1)
               
        else:
            print('Could not create connection to base unit. Check connection.')
            #self.client_sock.close()
            #return(1)
               
if __name__ == "__main__":

    try:
        #-------initialise IR remote
        wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
        ir_gpio = 5
        
        gpio_input = IR_reciever(ir_gpio, wait_time)  #initialte the function by inputting the input pin number and the wait time (longest time between individual pulses
        thread = threading.Thread(target = gpio_input.wait_for_falling_edge) #place this into a thread so that it can run in parallel with the 
        thread.start() 

        print("running program press ctrl+c to stop")
        while True:
            sleep(5)
            print("running main loop")                        
    
    except KeyboardInterrupt:
        print("")
        print("program stopping") 
        
    finally: 
        gpio_input.stop_detection(True) #stop the ir funcion and clean up the gpio's so they dont block in future
        thread.join()