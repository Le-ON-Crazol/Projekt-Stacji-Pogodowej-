import network
import socket  # Zmiana: używamy surowych gniazd
import json
import time
import secret
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_4

# --- Inicjalizacja wyświetlacza ---
display = PicoGraphics(display=DISPLAY_INKY_FRAME_4)
BLACK = 0
WHITE = 1
RED = 4

# --- Połączenie z Wi-Fi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secret.WIFI_SSID, secret.WIFI_PASS)

print("Inky łączy się z Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)
print("Połączono!")

# Upewniamy się, że mamy czysty adres IP bez dopisku "http://"
ip_serwera = secret.IP_STACJI.replace("http://", "").replace("/", "")

while True:
    try:
        print(f"Pobieranie danych z {ip_serwera} przez socket...")
        
        # 1. Tworzymy i łączymy gniazdo
        s = socket.socket()
        s.connect((ip_serwera, 80))
        
        # 2. Wysyłamy najprostsze możliwe żądanie HTTP GET
        s.send(b"GET / HTTP/1.0\r\n\r\n")
        
        # 3. Odbieramy całą odpowiedź z serwera w pętli
        odpowiedz_bajty = b""
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            odpowiedz_bajty += chunk
            
        s.close()
        
        # 4. Dekodujemy odpowiedź
        odpowiedz_tekst = odpowiedz_bajty.decode('utf-8')
        
        # Serwer wysyła najpierw nagłówki, potem pustą linię (\r\n\r\n), a na końcu JSON
        # Rozdzielamy tekst w tym miejscu, aby wyciągnąć tylko dane
        cialo_json = odpowiedz_tekst.split("\r\n\r\n")[1]
        
        # 5. Zamieniamy tekst na słownik
        dane = json.loads(cialo_json)
        
        temp = dane["temp"]
        pres = dane["pres"]
        hum = dane["hum"]
        
        print(f"Sukces! Odebrano: {temp}C, {pres}hPa, {hum}%")
        
        # --- Rysowanie po ekranie E-ink ---
        display.set_pen(WHITE)
        display.clear()
        
        display.set_pen(RED)
        display.set_font("serif")
        display.text("Stacja Pogodowa", 20, 35, scale=2)
        
        display.set_pen(BLACK)
        display.text(f"Temperatura: {temp} C", 20, 100, scale=1.5)
        display.text(f"Cisnienie: {pres} hPa", 20, 150, scale=1.5)
        display.text(f"Wilgotnosc: {hum} %", 20, 200, scale=1.5)
        
        display.set_pen(RED)
        display.text("Dane odswiezane co 5 min", 20, 350, scale=1)
        
        print("Aktualizacja e-ink...")
        display.update()
            
    except Exception as e:
        print(f"Blad komunikacji lub pobierania: {e}")
        
    print("Czekam 5 minut...")
    time.sleep(300)