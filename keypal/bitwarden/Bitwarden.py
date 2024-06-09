from s6r_bitwarden_cli import BitwardenCli
import subprocess
import json
import os
import requests
import pexpect
from requests.exceptions import MissingSchema
import shlex
import re

class BITWARDEN:
    def __init__(self,name,passw):
        """Initialization with Bitwarden account login and password, access to the Bitwarden vault 
           args: login and password from Bitwarden account
           example: my_account=Bitwarden("your_email_of_Bitwarden_account","your_password_of_Bitwarden_account")"""
        self.bw=BitwardenCli(username=name, password=passw)
        self.bw.login()
        self.bw.unlock()
        self.login=name
        self.password=passw

        
    def get_information(self,call):
        """Getting information about a key by its name 
           args: name of the key
           example:my_account.get_information("name of your key that you have in your key list")"""
        answer=()
        if call in self.get_list_of_names():
            infa=self.bw.get_item(call)
            information=infa["login"]
            answer=(information["username"],information["password"])
        return answer


    def get_list_of_names(self):
        """Display a list of all key names"""
        list_of_names=self.bw.search_objects()
        names = [item['name'] for item in list_of_names]
        return names




    def delete(self):
        """Logging out from Bitwarden account"""
        self.bw.logout()

    




