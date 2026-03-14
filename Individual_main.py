import board
import time
import digitalio
import adafruit_bh1750

i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)


def read_lux():
    print("Current Illuminance: %.2f Lux" % bh1750.lux)

while True:
    read_lux()
    time.sleep(2)