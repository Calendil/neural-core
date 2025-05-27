import requests
from os import getenv

NOTION_API_VERSION = "2022-06-28"
NOTION_API_KEY = getenv("NOTION_API_KEY")

ROOT_PAGE_ID = "1f855c99-70ec-80ca-bf5f-e44f51a2f511"

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_API_VERSION,
}

# Existing functions omitted for brevity, please keep all previous functions here unchanged

def notion_section_update(**body):
    """
    Replace or create a section by title in a given parent page.
    body should contain:
    - parent_id: str - ID of the parent page (use 'root' for ROOT_PAGE_ID)
    - section_title: str - title of the section to replace
    - blocks: list - list of Notion block JSON objects for the section content (excluding title)
    """

    parent_id = body.get("parent_id")
    if parent_id == "root":
        parent_id = ROOT_PAGE_ID

    section_title = body.get("section_title")
    new_blocks = body.get("blocks", [])

    if not parent_id or not section_title:
        return {"error": "parent_id and section_title are required."}

    # Step 1: Get all blocks of the parent page
    url_children = f"https://api.notion.com/v1/blocks/{parent_id}/children"
    response = requests.get(url_children, headers=HEADERS)
    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}
    blocks = response.json().get("results", [])

    # Step 2: Find blocks belonging to the section (starting at title block)
    # We assume title block is heading_1, heading_2, or heading_3 matching section_title
    # Collect blocks to delete (the section)
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

    # Step 3: Archive blocks in to_delete to remove the section
    for block in to_delete:
        block_id = block.get("id")
        url_archive = f"https://api.notion.com/v1/blocks/{block_id}"
        patch_data = {"archived": True}
        r = requests.patch(url_archive, headers=HEADERS, json=patch_data)
        if r.status_code not in [200, 204]:
            return {"error": f"Failed to archive block {block_id}: {r.text}"}

    # Step 4: Build new section blocks including title block at the start
    section_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "text": [
                    {
                        "type": "text",
                        "text": {"content": section_title}
                    }
                ]
            }
        }
    ] + new_blocks

    # Step 5: Append new blocks as children to the parent page
    url_append = f"https://api.notion.com/v1/blocks/{parent_id}/children"
    append_data = {"children": section_blocks}
    r_append = requests.patch(url_append, headers=HEADERS, json=append_data)
    if r_append.status_code not in [200, 201]:
        return {"error": f"Failed to append new section blocks: {r_append.text}", "status_code": r_append.status_code}

    return {"status": "success", "detail": r_append.json()}
