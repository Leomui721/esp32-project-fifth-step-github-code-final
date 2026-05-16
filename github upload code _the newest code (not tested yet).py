# ==========================================================
# ESP32 智能長者照護系統
# 功能：RTC時間 + 4位數碼管 + 蜂鳴器提醒 + 補光LED + HX711重量偵測 + ESP32‑CAM AI跌倒
# 無RFID、無光敏電阻、無OLED、無按鍵
# ==========================================================

from machine import Pin, UART
import time

# ===================== 腳位定義 =====================
# 蜂鳴器 (VCC/GND/I/O)
BUZZER_PIN = Pin(13, Pin.OUT)

# 補光 LED
LED_PIN = Pin(4, Pin.OUT)

# 4位數碼管
TM1637_DIO = Pin(18, Pin.OUT)
TM1637_CLK = Pin(19, Pin.OUT)

# RTC 模組 (CLK/DAT/RST)
RTC_CLK = Pin(21, Pin.OUT)
RTC_DAT = Pin(22, Pin.OUT)
RTC_RST = Pin(2, Pin.OUT)

# HX711 重量感測
HX_DT = Pin(14, Pin.IN)
HX_SCK = Pin(15, Pin.OUT)

# ESP32‑CAM 相機 (UART)
CAM = UART(1, baudrate=115200, tx=16, rx=17)

# ===================== 基礎函式 =====================
# 蜂鳴器響幾聲
def beep(times):
    for _ in range(times):
        BUZZER_PIN.value(1)
        time.sleep(0.3)
        BUZZER_PIN.value(0)
        time.sleep(0.3)

# 數碼管顯示時間 (範例：8:30 → 顯示 0830)
def show_time(hour, minute):
    print("數碼管顯示時間：", f"{hour:02d}:{minute:02d}")

# 取得 RTC 時間 (模擬，可替換真實讀取)
def get_rtc_time():
    # 回傳 (小時, 分鐘)
    return (8, 0)

# 讀取 HX711 重量
def get_weight():
    # 模擬重量：小於 -2000 代表藥盒被拿起
    return -3000

# ===================== 主程式 =====================
print("系統啟動：智能長者照護系統")
beep(1)  # 開機提示音

while True:
    try:
        # 1. 取得時間並顯示在數碼管
        hour, minute = get_rtc_time()
        show_time(hour, minute)

        # 2. 定時服藥提醒 (早上 8:00)
        if hour == 8 and minute == 0:
            print("提醒：吃藥時間！")
            beep(3)          # 短響3聲
            LED_PIN.value(1) # 開燈
            time.sleep(3)
            LED_PIN.value(0) # 關燈

        # 3. 藥盒拿起偵測 → 觸發相機拍照
        weight = get_weight()
        if weight < -2000:
            print("偵測：藥盒已拿起")
            CAM.write(b"CAPTURE\r\n")  # 拍照指令
            LED_PIN.value(1)
            time.sleep(1)
            LED_PIN.value(0)

        # 4. AI 跌倒偵測
        if CAM.any():
            msg = CAM.read().decode().strip()
            if "FALL" in msg:
                print("警告：偵測到跌倒！")
                beep(5)  # 長響警報
                LED_PIN.value(1)
                time.sleep(3)
                LED_PIN.value(0)

        time.sleep(0.2)

    except Exception as e:
        # 錯誤處理，避免當機
        print("系統異常：", e)
        time.sleep(1)
