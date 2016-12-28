from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = 'some_secret'
from app import views
