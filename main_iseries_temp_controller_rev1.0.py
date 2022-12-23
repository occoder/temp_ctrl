# main.py -- put your code here!
from pyb import Pin, ExtInt, UART, delay
from time import sleep
import pyb

start_pin = Pin('Y3', Pin.IN, Pin.PULL_UP) # PB8 monitors start button push event.
stop_pin = Pin('X2', Pin.IN, Pin.PULL_UP) # PA1 monitors stop button push event.
led_pin = Pin('X5', Pin.OUT_PP) # PA4 drives LED indicator.
led_pin.low()
uart = UART(2, 9600) # UART2 communcates to CSi8.
uart.init(9600, bits=7, parity=1, stop=1)
start_pressed = 0
# stop_pressed = 0
t1_set = 200
t1_last = 30
t2_set = 600
t1_t2_step = 1
t1_t2_last = 480
t2_last = 120
off_last = 390
cmd_prefix = '*P012' # Write to RAM of point 1 with positive sign and decimal point 2
cmd_standby = '*D03' # Standby mode with output off
cmd_dis_standby = '*E03'# Disable standby
start_value = 0
stop_value = 0
print(f"stop_pin.value={str(stop_pin.value())}")
print(f"start_pin.value={str(start_pin.value())}")

def start_callback(line):
  
  global start_pressed, start_int, pyb, start_pin, stop_pin
  

  #print("%d"%start_pin.value())
  if ((start_pin.value() == 0) and (stop_pin.value() == 1)): # 1 = not pressed
    start_int.disable()
    start_pressed = 1
    print("start_pressed=========")
    #pyb.hard_reset()
  else:
    #start_pressed = 0
    print("should not get here=========")

  
start_int = pyb.ExtInt(start_pin, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, start_callback)

def stop_callback(line):
  global start_pressed, stop_int, stop_value, start_pin, stop_pin, pyb, led_pin
  
  #print("stop pressed = "+str(stop_value))
  if stop_pin.value() == 0: # 1 = not pressed
    stop_int.disable()
    led_pin.low()
    pyb.hard_reset() #reset and reboot
    print("stop pressed")
    start_pressed = 0
    
stop_int = pyb.ExtInt(stop_pin, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, stop_callback)

while 1:
  #global pyb
  print(f"one loop passed-----{str(start_pressed)}")
  sleep(1)
  if start_pressed == 1:
    uart.write(cmd_dis_standby+'\r') # Disable standby from last heating cycle
    led_pin.high() 
    #sleep(10) #for test
    uart.write(cmd_prefix+'%05X'%t1_set+'\r') # Set temperature point 1, i.e. 20C
    sleep(t1_last*60) #Keep t1_set for t1_last minutes
    #sleep(2) #for test
    for i in range (t1_set, t2_set+1, t1_t2_step): #Increase 1C per loop
      uart.write(cmd_prefix+'%05X'%i+'\r') # Increase temperature point 1 until t2_set
      sleep((t1_t2_last*60/((t2_set-t1_set)/t1_t2_step)))
      #sleep(1) #for test
    sleep(t2_last*60) #Keep t2_set for t2_last minutes
    #sleep(300) #for test
    uart.write(cmd_standby+'\r') # Shut off heater
    sleep(off_last*60) #Keep off state for off_last minutes
    #sleep(2) #for test
    led_pin.low() 
    pyb.hard_reset() # Mission accomplished then reset and reboot