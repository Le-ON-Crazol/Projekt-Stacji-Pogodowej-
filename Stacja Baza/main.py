import network
import socket
import json
import time
import secret
from pimoroni_i2c import PimoroniI2C
from breakout_bme280 import BreakoutBME280
from gfx_pack import GfxPack

# --- Inicjalizacja sprzętu ---
i2c = PimoroniI2C(sda=4, scl=5)
bme = BreakoutBME280(i2c)

gp = GfxPack()
display = gp.display
gp.set_backlight(0, 0, 0, 100) 

# --- Połączenie z Wi-Fi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secret.WIFI_SSID, secret.WIFI_PASS)

display.set_pen(0)
display.clear()
display.set_pen(15)
display.text("Laczenie z Wi-Fi...", 5, 20, 128, 1)
display.update()

while not wlan.isconnected():
    time.sleep(1)
    
ip_serwera = wlan.ifconfig()[0]
print(f"=====================================")
print(f"SKOPIUJ TEN ADRES DO secret.py: {ip_serwera}")
print(f"=====================================")

# --- Konfiguracja serwera HTTP ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)
s.settimeout(2.0) 

print("Serwer dziala. Odswiezanie ekranu aktywne.")

while True:
    temperature, pressure, humidity = bme.read()
    
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    
    display.text(f"IP: {ip_serwera}", 5, 2, 128, 1)
    display.text(f"T: {temperature:.1f} C", 5, 18, 128, 2)
    display.text(f"P: {pressure/100:.0f} hPa", 5, 35, 128, 2)
    display.text(f"W: {humidity:.0f} %", 5, 52, 128, 2)
    display.update()

# 3. Obsługa żądań HTTP (z timeoutem)
    try:
        klient, adres = s.accept()
        print(f"Zapytanie od: {adres}")
        
        klient.settimeout(5.0)
        
        request = klient.recv(1024)
        
        dane_pogodowe = {
            "temp": round(temperature, 1),
            "pres": round(pressure / 100, 0),
            "hum": round(humidity, 0)
        }
            
        cialo_odpowiedzi = json.dumps(dane_pogodowe)
        dlugosc = len(cialo_odpowiedzi)
            
        odpowiedz_http = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {dlugosc}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{cialo_odpowiedzi}"
        )
        
        klient.sendall(odpowiedz_http.encode('utf-8'))
                
        time.sleep(0.5) 
        
        klient.close()
        
    except OSError:
        pass