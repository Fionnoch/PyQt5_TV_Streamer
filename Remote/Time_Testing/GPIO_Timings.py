# importing the required module 
import timeit 
  
# code snippet to be executed only once 
mysetup = '''
import OPi.GPIO as GPIO
PWM_CHIP = 0
PWM_PIN = 0
FREQUENCY_HZ = 3800
DUTY_CYCLE_PERCENT = 50
pwm = GPIO.PWM(PWM_CHIP, PWM_PIN, FREQUENCY_HZ, DUTY_CYCLE_PERCENT) 
'''
  
# code snippet whose execution time is to be measured 
mycode = ''' 
def tutn_on_pwm(): 
    pwm.start() 
'''
  
# timeit statement 
time = timeit.timeit(setup = mysetup,
                     stmt = mycode,
                     number = 10000)
print (time/10000) 