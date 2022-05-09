from app import db

class RecordCuts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(80), db.ForeignKey("record.account_username"), unique=False, nullable=False)
    filename = db.Column(db.String(120), unique=False, nullable=False)
    start_timestamp = db.Column(db.Integer, nullable=False)
    end_timestamp = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<RecordCuts %d %d>' % (self.start_timestamp, self.end_timestamp)

