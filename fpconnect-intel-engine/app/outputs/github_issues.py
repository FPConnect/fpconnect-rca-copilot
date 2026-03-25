import os
import requests


def create_issue(title: str, body: str, labels: list[str] | None = None):
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO')
    if not token or not repo:
        return None

    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
    }
    payload = {'title': title, 'body': body, 'labels': labels or []}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()
