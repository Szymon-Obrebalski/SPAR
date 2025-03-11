import os

login = os.environ.get('login')
password = os.environ.get('password')
SPARpass = os.environ.get('SPARpass')
DB_HOST = os.environ.get('DB_HOST', '192.168.0.3')
IP = os.environ.get('IP')
PORT =  os.environ.get('PORT')
DEVICE_NAME = os.environ.get('DEVICE_NAME')
DEVICE_ID = os.environ.get('DEVICE_ID')

SparLogin = {
    'username':  os.environ.get('login'),
    'password': os.environ.get('SPARpass')
}
database_pointer = {
    'database': f'mysql+pymysql://{login}:{password}@{DB_HOST}/Production',
    'table': 'SPAR'
}
if '__main__' == __name__:
    print(SparLogin,SPARpass)