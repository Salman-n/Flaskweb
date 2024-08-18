from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import locale

def rupiah_format(angka, with_prefix=False, desimal=2):
    try:
        locale.setlocale(locale.LC_NUMERIC, 'id_ID.UTF-8')  # Menggunakan locale untuk Indonesia
    except locale.Error:
        locale.setlocale(locale.LC_NUMERIC, '')  # Fallback jika locale tidak tersedia
    rupiah = locale.format_string("%.*f", (desimal, angka), True)
    if with_prefix:
        return "Rp. {}".format(rupiah)
    return rupiah


app = Flask(__name__)

app.jinja_env.filters['rupiah'] = rupiah_format
app.config.from_object('config.Config')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
