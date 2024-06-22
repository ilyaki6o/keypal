import sqlite3

class Database:

    def __init__(self,id):
        self.id=id
        self.db=sqlite3.connect('./database.db')
        self.cursor=self.db.cursor()
        query=""" CREATE TABLE IF NOT EXISTS APIKEYS(id TEXT, client_id TEXT, client_secret TEXT) """
        self.cursor.execute(query)

 






