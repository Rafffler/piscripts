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

# Setup for relaisboard switching the heater
heater = digitalio.DigitalInOut(board.D4)
heater.direction = digitalio.Direction.OUTPUT
heater.value = True

def light_control(illuminance_lvl, illuminance, duty):
    error = illuminance_lvl - illuminance
    duty += int(Kp * error) # proportional control
    duty = max(0, min(65535, duty))  # clamp to valid range
    return duty

def temp_control(temp, temp_lvl):
    error = temp_lvl - temp
    # hysteresis is necessary to avoid flickering
    if error > 1.0:
        heater.value = False
        heater_on = True
        # print("Heating ON")
    elif error < -1.0:
        heater.value = True
        heater_on = False
        # print("Heating OFF")
    else:
        heater_on = heater.value == False
    return heater_on


def update_buttons():
    global last_state_1, last_state_2, last_time_1, last_time_2

    now = time.monotonic()
    set_temp = False
    set_illuminance = False

    current_1 = btn1.value
    # detect ONLY press (True → False)
    if last_state_1 and not current_1 and (now - last_time_1) > debounce_time:
        print("Temperature control activated")
        set_temp = True
        last_time_1 = now

    last_state_1 = current_1  # always update state

    current_2 = btn2.value
    # detect ONLY press (True → False)
    if last_state_2 and not current_2 and (now - last_time_2) > debounce_time:
        print("Illuminance control activated")
        set_illuminance = True
        last_time_2 = now

    last_state_2 = current_2  # always update state

    return set_temp, set_illuminance

def read_lux():
    return(bh1750.lux)

def read_temp():
    return(bmp280.temperature)

def mqtt_publish(illuminance_lvl, temp_lvl, fixed_temp, fixed_illuminance, temp, illuminance, topic):
    if fixed_temp and fixed_illuminance:
         payload = f"field1={temp}&field2={illuminance}&field3={temp_lvl}&field4={illuminance_lvl}"
    elif fixed_temp:
        payload = f"field1={temp}&field2={illuminance}&field3={temp_lvl}"
    elif fixed_illuminance:
        payload = f"field1={temp}&field2={illuminance}&field4={illuminance_lvl}"
    else:
        payload = f"field1={temp}&field2={illuminance}&field3=NaN&field4=NaN"
    result = client.publish(topic, payload)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print("MQTT publish failed:", result.rc)
    # print("Published:", payload)

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
topic = f"channels/{channel_id}/publish"

# Create client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=client_id)

# Set authentication
client.username_pw_set(username, password)

# Connect
client.connect(broker, port, 60)

# Start loop
client.loop_start()

fixed_temp = False
fixed_illuminance = False
heater_on = True

temp_lvl= 30
illuminance_lvl = 50

try:
    while True:
        now = time.monotonic()
        # update buttons
        set_temp, set_illuminance = update_buttons()
        # read sensors
        illuminance = read_lux()
        temp = read_temp()
        # update mode flags
        if set_temp:
            fixed_temp = not fixed_temp
        if set_illuminance:
            fixed_illuminance = not fixed_illuminance
        # control LED
        if fixed_illuminance:
            duty = light_control(illuminance_lvl, illuminance, duty)
            led.duty_cycle = duty
        else:
            duty = 0
            led.duty_cycle = duty
        # control heater
        if fixed_temp:
            heater_on = temp_control(temp, temp_lvl)
        else:
            heater.value = True
            heater_on = False
        # MQTT publishing every 15s
        if now - last_publish > interval:
            print("Current Temperature: %.2f Celsius" % bmp280.temperature)
            print("Current Illuminance: %.2f Lux" % bh1750.lux)
            mqtt_publish(illuminance_lvl, temp_lvl, fixed_temp, fixed_illuminance, temp, illuminance, topic)
            last_publish = now
        # necessary because the BH1750 is too slow
        time.sleep(0.1) 
except KeyboardInterrupt:
    print("\nProgram stopped by user")
    # cleanup
    led.duty_cycle = 0
    client.loop_stop()
    client.disconnect()
    