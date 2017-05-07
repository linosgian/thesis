import ipaddress
import requests
from .models import Reputation
from . import app,db

def ipv4_validation(IPv4):
# Check if the given IP is a valid IPv4
	try:
		ipaddress.ip_address(IPv4)
	except ValueError:
		print('\033[91m[*] Given IP is not a valid IPv4.\033[0m')
		exit()


def update_domain_list(IPv4):
	
	ipv4_validation(IPv4)
	latest_domain_id = app.config['LATEST_DOMAIN_ID']
	url = "http://" + IPv4 + "/test.json?id=" + str(latest_domain_id)
	print(url)
	req = requests.get(url)
	json = req.json()
	RepObjects = []
	for key,value in json.items():
	 	domain = Reputation(key)
 		RepObjects.append(domain)
	print(RepObjects)
	#db.session.bulk_save_objects(RepObjects)
	#db.session.commit()
