import datetime

class IdeaFeed():
    def __init__(self, user, idea):
        self.user = user
        self.idea = idea

    def __repr__(self):
        return self.user.username + " " + self.idea.datetime + "," + self.idea.body
