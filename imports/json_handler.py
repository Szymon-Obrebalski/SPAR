import re
import json

def json_from_text(text):
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError:
            print("Nieprawidłowy format JSON.")
    else:
        print("Nie znaleziono bloku JSON.")
    print(json_data)
    return json_data

if '__main__' == __name__:
    json_from_text("""
```json
{
"product_name": "Banan",
"href": "/towar/banan/208527"
}
```
""")