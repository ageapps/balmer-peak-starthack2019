from app import db

class Signal(db.Model):
    __tablename__ = 'signal'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String())
    timestamp = db.Column(db.Date())
    value = db.Column(db.String())

    def __init__(self, key, timestamp, value):
        self.key = key
        self.timestamp = datetime.datetime.utcfromtimestamp(timestamp)
        self.value = value
        db.create_all()
