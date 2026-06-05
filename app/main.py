import json
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from .agent import agent

app = FastAPI(
    title="LangChain Multi-Tool Agent",
    description="LangGraph ReAct agent with web search, calculator, and datetime tools. Supports multi-turn conversation with persistent memory.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str = ""


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    tool_calls: list[str]


@app.get("/")
def root():
    return {
        "service": "LangChain Multi-Tool Agent",
        "endpoints": {
            "POST /chat": "Multi-turn conversation (returns JSON)",
            "POST /chat/stream": "Multi-turn conversation (SSE streaming)",
            "GET /health": "Health check",
        },
        "tools": ["web_search", "calculator", "get_current_datetime"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages = result["messages"]
    response_text = messages[-1].content

    tool_calls = []
    for msg in messages:
        if hasattr(msg, "tool_calls"):
            for tc in msg.tool_calls:
                tool_calls.append(tc["name"])

    return ChatResponse(
        response=response_text,
        thread_id=thread_id,
        tool_calls=tool_calls,
    )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    async def generate() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'thread_id': thread_id})}\n\n"
        try:
            async for event in agent.astream_events(
                {"messages": [HumanMessage(content=request.message)]},
                config=config,
                version="v2",
            ):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'token': chunk.content})}\n\n"
                elif kind == "on_tool_start":
                    tool_name = event.get("name", "tool")
                    yield f"data: {json.dumps({'tool_start': tool_name})}\n\n"
                elif kind == "on_tool_end":
                    tool_name = event.get("name", "tool")
                    yield f"data: {json.dumps({'tool_end': tool_name})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
