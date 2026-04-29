import requests
import json

BASE_URL = "http://localhost:8787"

def test_health():
    print("Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_command_normal():
    print("\nTesting /agent-command (normal)...")
    payload = {"command": "What is this page about?"}
    try:
        response = requests.post(f"{BASE_URL}/agent-command", json=payload)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_command_risky():
    print("\nTesting /agent-command (risky)...")
    payload = {"command": "click approve"}
    try:
        response = requests.post(f"{BASE_URL}/agent-command", json=payload)
        print(f"Response: {response.json()}")
        return response.json().get("action_id")
    except Exception as e:
        print(f"Error: {e}")

def test_confirm_action(action_id):
    if not action_id:
        return
    print(f"\nTesting /confirm-action (confirmed) for {action_id}...")
    payload = {"action_id": action_id, "confirmed": True}
    try:
        response = requests.post(f"{BASE_URL}/confirm-action", json=payload)
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Ensure main.py is running before running this test.")
    test_health()
    test_command_normal()
    action_id = test_command_risky()
    test_confirm_action(action_id)
