from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os 
db_path = os.path.join(os.path.dirname(__file__), 'dev.db')
app = Flask(__name__)

app.config.from_pyfile('../config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)

db = SQLAlchemy(app)

from . import views
