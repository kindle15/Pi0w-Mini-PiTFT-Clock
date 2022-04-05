#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Import Python System Libraries
import time
import json
import subprocess
import os

# Import Requests Library
import requests

#Import Blinka
import digitalio
import board

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
import adafruit_rgb_display.st7789 as st7789

api_url = 'http://localhost/admin/api.php'

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, width=135, height=240, x_offset=53, y_offset=40)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width   # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new('RGB', (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38)
# https://github.com/opensourcedesign/fonts/blob/master/anonymousPro/AnonymousPro-1.002.001/Anonymous%20Pro.ttf
font2 = ImageFont.truetype('/usr/share/fonts/truetype/anonymous-pro/Anonymous Pro.ttf', 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Add buttons as inputs
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    #
    cmd = "date \'+%A\'" #day
    WNOW = DNOW = ""+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "date \'+%b %d %Y\'" #date
    DNOW = ""+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "date \'+%H:%M:%S\'" #time
    TNOW = ""+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "hostname -I | cut -d\' \' -f1" #hostname & ssid
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    #cmd = "hostname | tr [:lower:] [:upper:] #\'\\n\'"
    cmd = "hostname"# | tr [:lower:] [:upper:]"
    HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "iwgetid -r"# | tr [:lower:] [:upper:]"
    SSID = subprocess.check_output(cmd, shell=True).decode("utf-8")
    HS = ''+HOST.strip()+''+'|'+SSID.strip()
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    #cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    cmd = "free -m | awk 'NR==2{printf \"Mem: %.2f%%\", $3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    #cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %s\", $5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    #Show CPU temp with two decimal places
    cmd = "cat /sys/class/thermal/thermal_zone0/temp | awk \'{printf \"CPU TempC: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long
    TempC = subprocess.check_output(cmd, shell=True).decode("utf-8")
    #Converting temperature from Centigrade to Fahrenheit
    cmd = "cat /sys/class/thermal/thermal_zone0/temp | awk \'{printf \"CPU TempF: %.1f F\", $(NF-0) / 1000*(9/5)+32}\'"
    TempF = subprocess.check_output(cmd, shell=True).decode("utf-8")

    y = top
    if not buttonA.value:  # just button A pressed
        draw.text((x, y), IP, font=font2, fill="#FFFF00")
        y += font.getsize(IP)[1]

#        draw.text((x, y), CPU, font=font, fill="#FFFF00")
#        y += font.getsize(CPU)[1]
#        draw.text((x, y), MemUsage, font=font, fill="#00FF00")
#        y += font.getsize(MemUsage)[1]
#        draw.text((x, y), Disk, font=font, fill="#0000FF")
#        y += font.getsize(Disk)[1]
#        draw.text((x, y), TempC, font=font, fill="#FF00FF")
#        y += font.getsize(TempC)[1]
#        draw.text((x, y), TempF, font=font, fill="#FF00FF")
#        y += font.getsize(TempF)[1]

    else:   # No button pushed
        draw.text((x, y), WNOW, font=font, fill="#00FFFF") #Weekday
        y += font.getsize(WNOW)[1]
        draw.text((x, y), DNOW, font=font, fill="#FF00FF") #date
        y += font.getsize(DNOW)[1]
        draw.text((x, y), TNOW, font=font, fill="#00FF00") #time
        y += font.getsize(TNOW)[1]
    if not buttonB.value: # button B pushed
        backlight.value = False
    if not buttonA.value: # button A pushed after B is pushed first
        backlight.value = True
    if not buttonA.value and not buttonB.value: # Both buttons pushed together
        disp.fill(color565(53, 145, 161))
        os.system("sudo shutdown now")
    # Display image.
    disp.image(image, rotation)
    time.sleep(.1)
