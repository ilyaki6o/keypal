import sqlite3

class Database:

    def __init__(self,id):
        self.id=id
        self.db=sqlite3.connect('./database.db')
        self.cursor=self.db.cursor()
        query=""" CREATE TABLE IF NOT EXISTS APIKEYS(id TEXT, client_id TEXT, client_secret TEXT) """
        self.cursor.execute(query)

    def check(self):
        query1=f"""SELECT COUNT(*) FROM APIKEYS WHERE id='{self.id}'"""
        self.cursor.execute(query1)
        result=self.cursor.fetchone()[0]
        if result !=0:
            query2=f"""SELECT client_id,client_secret FROM APIKEYS WHERE id='{self.id}'"""
            self.cursor.execute(query2)
            return self.cursor.fetchone()
        return ()
    
   






