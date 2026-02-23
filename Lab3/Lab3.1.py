import time
import board
import digitalio

led = digitalio.DigitalInOut(board.D17)
led.direction = digitalio.Direction.OUTPUT
while True:
	led.value = True
	
	