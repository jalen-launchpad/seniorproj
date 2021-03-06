from app import db

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_username = db.Column(db.String(80), unique=False, nullable=False)
    filename = db.Column(db.String(120), unique=False, nullable=False)
    play_count = db.Column(db.Integer, nullable=False)
    share_count = db.Column(db.Integer, nullable=False)
    comment_count = db.Column(db.Integer, nullable=False)
    success_level = db.Column(db.String(120), unique=False, nullable=False) 


    __table_args__ = (
        db.UniqueConstraint('account_username', 'filename', name='uix_1'),
    )

    def __repr__(self):
        return '<Record %r>' % self.account_username