"""Main logic for database interactions."""
import sqlite3


class Database:
    """A class to manage Bitwarden API keys in a SQLite database."""

    def __init__(self, id):
        """
        Create the APIKEYS table in the database if it does not already exist.

        :param id: The unique identifier for the API key.
        :type id: str
        """
        self.id = id
        self.db = sqlite3.connect('./database.db')
        self.cursor = self.db.cursor()
        query = """ CREATE TABLE IF NOT EXISTS APIKEYS(id TEXT PRIMARY KEY, client_id TEXT, client_secret TEXT) """
        self.cursor.execute(query)

    def check(self):
        """
        Verify if an API key with the specified id is present in the database.

        :return: A tuple with (client_id, client_secret) if found, otherwise an empty tuple.
        :rtype: tuple
        """
        query1 = f"""SELECT COUNT(*) FROM APIKEYS WHERE id='{self.id}'"""
        self.cursor.execute(query1)
        result = self.cursor.fetchone()[0]
        if result != 0:
            query2 = f"""SELECT client_id,client_secret FROM APIKEYS WHERE id='{self.id}'"""
            self.cursor.execute(query2)
            return self.cursor.fetchone()
        return ()

    def add_new(self, client_id, client_secret):
        """
        Insert a new API key  into the database.

        :param client_id: The client id of the API key.
        :type client_id: str
        :param client_secret: The client secret of the API key.
        :type client_secret: str
        :return: True if the key was added successfully, False if a key with this id already exists.
        :rtype: bool
        """
        if self.check() == ():
            query3 = f""" INSERT INTO APIKEYS (id,client_id,client_secret) VALUES('{self.id}','{client_id}','{client_secret}')"""
            self.cursor.execute(query3)
            self.db.commit()
            return True
        return False

    def delete_key(self):
        """Delete the API key with the current id from the database."""
        query4 = f"""DELETE FROM APIKEYS WHERE id ='{self.id}' """
        self.cursor.execute(query4)
        self.db.commit()

    def change_password(self, client_id, client_secret):
        """
        Update the client ID and client secret for the current API key in the database.

        :param client_id: The new value of client identifier.
        :type client_id: str
        :param client_secret: The new value of client secret.
        :type client_secret: str
        """
        query5 = f"""UPDATE APIKEYS SET [client_id]='{client_id}', [client_secret]='{client_secret}' WHERE id='{self.id}'"""
        self.cursor.execute(query5)
        self.db.commit()

    def get_all_information(self):
        """
        Retrieve all information from the APIKEYS table in the database.

        :return: A list containing all records from the APIKEYS table.
        :rtype: list of tuples
        """
        query6 = """SELECT * FROM APIKEYS"""
        self.cursor.execute(query6)
        records = self.cursor.fetchall()
        answer = []
        for record in records:
            answer.append(record)
        return answer

    def close(self):
        """Close the database connection."""
        self.db.close()
