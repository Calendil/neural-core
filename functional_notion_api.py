# functional_notion_api.py

import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
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
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
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


def create_page_in_notion(parent_id: str, title: str):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION,
    }
    data = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id
        },
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return {"error": response.text}
    return {"status": "success", "detail": response.json()}
