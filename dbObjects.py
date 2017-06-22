# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from flask import Flask
import re

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first = Column(String)
    last = Column(String)
    email = Column(String)
    status = Column(Integer)
    password = Column(String)
    pin = Column(Integer)
    username = Column(String)

    posts = relationship("Idea", back_populates = "user")
    comments = relationship("Comment", back_populates="user")

    def __repr__(self):
        return "<User(%s %s )>" % (str(self.first), str(self.last))

class Idea(Base):
    __tablename__ = 'ideas'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    body = Column(String)
    datetime = Column(DateTime)
    status = Column(Integer)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="idea", order_by="desc(Comment.datetime)")  #### NOTE ORDER_BY!!!

    def __repr__(self):
        return "<User(UID:%s, BODY:%s, STATUS:%s )>" % (str(self.user_id), str(self.body),str(self.status))

    def numberOfComments(self):
        # returns number of coments for current idea() object
        # called from template to show # of comments
        return len(self.comments)

    def getLastComments(self,num = 5):
        # returns a list of n Comment() objects

        numOfComm = self.numberOfComments()
        print "getLastComments numOfComm:",numOfComm
        print "getLastComments n:", num

        if(num>numOfComm):
            print("here222")
            print(num > numOfComm)
            head = numOfComm
        else:
            print("here")
            head = num

        print "getLastComments head:", head

        result = self.comments[:head]
        return result

    def getTime(self):

        now = datetime.datetime.now()
        t_diff = now - self.datetime

        if(t_diff.days > 31):
            result = "Posted " + str(t_diff.days) + " days ago"
        elif(t_diff.days >= 7):                                         ### added proper week/weekS nding - still to be improved
            if (t_diff.days >= 14 ):
                result = "Posted " + str(t_diff.days//7) + " weeks ago"
            else:
                result = "Posted " + str(t_diff.days//7) + " week ago"
        elif(t_diff.days):
            result = "Posted " + str(t_diff.days) + " days and " + str(t_diff.seconds//3600) + " hours ago."
        elif(t_diff.seconds//3600):
            result = "Posted "+ str(t_diff.seconds//3600) + " hours and " + str((t_diff.seconds//60)%60) + " minutes ago"
        elif((t_diff.seconds//60)%60):
            result = "Posted " + str((t_diff.seconds//60)%60) + " minutes ago"
        else:
            result = "Posted just now"
        return result



class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    idea_id = Column(ForeignKey('ideas.id'))
    datetime = Column(DateTime)
    body = Column(String)

    user = relationship("User",back_populates="comments")
    idea = relationship("Idea",back_populates="comments")

    def __repr__(self):
        return "<Comment(UID:%s, IDEAID:%s, BODY:%s )>" % (str(self.user_id), str(self.idea_id),str(self.body))

    def getTime(self):

        now = datetime.datetime.now()
        t_diff = now - self.datetime

        if(t_diff.days > 31):
            result = "" + str(t_diff.days) + " days ago"
        elif(t_diff.days >= 7):
            result = "" + str(t_diff.days//7) + " weeks ago"
        elif(t_diff.days):
            result = "" + str(t_diff.days) + " days and " + str(t_diff.seconds//3600) + " hours ago."
        elif(t_diff.seconds//3600):
            result = ""+ str(t_diff.seconds//3600) + " hours and " + str((t_diff.seconds//60)%60) + " minutes ago"
        elif((t_diff.seconds//60)%60):
            result = "" + str((t_diff.seconds//60)%60) + " minutes ago"
        else:
            result = "just now"
        return result

    def linkify(self):
        url_regex = re.compile(r"""
               [^\s]             # not whitespace
               [a-zA-Z0-9:/\-]+  # the protocol and domain name
               \.(?!\.)          # A literal '.' not followed by another
               [\w\-\./\?=&%~#]+ # country and path components
               [^\s]             # not whitespace""", re.VERBOSE)

        raw_message = self.body
        message = raw_message

        for url in url_regex.findall(raw_message):
            if url.endswith('.'):
                url = url[:-1]
            if 'http://' not in url or 'https://' not in url:
                hasurl=False
            else:
                hasurl=True

            if hasurl:
                if 'http://' in url:
                    href = 'http://' + url
                if 'https://' in url:
                    href = 'https://' + url
            else:
                href = 'http://' + url
            message = message.replace(url, '<a href="%s">%s</a>' % (href, url))

        return message

if __name__ == "__main__":
    from sqlalchemy import create_engine, desc, update
    from sqlalchemy.orm import sessionmaker


    print "test"
    engine = create_engine('mysql://aba:007@127.0.0.1/idea?charset=utf8',encoding='utf-8')
    Session = sessionmaker(bind=engine)
    dbSession = Session()

    #userlist = dbSession.query(User).order_by(desc(User.id))
    #print userlist

    #for user in userlist:
    #    print "User:" + user.username
    #    print(user.posts)

    print "-------------------------------ideas:"
    ideasLst = dbSession.query(Idea).order_by(desc(Idea.datetime))
    for idea in ideasLst:
        print idea.user.username
        print idea.datetime,idea.body
        print"--"

