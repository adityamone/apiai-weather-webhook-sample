from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_db(app):
	db = SQLAlchemy()
	
	app.config.from_pyfile('config.py')
	app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
	db.init_app(app)
	return app, db
	with app.app_context():
		db.create_all()

		db.engine.execute("SELECT 1;");
		l = db.engine.execute("SELECT * FROM customer LIMIT 1")
		import pdb; pdb.set_trace()
