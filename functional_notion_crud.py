{
  "openapi": "3.1.0",
  "info": {
    "title": "GPT Beyond Neural Core API",
    "description": "Bridge API for Notion page and block creation only.",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://neural-core.onrender.com"
    }
  ],
  "paths": {
    "/bridge/notion/notion_crud_notion_create": {
      "post": {
        "summary": "Create Notion Page",
        "description": "Creates a new Notion page under a parent page. Use 'root' as parent_id to target the configured root page.",
        "operationId": "notion_crud_notion_create",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["parent_id", "title"],
                "properties": {
                  "parent_id": {
                    "type": "string",
                    "description": "Parent page ID or 'root' to use the configured root page ID."
                  },
                  "title": {
                    "type": "string",
                    "description": "Title of the new page."
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    },
    "/bridge/notion/notion_crud_notion_append_blocks": {
      "post": {
        "summary": "Append Notion Blocks",
        "description": "Appends formatted blocks to a Notion page. Use markdown-style input to define headings, lists, and paragraphs.",
        "operationId": "notion_crud_notion_append_blocks",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "required": ["page_id", "content"],
                "properties": {
                  "page_id": {
                    "type": "string",
                    "description": "Target Notion page ID. Use 'root' to reference the configured root page."
                  },
                  "content": {
                    "type": "string",
                    "description": "Markdown-style content for Notion blocks."
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    }
  }
}
