import requests
import csv
import os
from datetime import datetime  # Importowanie modułu datetime

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
csv_filename = 'parking_history_data.csv'

def send_request(parking_id):
    """Funkcja do wysyłania zapytania POST z obsługą wyjątków"""
    payload = {
        "o": "get_today_chart",
        "i": str(parking_id)  # Zmienna "i" jest teraz dynamiczna
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Zgłoszenie wyjątku w przypadku błędu HTTP

        return response.json()  # Zwraca odpowiedź w formacie JSON
    except requests.exceptions.RequestException as e:
        print(f'Błąd podczas wysyłania żądania dla parkingu {parking_id}: {e}')
        return None

def save_to_csv(all_data):
    """Funkcja do zapisania danych do pliku CSV"""

    # Zbieranie unikalnych wartości czasu (godziny) z wszystkich parkingów
    unique_times = set()
    for data in all_data:
        if 'slots' in data and 'labels' in data['slots']:
            unique_times.update(data['slots']['labels'])
    
    # Sortowanie czasów rosnąco
    unique_times = sorted(unique_times)

    # Pobieranie bieżącej daty
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Zapis danych do pliku CSV
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Zapis nagłówków z nazwami parkingów i kolumną daty
            headers = ['Data', 'Czas', 'Polinka', 'Parking Wrońskiego', 'D20 - D21', 'GEO LO1 Geocentrum', 'Architektura']
            writer.writerow(headers)

            # Przechowywanie danych dla każdego parkingu na podstawie czasu
            data_by_time = {czas: [current_date, czas] + [''] * 5 for czas in unique_times}

            # Wypełnianie danych dla każdego parkingu
            for idx, parking_id in enumerate([2, 4, 5, 6, 7], start=0):
                data = all_data[idx]
                if 'slots' in data and 'labels' in data['slots'] and 'data' in data['slots']:
                    history_labels = data['slots']['labels']  # Czas (godziny)
                    history_data = data['slots']['data']  # Liczba wolnych miejsc

                    # Uzupełnianie wartości dla odpowiednich godzin
                    for czas, wolne_miejsca in zip(history_labels, history_data):
                        if czas in data_by_time:
                            data_by_time[czas][idx + 2] = wolne_miejsca  # +2, bo kolumna daty i czasu są pierwsze

            # Zapisz dane do pliku CSV
            for row in data_by_time.values():
                writer.writerow(row)

    except IOError as e:
        print(f'Błąd podczas zapisu do pliku CSV: {e}')

def main():
    # Przechowywanie danych dla parkingów 2, 4-7 (pomijamy parkingi 1 i 3)
    all_data = []

    # Pętla przez parkingi o id 2, 4-7
    for parking_id in [2, 4, 5, 6, 7]:
        # Wysyłanie zapytania i pobieranie danych
        data = send_request(parking_id)

        if data:
            all_data.append(data)
        else:
            print(f"Nie udało się pobrać danych z serwera dla parkingu {parking_id}.")

    # Jeśli zebrano dane, zapisz je do CSV
    if all_data:
        save_to_csv(all_data)

if __name__ == "__main__":
    main()
