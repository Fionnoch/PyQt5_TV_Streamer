
from time import sleep
from time import perf_counter, perf_counter_ns
import threading

# ===================================================================================================
# IR controls
class IR_reciever:
    
    def __init__(self, setup_imports, pin_num, delay_time):
        if setup_imports is True:
            import OPi.GPIO as GPIO
            import threading
            from time import perf_counter
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BOARD) 
            self.GPIO.setup(ir_gpio, GPIO.IN)
        self.pin_num = pin_num
        self.delay_time = delay_time
        self.thread_flag_event = threading.Event()

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
        self.thread_flag_event.clear()
        if clean_GPIO is True:
            self.GPIO.cleanup()

    def read_command(self, start_val):
        print("input detected")
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
        
        len_command = len(command)
          
        if len_command> 2:
            print("finished event detect, lengh of command = ", len(command), "  command recorded = ")
            print(command, 5)
            print("")

if __name__ == "__main__":
    try:
        wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
        ir_gpio = 5 # pin 
        
        gpio_input = IR_reciever(True, ir_gpio, wait_time)  #initialte the function by inputting the input pin number and the wait time (longest time between individual pulses
        thread = threading.Thread(target = gpio_input.wait_for_falling_edge) #place this into a thread so that it can run in parallel with the 
        thread.start() 
        
        print("running program press ctrl+c to stop")
        while True:
            sleep(5)
            #print("running main loop")
                        
    except KeyboardInterrupt:
        print("")
        print("program stopping") 
        
    finally: 
        gpio_input.stop_detection(True)
        thread.join()
