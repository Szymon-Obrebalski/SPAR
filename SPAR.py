import logging
from io import StringIO

import google.generativeai as genai
import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from sqlalchemy import create_engine, text

import Synology
from imports.json_handler import json_from_text
from imports.passwords import SparLogin, database_pointer
from imports.prompts import ShoppingAssistant

import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Logowanie do stdout
        logging.FileHandler('./logs/SPAR.log'),
    ]
)

class SparShopper:
    SCRAPPING_URL = "https://e-spar.com.pl/"
    LOGIN_URL = 'https://e-spar.com.pl/klient/logowanie'
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    HEADERS = {
        'User-Agent': USER_AGENT,
        'Referer': LOGIN_URL,
        'Accept-Language': 'pl-PL,pl;q=0.9'
    }
    PRODUCT_SEARCH_PAGES = 5
    database = database_pointer['database']
    table_name = database_pointer['table']

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=ShoppingAssistant,
        )

    def login(self):
        credentials = {
            'store_models_StoreLoginForm[username]': SparLogin['username'],
            'store_models_StoreLoginForm[password]': SparLogin['password'],
            'yt0': 'Zaloguj się'
        }
        self.session.post(self.LOGIN_URL, data=credentials, headers=self.HEADERS, verify=False)
        self.logger.info('Zalogowano')

    def choose_product(self, product: str, products: list):
        chat_session = self.model.start_chat()
        chosen_product = chat_session.send_message(f"{product},{products}")
        response_text = chosen_product.candidates[0].content.parts[0].text
        product_info = json_from_text(response_text)
        self.logger.info(product_info)
        return product_info

    def search_product(self, product: str):
        products = []
        searching_url = f"{self.SCRAPPING_URL}/index/asortyment?sort=relevancy.desc&query={product}"
        request = self.session.get(url=searching_url, allow_redirects=True, verify=False)
        soup = BeautifulSoup(request.text, 'html.parser')
        for product_box in soup.find_all('div', class_='product-box-container'):
            link = product_box.find('a', href=True)['href']
            name = product_box.find('span', class_='product-box__name').text
            if link and name: products.append((link, name.strip()))
        return self.choose_product(product=product, products=products)

    def add_to_cart(self, add_to_cart_url: str, quantity: int = 1):
        add_to_cart_page = self.session.get(add_to_cart_url, verify=False)
        soup = BeautifulSoup(add_to_cart_page.text, 'html.parser')
        add_to_cart_form = soup.find('form', {'id': 'productViewSubmit'})

        if add_to_cart_form:
            action_url = add_to_cart_form['action']
            if not action_url.startswith('http'):
                action_url = f"{self.SCRAPPING_URL.rstrip('/')}{action_url}"
            form_data = {input_tag['name']: input_tag.get('value', '') for input_tag in
                         add_to_cart_form.find_all('input')}

            amount_input = add_to_cart_form.find('input', {'name': 'app_models_api_AProductSignature[amount]'})
            unit_step = float(amount_input.get('data-product-unit-step', '1').replace(',', '.'))

            adjusted_quantity = quantity / 10 if unit_step == 0.1 else quantity
            form_data['app_models_api_AProductSignature[amount]'] = str(adjusted_quantity)

            self.session.post(url=action_url, data=form_data, headers=self.HEADERS, verify=False)
            self.logger.info('Dodano do koszyka')
        else:
            self.logger.info(f'Nie znaleziono formularza')  ##TUTAJ FALLBACK JAK NIE ZNAJDZIE!

    def shop(self, products: list[str]):
        self.login()
        for product in products:
            try:
                product_url = self.search_product(product)
                if product_url:
                    self.logger.info(f"{self.SCRAPPING_URL}{product_url['href']}")
                    self.add_to_cart(f"{self.SCRAPPING_URL}{product_url['href']}", quantity=product_url['amount'])
                else:
                    self.logger.warning("nie znaleziono produktu")
            except Exception as e:
                self.logger.exception(f'Wystąpił błąd {e}')

        self.session.close()
        self.logger.info('Sesja zakończona')

    def store_cart_data(self, order_number):
        self.login()
        order_url = f'https://e-spar.com.pl/zamowienia/self.logger.info/id/{order_number}'

        response = self.session.get(order_url, headers=self.HEADERS, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'table table-striped table-bordered products table-condensed'})
        if not table:
            raise ValueError("Tabela nie została znaleziona na stronie zamówienia.")
        self.logger.info(table)
        df = pd.read_html(StringIO(str(table)))[0]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(0)
        df['Kod kreskowy'] = df['Kod kreskowy'].apply(lambda x: f'{int(x):013}' if pd.notnull(x) else '')
        df['Ilość zamówiona'] = df['Ilość zamówiona'].apply(
            lambda x: float(x) / 1000 if x != "Razem:" else float('nan'))
        df.dropna(subset=['Kod kreskowy', 'Nazwa towaru'], inplace=True)
        df.rename(columns={
            'Kod kreskowy': 'Kod_kreskowy',
            'Nazwa towaru': 'Nazwa_towaru',
            'Ilość zamówiona': 'Ilość_zamówiona',
            'Opcja produktu': 'Opcja_produktu'
        }, inplace=True)
        df = df.where(pd.notnull(df), None)
        df['Cena'] = df['Cena'].str.replace(' zł', '').str.replace(',', '.').astype(float)
        df['Wartość'] = df['Wartość'].str.replace(' zł', '').str.replace(',', '.').astype(float)
        df = df.drop(['LP', 'Jm'], axis=1)

        engine = create_engine(self.database, echo=True)

        insert_query = f"""
            INSERT INTO {self.table_name} ({', '.join(df.columns)},data) 
            VALUES ({', '.join([f':{col}' for col in df.columns])},NOW())
            ON DUPLICATE KEY UPDATE 
            {', '.join([f'{col}=VALUES({col})' for col in df.columns])},
            data=NOW()
        """

        with engine.begin() as conn:
            conn.execute(text(insert_query), df.to_dict(orient='records'))
        self.logger.info(f"✅ Dane z zamówienia {order_number} zostały zapisane do tabeli {self.table_name}.")
        self.logger.info(f"Dane z zamówienia {order_number} zostały zapisane do tabeli {self.table_name}.")


app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

class UploadRequest(BaseModel):
   calendarid: str

@app.post("/upload")
def upload(calendarid: UploadRequest):
    shopper = SparShopper()
    shopper.logger.info('Started')
    shopper.logger.info('Stopped')
    shopper.shop(Synology.getwishlist(calendarid.calendarid))
    return True


class OrderRequest(BaseModel):
    orderid: int


@app.post('/store')
def store(order_request: OrderRequest):
    shopper = SparShopper()
    shopper.logger.info('Started')
    shopper.store_cart_data(order_request.orderid)
    shopper.logger.info('Stopped')
    return True
