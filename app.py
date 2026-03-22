import os
#from flask import Flask
import flask
#from pymongo import MongoClient
import pymongo
#from routes import pages
import routes
#from dotenv import load_dotenv
import dotenv
dotenv.load_dotenv() # This loads environment variables from .env and .flaskenv

def create_app():  # app factory
    app = flask.Flask(__name__)
    mongo_client = pymongo.MongoClient(os.environ.get("MONGODB_URI"))
    app.db = mongo_client.get_default_database() # This is defined at the end of the URI string in .env
    # This could also just be client.<default db name>: client.habittracker

    app.register_blueprint(routes.pages)
    return app

app = create_app()
if __name__ == '__main__':
    app.run()
