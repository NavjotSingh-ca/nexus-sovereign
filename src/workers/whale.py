import sys
sys.path.insert(0, 'src/vip')
from killswitch import check_kill_switch
from byzantine_voter import cast_vote, generate_event_hash

import os, requests
from dotenv import load_dotenv
from supabase import create_client
import time

load_dotenv('config/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
api_key = os.getenv('ETHERSCAN_API_KEY')

def fetch_whale_tx(min_usd=10000000):
    """Fetch transactions > $10M USD and cast votes"""
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
            
            # Calculate confidence based on amount (higher = more confident)
            confidence = min(0.95, 0.7 + (usd_value / 100000000))
            
            # Cast vote to Byzantine consensus
            event_data = {
                'type': 'large_transfer',
                'entity': wallet['entity_name'],
                'amount': usd_value,
                'token': token,
                'tx_hash': tx['hash']
            }
            
            cast_vote(
                agent_id='whale_001',
                agent_type='whale',
                event_data=event_data,
                confidence_score=round(confidence, 2),
                vote_category='market_anomaly'
            )
            
            # Also write to legacy ledger for backward compat
            alert = {
                'agent_id': 'whale_001',
                'agent_type': 'whale',
                'message_type': 'mega_whale_alert',
                'payload': event_data,
                'status': 'pending_review'
            }
            supabase.table('ledger').insert(alert).execute()
            
            print(f"MEGA WHALE: {wallet['entity_name']} moved ${usd_value:,.0f} {token} (confidence: {confidence:.2f})")
            time.sleep(1)

if __name__ == "__main__":
    if not check_kill_switch():
        print("Whale: HALTED by kill switch")
        sys.exit(0)
    fetch_whale_tx()
    print("Whale scan complete")