from flask import render_template
from . import app
from .models import Reputation

@app.route('/')
def index():
	domains = Reputation.query.all()
	return render_template('app/index.html',domains=domains )


@app.route('/ttp')
def ttp_feed():
	return render_template('app/ttp.html')