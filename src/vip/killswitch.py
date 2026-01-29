import os
from supabase import create_client

def check_kill_switch():
    """Dead Man's Switch - returns False if system should halt"""
    override = os.getenv('SOVEREIGN_OVERRIDE', 'ACTIVE')
    
    if override != 'ACTIVE':
        print("SOVEREIGN OVERRIDE: HALT signal detected. Shutting down.")
        return False
    
    # Also check Supabase for remote kill signal
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL'), 
            os.getenv('SUPABASE_KEY')
        )
        status = supabase.table('system_status').select('kill_signal').execute()
        if status.data and status.data[0].get('kill_signal') == 'HALT':
            print("REMOTE KILL: HALT signal in Ledger. Shutting down.")
            return False
    except:
        pass  # If can't reach DB, continue running (fail-safe)
    
    return True

if __name__ == "__main__":
    if check_kill_switch():
        print("Kill switch: CLEAR. System operational.")
    else:
        print("Kill switch: TRIGGERED. Exit.")
        exit(1)