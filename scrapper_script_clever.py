import requests
import csv
import os
from datetime import datetime

url = 'https://iparking.pwr.edu.pl/modules/iparking/scripts/ipk_operations.php'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'https://iparking.pwr.edu.pl',
    'Referer': 'https://iparking.pwr.edu.pl/',
    'X-Requested-With': 'XMLHttpRequest'
}

csv_filename = 'parking_history_data.csv'

def send_request(parking_id):
    payload = {
        "o": "get_today_chart",
        "i": str(parking_id)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Błąd podczas wysyłania żądania dla parkingu {parking_id}: {e}')
        return None

def file_has_data_for_today(filename, current_date):
    """Sprawdza, czy w pliku CSV są dane dla bieżącej daty"""
    if not os.path.exists(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and row[0] == current_date:
                return True
    return False

def save_to_csv(all_data):
    unique_times = set()
    for data in all_data:
        if 'slots' in data and 'labels' in data['slots']:
            unique_times.update(data['slots']['labels'])
    
    unique_times = sorted(unique_times)
    current_date = datetime.now().strftime('%Y-%m-%d')

    file_exists = os.path.exists(csv_filename)
    has_data_today = file_has_data_for_today(csv_filename, current_date)

    try:
        with open(csv_filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                headers = ['Data', 'Czas', 'Polinka', 'Parking Wrońskiego', 'D20 - D21', 'GEO LO1 Geocentrum', 'Architektura']
                writer.writerow(headers)

            data_by_time = {czas: [current_date, czas] + [''] * 5 for czas in unique_times}

            for idx, parking_id in enumerate([2, 4, 5, 6, 7], start=0):
                data = all_data[idx]
                if 'slots' in data and 'labels' in data['slots'] and 'data' in data['slots']:
                    history_labels = data['slots']['labels']
                    history_data = data['slots']['data']

                    for czas, wolne_miejsca in zip(history_labels, history_data):
                        if czas in data_by_time:
                            data_by_time[czas][idx + 2] = wolne_miejsca

            for row in data_by_time.values():
                writer.writerow(row)

    except IOError as e:
        print(f'Błąd podczas zapisu do pliku CSV: {e}')

def main():
    all_data = []

    for parking_id in [2, 4, 5, 6, 7]:
        data = send_request(parking_id)
        if data:
            all_data.append(data)
        else:
            print(f"Nie udało się pobrać danych z serwera dla parkingu {parking_id}.")

    if all_data:
        save_to_csv(all_data)

if __name__ == "__main__":
    main()
