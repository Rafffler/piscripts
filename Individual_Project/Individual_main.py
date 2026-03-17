import board
import time
import digitalio
import adafruit_bh1750
import adafruit_bmp280
import paho.mqtt.client as mqtt

# Initialization for the I2C bus
i2c = board.I2C()
bh1750 = adafruit_bh1750.BH1750(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Initialization for digital GPIOs
btn1 = digitalio.DigitalInOut(board.D17)
btn1.direction = digitalio.DigitalInOut.INPUT
btn1.pull = digitalio.Pull.UP
btn2 = digitalio.DigitalInOut(board.D27)
btn2.direction = digitalio.DigitalInOut.INPUT
btn2.pull = digitalio.Pull.UP

# Setup for button input
last_state_1 = btn1.value
last_state_2 = btn2.value
last_time_1 = 0
last_time_2 = 0
debounce_time = 0.02  # 20 ms

def update_buttons():
    global last_state_1, last_state_2, last_time_1, last_time_2

    now = time.monotonic()

    current_1 = btn1.value
    if current_1 != last_state_1 and (now - last_time_1) > debounce_time:
        print("Button 1 Pressed" if not current_1 else "Button 1 Released")
        last_state_1 = current_1
        last_time_1 = now

    current_2 = btn2.value
    if current_2 != last_state_2 and (now - last_time_2) > debounce_time:
        print("Button 2 Pressed" if not current_2 else "Button 2 Released")
        last_state_2 = current_2
        last_time_2 = now

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

while True:
    update_buttons()
    now = time.monotonic()
    # MQTT publishing every 15s
    if now - last_publish > interval:
        illuminance = read_lux()
        temp = read_temp()
        mqtt_publish(temp, illuminance, topic)
        last_publish = now