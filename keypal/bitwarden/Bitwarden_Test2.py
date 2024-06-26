import unittest
from unittest.mock import patch, MagicMock

from Bitwarden import BitwardenClient, LoginError, SessionError

class TestBitwardenClient(unittest.TestCase):

    def setUp(self):
        self.client = BitwardenClient()
        self.client.login('user.bf9659c9-d39d-4520-a6bf-b19a00b9d664' , 'nA6wX8AFP88XAhcqjBGy058JxhPqVx')
        self.client.unlock("KUCHEROV878697")

    def tearDown(self):
        self.client.lock()
        self.client.logout()
    
    def test_list_items(self):
        data=self.client.list_items()
        self.assertTrue({'passwordHistory': None, 'revisionDate': '2024-06-26T07:33:56.573Z',
                                 'creationDate': '2024-06-25T12:32:49.866Z', 'deletedDate': None, 
                                 'object': 'item', 'id': 'cadfbea5-8a5c-4fe3-bc34-b19a00cec572', 
                                 'organizationId': None, 'folderId': None, 'type': 1, 'reprompt': 0, 
                                 'name': 'HOHO', 'notes': None, 'favorite': False,
                                  'login': {'fido2Credentials': [], 'uris': [{'match': None, 'uri': 'mail'}], 
                                  'username': 'MEME', 'password': 'OHMY', 'totp': None, 'passwordRevisionDate': None}, 'collectionIds': []} in data)


    def test_get_password_by_id(self):
        id='cadfbea5-8a5c-4fe3-bc34-b19a00cec572'
        data=self.client.get_password_by_id(id)
        self.assertEqual(data,('MEME', 'OHMY'))

    def test_create_password(self):
        uri='google'
        username='ROMAN'
        password='BITWARDENFOREVER'
        new_password=self.client.create_password(uri,username,password)
        data=self.client.list_items()
        self.assertEqual(data[-1]['login']['password'],new_password['login']['password'])

    def test_create_and_del_password(self):
        uri='yaho'
        username='ILYA'
        password='iLOVETGBOT'
        new_password=self.client.create_password(uri,username,password)
        self.client.del_password_by_id(new_password['id'])
        self.assertTrue(new_password not in self.client.list_items())

    def test_get_status(self):
        data=self.client.get_status()
        self.assertEqual(data,'unlocked')

    def test_search_items_with_uri_part(self):
        uri='ma'
        res=self.client.search_items_with_uri_part(uri)
        answer=[item['login']['uris'][0]['uri'] for item in res]
        self.assertEqual(answer,['gmail', 'mail'])



    




if __name__ == '__main__':
    unittest.main()