import requests
import re
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")
ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def parse_markdown_to_notion_blocks(text):
    def create_block(block_type, content):
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "text": [{"type": "text", "text": {"content": content}}]
            }
        }

    lines = text.splitlines()
    blocks = []
    i, n = 0, len(lines)

    while i < n:
        line = lines[i].rstrip()

        for pattern, block_type in [
            (r"^# (.+)", "heading_1"),
            (r"^## (.+)", "heading_2"),
            (r"^### (.+)", "heading_3")
        ]:
            match = re.match(pattern, line)
            if match:
                blocks.append(create_block(block_type, match.group(1)))
                i += 1
                break
        else:
            if re.match(r"^\d+\. (.+)", line):
                pattern, block_type = r"^\d+\. (.+)", "numbered_list_item"
            elif re.match(r"^[-*] (.+)", line):
                pattern, block_type = r"^[-*] (.+)", "bulleted_list_item"
            else:
                pattern, block_type = None, "paragraph"

            if pattern:
                items = []
                while i < n and re.match(pattern, lines[i].rstrip()):
                    content = re.match(pattern, lines[i].rstrip()).group(1)
                    items.append(create_block(block_type, content))
                    i += 1
                blocks.extend(items)
            elif line.strip():
                blocks.append(create_block("paragraph", line))
                i += 1
            else:
                i += 1

    return blocks

def notion_create(**body):
    parent_id = ROOT_PAGE_ID if body.get("parent_id") == "root" else body.get("parent_id")
    title = body.get("title")
    if not parent_id or not title:
        return {"error": "parent_id and title are required."}

    data = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        }
    }
    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=data)
    return handle_response(response)

def notion_append_blocks(**body):
    page_id = ROOT_PAGE_ID if body.get("page_id") == "root" else body.get("page_id")
    content = body.get("content")
    if not page_id or not content:
        return {"error": "page_id and content are required."}

    blocks = parse_markdown_to_notion_blocks(content)
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.patch(url, headers=HEADERS, json={"children": blocks})
    return handle_response(response)

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
