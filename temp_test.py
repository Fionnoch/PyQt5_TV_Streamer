import OPi.GPIO as GPIO

if __name__ == "__main__":

    PWM_chip = 0
    PWM_pin = 0
    frequency_Hz = 38000
    Duty_Cycle_Percent = 100

    p = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, Duty_Cycle_Percent)    # new PWM on channel=LED_gpio frequency=38KHz

    print("Enable pwm by pressing button, signal wont start until duty cycle is set")
    input()
    p.start_pwm()

    print("set light to full brightness")
    input()
    p.duty_cycle(100)

    print("dimm pwm by pressing button")
    input()
    p.duty_cycle(50)

    print("change pwm frequency by pressing button")
    input()
    p.change_frequency(500)

    print("stop pwm by reducing duty cycle to 0 by pressing button")
    input()
    p.duty_cycle(0)

    print("Invert PWM polarity by pressing button")
    input()
    p.pwm_polarity("invert")

    print("increase duty cycle but inverted so light will dim. press button to contunue")
    input()
    p.duty_cycle(75)

    print("reduce duty cycle. press button to contunue")
    input()
    p.duty_cycle(25)

    print("stop pwm (it was inverted so it shoudl be full brightness), press button to contunue")
    input()
    p.duty_cycle(0)
    
    print("change polarity by pressing button")
    input()
    p.pwm_polarity() # this should turn off the light but pwm_polarity only seems to work once

    print("disable PWM. Press button to continue")
    input()
    p.stop_pwm() # this should turn off the light but pwm_polarity only seems to work once


    print("remove object and deactivate pwm pin, press button to contunue")
    input()
    p.pwm_close()
    del p  # delete the class