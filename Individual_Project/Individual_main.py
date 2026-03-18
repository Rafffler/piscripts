import board
import time
import digitalio
import adafruit_bh1750
import adafruit_bmp280
import pwmio
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

# Setup LED for PWM
duty = 0
led = pwmio.PWMOut(board.D12, frequency=1000, duty_cycle=duty)
Kp = 20 # proportional gain of the control loop, value between 10 and 100

def light_control(illuminance_lvl, illuminance, duty):
    error = illuminance_lvl - illuminance
    duty += int(Kp * error) # proportional control
    duty = max(0, min(65535, duty))  # clamp to valid range
    return duty

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
    # print("Current Illuminance: %.2f Lux" % bh1750.lux)
    return(bh1750.lux)

def read_temp():
    # print("Current Temperature: %.2f Celsius" % bmp280.temperature)
    return(bmp280.temperature)

def mqtt_publish(illuminance_lvl, temp_lvl, fixed_temp, fixed_illuminance, temp, illuminance, topic):
    if fixed_temp & fixed_illuminance:
         payload = f"field1={temp}&field2={illuminance}&field3={temp_lvl}&field4={illuminance_lvl}"
    elif fixed_temp:
        payload = f"field1={temp}&field2={illuminance}&field3={temp_lvl}"
    elif fixed_illuminance:
        payload = f"field1={temp}&field2={illuminance}&field4={illuminance_lvl}"
    else:
        payload = f"field1={temp}&field2={illuminance}&field3=NaN&field4=NaN"
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
illuminance_lvl = 50

try:
    while True:
        illuminance = read_lux()
        temp = read_temp()
        set_temp, set_illuminance = update_buttons()
        if set_temp:
            fixed_temp = not fixed_temp
        if set_illuminance:
            fixed_illuminance = not fixed_illuminance
        now = time.monotonic()
        # MQTT publishing every 15s
        if now - last_publish > interval:
            mqtt_publish(illuminance_lvl, temp_lvl, fixed_temp, fixed_illuminance, temp, illuminance, topic)
            last_publish = now
        set_illuminance = False
        set_temp = False
        if fixed_illuminance:
            duty = light_control(illuminance_lvl, illuminance, duty)
            led.duty_cycle = duty
        else:
            duty = 0
            led.duty_cycle = duty
        time.sleep(0.1) # necessary because the BH1750 is too slow

except KeyboardInterrupt:
    print("\nProgram stopped by user")
    # cleanup
    led.duty_cycle = 0
    client.loop_stop()
    client.disconnect()
    