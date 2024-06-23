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
    
    def add_new(self, client_id, client_secret):
        query3=f""" INSERT INTO APIKEYS (id,client_id,client_secret) VALUES('{self.id}','{client_id}','{client_secret}')"""
        self.cursor.execute(query3)
        self.db.commit()

    def delete_key(self):
        """
        Delete the API key with the current id from the database.
        """
        query4=f"""DELETE FROM APIKEYS WHERE id ='{self.id}' """
        self.cursor.execute(query4)
        self.db.commit()

    def change_password(self,client_id, client_secret):
        """
        Update the client ID and client secret for the current API key.

        Args:
            client_id (str): The new client_id.
            client_secret (str): The new client_secret.
        """
        query5=f"""UPDATE APIKEYS SET [client_id]='{client_id}', [client_secret]='{client_secret}' WHERE id='{self.id}'"""
        self.cursor.execute(query5)
        self.db.commit()

    def close(self):
        self.db.close()






