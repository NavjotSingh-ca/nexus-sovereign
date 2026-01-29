import os
from dotenv import load_dotenv
from supabase import create_client
import hashlib
import json

load_dotenv('config/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

MIN_AGENTS = 3
CONFIDENCE_THRESHOLD = 0.8

def generate_event_hash(event_data):
    """Create unique ID for an event"""
    event_string = json.dumps(event_data, sort_keys=True)
    return hashlib.md5(event_string.encode()).hexdigest()

def cast_vote(agent_id, agent_type, event_data, confidence_score, vote_category):
    """Agent submits vote to consensus table"""
    event_hash = generate_event_hash(event_data)
    
    vote = {
        'event_hash': event_hash,
        'agent_id': agent_id,
        'agent_type': agent_type,
        'vote_category': vote_category,
        'confidence_score': confidence_score,
        'evidence_payload': event_data,
        'vote_status': 'pending'
    }
    
    supabase.table('consensus_votes').insert(vote).execute()
    print(f"Vote cast: {agent_type} -> {vote_category} (confidence: {confidence_score})")
    return event_hash

def check_consensus(event_hash):
    """Check if event reached Sovereign Truth (3+ agents, >0.8 confidence)"""
    votes = supabase.table('consensus_votes').select('*').eq('event_hash', event_hash).execute()
    
    if len(votes.data) < MIN_AGENTS:
        return False, f"Insufficient votes: {len(votes.data)}/{MIN_AGENTS}"
    
    avg_confidence = sum(v['confidence_score'] for v in votes.data) / len(votes.data)
    
    if avg_confidence < CONFIDENCE_THRESHOLD:
        return False, f"Low confidence: {avg_confidence:.2f} < {CONFIDENCE_THRESHOLD}"
    
    # Mark as confirmed
    supabase.table('consensus_votes').update({'vote_status': 'confirmed'}).eq('event_hash', event_hash).execute()
    return True, f"Sovereign Truth confirmed: {avg_confidence:.2f} confidence"

def get_pending_events():
    """Get events awaiting consensus"""
    votes = supabase.table('consensus_votes').select('event_hash').eq('vote_status', 'pending').execute()
    return list(set(v['event_hash'] for v in votes.data))

if __name__ == "__main__":
    # Test: Check all pending events
    pending = get_pending_events()
    print(f"Pending events: {len(pending)}")
    for event_hash in pending:
        is_truth, msg = check_consensus(event_hash)
        print(f"  {event_hash[:8]}...: {msg}")