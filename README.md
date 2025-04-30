neural-core

neural-core is a modular, GPT-integrated bridge API.
It connects a Custom GPT to multiple functional systems like Notion, memory databases, and direct SQL execution.
Built for extensibility, neural-core acts as a central control layer — isolating GPT-facing routes from internal logic execution.

Core Design:

main.py: The bridge layer — exposes clean endpoints to GPT only.

Functional APIs (e.g., functional_notion_api.py) handle actual logic.

GPT communicates via OpenAPI schema and uses Actions to trigger functionality.

Current Status:

Bridge API: Live

Memory DB: On Hold

Notion Sync: In Progress

SQL Execution: Active

Quick Start:

Clone the repository

Install dependencies

Run with: uvicorn main:app --reload

Designed to scale. Controlled by GPT. Executed by core.
