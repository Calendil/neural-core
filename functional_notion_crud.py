def notion_replace_block(**body):
    page_id = body.get("page_id", "root")
    match_text = body.get("match_text", "").strip()
    new_block_type = body.get("new_block_type")
    new_content = body.get("new_content", "").strip()

    if page_id == "root":
        page_id = ROOT_PAGE_ID
    if not all([page_id, match_text, new_block_type, new_content]):
        return {"error": "Missing required fields."}

    def get_text_from_block(block):
        rich_text = block.get(block["type"], {}).get("rich_text", [])
        return "".join(rt.get("text", {}).get("content", "") for rt in rich_text)

    def make_block(block_type, content):
        return {
            "object": "block",
            "type": block_type,
            block_type: {
                "rich_text": rich_text_block(content)
            }
        }

    # Fetch all child blocks
    try:
        resp = requests.get(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=HEADERS)
        if resp.status_code != 200:
            return {"error": f"Fetch failed: {resp.text}"}
        original_blocks = resp.json().get("results", [])
    except Exception as e:
        return {"error": f"Exception during fetch: {str(e)}"}

    # Build new block list with replacement
    updated_blocks = []
    replaced = False
    for block in original_blocks:
        if not replaced and match_text in get_text_from_block(block):
            updated_blocks.append(make_block(new_block_type, new_content))
            replaced = True
        else:
            updated_blocks.append(block)

    if not replaced:
        return {"error": f"No block matched text: '{match_text}'"}

    # Archive all original blocks
    for block in original_blocks:
        try:
            requests.patch(
                f"https://api.notion.com/v1/blocks/{block['id']}",
                headers=HEADERS,
                json={"archived": True}
            )
        except:
            pass  # Continue even if one block fails

    # Append updated blocks
    try:
        append = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=HEADERS,
            json={"children": updated_blocks}
        )
        if append.status_code not in [200, 201]:
            return {"error": f"Re-append failed: {append.text}"}
        return {"status": "success", "detail": append.json()}
    except Exception as e:
        return {"error": f"Exception during re-append: {str(e)}"}
