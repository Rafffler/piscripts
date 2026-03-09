import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# ---------------------------
# OLED CONFIGURATION
# ---------------------------

WIDTH = 128
HEIGHT = 32
BORDER = 5

# Define pins
oled_reset = digitalio.DigitalInOut(board.D25)
oled_dc = digitalio.DigitalInOut(board.D24)
oled_cs = digitalio.DigitalInOut(board.D17)

# Initialize SPI
spi = board.SPI()

# Initialize OLED display
oled = adafruit_ssd1306.SSD1306_SPI(
    WIDTH,
    HEIGHT,
    spi,
    oled_dc,
    oled_reset,
    oled_cs
)

# ---------------------------
# CLEAR DISPLAY
# ---------------------------

oled.fill(0)
oled.show()

# ---------------------------
# CREATE IMAGE BUFFER
# ---------------------------

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Draw white background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Draw inner black rectangle
draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0
)

# ---------------------------
# TEXT SETTINGS
# ---------------------------

font = ImageFont.load_default()
text = "Hello IoT World!"

# Get text size
bbox = font.getbbox(text)
font_width = bbox[2] - bbox[0]
font_height = bbox[3] - bbox[1]

# Center the text
x = oled.width // 2 - font_width // 2
y = oled.height // 2 - font_height // 2

# Draw text
draw.text((x, y), text, font=font, fill=255)

# ---------------------------
# DISPLAY IMAGE
# ---------------------------

oled.image(image)
oled.show()

print("Test sent to OLED")