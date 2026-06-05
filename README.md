# LangChain Multi-Tool Agent

A production-pattern LangGraph ReAct agent with web search, calculator, and datetime tools. FastAPI backend with multi-turn conversation memory and SSE streaming.

**Live:** [Deployed on AWS EC2](http://18.218.110.243:8000)

---

## What This Demonstrates

My production work at RTV Engineering was built on the raw Anthropic API — I wrote the agent loop, tool dispatch, history management, and error recovery from scratch. This project shows the same agentic patterns implemented through LangChain/LangGraph, which abstracts those mechanics into framework components.

**Mapping to production patterns:**

| Raw Anthropic API (production) | LangChain/LangGraph (this project) |
|---|---|
| Manual `tool_use` / `tool_result` loop | `create_react_agent` ReAct graph |
| History list with tool pairs preserved | `MemorySaver` checkpointer |
| Custom tool dispatch and error handling | `@tool` decorated functions |
| SSE streaming with `stream=True` | `astream_events` with `v2` protocol |

---

## Architecture

```
POST /chat  ──►  FastAPI  ──►  LangGraph ReAct Agent  ──►  Claude (Haiku)
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                    web_search   calculator  get_datetime
                  (DuckDuckGo)   (Python)    (zoneinfo)
```

**Multi-turn memory:** LangGraph `MemorySaver` checkpointer persists conversation state across requests by `thread_id`. Same conversation, same context — no state sent from the client.

**SSE streaming:** `/chat/stream` uses `astream_events` to push tokens and tool status events as they occur.

---

## Tools

| Tool | Description |
|---|---|
| `web_search` | DuckDuckGo search via `langchain-community` |
| `calculator` | Evaluates math expressions using Python `math` module |
| `get_current_datetime` | Returns current date/time in any IANA timezone |

---

## Endpoints

```
GET  /               — Service info and available endpoints
GET  /health         — Health check
POST /chat           — Multi-turn chat (JSON response)
POST /chat/stream    — Multi-turn chat (SSE streaming)
```

### Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the square root of 1764, and what time is it in Tokyo?", "thread_id": "demo"}'
```

```json
{
  "response": "The square root of 1764 is 42. The current time in Tokyo is 2025-08-14 09:32:11 JST (Asia/Tokyo).",
  "thread_id": "demo",
  "tool_calls": ["calculator", "get_current_datetime"]
}
```

---

## Run Locally

```bash
git clone https://github.com/marcusrjcook/langchain-agent-demo
cd langchain-agent-demo

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

---

## Deploy to AWS EC2

```bash
# On your EC2 instance (t2.micro, Ubuntu 22.04)
sudo apt update && sudo apt install -y python3-pip python3-venv git

git clone https://github.com/marcusrjcook/langchain-agent-demo
cd langchain-agent-demo

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run (port 8000, open in EC2 security group)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Stack

**AI/LLM:** LangChain · LangGraph · Anthropic Claude (Haiku) · ReAct agent pattern · Multi-turn memory · SSE streaming  
**Backend:** Python · FastAPI · Pydantic  
**Tools:** DuckDuckGo Search · Custom tool definitions  
**Deployment:** AWS EC2

---

## Related Projects

- [SiteTrack RTLS Dashboard](https://github.com/marcusrjcook/rtls-dashboard) — 12 SQL-backed AI tools built on raw Anthropic API, same patterns this project abstracts
- [Claude Agentic Query Agent](https://github.com/marcusrjcook/claude-agentic-query-agent) — raw tool use loop, history management from scratch
- [RTLS Operations Automation](https://github.com/marcusrjcook/rtls-ops-automation) — 39-node n8n multi-agent orchestration
