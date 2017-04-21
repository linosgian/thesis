import requests
from app import db
from app.models import Reputation
from setuptools import Command, find_packages, setup


class InitializeDB(Command):
	user_options = [
		('ip=', 't', 'TTP\'s IP'),
	]
	def initialize_options(self):
		self.ip = None

	def finalize_options(self):
		if self.ip is " ":
			print("You have to define the TTP's IP")
			exit()

	def run(self):
		try:
			req = requests.get("http://" + self.ip)
		except Exception as e:
			print('Error:', e)
			exit()
		json = req.json()
		RepObjects = []
		for key,value in json.items():
		 	domain = Reputation(key)
	 		RepObjects.append(domain)
		print(RepObjects)
		db.session.bulk_save_objects(RepObjects)
		#db.session.commit()

setup(
	name = "repflask",
	cmdclass={
		'ttp': InitializeDB,	
	}
)