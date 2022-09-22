# -*- coding: utf-8 -*-

# pre-minter modules
from colorama import Fore

from src.modules.twitter.twitter import twitter
from src.modules.logger.log import log

# python libs
from bs4 import BeautifulSoup
import httpx


class premint:
    def __init__(self, premint_link: str, eth_balance, settings):
        # client stuff
        self.client = httpx.Client(timeout=30000)
        self.url = premint_link

        # user configuration
        self.settings = settings
        self.eth_balance = eth_balance

        # html information
        self.website_html = None

        # logger
        self.logger = log

    def isRegistered(self):
        response = self.client.get(self.url)
        if response.status_code == 200:
            # parse new html data
            html_site = BeautifulSoup(response.text, "html.parser")
            # check if register even exists or not
            register_div = html_site.find("div", {"class": "heading heading-3 mb-2 d-block"})
            if register_div is not None:
                if 'fas fa-check-circle text-success mr-2' in str(register_div):
                    return True, 'REGISTERED', response.status_code
                else:
                    return False, 'NOT_REGISTERED', response.status_code
            else:
                return False, 'NO_HTML_PAGE_RENDERED', response.status_code
        else:
            return False, 'FAILED_REQUEST', response.status_code

    def checkStatus(self):
        try:
            try:
                response = self.client.get(self.url)
                if response.status_code == 200:
                    # place html contents inside of self.website_html, so we don't need to create another request.
                    self.website_html = response.text
                    # return important data to show that the link is valid.
                    return True, response.status_code, None
                else:
                    return False, response.status_code, None
            except Exception as e:
                return False, 401, str(e)
        except Exception as e:
            return False,

    def getChallenges(self):
        try:
            html_site = BeautifulSoup(self.website_html, "html.parser")
            # check for any discord challenges
            discord_challenges = html_site.find("div", {"id": f"step-discord"})
            if discord_challenges is not None:
                ...
            # check for any twitter challenges
            twitter_challenges = html_site.find("div", {"id": f"step-twitter"})
            if twitter_challenges is not None:
                # create twitter challenger
                twitter_challenger = twitter(tweet_url="", authorization=self.settings['twitter']['authorization'], x_csrf_token=self.settings['twitter']['ct0'], auth_token=self.settings['twitter']['auth_token'], ct0=self.settings['twitter']['ct0'], queryId="lI07N6Otwv1PhnEgXILM7A")
                for challenge in twitter_challenges.find_all("a", {"class": "c-base-1 strong-700 text-underline"}):
                    # check if it's a follow challenge or not
                    if '<a class="c-base-1 strong-700 text-underline" href="https://twitter.com/user' not in str(challenge):
                        userHandle = challenge['href'].split("/")[3]
                        handle_status, user_id = twitter_challenger.handleToUserID(userHandle=userHandle)
                        if handle_status:
                            follow_status, error_code = twitter_challenger.follow(userID=user_id)
                            if follow_status:
                                self.logger.print(caller="Premint-Challenger", text=f"Solved Follow Challenge for '{userHandle}'")
                                mute_status, username = twitter_challenger.muteUserID(userID=user_id)
                                if mute_status:
                                    self.logger.print(caller="Premint-Challenger", text=f"Muted '{username}' from current feed.")
                                else:
                                    self.logger.print(caller="Premint-Challenger", text=f"{Fore.RED}Failed! {Fore.WHITE}Failed to mute '{username}' from current feed.")
                            else:
                                raise Exception("Failed to follow user")
                        else:
                            raise Exception("Failed to check for handle status")
                    else:
                        twitter_challenger.filter_tweet_id(caller="challenger", url=challenge['href'])
                        if '&amp; Retweet' in str(twitter_challenges) or 'Must Retweet' in str(twitter_challenges):
                            retweet_status, wrapper_response, error_code = twitter_challenger.retweetTweet()
                            if retweet_status:
                                self.logger.print(caller="Premint-Challenger",
                                                  text=f"Solved Retweet Challenge for '{twitter_challenger.tweet_id}'")
                            else:
                                raise Exception("Failed to retweet tweet")
                        if 'Must Like' in str(twitter_challenges):
                            like_status, wrapper_response, error_code = twitter_challenger.likeTweet()
                            if like_status:
                                self.logger.print(caller="Premint-Challenger", text=f"Solved Like Challenge for '{twitter_challenger.tweet_id}'")
                            else:
                                raise Exception("Failed to like tweet")
            return True, 'None'
        except Exception as e:
            return False, str(e)

    def isRegisterable(self):
        try:
            # blacklisted challenges
            blacklisted_challenges = [
                'ownership'
            ]
            html_site = BeautifulSoup(self.website_html, "html.parser")
            has_blacklisted_challenge = False
            # check for any balance challenges
            if self.eth_balance is not None:
                balance_challenges = html_site.find("div", {"id": f"step-balance"})
                if balance_challenges is not None:
                    eth_balance = float(balance_challenges.find("span").text.split(" ")[0])
                    if self.eth_balance < eth_balance:
                        return False, 'LOW_WALLET_BALANCE'
            else:
                blacklisted_challenges.append("balance")
            # check if there is a blacklisted challenge
            for challenge in blacklisted_challenges:
                if html_site.find("div", {"id": f"step-{challenge}"}) is not None:
                    return False, f'BLACKLISTED_CHALLENGE_{challenge.upper()}'
            # check if there is any 'join before' or 'discord role' for discord challenges
            discord_challenges = html_site.find("div", {"id": f"step-discord"})
            if discord_challenges is not None:
                blacklisted_strings = [
                    # 'join before' check
                    'before <strong class="c-base-1">',
                    # 'role' check
                    'and have the <span class="c-base-1 strong-700">'
                ]
                for string in blacklisted_strings:
                    if string in str(discord_challenges):
                        return False, 'BLACKLISTED_DISCORD_CHALLENGES'
            # check if there are any blacklisted/required things inside of 'step-custom'
            custom_challenges = html_site.find("div", {"id": f"step-custom"})
            if custom_challenges is not None:
                blacklisted_strings = [
                    # required input check
                    'The field above was added by the project and your response will be shared with the project owners.'
                ]
                for string in blacklisted_strings:
                    if string in str(custom_challenges):
                        return False, 'CUSTOM_EMAIL_CHALLENGE'
            # return status
            return True if has_blacklisted_challenge is False else False, 'SUCCESS'
        except Exception as e:
            return False, str(e)

    def isValid(self):
        try:
            response = self.client.get(self.url)
            if response.status_code == 200:
                # place html contents inside of self.website_html so we don't need to create another request.
                self.website_html = response.text
                # return important data to show that the link is valid.
                return True, response.status_code, None
            else:
                return False, response.status_code, None
        except Exception as e:
            return False, 401, str(e)

    def register(self):
        try:
            html_site = BeautifulSoup(self.website_html, "html.parser")
            csrf_token = ""
            for script in html_site.find_all("script"):
                if 'const CSRF_TOKEN' in str(script):
                    csrf_token = str(script).split("\n")[1].split(" ")[7].replace("'", "").replace(";","")
            if csrf_token != "":
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': f'_ga=GA1.1.84934033.1660288763; csrftoken={csrf_token}; session_id={self.settings["pre-minter"]["session_id"]}; __cf_bm={self.client.cookies.get("__cf_bm")}; _ga_NMJ1VJK44S=GS1.1.1660430040.11.1.1660434646.0',
                    'Referer': self.url,
                    'Origin': 'https://www.premint.xyz',
                    'pragma': 'no-cache',
                    'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
                }
                payload = f"csrfmiddlewaretoken={csrf_token}&params_field=%7B%7D&email_field=&minting_wallet={self.settings['pre-minter']['minting_wallet']}&registration-form-submit="
                response = self.client.post(url=self.url, headers=headers, data=payload)
                if response.status_code == 302:
                    return True, 'SUCCESS'
                else:
                    return False, 'UNAUTHORIZED'
            else:
                return False, 'FAILED_TO_FIND_CSRF_TOKEN'
        except Exception as e:
            return False, str(e)