
import time
from time import perf_counter, perf_counter_ns
import threading

import OPi.GPIO as GPIO 
 
class ir:
    
    def __init__(self):
        
        PWM_CHIP = 0
        PWM_PIN = 0
        frequency_hz = 38000
        DUTY_CYCLE_PERCENT = 50
        self.listening_for_connection = True
        self.pwm = GPIO.PWM(PWM_CHIP, PWM_PIN, frequency_hz, DUTY_CYCLE_PERCENT) 
        
        self.event = threading.Event()
        
    def change_hz(self, hz):
        self.pwm.change_frequency(hz)
        print("frequency set to ", hz)
        
    def stop_pwm(self):
        self.pwm.pwm_close()

    def flash_led(self, command, on_adjust, off_adjust):
        #self.thread_queue.append('1') # add something to the queue as an indicator to show the process is running. This is to stop overlaps
        print("flashing led")
        alternator = True #
         
        for i in command:
            if alternator is True:
                #start = perf_counter_ns() 
                self.pwm.start_pwm()
                #time.sleep(i+on_adjust) # need to minus time taken to start up 
                self.event.wait(i)
                #while perf_counter_ns() - start + on_adjust <= i:
                #    pass
            else:
                self.pwm.stop_pwm()
                #time.sleep(i+off_adjust)
                self.event.wait(i)
                #while perf_counter_ns() - start + off_adjust <= i:
                #    pass
                
            alternator = not(alternator)
    
        self.pwm.stop_pwm()
        #self.thread_queue.popleft() # remove item from queue to allow something to be inputted
        print("finished flashing LED")





if __name__ == "__main__":
    try:
        wait_time = 6e-3 # in seconds should be just higher than the longest wait. think longest is about 5ms. noted from looking theough sky remote commands
        ir_gpio = 5 # pin 
        calibration = ir()
        test_command = [.02, .02, .02, .02, .02, 
                        .02, .02, .02, .02, .02 ]
        wait_time = 5
        
        test = [38000, 38000, 38000] #range(37900, 38100, 100)
        
        on_adjust = 0 #-0.0011
        off_adjust = 0 #0.0006
        
        print("running program press ctrl+c to stop")
        while True:
            for i in test:
                #calibration.change_hz(i)
                print ("flashing Command at ", i, " Hz")
                print("Command is: ")
                print( test_command )
                test_command_adj = [x + on_adjust for x in test_command]
                calibration.flash_led(test_command_adj, on_adjust, off_adjust)
                print("waiting ", wait_time, "seconds")
                time.sleep(wait_time)
                print("")
                        
    except KeyboardInterrupt:
        print("")
        #print("program stopping") 
        
    finally: 
        calibration.stop_pwm()
