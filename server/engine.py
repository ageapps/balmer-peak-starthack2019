from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import datetime


POSTGRES = {
    'db': 'starthack',
    'host': 'localhost',
    'port': '5432',
}

db_string = 'postgresql://%(host)s:%(port)s/%(db)s' % POSTGRES

db = create_engine(db_string)  
base = declarative_base()

class Signal(base):
    __tablename__ = 'signal'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    timestamp = Column(Date)
    value = Column(String)


Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)


# Read every X seconds

signals = session.query(Signal)  
for s in signals:  
    print(s.value)
