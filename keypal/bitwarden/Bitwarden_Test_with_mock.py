import unittest
from unittest.mock import patch, MagicMock

from Bitwarden import BitwardenClient, LoginError, SessionError

class TestBitwardenClient(unittest.TestCase):

    def setUp(self):
        self.client = BitwardenClient("test_id", "test_secret")

    def test_init(self):
        self.assertEqual(self.client.client_id, "test_id")
        self.assertEqual(self.client.client_secret, "test_secret")
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_login_success(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.login()

        mock_spawn.assert_called_with("bw login --apikey")
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_login_failure(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 1

        with self.assertRaises(LoginError):
            self.client.login()

    @patch('pexpect.spawn')
    def test_logout_success(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.logout()

        mock_spawn.assert_called_with("bw logout")
        self.assertFalse(self.client.unlocked)

   
    @patch('pexpect.spawn')
    def test_lock_success(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.lock()

        mock_spawn.assert_called_with("bw lock")
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_list_items_success(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = "test_session_key"
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'[{"id": "1", "name": "Test Item"}]'

        items = self.client.list_items()

        self.assertEqual(items, [{"id": "1", "name": "Test Item"}])

    def test_list_items_locked(self):
        self.client.unlocked = False

        with self.assertRaises(SessionError):
            self.client.list_items()
    
    @patch('pexpect.spawn')
    def test_get_status(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'{"status": "unlocked"}'

        status = self.client.get_status()

        self.assertEqual(status, "unlocked")



    @patch('pexpect.spawn')
    def test_sync_success(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.sync()

        mock_spawn.assert_called_with("bw sync")

    @patch('pexpect.spawn')
    def test_sync_failure(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 1

        with self.assertRaises(LoginError):
            self.client.sync()

   


if __name__ == '__main__':
    unittest.main()