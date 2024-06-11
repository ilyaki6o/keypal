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


    




