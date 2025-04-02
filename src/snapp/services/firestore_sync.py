import requests
from snapp.services.auth import extract_user_id  # ✅ Moved from inline import

FIREBASE_PROJECT_ID = "sacred-nihilism"

def upload_to_firestore(user_token, entry):
    user_id = extract_user_id(user_token)

    if not user_id:
        print("❌ Cannot upload, no user_id found.")
        return False

    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users/{user_id}/activity_logs"

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    firestore_entry = {
        "fields": {
            "goal_type": {"stringValue": entry["goal_type"]},
            "time_frame": {"stringValue": entry["time_frame"]},
            "note": {"stringValue": entry["note"]},
            "timestamp": {"stringValue": entry["timestamp"]}
        }
    }

    response = requests.post(url, headers=headers, json=firestore_entry)
    if response.status_code in [200, 202]:
        print("✅ Firestore upload successful.")
        return True
    else:
        print(f"❌ Firestore upload failed: {response.status_code} - {response.text}")
        return False


def fetch_from_firestore(user_token):
    """Fetch all activity logs for the current user from Firestore."""
    user_id = extract_user_id(user_token)

    if not user_id:
        print("❌ Cannot fetch data, no user_id found.")
        return []

    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users/{user_id}/activity_logs"

    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        documents = response.json().get("documents", [])
        entries = []

        for doc in documents:
            fields = doc.get("fields", {})
            entries.append({
                "goal_type": fields.get("goal_type", {}).get("stringValue", ""),
                "time_frame": fields.get("time_frame", {}).get("stringValue", ""),
                "note": fields.get("note", {}).get("stringValue", ""),
                "timestamp": fields.get("timestamp", {}).get("stringValue", "")
            })

        print("✅ Data fetched from Firestore:", entries)
        return entries
    else:
        print(f"❌ Firestore fetch failed: {response.status_code} - {response.text}")
        return []
