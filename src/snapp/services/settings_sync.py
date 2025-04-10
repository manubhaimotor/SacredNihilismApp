import requests
from datetime import datetime

FIRESTORE_URL_BASE = "https://firestore.googleapis.com/v1/projects/sacred-nihilism/databases/(default)/documents"

def get_settings_collection_url(user_id):
    return f"{FIRESTORE_URL_BASE}/users/{user_id}/settings"

def save_settings_to_firestore(id_token, user_id, settings_dict):
    url = get_settings_collection_url(user_id)

    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "nudges_per_day": {"integerValue": settings_dict["nudges_per_day"]},
            "hours_start": {"stringValue": settings_dict["hours_start"]},
            "hours_end": {"stringValue": settings_dict["hours_end"]},
            "nudge_type": {"stringValue": settings_dict["nudge_type"]},
            "timestamp": {"timestampValue": datetime.utcnow().isoformat() + "Z"}
        }
    }

    res = requests.post(url, headers=headers, json=payload)
    print("📤 Saving to:", url)
    print("📦 Payload:", payload)
    print("🧾 Response:", res.status_code, res.text)
    return res.status_code in (200, 201)

def load_settings_from_firestore(id_token, user_id):
    url = f"{get_settings_collection_url(user_id)}?orderBy=timestamp%20desc&pageSize=1"

    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }

    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        documents = res.json().get("documents", [])
        if documents:
            fields = documents[0].get("fields", {})
            return {
                "nudges_per_day": int(fields.get("nudges_per_day", {}).get("integerValue", 3)),
                "hours_start": fields.get("hours_start", {}).get("stringValue", "9 AM"),
                "hours_end": fields.get("hours_end", {}).get("stringValue", "9 PM"),
                "nudge_type": fields.get("nudge_type", {}).get("stringValue", "Random")
            }
        else:
            print("⚠️ No settings found in collection.")
            return {}
    else:
        print("❌ Firestore fetch failed:", res.status_code, res.text)
        return {}
