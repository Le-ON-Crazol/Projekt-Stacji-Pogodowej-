# Projekt Stacji Pogodowej (Klient-Serwer)

Projekt zaliczeniowy z przedmiotu Zaawansowane Programowanie w Pythonie na kierunku Fizyka Techniczna, Politechnika Warszawska.

## Cel projektu

Zbudowanie dwuczęściowego systemu do pomiaru parametrów środowiskowych i ich bezprzewodowego przesyłania. Całość opiera się na mikrokontrolerach z układem RP2040 z wykorzystaniem środowiska MicroPython. System działa w architekturze klient-serwer, wykorzystując do komunikacji zewnętrzną sieć Wi-Fi.

## Wykorzystany sprzęt

- Moduł pomiarowy (Serwer HTTP):
  - Raspberry Pi Pico W
  - Czujnik BME280 (pomiar temperatury, ciśnienia i wilgotności) podłączony przez I2C
  - Pimoroni Pico GFX Pack (mały ekran LCD do podglądu działania i adresu IP przypisanego przez router)

- Moduł wyświetlający (Klient):
  - Pimoroni Inky Frame 4.0" (ekran typu e-paper)

## Zasada działania

Skrypt serwera (Pico W z czujnikiem) w pierwszej kolejności łączy się z zewnętrzną siecią Wi-Fi, a następnie działa w pętli, odczytując dane fizyczne z układu BME280. Został na nim postawiony prosty serwer HTTP oparty na gniazdach (sockets). Posiada on zdefiniowany timeout na 2 sekundy, aby uniknąć zablokowania pętli głównej w przypadku braku zapytań. Gdy przychodzi żądanie, mikrokontroler pakuje dane pomiarowe do formatu JSON i odsyła do klienta.

Skrypt klienta (Inky Frame) po uwierzytelnieniu i połączeniu z tą samą zewnętrzną siecią Wi-Fi, nawiązuje połączenie TCP z adresem IP serwera i wysyła surowe żądanie HTTP GET. Po odebraniu odpowiedzi (odrzuceniu nagłówków i zdekodowaniu pliku JSON), wyciąga poszczególne parametry. Następnie odświeża trójkolorowy ekran e-ink z aktualnymi wartościami i zatrzymuje pętlę na 5 minut (time.sleep()), co jest wymuszone charakterystyką pracy ekranów elektroforetycznych.

## Instrukcja uruchomienia

Przed uruchomieniem skryptów na mikrokontrolerach należy wgrać dedykowany firmware MicroPython od firmy Pimoroni (zawierający wbudowane moduły takie jak picographics czy breakout_bme280).

Ze względu na wykorzystanie zewnętrznej infrastruktury sieciowej, w kodzie źródłowym obu urządzeń (lub w dedykowanym pliku konfiguracyjnym, np. secrets.py) należy uzupełnić poświadczenia Wi-Fi (SSID oraz hasło) dla docelowej sieci, w której będą pracować moduły. Odczytanie adresu IP przypisanego serwerowi przez DHCP jest możliwe z poziomu ekranu Pico GFX Pack.
