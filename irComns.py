# Setup File
import RPi.GPIO as GPIO
import time
import adcUtil as adc
import numpy as np
import pigpio
 

IRLED = 19
DETECTOR = 25
BUTTON_1 = 17
BUTTON_2 = 16
REED_SWITCH = 13

# PWM parameters
FREQ = 38000    # [Hz] frequency
DUTY_CYCLE = 500_000   #      duty cycle
DURATION = 0.25

GPIO.setmode(GPIO.BCM)
GPIO.setup(IRLED, GPIO.OUT)

GPIO.setup(DETECTOR, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(REED_SWITCH, GPIO.IN, pull_up_down = GPIO.PUD_UP)

pi = pigpio.pi(port = 8887)


# Definitions
# Read Code
def readIR():
    start_time = time.time() # Log start time
    volts = np.zeros(0)
    while(time.time()-start_time < DURATION): # Senor Bent Measuing Data
        volts = np.append(volts, GPIO.input(DETECTOR))
    return( "1" if (volts.mean() < 0.1) else "0")
    
def waitForMove():
    # Loop Maiting Move Receive
    while GPIO.input(DETECTOR) == 1:
        time.sleep(0.01)
    time.sleep(DURATION) # Wait for duration for MSB
    
    b = readIR() # First bit
    b = b + readIR() # Second bit
    b = b + readIR() # Thrid bit
    
    return int(b, 2)

# Write Code
def sendMove(move): # Move will be from (0 - 7)
    # Convert to Binary
    binaryMove = bin(move)[2:]

    while(len(binaryMove) < 3):
        binaryMove = "0"+ binaryMove # Format into a 3 long string
    
    binaryMove = "1"+ binaryMove # Add initial Message Value

    for c in binaryMove: # Loop through the array
        if c == "1": 
            pi.hardware_PWM(IRLED, FREQ, DUTY_CYCLE) # turn the IR LED on
            time.sleep(DURATION) # Wait for time
            pi.hardware_PWM(IRLED,0,0) # turn IR Led off

        else:
            time.sleep(DURATION) # Wait for dead time
            
# Move Code
def readMove():
    buttonState_1 = 0 
    buttonState_2 = 0 
    
    move = 0
    print(f"Move: {move}")
    while GPIO.input(REED_SWITCH) == 0:
        if(buttonState_1 == 0 and GPIO.input(BUTTON_1) == 1): # Button Press
            if(move < 7):
                move = move + 1
            buttonState_1 = 1
            print(f"Move: {move}")
            
        elif(buttonState_1 == 1 and GPIO.input(BUTTON_1) == 0): # Button Release
            buttonState_1 = 0
            
        if(buttonState_2 == 0 and GPIO.input(BUTTON_2) == 1): # Button Press
            if(move > 0):
                move = move - 1
            buttonState_2 = 1
            print(f"Move: {move}")
            
        elif(buttonState_2 == 1 and GPIO.input(BUTTON_2) == 0): # Button Release
            buttonState_2 = 0
            
    print(f"Sending Move: {move}")
    return move
        
            
# Host Code
def host():
    while True:
        send_move = readMove()
        # Update Graphics
        sendMove(send_move)
        
        receive_move = waitForMove()
        # Update Graphics
    
# Partner Code
def partner():
    while True:
        receive_move = waitForMove()
        # Update Graphics
        
        send_move = readMove()
        # Update Graphics
        sendMove(send_move)


# If this is the host pi run this
host()

# If this is the partner pi run this
#partner()