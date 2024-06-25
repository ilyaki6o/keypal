"""Module for interaction with Bitwarden cli."""

import pexpect
import json
import os
import tempfile


class LoginError(Exception):
    """Exception for handling login errors."""

    pass


class SessionError(Exception):
    """Excepion for handling session errors."""

    pass


class BitwardenClient:
    """Class for interacting with the Bitwarden password manager."""

    def __init__(self, client_dir='', client_id='', client_secret=''):
        """Init BitwardenClient class with user's secret info."""
        self.client_id = client_id
        self.env_dict = os.environ | {'BITWARDENCLI_APPDATA_DIR': client_dir}
        self.client_secret = client_secret
        self.unlocked = False
        self.spoiled_data = True

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
        child = pexpect.spawn("bw login --apikey", env=self.env_dict)
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
        child = pexpect.spawn("bw logout", env=self.env_dict)
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
        child = pexpect.spawn("bw unlock --raw", env=self.env_dict)
        child.expect("Master password")
        child.sendline(password)
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.session_key = child.before.splitlines()[-1].decode()
        self.unlocked = True

    def lock(self):
        """Lock the Bitwarden vault."""
        child = pexpect.spawn("bw lock", env=self.env_dict)
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.unlocked = False

    def list_items(self):
        """Get list of all items in Bitwarden vault."""
        if self.unlocked:
            if self.spoiled_data:
                child = pexpect.spawn('bw list items',
                                      env=self.env_dict | {"BW_SESSION": self.session_key})
                raw_data = child.read().decode()
                data = json.loads(raw_data.splitlines()[-1])
                self.password_data = data
                self.spoiled_data = False
            else:
                data = self.password_data
            return data
        else:
            raise SessionError("Your vault is locked")

    def search_items_with_uri_part(self, uri_part):
        """
        Search for Bitwarden items that have a URI containing with the provided URI part.

        :param uri: URI to search for.
        :type uri: str
        :return: List of URIs that match the search criteria.
        :rtype: list
        """
        data = self.list_items()
        res = []
        for item in data:
            login = item['login']
            uris = login['uris']
            if any(uri_part in uri['uri'] for uri in uris):
                res.append(item.copy())
        return res

    def get_status(self):
        """Get current status of Bitwarden vault."""
        cmd = "bw status"
        env = {}
        if self.unlocked:
            env["BW_SESSION"] = self.session_key
        child = pexpect.spawn(cmd, env=self.env_dict | env)
        data = child.read().decode().splitlines()[-1]
        values = json.loads(data)
        return values.get('status', '')

    def sync(self):
        """Synchronize Bitwarden vault."""
        child = pexpect.spawn("bw sync", env=self.env_dict)
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              LoginError,
                              "You are not logged in.")
        self.spoiled_data = True
        if self.unlocked:
            self.list_items()

    def get_password_by_id(self, id):
        """
        Retrieve username and password for the Bitwarden item with the provided ID.

        :param id: The ID of the Bitwarden item.
        :type id: str
        :return: Tuple containing the username and password, or empty tuple if item is not found.
        :rtype: tuple
        """
        items = self.list_items()
        for item in items:
            if item['id'] == id:
                return (item['login']['username'], item['login']['password'])
        return ()

    def del_password_by_id(self, id):
        """
        Delete Bitwarden item with the provided ID.

        :param id: ID of the Bitwarden item to delete.
        :type id: str
        """
        child = pexpect.spawn(f"bw delete item {id}",
                              env=self.env_dict | {"BW_SESSION": self.session_key})
        child.expect(pexpect.EOF)
        child.close()
        self.check_exitstatus(child.exitstatus,
                              Exception,
                              "Password not found")
        self.spoiled_data = True
        self.sync()

    def create_password(self, uri, username, password):
        """
        Create password in Bitwarden vault by uri and username.

        :param uri: network address associated with password
        :type uri: str
        :param username: login associated with password
        :type username: str
        :password: password
        :type password: str
        :return: parsed json object returned by Bitwarden
        :rtype: Json dictionary
        """
        if self.unlock:
            child = pexpect.spawn("bw get template item",
                                  env=self.env_dict | {"BW_SESSION": self.session_key})
            item_template = child.read().decode().splitlines()[-1]
            item_template = json.loads(item_template)
            child.expect(pexpect.EOF)
            child.close()
            child = pexpect.spawn("bw get template item.login",
                                  env=self.env_dict | {"BW_SESSION": self.session_key})
            login_template = child.read().decode().splitlines()[-1]
            login_template = json.loads(login_template)
            child.expect(pexpect.EOF)
            child.close()
            login_template["username"] = username
            login_template["password"] = password
            login_template["uris"].append({"match": None, "uri": uri})
            item_template["name"] = "KeyPal_generated"
            item_template["login"] = login_template
            with tempfile.NamedTemporaryFile("w+") as tmp:
                tmp.write(json.dumps(item_template))
                tmp.seek(0)
                child = pexpect.spawn(f'/bin/bash -c "bw encode < {tmp.name}"')
                encoded_json = child.read().decode().splitlines()[-1]
            child = pexpect.spawn(f"bw create item {encoded_json}",
                                  env=self.env_dict | {"BW_SESSION": self.session_key})
            new_password = child.read().decode().splitlines()[-1]
            new_password = json.loads(new_password)
            child.expect(pexpect.EOF)
            child.close()
            self.sync()
            return new_password

    def generate_password(self):
        """Generate password with length of 14 symbols containing letters and digits."""
        child = pexpect.spawn("bw generate")
        password = child.read()
        child.expect(pexpect.EOF)
        child.close()
        return password.decode().splitlines()[-1]

    def generate_passphrase(self):
        """Generate passphrase containing 3 words split by '-'."""
        child = pexpect.spawn("bw generate --passphrase")
        passphrase = child.read()
        child.expect(pexpect.EOF)
        child.close()
        return passphrase.decode().splitlines()[-1]


if __name__ == "__main__":
    bw1 = BitwardenClient('Igor')
    bw2 = BitwardenClient('Roma')
    bw1.login("user.63b0f8d5-c939-4fe9-94ef-b18300c96a51", "CsQTsbVedEMzR2v9Ji8bFLikgHbo9Y")
    bw2.login("user.65ba2bf2-52e7-461f-8a60-b199007a8fcd", "4dhEts3hBIsCDVYm5WwGklJ8N7cGZ5")
    bw1.unlock("CROSBY878697")
    bw2.unlock("passwordforbitwarden")
    print(bw1.list_items())
    bw2.create_password("google.com", "roma", "aaaaaaa")
    print(bw2.list_items())
    bw1.logout()
    bw2.logout()
