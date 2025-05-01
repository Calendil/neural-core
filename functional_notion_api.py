# functional_notion_api.py

import requests

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_API_VERSION = "2022-06-28"
from os import getenv

NOTION_API_KEY = getenv("NOTION_API_KEY")

def push_to_notion(page_id: str, content: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }
    data = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"text": [{"type": "text", "text": {"content": content}}]},
            }
        ]
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        return {"error": response.text}
    return {"status": "success", "detail": response.json()}


def fetch_blocks_from_notion(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_API_VERSION,
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": response.text}
    return {"status": "success", "blocks": response.json()}
