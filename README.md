# SPAR Automatyczny Asystent Zakupów

## Opis
Skrypt automatyzujący proces zakupów w sklepie internetowym e-spar.com.pl. Program loguje się do serwisu, wyszukuje produkty z listy i dodaje je do koszyka.

## Główne funkcjonalności
- Automatyczne logowanie do e-spar.com.pl
- Wyszukiwanie produktów według nazwy
- Inteligentny wybór produktów przy użyciu Google Gemini AI
- Automatyczne dodawanie produktów do koszyka
- Logowanie operacji

## Wymagania
- Python 3.x
- Biblioteki: requests, beautifulsoup4, google-generativeai, pandas, sqlalchemy, fastapi, uvicorn
- Plik konfiguracyjny z danymi logowania (zmienne środowiskowe)
- Dostęp do API Google Gemini

## Użycie

### Konfiguracja
1.  Zdefiniuj zmienne środowiskowe:
    *   `login` - Login do e-spar.com.pl
    *   `SPARpass` - Hasło do e-spar.com.pl
    *   `password` - Hasło do bazy danych MySQL
    *   `DB_HOST` - Host bazy danych MySQL (domyślnie `192.168.0.3`)

### Uruchomienie

1.  Zbuduj i uruchom kontener Docker:

    ```bash
    docker build -t spar-assistant .
    docker run -p 8000:8000 spar-assistant
    ```

2.  Użyj API do przesyłania listy produktów lub zapisywania danych zamówienia.

### Endpointy API

*   **/upload** (POST): Przyjmuje plik CSV z listą produktów do zakupu. Plik powinien być oddzielony znakiem '|'. Kolumna z nazwami produktów powinna się nazywać 'Tytuł'.
    *   Przykład użycia z `curl`:

        ```bash
        curl -X POST -F "file=@products.csv" http://localhost:8000/upload
        ```
*   **/store** (POST): Zapisuje dane zamówienia do bazy danych. Przyjmuje JSON z numerem zamówienia.
    *   Przykład użycia z `curl`:

        ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"orderid": 12345}' http://localhost:8000/store
        ```
