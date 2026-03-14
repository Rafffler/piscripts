import board
import time
# import digitalio
import adafruit_bh1750
import adafruit_bmp280
import paho.mqtt.client as mqtt

i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)


def read_lux():
    print("Current Illuminance: %.2f Lux" % bh1750.lux)
    return(bh1750.lux)

def read_temp():
    print("Current Temperature: %.2f Celsius" % bmp280.temperature)
    return(bmp280.temperature)

while True:
    illuminance = read_lux()
    temp = read_temp()
    time.sleep(1)
    # next step implement MQTT publishing of values to Thingspeak dashboard