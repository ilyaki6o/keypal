import unittest
import os
from unittest.mock import patch, MagicMock
from bitwarden import BitwardenClient, LoginError, SessionError


class TestBitwardenClient(unittest.TestCase):
    def setUp(self):
        self.client = BitwardenClient("test_dir", "test_id", "test_secret")

    def test_init(self):
        self.assertEqual(self.client.client_id, "test_id")
        self.assertEqual(self.client.client_secret, "test_secret")
        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_login(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0

        self.client.login()

        mock_spawn.assert_called_with("bw login --apikey",
                                      env=os.environ | {'BITWARDENCLI_APPDATA_DIR': 'test_dir'})
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

        mock_spawn.assert_called_with("bw logout",
                                      env=os.environ | {'BITWARDENCLI_APPDATA_DIR': 'test_dir'})
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

        mock_spawn.assert_called_with("bw lock",
                                      env=os.environ | {'BITWARDENCLI_APPDATA_DIR': 'test_dir'})
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
    def test_sync(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.exitstatus = 0
        self.client.sync()
        mock_spawn.assert_called_with("bw sync",
                                      env=os.environ | {'BITWARDENCLI_APPDATA_DIR': 'test_dir'})
        self.assertTrue(self.client.spoiled_data)

    @patch('pexpect.spawn')
    def test_generate_password(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'generated_password'
        mock_spawn.return_value = mock_child
        self.client.session_key = 'test_session_key'

        password = self.client.generate_password()

        self.assertEqual(password, 'generated_password')

    @patch('pexpect.spawn')
    def test_get_password_by_id(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        mock_child = MagicMock()
        mock_child.read.return_value = b'[{"id": "test_id", "login": {"username": "testuser", "password": "testpass"}}]'
        mock_spawn.return_value = mock_child

        username, password = self.client.get_password_by_id('test_id')

        self.assertEqual(username, 'testuser')
        self.assertEqual(password, 'testpass')

    @patch('pexpect.spawn')
    def test_get_status(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'{"status": "unlocked"}'
        mock_spawn.return_value = mock_child

        status = self.client.get_status()

        self.assertEqual(status, 'unlocked')

    @patch('pexpect.spawn')
    def test_get_password_by_id_not_found(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        mock_child = MagicMock()
        mock_child.read.return_value = b'[{"id": "other_id", "login": {"username": "testuser", "password": "testpass"}}]'
        mock_spawn.return_value = mock_child

        result = self.client.get_password_by_id('nonexistent_id')

        self.assertEqual(result, ())

    def test_search_items_with_uri_part_no_match(self):
        self.client.unlocked = True
        self.client.password_data = [
            {'login': {'uris': [{'uri': 'https://example.com'}]}}
        ]
        self.client.spoiled_data = False

        items = self.client.search_items_with_uri_part('nonexistent.com')

        self.assertEqual(len(items), 0)

    @patch('pexpect.spawn')
    def test_generate_passphrase(self, mock_spawn):
        mock_child = MagicMock()
        mock_spawn.return_value = mock_child
        mock_child.read.return_value = b'generated-pass-phrase'

        passphrase = self.client.generate_passphrase()

        self.assertEqual(passphrase, 'generated-pass-phrase')

    def test_check_exitstatus(self):
        with self.assertRaises(LoginError):
            self.client.check_exitstatus(1, LoginError, "Test error message")
        try:
            self.client.check_exitstatus(0, LoginError, "Test error message")
        except LoginError:
            self.fail("check_exitstatus raised LoginError unexpectedly!")

    @patch('pexpect.spawn')
    def test_login_with_custom_credentials(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.exitstatus = 0
        mock_spawn.return_value = mock_child

        self.client.login(client_id='custom_id', client_secret='custom_secret')

        mock_spawn.assert_called_with("bw login --apikey", env=self.client.env_dict)
        mock_child.sendline.assert_any_call('custom_id')
        mock_child.sendline.assert_any_call('custom_secret')

    @patch('pexpect.spawn')
    def test_list_items_cache(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        self.client.spoiled_data = False
        self.client.password_data = [{"id": "1", "name": "Cached Item"}]

        items = self.client.list_items()

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Cached Item')
        mock_spawn.assert_not_called()

    def test_search_items_with_uri_part_multiple_matches(self):
        self.client.unlocked = True
        self.client.password_data = [
            {'id': '1', 'login': {'uris': [{'uri': 'https://example.com'}]}},
            {'id': '2', 'login': {'uris': [{'uri': 'https://example.org'}]}},
            {'id': '3', 'login': {'uris': [{'uri': 'https://example.net'}]}}
        ]
        self.client.spoiled_data = False

        items = self.client.search_items_with_uri_part('example')

        self.assertEqual(len(items), 3)
        self.assertEqual([item['id'] for item in items], ['1', '2', '3'])

    @patch('pexpect.spawn')
    def test_get_status_locked(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'{"status": "locked"}'
        mock_spawn.return_value = mock_child

        status = self.client.get_status()

        self.assertEqual(status, 'locked')

    @patch('pexpect.spawn')
    def test_get_status_unlocked(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        mock_child = MagicMock()
        mock_child.read.return_value = b'{"status": "unlocked"}'
        mock_spawn.return_value = mock_child

        status = self.client.get_status()

        self.assertEqual(status, 'unlocked')
        mock_spawn.assert_called_with("bw status", env=self.client.env_dict | {"BW_SESSION": self.client.session_key})

    @patch('pexpect.spawn')
    def test_generate_password_with_options(self, mock_spawn):
        mock_child = MagicMock()
        self.client.session_key = 'test_session_key'
        mock_child.read.return_value = b'generated_password_with_options'
        mock_spawn.return_value = mock_child

        password = self.client.generate_password()

        mock_spawn.assert_called_with("bw generate", env=self.client.env_dict | {"BW_SESSION": self.client.session_key})
        self.assertEqual(password, 'generated_password_with_options')

    @patch('pexpect.spawn')
    def test_generate_passphrase_with_options(self, mock_spawn):
        mock_child = MagicMock()
        self.client.session_key = 'test_session_key'
        mock_child.read.return_value = b'word1-word2-word3'
        mock_spawn.return_value = mock_child

        passphrase = self.client.generate_passphrase()

        mock_spawn.assert_called_with("bw generate --passphrase")
        self.assertEqual(passphrase, 'word1-word2-word3')

    @patch('pexpect.spawn')
    def test_del_password_by_id_failure(self, mock_spawn):
        self.client.unlocked = True
        self.client.session_key = 'test_session_key'
        mock_child = MagicMock()
        mock_child.exitstatus = 1
        mock_spawn.return_value = mock_child

        with self.assertRaises(Exception):
            self.client.del_password_by_id('non_existent_id')

    def test_check_exitstatus_success(self):
        self.client.check_exitstatus(0, Exception, "Test message")

    def test_check_exitstatus_failure(self):
        with self.assertRaises(Exception) as context:
            self.client.check_exitstatus(1, Exception, "Test message")
        self.assertEqual(str(context.exception), "Test message")

    @patch('pexpect.spawn')
    def test_unlock_incorrect_password(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.exitstatus = 1
        mock_spawn.return_value = mock_child

        with self.assertRaises(LoginError):
            self.client.unlock('incorrect_password')

        self.assertFalse(self.client.unlocked)

    @patch('pexpect.spawn')
    def test_sync_updates_spoiled_data(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.exitstatus = 0
        mock_spawn.return_value = mock_child

        self.client.spoiled_data = False
        self.client.sync()

        self.assertTrue(self.client.spoiled_data)

    @patch('pexpect.spawn')
    def test_generate_password_length(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'abcdefghijklmn'  # 14 characters
        mock_spawn.return_value = mock_child
        self.client.session_key = 'test_session_key'

        password = self.client.generate_password()

        self.assertEqual(len(password), 14)

    @patch('pexpect.spawn')
    def test_generate_passphrase_word_count(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'word1-word2-word3'
        mock_spawn.return_value = mock_child

        passphrase = self.client.generate_passphrase()

        self.assertEqual(len(passphrase.split('-')), 3)

    def test_get_password_by_id_case_sensitivity(self):
        self.client.unlocked = True
        self.client.password_data = [
            {'id': 'ABC123', 'login': {'username': 'user1', 'password': 'pass1'}},
            {'id': 'DEF456', 'login': {'username': 'user2', 'password': 'pass2'}}
        ]
        self.client.spoiled_data = False

        result = self.client.get_password_by_id('abc123')

        self.assertEqual(result, ())

    @patch('pexpect.spawn')
    def test_login_with_empty_credentials(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.exitstatus = 1
        mock_spawn.return_value = mock_child

        with self.assertRaises(LoginError):
            self.client.login(client_id='', client_secret='')

    @patch('pexpect.spawn')
    def test_unlock_sets_session_key(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.exitstatus = 0
        mock_child.before = b'test_session_key\n'
        mock_spawn.return_value = mock_child

        self.client.unlock('test_password')

        self.assertEqual(self.client.session_key, 'test_session_key')

    @patch('pexpect.spawn')
    def test_generate_passphrase_does_not_use_session(self, mock_spawn):
        mock_child = MagicMock()
        mock_child.read.return_value = b'word1-word2-word3'
        mock_spawn.return_value = mock_child

        self.client.session_key = 'test_session_key'
        self.client.generate_passphrase()

        mock_spawn.assert_called_with("bw generate --passphrase")

    @patch('pexpect.spawn')
    def test_unlock_with_empty_password(self, mock_spawn):
        with self.assertRaises(LoginError):
            self.client.unlock('')


if __name__ == '__main__':
    unittest.main()
