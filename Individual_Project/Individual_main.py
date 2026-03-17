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
btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.UP
btn2 = digitalio.DigitalInOut(board.D27)
btn2.direction = digitalio.Direction.INPUT
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
    set_temp = False
    set_illuminance = False

    current_1 = btn1.value
    # detect ONLY press (True → False)
    if last_state_1 and not current_1 and (now - last_time_1) > debounce_time:
        print("Button 1 Pressed")
        set_temp = True
        last_time_1 = now

    last_state_1 = current_1  # always update state

    current_2 = btn2.value
    # detect ONLY press (True → False)
    if last_state_2 and not current_2 and (now - last_time_2) > debounce_time:
        print("Button 2 Pressed")
        set_illuminance = True
        last_time_2 = now

    last_state_2 = current_2  # always update state

    return set_temp, set_illuminance

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

fixed_temp = False
fixed_illuminance = False

temp_lvl= 30
illuminance_lvl = 800

while True:
    set_temp, set_illuminance = update_buttons()
    #print(f"Temp_btn: {set_temp} \nIllum_btn: {set_illuminance}")
    if set_temp:
        fixed_temp = not fixed_temp
        print(fixed_temp)
    if set_illuminance:
        fixed_illuminance = not fixed_illuminance
        print(fixed_illuminance)

    now = time.monotonic()
    # MQTT publishing every 15s
    if now - last_publish > interval:
        illuminance = read_lux()
        temp = read_temp()
        mqtt_publish(temp, illuminance, topic)
        last_publish = now
    set_illuminance = False
    set_temp = False