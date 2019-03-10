from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask import request
import os

app = Flask(__name__)



POSTGRES = {
    'db': 'starthack',
    'host': 'localhost',
    'port': '5432',
}

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


@app.route('/signal', methods=['POST'])
def insertUser():
    signal = request.form['signal']
    time = request.form['timestamp']
    value = request.form['value']
    saveData(signal,time,value)
    return "<p>Data is updated</p>"


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


def saveData(signal,time,value):
    signal = Signal(signal, int(time[:10]), value)
    db.session.add(signal)
    db.session.commit()


if __name__ == '__main__':
    app.run()
