# -*- coding: utf-8 -*-
from colorama import Fore


class log:
    @staticmethod
    def print(caller: str, text: str):
        print(f"{Fore.WHITE}[{Fore.CYAN}{caller}{Fore.WHITE}] {text}")