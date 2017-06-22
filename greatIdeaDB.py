from flask import Flask, render_template, json, request, redirect, session, url_for, Response,json
from functools import wraps
from sqlalchemy import create_engine, desc, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from dbObjects import User, Idea


class GreatIdeaDB():
    def __init__(self):
        engine = create_engine('mysql://aba:007@127.0.0.1/idea?charset=utf8',encoding='utf-8')
        Session = sessionmaker(bind=engine)
        self.dbSession = Session()

    def findUserByUsername(self,username):
        result = self.dbSession.query(User).filter(User.username == username).first()
        return result

    def findUserByPin(self,pin):
        result = self.dbSession.query(User).filter(User.pin == pin).first()
        return result

    def getAllIdeasByUserId(self,userid,order = 0):       #-1 dec 0-default ,1-acc
        if(order == -1):
           result = self.dbSession.query(Idea).filter(Idea.user_id == userid).order_by(desc(Idea.datetime))
        elif(order == 1):
            result = self.dbSession.query(Idea).filter(Idea.user_id == userid).order_by(Idea.datetime)
        else:
            reuslt = self.dbSession.query(Idea).filter(Idea.user_id == userid)

        return result

    def getIdeaById(self,id):
        idea = self.dbSession.query(Idea).filter(Idea.id == id).first()
        print(idea)
        return idea


    def activateUser(self,user):
        user.status = 1
        self.dbSession.commit()

    def add(self,entity):
        add = self.dbSession.add(entity)
        commit = self.dbSession.commit()