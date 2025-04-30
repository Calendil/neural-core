import os
import requests

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

NOTION_TOKEN = os.getenv("NOTION_API_KEY")  # Store this in your environment

def push_to_notion(page_id: str, content: str) -> dict:
    if not NOTION_TOKEN:
        return {"error": "Missing Notion API token."}

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
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
                            "text": {"content": content}
                        }
                    ]
                }
            }
        ]
    }

    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"error": str(e)}
