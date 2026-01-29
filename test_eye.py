import os, requests
from dotenv import load_dotenv
load_dotenv('config/.env')
key = os.getenv('ETHERSCAN_API_KEY')
url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address=0x28c6c06298d514db089934071355e5743bf21d60&page=1&offset=1&sort=desc&apikey={key}"
r = requests.get(url).json()
print(r['message'])