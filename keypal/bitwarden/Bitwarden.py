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
        answer=(information["username"], information["password"])
        return answer

    def get_list_of_names(self):
        """Выводим список имен всех существующих ключей"""
        list_of_names=self.bw.search_objects()
        names = [item['name'] for item in list_of_names]
        return names

    def delete(self):
        """Когда пользователь закончил работу вызывает функцию, чтобы выйти из аккаунта Bitwarden"""
        self.bw.logout()
