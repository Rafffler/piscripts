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

delays = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 0.5, 0.5, 0.5]

while True:
	for delay in delays:
		led1.value = True
		led2.value = True
		led3.value = True
		led4.value = True
		time.sleep(delay)
		led1.value = False
		led2.value = False
		led3.value = False
		led4.value = False
		time.sleep(0.5)
	time.sleep(1)




