import requests
from . import db
from .models import Reputation

def initialize_database():
	req = requests.get("http://api.myjson.com/bins/16givj")
	json = req.json()
	RepObjects = []
	for key,value in json.items():
	 	domain = Reputation(key)
 		RepObjects.append(domain)
	print(RepObjects)
	db.session.bulk_save_objects(RepObjects)
	db.session.commit()
