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

     def add_password(self,name,username,pas):
        """
        Add new password to the Bitwarden account

        args: key name, username , password

        example: my_account.add_password("name_of_your_new_key","new_key_username","new_key_password")
        """
        bw_create_item = subprocess.Popen(f"bw get template item | jq '.name=\"{name}\"' | jq '.login={{username:\"{username}\",password:\"{pas}\"}}' | bw encode | bw create item --session {self.bw_session}",
                                  shell=True, stdin=subprocess.PIPE)
        bw_create_item.communicate(input=f"{self.password}".encode())

    




