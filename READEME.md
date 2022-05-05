RUN FLASK_APP=src/main.py flask run from top-level directory or it will break.

If the DB is not initialized... to initialize follow below commands
Go to src/directory of flask
jalengabbidon$ Python3
>>from app import db
>>from record import *
>>db.create_all()
>>db.session.commit()