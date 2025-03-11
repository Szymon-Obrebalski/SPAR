# SPAR Automatyczny Asystent Zakupów

## Opis
Skrypt automatyzujący proces zakupów w sklepie internetowym [e-spar.com.pl](https://e-spar.com.pl).  
Program loguje się do serwisu, wyszukuje produkty z listy i dodaje je do koszyka.

## Główne funkcjonalności
- ✅ Automatyczne logowanie do e-spar.com.pl
- 🔍 Wyszukiwanie produktów według nazwy
- 🤖 Inteligentny wybór produktów przy użyciu **Google Gemini AI**
- 🛒 Automatyczne dodawanie produktów do koszyka
- 📜 Logowanie operacji
- 📅 Integracja z **kalendarzem Synology** do pobierania listy zakupów
- 💾 Zapis danych zamówienia do **bazy MySQL**

## Wymagania
- **Python 3.x**
- Biblioteki:  
  `requests`, `beautifulsoup4`, `google-generativeai`, `pandas`, `sqlalchemy`, `fastapi`, `uvicorn`
- Plik konfiguracyjny z danymi logowania (zmienne środowiskowe)
- Dostęp do **API Google Gemini**
- Dostęp do **API kalendarza Synology**
- **Baza danych MySQL**

---

## Użycie

### Konfiguracja
Zdefiniuj zmienne środowiskowe:

| Zmienna        | Opis |
|---------------|------|
| `login`       | Login do e-spar.com.pl |
| `SPARpass`    | Hasło do e-spar.com.pl |
| `password`    | Hasło do bazy danych MySQL |
| `DB_HOST`     | Host bazy danych MySQL (domyślnie `192.168.0.3`) |
| `IP`          | Adres IP serwera Synology |
| `PORT`        | Port serwera Synology |
| `DEVICE_NAME` | Nazwa urządzenia Synology |
| `DEVICE_ID`   | ID urządzenia Synology |

---

### Uruchomienie
Zbuduj i uruchom kontener Docker:

```bash
docker build -t spar-assistant .
docker compose up
```

Aplikacja dostępna jest na http://localhost:8127
