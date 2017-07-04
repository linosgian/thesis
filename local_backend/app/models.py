from . import db
from app import app
import datetime

class Reputation(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	date_modified 	= db.Column(db.DateTime, default=datetime.datetime.utcnow,
											onupdate=datetime.datetime.utcnow)
	date_created 	= db.Column(db.DateTime, default=datetime.datetime.utcnow)
	district		= db.Column(db.String(40), unique=True)
	rep 			= db.Column(db.SmallInteger, default=app.config['DEFAULT_REP'])
	
	def __init__(self, district):
		self.district = district

	def __repr__(self):
		return '%s' % self.district