from flask import render_template, request
from . import app
from .models import Reputation


#@app.before_first_request
def update_domain_list():
	#print (app.config['LATEST_DOMAIN_ID'])
	pass

@app.route('/')
def index():
	domains = Reputation.query.all()
	return render_template('app/index.html',domains=domains )

@app.route('/ttp')
def ttp_feed():
	return render_template('app/ttp.html')

