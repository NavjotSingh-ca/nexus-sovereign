import os, requests
from dotenv import load_dotenv
from supabase import create_client
import time

load_dotenv('config/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
api_key = os.getenv('ETHERSCAN_API_KEY')

def fetch_whale_tx(min_usd=10000000):
    """Fetch transactions > $10M USD from tracked wallets"""
    stablecoins = {'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD'}
    
    wallets = supabase.table('wallet_directory').select('*').execute()
    
    for wallet in wallets.data:
        url = f"https://api.etherscan.io/v2/api?chainid=1&module=account&action=tokentx&address={wallet['address']}&page=1&offset=20&sort=desc&apikey={api_key}"
        r = requests.get(url).json()
        
        if r['status'] != '1':
            continue
            
        for tx in r['result']:
            token = tx['tokenSymbol']
            value = int(tx['value']) / (10 ** int(tx['tokenDecimal']))
            
            if token not in stablecoins:
                continue
                
            usd_value = value
            
            if usd_value < min_usd:
                continue
                
            alert = {
                'agent_id': 'whale_001',
                'agent_type': 'whale',
                'message_type': 'mega_whale_alert',
                'payload': {
                    'from': tx['from'],
                    'to': tx['to'],
                    'token': token,
                    'value': value,
                    'usd_value': usd_value,
                    'entity_from': wallet['entity_name'],
                    'tx_hash': tx['hash']
                },
                'status': 'pending_review'
            }
            supabase.table('ledger').insert(alert).execute()
            print(f"MEGA WHALE: {wallet['entity_name']} moved ${usd_value:,.0f} {token}")
            time.sleep(1)

if __name__ == "__main__":
    fetch_whale_tx()
    print("Whale scan complete")