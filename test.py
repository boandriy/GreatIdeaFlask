# -*- coding: utf-8 -*-

from flask import Flask, render_template, json, request, redirect, session, url_for, Response
from flask.ext.mysql import MySQL

from werkzeug import generate_password_hash, check_password_hash


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

print "\nfinished with import"

app = Flask(__name__)

print "Approach #1"
print("\ncreating DB engine")
engine = create_engine('mysql://username:pass@127.0.0s.1/idea')         #username and pass to your database
print engine

print("\ncreating DB session")
Session = sessionmaker(bind=engine)
db_session = Session()
print ("Session:", db_session)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first = Column(String)
    last = Column(String)
    email = Column(String)
    status = Column(Integer)
    password = Column(String)
    pin = Column(String)
    username = Column(String)


    def __repr__(self):
        return "<User(name='%s', last='%s', username='%s', email='%s')>" % (
            self.first, self.last, self.username, self.email)

print("\nquery test - one")
result = db_session.query(User).order_by(User.id).first()
print result

print("\nquery test - all")

for row in db_session.query(User).order_by(User.id):
    print(row)

print("\n Pure SQL")
cursor = db_session.connection()
results = cursor.execute("SELECT * from users").fetchall()
for res in results:
    print res


quit()
