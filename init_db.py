from app import db
from record import *
from record_cuts import *
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
CORS(app)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/jalengabbidon/Desktop/seniorproject/flask/seniorproject.db'
db = SQLAlchemy(app)

db.create_all()
db.session.commit()