from dbObjects import User, Idea
from sqlalchemy import create_engine, desc, update

def generateFeed(session):
    ideas = session.query(Idea).filter(Idea.status == 1).order_by(desc(Idea.datetime))
    return ideas

