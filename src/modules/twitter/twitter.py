# -*- coding: utf-8 -*-
import httpx


class twitter:
    def __init__(self, tweet_url: str, authorization: str, x_csrf_token: str, queryId: str, auth_token: str, ct0: str):

        # grab everything to do twitter retweets & likes
        self.tweet_url = tweet_url
        self.tweet_id = None
        self.filter_tweet_id(caller="__init__", url=None)

        # account management
        self.authorization_token = authorization
        self.x_csrf_token = x_csrf_token
        self.queryId = queryId
        self.cookie = f"auth_token={auth_token}; ct0={ct0}"

        # initialize requests client
        self.client = httpx.Client(timeout=30000)

    def retweetTweet(self):
        # twitter request payload
        payload = {
            'variables': {
                'tweet_id': self.tweet_id,
                'dark_request': False
            },
            'queryId': 'ojPdsZsimiJrUGLR1sjUtA'
        }
        # twitter headers
        retweet_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}',
            'x-csrf-token': self.x_csrf_token,
            'cookie': self.cookie
        }
        response = self.client.post("https://twitter.com/i/api/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet", headers=retweet_headers, json=payload)
        if response.status_code == 200:
            try:
                # check if there is any api errors
                if response.json().get('errors') is None:
                    return True, 'SUCCESSFUL_RETWEET', response.json()['data']['create_retweet']['retweet_results']['result']['legacy']['full_text']
                else:
                    if 'Authorization: You have already retweeted this Tweet.' in response.json()['errors'][0]['message']:
                        return True, 'SUCCESSFUL_RETWEET', 'ALREADY_TWEETED'
                    else:
                        return False, 'FAILED_RETWEET_TWO', response.json()['errors'][0]['message']
            except:
                return False, 'FAILED_RETWEET', response.json()['errors'][0]['message']
        # return status code not 200 if it isn't 200
        return False, 'STATUS_CODE_NOT_200', response.json()['errors'][0]['message']

    def likeTweet(self):
        # twitter request payload
        payload = {
            "variables": {
                "tweet_id": str(self.tweet_id)
            },
            "queryId":"lI07N6Otwv1PhnEgXILM7A"
        }
        # twitter headers
        liketweet_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}',
            'x-csrf-token': self.x_csrf_token,
            'cookie': self.cookie
        }
        response = self.client.post("https://twitter.com/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet", headers=liketweet_headers, json=payload)
        if response.status_code == 200:
            try:
                if response.json().get("errors") is None:
                    return True, 'SUCCESSFUL_LIKED_TWEET', response.json()['data']['favorite_tweet']
                else:
                    if 'has already favorited' in response.json().get("errors")[0]['message']:
                        return True, 'SUCCESSFUL_LIKED_TWEET', 'ALREADY_LIKED'
                    else:
                        return False, 'FAILED_RETWEET', response.json()['errors'][0]['message']
            except:
                return False, 'FAILED_RETWEET', response.json()['errors'][0]['message']
        else:
            return False, 'STATUS_CODE_NOT_200', response.json()['errors'][0]['message']

    def follow(self, userID):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self.authorization_token}',
            'x-csrf-token': self.x_csrf_token,
            'cookie': self.cookie
        }
        payload = f"include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&skip_status=1&user_id={userID}"
        response = self.client.post(url="https://twitter.com/i/api/1.1/friendships/create.json", headers=headers, data=payload)
        if response.status_code == 200:
            if response.json().get("screen_name") is not None:
                return True, response.json().get("screen_name")
            else:
                return False, 'UNKNOWN_USER'
        else:
            return False, response.status_code

    def muteUserID(self, userID):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self.authorization_token}',
            'x-csrf-token': self.x_csrf_token,
            'cookie': self.cookie
        }
        payload = f"user_id={userID}"
        response = self.client.post(url="https://twitter.com/i/api/1.1/mutes/users/create.json", headers=headers, data=payload)
        if response.status_code == 200:
            if response.json().get("screen_name") is not None:
                return True, response.json().get("screen_name")
            else:
                return False, 'UNKNOWN_USER'
        else:
            return False, response.status_code

    def handleToUserID(self, userHandle: str):
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"104\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest"
        }
        response = self.client.post("https://tweeterid.com/ajax.php", data=f"input={userHandle}", headers=headers)
        if response.text != "error":
            return True, response.text
        else:
            return False, 'error'

    def filter_tweet_id(self, caller: str, url: str):
        """
        # Example Twitter URLs
        # https://twitter.com/badcoder_tbh/status/1557987173873225728
        # https://twitter.com/user/status/1557454541292859392
        # https://twitter.com/user/status/1558005373499580416
        :param url:
        # Split Twitter URL to retrieve Unique Tweet ID
        :return:
        """

        """
        if self.tweet_url is not None and caller == "__init__":
            self.tweet_id = self.tweet_url.split("/")[5]
        else:
            self.tweet_id = url.split("/")[5]
        """

        try:
            if caller == "__init__" and self.tweet_url != "":
                self.tweet_id = self.tweet_url.split("/")[5]
                return True, 'SUCCESS'
            elif caller != "__init__" and url != "":
                self.tweet_id = url.split("/")[5]
                return True, 'SUCCESS'
            else:
                return False, 'unknown_error'
        except Exception as e:
            return False, str(e)