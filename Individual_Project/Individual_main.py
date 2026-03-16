import board
import time
# import digitalio
import adafruit_bh1750
import adafruit_bmp280
import paho.mqtt.client as mqtt

# Initialization for the I2C bus
i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)


def read_lux():
    print("Current Illuminance: %.2f Lux" % bh1750.lux)
    return(bh1750.lux)

def read_temp():
    print("Current Temperature: %.2f Celsius" % bmp280.temperature)
    return(bmp280.temperature)

def mqtt_publish(temp, illuminance, topic):
    payload = f"field1={temp}&field2={illuminance}"
    client.publish(topic, payload)
    print("Published:", payload)


# ThingSpeak MQTT credentials
broker = "mqtt3.thingspeak.com"
port = 1883

client_id = "AwwzCBAZOQwDNgIEMjAOETo"
username = "AwwzCBAZOQwDNgIEMjAOETo"
password = "JCTweFsgwqOj5XtTaYBl0/j9"

channel_id = "3300174"
# intervall of 15 secs for MQTT transmission
interval = 15
last_publish = 0
# f allows to embed variables directly inside a string
topic = f"channels/{channel_id}/publish"

# Create client
client = mqtt.Client(client_id=client_id)

# Set authentication
client.username_pw_set(username, password)

# Connect
client.connect(broker, port, 60)

# Start loop
client.loop_start()
i = 0

while True:
    # gather sensor values
    illuminance = read_lux()
    temp = read_temp()
    now = time.monotonic()
    if now - last_publish > interval:
        mqtt_publish(temp, illuminance, topic)
        last_publish = now
    i += 1
    print("Loop number ", i)

    
   