from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_pyfile('../config.py')

db = SQLAlchemy(app)

from .utils import update_domain_list

#update_domain_list(app.config['TTP'])

from . import views
