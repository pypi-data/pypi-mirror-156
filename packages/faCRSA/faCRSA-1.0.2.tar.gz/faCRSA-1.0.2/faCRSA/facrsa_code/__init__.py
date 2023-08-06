from flask import Flask
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

from facrsa_code.library.web import views,dataApi
