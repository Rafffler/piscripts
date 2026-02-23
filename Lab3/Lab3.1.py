import time
import board
import digitalio

led1 = digitalio.DigitalInOut(board.D2)
led1.direction = digitalio.Direction.OUTPUT
led2 = digitalio.DigitalInOut(board.D3)
led2.direction = digitalio.Direction.OUTPUT
led3 = digitalio.DigitalInOut(board.D4)
led3.direction = digitalio.Direction.OUTPUT
led4 = digitalio.DigitalInOut(board.D17)
led4.direction = digitalio.Direction.OUTPUT

while True:
	led1.value = True
	led2.value = True
	led3.value = True
	led4.value = True
	time.sleep(0.1)
	led1.value = False
	led2.value = False
	led3.value = False
	led4.value = False
	time.sleep(0.1)



