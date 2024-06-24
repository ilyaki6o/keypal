import pexpect
from typing import List
import json


class BitwardenClient:
    """A client for interacting with the Bitwarden password manager."""
    def login(self, client_id: str, client_secret: str) -> None:
        """
        Log in to the Bitwarden API using the provided client ID and client secret.

        :param client_id: The client ID for the Bitwarden API.
        :type client_id: str
        :param client_secret: The client secret for the Bitwarden API.
        :type client_secret: str
        """
        child = pexpect.spawn("bw login --apikey")
        child.expect("client_id")
        child.sendline(client_id)
        child.expect("client_secret")
        child.sendline(client_secret)
        child.expect(pexpect.EOF)

    def logout(self) -> None:
        """
        Log out of the Bitwarden API.
        """
        child = pexpect.spawn("bw logout")
        child.expect(pexpect.EOF)

    def unlock(self, password: str) -> str:
        """
        Unlock the Bitwarden vault using the provided master password.

        :param password: The master password for the Bitwarden vault.
        :type password: str
        :return: The session key obtained after unlocking the vault.
        :rtype: str
        """
        self.password=password
        child = pexpect.spawn("bw unlock --raw")
        child.expect("Master password")
        child.sendline(password)
        child.expect(pexpect.EOF)
        self.session_key = child.before.splitlines()[-1]

    def lock(self) -> None:
        """
        Lock the Bitwarden vault.
        """
        child = pexpect.spawn("bw lock")
        child.expect(pexpect.EOF)

    def search_items_with_uri(self, uri: str):
        """
        Search for Bitwarden items that have a URI starting with the provided URI.

        :param uri: The URI to search for.
        :type uri: str
        :return: A list of URIs that match the search criteria.
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


    def sync(self) -> None:
        """
        Synchronize the Bitwarden vault with the server.
        """
        child = pexpect.spawn("bw sync")
        child.expect(pexpect.EOF)

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

        :param id: The ID of the Bitwarden item to delete.
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
    bw = BitwardenClient()
    bw.login("user.63b0f8d5-c939-4fe9-94ef-b18300c96a51", "CsQTsbVedEMzR2v9Ji8bFLikgHbo9Y")
    bw.unlock("CROSBY878697")
    #print(bw.get_password('y'))
    print(bw.search_items_with_uri('k'))
    #bw.del_password('asvko')
    bw.lock()
    bw.logout()
