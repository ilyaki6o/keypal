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
        """
        Initialization with Bitwarden account login and password, access to the Bitwarden vault 

        args: login and password from Bitwarden account

        example: my_account=Bitwarden("your_email_of_Bitwarden_account","your_password_of_Bitwarden_account")"""
        self.bw_login = subprocess.Popen(f"bw login {name} {passw}",
                            stdout=subprocess.PIPE, shell=True)
        self.bw_data = self.bw_login.communicate()[0].decode()
        self.bw_session = re.findall('"([^"]*)"', self.bw_data)[0]
        self.login=name
        self.password=passw

    def get_information(self,call):
        """
        Getting information about a key by its name 
            
        args: name of the key
            
        example: my_account.get_information("name of your key that you have in your key list")"""
        answer=()
        if call in self.get_list_of_names():
            infa=subprocess.Popen(f"bw get item {call} --session {self.bw_session}",
                                    shell=True, stdout=subprocess.PIPE)
            data=infa.communicate()[0].decode()
            items = json.loads(data)
            information=items["login"]
            answer=(information["username"],information["password"])
        return answer

     def get_list_of_names(self):
        """Display a list of all key names"""
        list_of_names=subprocess.Popen(f"bw list items --session {self.bw_session}",
                                  shell=True, stdout=subprocess.PIPE)
        data=list_of_names.communicate()[0].decode()
        items = json.loads(data)
        names = [item['name'] for item in items]
        return names

    




