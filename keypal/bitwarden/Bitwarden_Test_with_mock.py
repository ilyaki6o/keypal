import unittest
from unittest.mock import patch, MagicMock
from Bitwarden import BitwardenClient, LoginError, SessionError

class TestBitwardenClient(unittest.TestCase):

    def setUp(self):
        self.client = BitwardenClient(client_dir='/test/dir', client_id='test_id', client_secret='test_secret')

    @patch('pexpect.spawn')
    def test_login(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.login()

        mock_spawn.assert_called_with("bw login --apikey", env=self.client.env_dict)
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_login_error(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 1

        with self.assertRaises(LoginError):
            self.client.login()

    @patch('pexpect.spawn')
    def test_logout(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.logout()

        mock_spawn.assert_called_with("bw logout", env=self.client.env_dict)
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_unlock(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0
        mock_child.before.splitlines.return_value = [b'test_session_key']

        self.client.unlock('test_password')

        mock_spawn.assert_called_with("bw unlock --raw", env=self.client.env_dict)
        self.assertTrue(self.client.unlocked)
        self.assertEqual(self.client.session_key, 'test_session_key')

    @patch('pexpect.spawn')
    def test_lock(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.lock()

        mock_spawn.assert_called_with("bw lock", env=self.client.env_dict)
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_list_items(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'[{"id": "1", "name": "Test Item"}]'

        items = self.client.list_items()

        self.assertEqual(items, [{"id": "1", "name": "Test Item"}])

    def test_list_items_locked(self):
        self.client.unlocked = False

        with self.assertRaises(SessionError):
            self.client.list_items()

    def test_search_items_with_uri_part(self):
        self.client.unlocked = True
        self.client.password_data = [
            {'login': {'uris': [{'uri': 'https://example.com'}]}},
            {'login': {'uris': [{'uri': 'https://test.com'}]}}
        ]
        self.client.spoiled_data = False

        results = self.client.search_items_with_uri_part('example')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['login']['uris'][0]['uri'], 'https://example.com')

    @patch('pexpect.spawn')
    def test_get_status(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'{"status": "unlocked"}'

        status = self.client.get_status()

        self.assertEqual(status, 'unlocked')

    @patch('pexpect.spawn')
    def test_sync(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.sync()

        mock_spawn.assert_called_with("bw sync", env=self.client.env_dict)
        self.assertTrue(self.client.spoiled_data)

    def test_get_password_by_id(self):
        self.client.unlocked = True
        self.client.password_data = [
            {'id': '1', 'login': {'username': 'user1', 'password': 'pass1'}},
            {'id': '2', 'login': {'username': 'user2', 'password': 'pass2'}}
        ]
        self.client.spoiled_data = False

        result = self.client.get_password_by_id('1')

        self.assertEqual(result, ('user1', 'pass1'))



    @patch('pexpect.spawn')
    def test_generate_passphrase(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'generated-pass-phrase'

        passphrase = self.client.generate_passphrase()

        self.assertEqual(passphrase, 'generated-pass-phrase')



if __name__ == '__main__':
    unittest.main()