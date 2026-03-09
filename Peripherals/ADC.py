import time
import board
import busio
import digitalio
# --- Setup ---
# Initialize SPI (SCLK, MOSI, MISO)
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
# Initialize CS (GPIO 24)
cs_adc = digitalio.DigitalInOut(board.D24)
cs_adc.direction = digitalio.Direction.OUTPUT
cs_adc.value = True # Idle High
# Configure SPI speed and mode
while not spi.try_lock():
    pass
spi.configure(baudrate=500000, polarity=0, phase=0)
spi.unlock()
def activate_adc():
    cs_adc.value = False # Select the chip
    time.sleep(0.000005)
def deactivate_adc():
    cs_adc.value = True # Deselect the chip
    time.sleep(0.000005)
def read_adc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    # SPI Command: [Start Bit, (SGL/DIFF + Channel bits), Don't Care]
    command = bytes([1, (8 + adcnum) << 4, 0])
    result = bytearray(3)
    if spi.try_lock():
        # This sends command and fills result simultaneously
        spi.write_readinto(command, result)
        spi.unlock()
    # Extract 10-bit result from MCP3008 response
    adcout = ((result[1] & 3) << 8) + result[2]
    return adcout
# --- Main Loop ---
try:
    while True:
        activate_adc()
        tmp0 = read_adc(0)
        deactivate_adc()
        print(f"Channel 0 Value: {tmp0}")
        time.sleep(0.2)
except KeyboardInterrupt:
    cs_adc.value = True
    print("\nProgramm terminated")