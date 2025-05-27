import requests
from os import getenv
import re

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

def parse_markdown_to_notion_blocks(text):
    """
    Parse markdown-like text into a list of Notion block JSON objects.
    Supports:
    - Headings (#, ##, ###)
    - Bullet lists (-, *)
    - Numbered lists (1., 2., ...)
    - Paragraphs (plain text)
    """

    lines = text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip()

        # Heading 1
        if re.match(r"^# (.+)", line):
            content = re.match(r"^# (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "text": [{"type": "text", "text": {"content": content}}]
                }
            })
            i += 1
            continue

        # Heading 2
        if re.match(r"^## (.+)", line):
            content = re.match(r"^## (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "text": [{"type": "text", "text": {"content": content}}]
                }
            })
            i += 1
            continue

        # Heading 3
        if re.match(r"^### (.+)", line):
            content = re.match(r"^### (.+)", line).group(1)
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "text": [{"type": "text", "text": {"content": content}}]
                }
            })
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\. (.+)", line):
            # Collect consecutive numbered list items
            items = []
            while i < n and re.match(r"^\d+\. (.+)", lines[i].rstrip()):
                content = re.match(r"^\d+\. (.+)", lines[i].rstrip()).group(1)
                items.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1
            blocks.extend(items)
            continue

        # Bulleted list
        if re.match(r"^[-*] (.+)", line):
            # Collect consecutive bullet list items
            items = []
            while i < n and re.match(r"^[-*] (.+)", lines[i].rstrip()):
                content = re.match(r"^[-*] (.+)", lines[i].rstrip()).group(1)
                items.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "text": [{"type": "text", "text": {"content": content}}]
                    }
                })
                i += 1
            blocks.extend(items)
            continue

        # Paragraph (default)
        if line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [{"type": "text", "text": {"content": line}}]
                }
            })

        i += 1

    return blocks

def notion_section_update(**body):
    parent_id = body.get("parent_id")
    if parent_id == "root":
        parent_id = ROOT_PAGE_ID

    section_title = body.get("section_title")
    raw_text = body.get("content")  # expecting raw markdown-style text

    if not parent_id or not section_title:
        return {"error": "parent_id and section_title are required."}

    # Parse raw text content into Notion blocks
    new_blocks = parse_markdown_to_notion_blocks(raw_text or "")

    # Fetch existing blocks under parent page
    url_children = f"https://api.notion.com/v1/blocks/{parent_id}/children"
    response = requests.get(url_children, headers=HEADERS)
    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}
    blocks = response.json().get("results", [])

    # Find blocks belonging to the section by matching heading blocks with section_title
    to_delete = []
    in_section = False
    for block in blocks:
        block_type = block.get("type")
        if block_type in ["heading_1", "heading_2", "heading_3"]:
            title_text = ""
            title_content = block[block_type].get("text", [])
            if title_content:
                title_text = "".join([t.get("plain_text", "") for t in title_content])
            if title_text == section_title:
                in_section = True
                to_delete.append(block)
                continue
            else:
                if in_section:
                    break
        elif in_section:
            to_delete.append(block)

    # Archive blocks of the old section
    for block in to_delete:
        block_id = block.get("id")
        url_archive = f"https://api.notion.com/v1/blocks/{block_id}"
        patch_data = {"archived": True}
        r = requests.patch(url_archive, headers=HEADERS, json=patch_data)
        if r.status_code not in [200, 204]:
            return {"error": f"Failed to archive block {block_id}: {r.text}"}

    # Compose new section blocks, starting with heading_2 title block
    section_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "text": [{"type": "text", "text": {"content": section_title}}]
            }
        }
    ] + new_blocks

    # Append new blocks as children to parent page
    url_append = f"https://api.notion.com/v1/blocks/{parent_id}/children"
    append_data = {"children": section_blocks}
    r_append = requests.patch(url_append, headers=HEADERS, json=append_data)
    if r_append.status_code not in [200, 201]:
        return {"error": f"Failed to append new section blocks: {r_append.text}", "status_code": r_append.status_code}

    return {"status": "success", "detail": r_append.json()}

# All other existing functions unchanged...

def notion_fetch(**params):
    page_id = params.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    return handle_response(response)

def notion_sync(**body):
    page_id = body.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    content = body.get("content")
    if not page_id or not content:
        return {"error": "page_id and content are required."}

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
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
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_create(**body):
    parent_id = body.get("parent_id")
    if parent_id == "root":
        parent_id = ROOT_PAGE_ID
    title = body.get("title")
    if not parent_id or not title:
        return {"error": "parent_id and title are required."}

    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {
            "type": "page_id",
            "page_id": parent_id
        },
        "properties": {
            "title": {
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
    }
    response = requests.post(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_update(**body):
    page_id = body.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    properties = body.get("properties")
    if not page_id or not properties:
        return {"error": "page_id and properties are required."}

    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "properties": properties
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def notion_delete(**body):
    page_id = body.get("page_id")
    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not page_id:
        return {"error": "page_id is required."}

    url = f"https://api.notion.com/v1/pages/{page_id}"
    data = {
        "archived": True
    }
    response = requests.patch(url, headers=HEADERS, json=data)
    return handle_response(response)

def handle_response(response):
    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}
    return {"status": "success", "detail": response.json()}
