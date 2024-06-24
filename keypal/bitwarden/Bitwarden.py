"""Module for interaction with Bitwarden cli."""

import pexpect
from typing import List
import json
import os


class LoginError(Exception):
    """Exception for handling login errors."""

    pass


class SessionError(Exception):
    """Excepion for handling session errors."""

    pass


class BitwardenClient:
    """Class for interacting with the Bitwarden password manager."""

    def __init__(self, client_id='', client_secret=''):
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

    def login(self, client_id='', client_secret=''):
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

    def unlock(self, password):
        """
        Unlock Bitwarden vault using provided master password.

        :param password: Master password for the Bitwarden vault.
        :type password: str
        :return: Session key obtained after unlocking the vault.
        :rtype: str
        """
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
        if self.unlocked:
            cmd = "bw list items"
            child = pexpect.spawn('bw list items',
                                  env=os.environ | {"BW_SESSION": self.session_key})
            raw_data = child.read().decode()
            data = json.loads(raw_data.splitlines()[-1])
            return data
        else:
            raise SessionError("Your vault is locked")

    def search_items_with_uri(self, uri):
        """
        Search for Bitwarden items that have a URI starting with the provided URI.

        :param uri: URI to search for.
        :type uri: str
        :return: List of URIs that match the search criteria.
        :rtype: list
        """
        # with pexpect.spawn("bw list items") as child:
            # child.expect("Master password:")
            # child.sendline(self.password)
            # response = child.read().decode()
        # json_start = response.find('')
        # json_string = response[json_start:]
        # items = json.loads(json_string)
        # all_uris=[]
        # for item in items:
            # for uri_obj in item['login']['uris']:
                # all_uris.append(uri_obj['uri'])
        # return [url for url in all_uris if url.startswith(uri)]

    def get_status(self):
        cmd = "bw status"
        env = {}
        if self.unlocked:
            env["BW_SESSION"] = self.session_key
        child = pexpect.spawn(cmd, env=os.environ | env)
        data = child.read().decode().splitlines()[-1]
        values = json.loads(data)
        return values.get('status', '')

    def is_locked(self):
        return self.get_status() == 'locked'

    def sync(self):
        """Synchronize Bitwarden vault."""
        child = pexpect.spawn("bw sync")
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")

    def get_password(self, id):
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
        
            data = json.loads(response[response.find(''):])
            login = data["login"]
            return (login["username"], login["password"])
        return ()


    def del_password(self, id):
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
            data = json.loads(response[response.find(''):])
            id_del = data["id"]
            child = pexpect.spawn(f"bw  delete item {id_del}")
            child.expect("Master password")
            child.sendline(self.password)
            child.expect(pexpect.EOF)

    def edit_password(self, id):
        pass


if __name__ == "__main__":
    bw1 = BitwardenClient()
    try:
        bw1.lock()
    except Exception as e:
        print(e)
    bw1.login("user.63b0f8d5-c939-4fe9-94ef-b18300c96a51", "CsQTsbVedEMzR2v9Ji8bFLikgHbo9Y")
    print(bw1.get_status())
    bw1.unlock("CROSBY878697")
    print(bw1.get_status())
    print(bw1.list_items())
    bw1.lock()
    try:
        bw1.list_items()
    except Exception as e:
        print(e)
    print(bw1.get_status())
    bw1.logout()
