import csv
import random
import chardet

# Ścieżka do pliku CSV
plik_csv = "data.csv"  # <-- tutaj podaj nazwę swojego pliku

nazwy_kolumn = ["PL", "Artikel", "SINGULAR", "PLURAL", "SHOW", "POSITIVE"]

# --- KROK 1: automatyczne wykrycie kodowania ---
with open(plik_csv, 'rb') as f:
    wynik = chardet.detect(f.read(5000))
    kodowanie = wynik['encoding']


# Wczytanie zawartości pliku
with open(plik_csv, newline='', encoding=kodowanie) as f:
    reader = csv.DictReader(f, fieldnames=nazwy_kolumn, delimiter=';')
    for wiersz in reader:
        print(wiersz)


