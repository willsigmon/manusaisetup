#!/usr/bin/env python3
"""
Manus.im Official API Client
Base URL: https://api.manus.im
Auth: API_KEY header
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

MANUS_API_KEY = os.getenv("MANUS_API_KEY")
MANUS_BASE_URL = "https://api.manus.im"


def create_task(prompt: str, connectors: list = None) -> dict:
    """Create a new Manus task"""
    headers = {
        "API_KEY": MANUS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt}
    if connectors:
        payload["connectors"] = connectors

    resp = requests.post(f"{MANUS_BASE_URL}/v1/tasks", headers=headers, json=payload)
    return resp.json()


def get_task(task_id: str) -> dict:
    """Get task status and results"""
    headers = {"API_KEY": MANUS_API_KEY}
    resp = requests.get(f"{MANUS_BASE_URL}/v1/tasks/{task_id}", headers=headers)
    return resp.json()


def list_tasks(limit: int = 10) -> dict:
    """List recent tasks"""
    headers = {"API_KEY": MANUS_API_KEY}
    resp = requests.get(f"{MANUS_BASE_URL}/v1/tasks", headers=headers, params={"limit": limit})
    return resp.json()


def upload_file(file_path: str) -> dict:
    """Upload a file to Manus"""
    headers = {"API_KEY": MANUS_API_KEY}
    with open(file_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f"{MANUS_BASE_URL}/v1/files", headers=headers, files=files)
    return resp.json()


def run_and_wait(prompt: str, timeout: int = 300, poll_interval: int = 5) -> dict:
    """Create task and poll until complete"""
    result = create_task(prompt)
    if "error" in result:
        return result

    task_id = result.get("task_id")
    if not task_id:
        return {"error": "No task_id in response", "response": result}

    start = time.time()
    while time.time() - start < timeout:
        status = get_task(task_id)
        state = status.get("status", status.get("state", "unknown"))
        if state in ["completed", "failed", "done"]:
            return status
        time.sleep(poll_interval)

    return {"error": "timeout", "task_id": task_id}


if __name__ == "__main__":
    import sys
    import json

    if not MANUS_API_KEY:
        print("Error: MANUS_API_KEY not set in .env")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Manus.im API Client")
        print(f"API Key: {MANUS_API_KEY[:10]}...")
        print("\nUsage:")
        print("  python manus_client.py create <prompt>")
        print("  python manus_client.py get <task_id>")
        print("  python manus_client.py list")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "create" and len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
        result = create_task(prompt)
        print(json.dumps(result, indent=2))

    elif cmd == "get" and len(sys.argv) > 2:
        task_id = sys.argv[2]
        result = get_task(task_id)
        print(json.dumps(result, indent=2))

    elif cmd == "list":
        result = list_tasks()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
