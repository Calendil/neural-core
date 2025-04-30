import requests
import os

NOTION_API_URL = "https://api.notion.com/v1/blocks"
NOTION_VERSION = "2022-06-28"

NOTION_TOKEN = os.getenv("NOTION_API_KEY")  # Store this in your environment

def fetch_blocks_from_notion(page_id: str) -> dict:
    if not NOTION_TOKEN:
        return {"error": "Missing Notion API token."}

    url = f"{NOTION_API_URL}/{page_id}/children"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"error": str(e)}
