"""Module for interaction with Bitwarden cli."""

import pexpect
from typing import List
import json


class LoginError(Exception):
    """Exception for handling login errors."""

    pass


class BitwardenClient:
    """Class for interacting with the Bitwarden password manager."""

    def __init__(self, client_id: str = '', client_secret: str = '') -> None:
        """Init BitwardenClient class with user's secret info."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.unlocked = False

    def check_exitstatus(self, exit_code, exception, message):
        """
        Check exit status of command.

        If it is not null raise given exception with given message
        """
        if exit_code:
            raise exception(message)

    def add_session_key(self, cmd):
        """Append session key to command."""
        return f"{cmd} --session {self.session_key}"

    def login(self, client_id: str = '', client_secret: str = '') -> None:
        """
        Log in to the Bitwarden API using provided client ID and client secret.

        :param client_id: Client ID for the Bitwarden API.
        :type client_id: str
        :param client_secret: Client secret for the Bitwarden API.
        :type client_secret: str
        """
        child = pexpect.spawn("bw login --apikey")
        child.expect("client_id")
        child.sendline(client_id or self.client_id)
        child.expect("client_secret")
        child.sendline(client_secret or self.client_secret)
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "Invalid client_id or client_secret")
        self.unlocked = False

    def logout(self) -> None:
        """Log out from the Bitwarden API."""
        child = pexpect.spawn("bw logout")
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.unlocked = False

    def unlock(self, password: str) -> str:
        """
        Unlock Bitwarden vault using provided master password.

        :param password: Master password for the Bitwarden vault.
        :type password: str
        :return: Session key obtained after unlocking the vault.
        :rtype: str
        """
        self.password = password
        child = pexpect.spawn("bw unlock --raw")
        child.expect("Master password")
        child.sendline(password)
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.session_key = child.before.splitlines()[-1].decode()
        self.unlocked = True

    def lock(self) -> None:
        """Lock the Bitwarden vault."""
        child = pexpect.spawn("bw lock")
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.unlocked = False

    def list_items(self):
        """Get list of all items in Bitwarden vault."""
        data = []
        if self.unlocked:
            cmd = self.add_session_key("bw list items")
            child = pexpect.spawn(cmd)
            raw_data = child.read().decode()
            payload_start = raw_data.find('[{')
            data = json.loads(raw_data[payload_start:])
        return data 


    def search_items_with_uri(self, uri: str):
        """
        Search for Bitwarden items that have a URI starting with the provided URI.

        :param uri: URI to search for.
        :type uri: str
        :return: List of URIs that match the search criteria.
        :rtype: list
        """
        with pexpect.spawn("bw list items") as child:
            child.expect("Master password:")
            child.sendline(self.password)
            response = child.read().decode()
        json_start = response.find('[{')
        json_string = response[json_start:]
        items = json.loads(json_string)
        all_uris=[]
        for item in items:
            for uri_obj in item['login']['uris']:
                all_uris.append(uri_obj['uri'])
        return [url for url in all_uris if url.startswith(uri)]


    def get_status(self) -> str:
        pass

    def sync(self) -> None:
        """Synchronize Bitwarden vault."""
        child = pexpect.spawn("bw sync")
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")

    def get_password(self, id: str):
        """
        Retrieve the username and password for the Bitwarden item with the provided ID.

        :param id: The ID of the Bitwarden item.
        :type id: str
        :return: A tuple containing the username and password, or an empty tuple if the item is not found.
        :rtype: tuple
        """
        if id in self.search_items_with_uri(id):
            with pexpect.spawn(f"bw get item {id}") as child:
                child.expect("Master password:")
                child.sendline(self.password)
                response = child.read().decode()
        
            data = json.loads(response[response.find('{'):])
            login = data["login"]
            return (login["username"], login["password"])
        return ()


    def del_password(self, id: str) :
        """
        Delete the Bitwarden item with the provided ID.

        :param id: ID of the Bitwarden item to delete.
        :type id: str
        """
        if id in self.search_items_with_uri(id):
            with pexpect.spawn(f"bw get item {id}") as child:
                child.expect("Master password:")
                child.sendline(self.password)
                response = child.read().decode()
            data = json.loads(response[response.find('{'):])
            id_del = data["id"]
            child = pexpect.spawn(f"bw  delete item {id_del}")
            child.expect("Master password")
            child.sendline(self.password)
            child.expect(pexpect.EOF)

    def edit_password(self, id: str) -> str:
        pass


if __name__ == "__main__":
    bw1 = BitwardenClient()
    bw1.login("user.63b0f8d5-c939-4fe9-94ef-b18300c96a51", "CsQTsbVedEMzR2v9Ji8bFLikgHbo9Y")
    # bw2 = BitwardenClient()
    # bw2.login("user.65ba2bf2-52e7-461f-8a60-b199007a8fcd", "4dhEts3hBIsCDVYm5WwGklJ8N7cGZ5")
    bw1.unlock("CROSBY878697")
    print(bw1.list_items())
    bw1.lock()
    bw1.logout()
