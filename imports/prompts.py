from sqlalchemy import create_engine, text
from imports.passwords import login,password

def get_engine():
    return create_engine(f'mysql+pymysql://{login}:{password}@192.168.0.3/')
def execute_test_query(query: str):
    engine = get_engine()
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    return results

PRIORITIZE_PRODUCTS = execute_test_query(text("""
                SELECT CONCAT('[''', GROUP_CONCAT(Nazwa_towaru SEPARATOR ''','''), ''']')
                FROM Production.SPAR;
"""))[0][0].strip("[]'").split("','")

PRIORITIZE_PRODUCTS = list(dict.fromkeys(x for x in PRIORITIZE_PRODUCTS if x))

ShoppingAssistant = (f"""# Asystent zakupów
## Jesteś asystentem do robienia zakupów przez stronę internetową. Musisz wybrać najbardziej pasujący produkt z listy. Jeżeli masz wybór między dwoma podobnymi produktami to wybieraj te z tej listy: {PRIORITIZE_PRODUCTS}. Jeżeli nie ma w liście priorytezowanej, to spróbuj sam dobrać produkt z listy zapewnionej przez użytkownika.BEZWZGLĘDNIE MUSI BYĆ PODANY PRAWIDŁOWY HREF!. Zapewniaj odpowiedź w postaci json:
json''{{\"product_name\":\"Nazwa Produktu\",
\"href\":\"Link do produktu\",
\"amount\": int}}
## Przykład Odpowiedzi na Produkt: \"banan 5\", Lista: \"...\" :
{{
\"product_name\": \"Banan\",
\"href\": \"/towar/banan/208527\",
\"amount\": 5,
}}
""")
if '__main__' == __name__:
    print(ShoppingAssistant)