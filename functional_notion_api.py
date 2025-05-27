import requests
from os import getenv
from fastapi import Request

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def notion_fetch(**params):
    page_id = params.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}
    data = response.json()
    blocks = data.get("results", [])
    return {"blocks": blocks}

def parse_page_sections(blocks):
    sections = []
    current_section = None

    for block in blocks:
        block_type = block.get("type")
        if block_type in ["heading_1", "heading_2", "heading_3"]:
            title_text = ""
            title_content = block[block_type].get("text", [])
            if title_content:
                title_text = "".join([t.get("plain_text", "") for t in title_content])
            current_section = {
                "title": title_text,
                "blocks": []
            }
            sections.append(current_section)
        else:
            if current_section is None:
                current_section = {
                    "title": None,
                    "blocks": []
                }
                sections.append(current_section)
            current_section["blocks"].append(block)

    return sections

async def notion_parse_sections(request: Request):
    try:
        params = await request.json()
    except Exception:
        params = {}
    blocks_response = notion_fetch(**params)
    if "error" in blocks_response:
        return blocks_response
    blocks = blocks_response.get("blocks", [])
    sections = parse_page_sections(blocks)
    return {"sections": sections}

# Other existing functions here unchanged...
# ...

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
