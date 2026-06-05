from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from .tools import calculator, get_current_datetime

load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
Use tools when they help you give accurate, up-to-date answers.
Be concise and direct. Always show your reasoning when using tools."""

_model = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)
_search = DuckDuckGoSearchRun()
_tools = [calculator, get_current_datetime, _search]
_checkpointer = MemorySaver()

agent = create_react_agent(
    model=_model,
    tools=_tools,
    checkpointer=_checkpointer,
    state_modifier=SYSTEM_PROMPT,
)
