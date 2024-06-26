import unittest
from unittest.mock import patch, MagicMock
from bitwarden import BitwardenClient, LoginError, SessionError


class TestBitwardenClient(unittest.TestCase):
    def setUp(self):
        self.client = BitwardenClient()
        self.client.login('user.bf9659c9-d39d-4520-a6bf-b19a00b9d664' , 'nA6wX8AFP88XAhcqjBGy058JxhPqVx')
        self.client.unlock("KUCHEROV878697")

    def tearDown(self):
        self.client.lock()
        self.client.logout()

    def test_1_list_items(self):
        data = self.client.list_items()
        id_set = {item['id'] for item in data}
        self.assertTrue(id_set == {"cadfbea5-8a5c-4fe3-bc34-b19a00cec572", "7aeb48e7-57af-4a82-aec5-b19b007f1775"} or id_set == {"7aeb48e7-57af-4a82-aec5-b19b007f1775", "cadfbea5-8a5c-4fe3-bc34-b19a00cec572"})

    def test_2_get_password_by_id(self):
        id = 'cadfbea5-8a5c-4fe3-bc34-b19a00cec572'
        data = self.client.get_password_by_id(id)
        self.assertEqual(data, ('MEME', 'OHMY'))

    def test_3_create_password(self):
        uri = 'google'
        username = 'ROMAN'
        password = 'BITWARDENFOREVER'
        new_password = self.client.create_password(uri, username, password)
        id = new_password['id']
        data = self.client.list_items()
        self.assertEqual(data[-1]['login']['password'], new_password['login']['password'])
        self.client.del_password_by_id(id)

    def test_4_create_and_del_password(self):
        uri = 'yaho'
        username = 'ILYA'
        password = 'iLOVETGBOT'
        new_password = self.client.create_password(uri, username, password)
        self.client.del_password_by_id(new_password['id'])
        self.assertTrue(new_password not in self.client.list_items())


if __name__ == '__main__':
    unittest.main()
