import pexpect
from typing import List


class BitwardenClient:
    def login(self, client_id: str, client_secret: str) -> None:
        child = pexpect.spawn("bw login --apikey")
        child.expect("client_id")
        child.sendline(client_id)
        child.expect("client_secret")
        child.sendline(client_secret)
        child.expect(pexpect.EOF)

    def logout(self) -> None:
        child = pexpect.spawn("bw logout")
        child.expect(pexpect.EOF)

    def unlock(self, password: str) -> str:
        child = pexpect.spawn("bw unlock --raw")
        child.expect("Master password")
        child.sendline(password)
        child.expect(pexpect.EOF)
        self.session_key = child.before.splitlines()[-1]

    def lock(self) -> None:
        child = pexpect.spawn("bw lock")
        child.expect(pexpect.EOF)

    def search_items_with_uri(self, uri: str) -> List[str]:
        pass

    def sync(self) -> None:
        pass

    def get_password(self, id: str) -> str:
        pass

    def del_password(self, id: str) -> str:
        pass

    def edit_password(self, id: str) -> str:
        pass


if __name__ == "__main__":
    bw = BitwardenClient()
    bw.login("user.63b0f8d5-c939-4fe9-94ef-b18300c96a51", "CsQTsbVedEMzR2v9Ji8bFLikgHbo9Y")
    bw.unlock("CROSBY878697")
    bw.lock()
    bw.logout()
