from . import db
from app import app

class Reputation(db.Model):
	id 				= db.Column(db.Integer, primary_key=True)
	date_modified 	= db.Column(db.DateTime, default=db.func.current_timestamp(),
											onupdate=db.func.current_timestamp())
	date_created 	= db.Column(db.DateTime, default=db.func.current_timestamp())
	domain_name		= db.Column(db.String(40), unique=True)
	rep 			= db.Column(db.SmallInteger, default=app.config['DEFAULT_REP'])
	
	def __init__(self, domain_name):
		self.domain_name = domain_name

	def __repr__(self):
		return '%s' % self.domain_name