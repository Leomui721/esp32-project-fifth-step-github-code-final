from machine import Pin, I2C, SPI, UART
import time
import mfrc522
import hx711
import ds3231

# 腳位設定
LED_LIGHT = 4
BUZZER = 13

# 初始化
led = Pin(LED_LIGHT, Pin.OUT)
buzzer = Pin(BUZZER, Pin.OUT)
rfid = mfrc522.MFRC522(spi_id=1, sck=18, mosi=23, miso=19, cs=5, rst=2)
scale = hx711.HX711(14, 15)
i2c = I2C(0, sda=Pin(21), scl=Pin(22))
rtc = ds3231.DS3231(i2c)
cam = UART(1, 115200, tx=16, rx=17)

scale.tare()

def beep(times):
    for _ in range(times):
        buzzer.value(1)
        time.sleep(0.2)
        buzzer.value(0)
        time.sleep(0.2)

# 主程式
while True:
    t = rtc.datetime()
    hour = t[4]
    minute = t[5]

    # 服藥提醒
    if hour == 8 and minute == 0:
        beep(3)
        led.value(1)
        time.sleep(2)
        led.value(0)

    # RFID 辨識
    stat, typ = rfid.request(rfid.REQIDL)
    if stat == rfid.OK:
        beep(2)
        led.value(1)
        time.sleep(1)
        led.value(0)

    # 藥盒拿起偵測
    w = scale.get_weight()
    if w < -2000:
        cam.write(b"CAPTURE\n")
        led.value(1)
        time.sleep(1)
        led.value(0)

    # AI 跌倒偵測
    if cam.any():
        data = str(cam.read())
        if "FALL" in data:
            beep(5)

    time.sleep(0.2)
