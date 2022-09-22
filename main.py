# -*- coding: utf-8 -*-

# premint module
from src.modules.etherscan.etherscan import etherscan
from src.modules.premint.premint import premint

# pre-minter console logger
from src.modules.logger.log import log

# python libs
from colorama import Fore
from os import system

import toml
import time


# automatic minter for baidjeet#0001
def pre_minter(settings, logger, ether):
    # instantiate etherscan api wallet check for preminter
    status, wrapper_response, wallet = ether.getWalletBalance(token=settings['pre-minter']['minting_wallet'])
    eth_balance = None
    if status:
        if wrapper_response == "OK":
            eth_balance = float(int(wallet) / 1000000000000000000)
            logger.print(caller="Wallet-Check",
                         text=f"Calculated Minting Wallet Balance to '{eth_balance}', Using this balance to determine if you are eligible to premint balance challenged links.")
        else:
            logger.print(caller="Wallet-Check",
                         text=f"An unknown error occurred, Please contact support and send us this error-log! Error: {wallet}")
    else:
        logger.print(caller="Wallet-Check",
                     text=f"Failed to get minting wallet balance, Will not be able to premint any links with balance requirements, Error: {wallet}")
    # infinitely ask the user to premint any links inputted
    while True:
        # get pre-mint link from operating user
        premint_url = input(f"{Fore.WHITE}[{Fore.CYAN}Link-Input{Fore.WHITE}] Please input a link you want to automatically pre-mint for!\n> ")
        # update the url if it's missing 'www'
        premint_url = premint_url.replace("https://premint.xyz/", "https://www.premint.xyz/").strip()
        # instantiate pre-mint module for checking if the link is scrabble
        minter = premint(premint_link=premint_url, settings=settings, eth_balance=eth_balance)
        # check if link is valid or not
        response_status, response_code, error_code = minter.isValid()
        # handle responses for a valid url
        if response_status:
            logger.print(caller="Link-Input", text=f"{Fore.GREEN}SUCCESS! {Fore.WHITE}The imported link '{premint_url}' is a valid url, Checking if the pre-mint is supported by our bot.")
            # check if link is supported by our bot or not
            support_status, error_code = minter.isRegisterable()
            if support_status:
                logger.print(caller="Preminter", text=f"{Fore.GREEN}SUCCESS! {Fore.WHITE}This link is supported by our software, Attempting to register for it.")
                # link is supported, try and solve all the challenges within it.
                challenge_status, error_code = minter.getChallenges()
                if challenge_status:
                    register_status, auth_status = minter.register()
                    if register_status:
                        logger.print(caller="Preminter", text=f"Waiting one second before checking registration status, The bot may say you've failed but it's possible the premint hasn't went through yet.")
                        time.sleep(1)
                        is_registered, register_status, status_code = minter.isRegistered()
                        if is_registered:
                            logger.print(caller="Preminter", text=f"{Fore.GREEN}SUCCESS! {Fore.WHITE}Successfully pre-minted '{premint_url}', Status: '{register_status}', Returning back to mint input.")
                        else:
                            if register_status == "NO_HTML_PAGE_RENDERED":
                                logger.print(caller="Preminter", text=f"{Fore.RED}FAILED! {Fore.WHITE}This premint link seems to be locked, ended, or not showing any visible signs that there was a change in registration, Please contact support if you believe this is an issue. Link: '{premint_url}'")
                            else:
                                logger.print(caller="Preminter", text=f"{Fore.RED}FAILED! {Fore.WHITE}Failed to minted '{premint_url}', Reason: '{register_status}', Returning back to mint input, Please contact support if this continuously happens.")
                    else:
                        logger.print(caller="Preminter", text=f"{Fore.RED}FAILED! {Fore.WHITE}Failed to minted '{premint_url}', Reason: '{auth_status}', Returning back to mint input, Please contact support if this continuously happens.")
                else:
                    logger.print(caller="Preminter", text=f"{Fore.RED}FAILED! {Fore.WHITE}Failed to submit and finish all challenges, Cannot solve premint. Error Code: '{error_code}'")
            else:
                logger.print(caller="Preminter", text=f"{Fore.RED}FAILED! {Fore.WHITE}This link isn't supported by our bot, Reason: {error_code}, You may not have enough balance or one of the challenges found isn't supported.")
        else:
            if response_code == 401:
                logger.print(caller="Link-Input", text=f"{Fore.RED}FAILED! {Fore.WHITE}The imported link '{premint_url}' isn't a valid url, Please contact support as this was not suppose to happen. Error Code: '{error_code}'")
            else:
                logger.print(caller="Link-Input", text=f"{Fore.RED}FAILED! {Fore.WHITE}The imported link '{premint_url}' isn't a valid url, Please contact support if you believe this is an issue. Status Code: '{response_code}'")


if __name__ == "__main__":
    # change the title of the program
    system(f"title VasilisAIO V1 - Preminter")

    # instantiate logger, etherscan api
    ether = etherscan("XCDRBD754CD4WW92ZBPZRNC2HUH8DB6IGK")
    console_logger = log

    # credits
    console_logger.print(caller="Main", text=f"VasilisAIO Loaded! Developed by Vasilis#5708 and made with <3")

    # sleep so the user can see it
    time.sleep(1)

    # load current configuration stuff
    with open("config/settings.toml", "r") as f:
        settings = toml.loads(f.read())

    # load pre-minter
    pre_minter(settings=settings, logger=console_logger, ether=ether)
    input(f"{Fore.WHITE}[{Fore.CYAN}FATAL{Fore.WHITE}] Please press enter to end the program.\n> ")
