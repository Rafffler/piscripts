import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

WIDTH = 128
HEIGHT = 32   # change to 64 if your display is 128x64
BORDER = 5

# SPI interface
spi = board.SPI()

# DC pin
oled_dc = digitalio.DigitalInOut(board.D6)

# OLED initialization (NO CS PIN for v3)
oled = adafruit_ssd1306.SSD1306_SPI(
    WIDTH,
    HEIGHT,
    spi,
    dc=oled_dc,
    reset=oled_reset,
    cs=None
)

# Clear display
oled.fill(0)
oled.show()

# Create image buffer
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Background
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

# Inner rectangle
draw.rectangle(
    (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
    outline=0,
    fill=0,
)

# Font
font = ImageFont.load_default()

text = "Hello IoT World!"
bbox = font.getbbox(text)
font_width = bbox[2] - bbox[0]
font_height = bbox[3] - bbox[1]

draw.text(
    (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
    text,
    font=font,
    fill=255,
)

# Show image
oled.image(image)
oled.show()