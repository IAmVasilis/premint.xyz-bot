import requests


class etherscan:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def getWalletBalance(self, token):
        try:
            response = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={token}&tag=latest&apikey={self.api_key}")
            response_json = response.json()
            if response.status_code == 200:
                response_json = response.json()
                if response_json['message'] == "OK":
                    return True, response_json['message'], response_json['result']
                else:
                    return False, response_json['message'], response_json['result']
            else:
                return False, response_json['message'], response.text
        except Exception as e:
            return False, 'ERROR', str(e)