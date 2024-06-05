from s6r_bitwarden_cli import BitwardenCli
import subprocess
import json
import os
import requests
import pexpect
from requests.exceptions import MissingSchema


class BITWARDEN:
    def __init__(self,name,passw):
        """При создании передаем логин и пароль от Bitwarden"""
        self.bw=BitwardenCli(username=name, password=passw)
        self.bw.login()
        self.bw.unlock()
        
    def get_information(self,call):
        """Получаем информацию по его имени, собственно говоря передаем название ключа"""
        infa=self.bw.get_item(call)
        information=infa["login"]
        answer=""
        answer="Username:\t"+ information["username"]+'\n'+"Password:\t"+ information["password"]
        return answer

    


    def delete(self):
        """Когда пользователь закончил работу вызывает функцию, чтобы выйти из аккаунта Bitwarden"""
        self.bw.logout()
    
    


