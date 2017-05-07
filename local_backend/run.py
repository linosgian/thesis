from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

from app import app, db


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

# @manager.option('-i', '--ttp', dest='IPv4',help='Provide your TTP\'s IPv4.')
# def update_domain_list(IPv4):
	
# 	ipv4_validation(IPv4)
# 	latest_domain_id = app.config['LATEST_DOMAIN_ID']
# 	url = "http://" + IPv4 + "/test.json?id=" + str(latest_domain_id)
# 	print(url)
# 	req = requests.get(url)
# 	json = req.json()
# 	RepObjects = []
# 	for key,value in json.items():
# 	 	domain = Reputation(key)
#  		RepObjects.append(domain)
# 	print(RepObjects)
# 	db.session.bulk_save_objects(RepObjects)
# 	#db.session.commit()

	
if __name__ == '__main__':
    manager.run()