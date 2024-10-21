import requests
import json
from datetime import datetime
import time
import csv
import os

# URL do którego wysyłamy zapytanie
url = 'https://iparking.pwr.edu.pl/modules/iparking/scripts/ipk_operations.php'

# Nagłówki HTTP, aby symulować normalne żądanie z przeglądarki
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'https://iparking.pwr.edu.pl',
    'Referer': 'https://iparking.pwr.edu.pl/',
    'X-Requested-With': 'XMLHttpRequest'
}

# Nazwa pliku CSV
csv_filename = 'parking_data.csv'

def get_timestamp():
    """Funkcja generująca znacznik czasu w milisekundach"""
    return str(int(time.time() * 1000))

def send_request():
    """Funkcja do wysyłania zapytania POST z obsługą wyjątków"""
    payload = {
        "o": "get_parks",
        "ts": get_timestamp()
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Zgłoszenie wyjątku w przypadku błędu HTTP

        # Wyświetlenie surowych danych przed przetworzeniem
        print("Otrzymane surowe dane (tekst):")
        print(response.text)  # Wyświetlamy surową odpowiedź w formie tekstu

        return response.json()  # Zwraca odpowiedź w formacie JSON
    except requests.exceptions.RequestException as e:
        print(f'Błąd podczas wysyłania żądania: {e}')
        return None
    except json.JSONDecodeError:
        print('Błąd parsowania odpowiedzi JSON.')
        return None

def save_to_csv(data, headers_written=False):
    """Funkcja do zapisania danych do pliku CSV"""

    # Pobieramy czas pomiaru z pierwszego parkingu (zakładamy, że czas jest taki sam dla wszystkich)
    czas_pomiaru = data.get("places", [{}])[0].get("czas_pomiaru", "Brak czasu")

    # Zbieranie danych o wolnych miejscach na parkingach
    parking_names = []
    free_spots = []

    for parking in data.get("places", []):
        nazwa = parking.get("nazwa", "Brak nazwy")
        liczba_wolnych_miejsc = parking.get("liczba_miejsc", "Brak danych")

        parking_names.append(nazwa)
        free_spots.append(liczba_wolnych_miejsc)

    # Zapis danych do pliku CSV
    try:
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Zapisz nagłówki, jeśli plik jest tworzony po raz pierwszy
            if headers_written:
                writer.writerow(['Czas pomiaru'] + parking_names)
            
            # Zapisz dane (czas pomiaru + liczba wolnych miejsc na parkingach)
            writer.writerow([czas_pomiaru] + free_spots)
    except IOError as e:
        print(f'Błąd podczas zapisu do pliku CSV: {e}')

def main():
    # Sprawdzenie, czy plik CSV istnieje (jeśli nie, trzeba zapisać nagłówki)
    headers_written = not os.path.exists(csv_filename)

    # Wysyłanie zapytania i pobieranie danych
    data = send_request()

    if data:
        # Sprawdzenie, czy odpowiedź zawiera oczekiwane dane
        if data.get("success") == 0 and "places" in data:
            save_to_csv(data, headers_written=headers_written)
            print(f"Dane zapisane do pliku {csv_filename}")
        else:
            print("Brak danych o parkingach lub niepoprawna odpowiedź z serwera.")
    else:
        print("Nie udało się pobrać danych z serwera.")

if __name__ == "__main__":
    main()
