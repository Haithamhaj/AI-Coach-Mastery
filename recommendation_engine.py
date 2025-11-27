import json
import random
import os
from firebase_config import get_user_stats

def load_markers():
    """
    Load markers from the JSON file.
    """
    try:
        with open('markers.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading markers: {e}")
        return None

def analyze_performance(user_id):
    """
    Analyze user's last 5 sessions and arcade games to generate a Smart Plan.
    """
    stats = get_user_stats(user_id)
    
    if not stats:
        return None
        
    # 1. Calculate Competency Scores from Recent Sessions
    competency_scores = {
        "C3": {"total": 0, "count": 0, "name": "Establishes and Maintains Agreements"},
        "C4": {"total": 0, "count": 0, "name": "Cultivates Trust and Safety"},
        "C5": {"total": 0, "count": 0, "name": "Maintains Presence"},
        "C6": {"total": 0, "count": 0, "name": "Listens Actively"},
        "C7": {"total": 0, "count": 0, "name": "Evokes Awareness"},
        "C8": {"total": 0, "count": 0, "name": "Facilitates Client Growth"}
    }
    
    # We only have detailed data in 'recent_sessions' which are Full Sessions or Rephrase
    # We need to look at the 'report_json' inside the session data.
    # get_user_stats returns 'recent_sessions' but it might not have the full report_json 
    # if get_user_stats only fetches summary fields. 
    # Looking at firebase_config.py, it does: sessions = [doc.to_dict() for doc in sessions_ref.stream()]
    # So it fetches everything. Good.
    
    sessions = stats.get('recent_sessions', [])
    
    for session in sessions:
        report = session.get('report_json', {})
        if not report:
            continue
            
        # Check if it's a Full Session report (has 'competencies' key)
        if 'competencies' in report:
            comps = report['competencies']
            for cid, data in comps.items():
                if cid in competency_scores:
                    # Calculate score for this competency in this session
                    # If it has markers, use observed/total
                    # If it's C1/C2, use status (Pass=100, Fail=0)
                    
                    score = 0
                    if 'markers' in data:
                        markers = data['markers']
                        if markers:
                            observed = sum(1 for m in markers if m.get('status') == 'Observed')
                            score = (observed / len(markers)) * 100
                    elif 'status' in data:
                        score = 100 if data['status'] == 'Pass' else 0
                        
                    competency_scores[cid]["total"] += score
                    competency_scores[cid]["count"] += 1
    
    # 2. Identify Weakest Competency
    weakest_cid = None
    lowest_avg = 101
    
    for cid, data in competency_scores.items():
        if data["count"] > 0:
            avg = data["total"] / data["count"]
            if avg < lowest_avg:
                lowest_avg = avg
                weakest_cid = cid
    
    # Default if no data
    if weakest_cid is None:
        # Default to C7 (Evokes Awareness) as it's a common struggle
        weakest_cid = "C7"
        lowest_avg = 0
        
    weakest_name = competency_scores[weakest_cid]["name"]
    
    # 3. Generate Action Plan
    markers_data = load_markers()
    
    # READ: Find a marker from this competency
    read_task = "Review ICF Core Competencies"
    if markers_data:
        # Find the competency object
        comp_obj = next((c for c in markers_data['competencies'] if c['id'] == weakest_cid), None)
        if comp_obj and comp_obj['markers']:
            # Pick a random marker
            marker = random.choice(comp_obj['markers'])
            read_task = f"Review Marker {marker['id']}: {marker['text']}"
    
    # DRILL: Arcade Mode
    drill_task = f"Play Arcade Mode (Focus on '{weakest_name}')"
    
    # CHALLENGE: Simulation
    # Map competency to a suitable persona/topic
    challenge_map = {
        "C3": "Complete a 'Goal Setting' simulation with a 'Looping' client.",
        "C4": "Complete a simulation with an 'Emotional' client.",
        "C5": "Complete a 'Silent Client' simulation (manage silence).",
        "C6": "Complete a simulation focusing on 'Active Listening' with a 'Resistant' client.",
        "C7": "Complete a simulation using only 'Open-Ended Questions'.",
        "C8": "Complete a simulation focusing on 'Action Planning' (Will Phase)."
    }
    challenge_task = challenge_map.get(weakest_cid, "Complete a Full Coaching Session.")
    
    return {
        "focus_area": {
            "id": weakest_cid,
            "name": weakest_name,
            "avg_score": round(lowest_avg, 1)
        },
        "plan": {
            "read": read_task,
            "drill": drill_task,
            "challenge": challenge_task
        }
    }
