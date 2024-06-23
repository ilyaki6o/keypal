import sqlite3



class Database:
    """
    A class to manage Bitwarden API keys in a SQLite database.
    """

    def __init__(self,id):
        """
        Initialize the Database object.

        Args:
            id (str): The unique identifier for the API key.

        This method establishes a connection to the SQLite database
        and creates the APIKEYS table if it doesn't exist.
        """
        self.id=id
        self.db=sqlite3.connect('./database.db')
        self.cursor=self.db.cursor()
        query=""" CREATE TABLE IF NOT EXISTS APIKEYS(id TEXT PRIMARY KEY, client_id TEXT, client_secret TEXT) """
        self.cursor.execute(query)


    def check(self):
        """
        Check if an API key with the given id exists in the database.

        Returns:
            tuple: A tuple containing (client_id, client_secret) if the key exists, 
                   an empty tuple otherwise.
        """
        query1=f"""SELECT COUNT(*) FROM APIKEYS WHERE id='{self.id}'"""
        self.cursor.execute(query1)
        result=self.cursor.fetchone()[0]
        if result !=0:
            query2=f"""SELECT client_id,client_secret FROM APIKEYS WHERE id='{self.id}'"""
            self.cursor.execute(query2)
            return self.cursor.fetchone()
        return ()

    
    def add_new(self, client_id, client_secret):
        """
        Add a new API key to the database.

        Args:
            client_id (str): The client_id for the API key.
            client_secret (str): The client_secret for the API key.

        Returns:
            bool: True if the key was successfully added, False if the key with this id already exists.
        """
        if self.check()==():
            query3=f""" INSERT INTO APIKEYS (id,client_id,client_secret) VALUES('{self.id}','{client_id}','{client_secret}')"""
            self.cursor.execute(query3)
            self.db.commit()
            return True
        return False


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
        """
        Close the database connection.
        """
        self.db.close()





