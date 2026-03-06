from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
import operator
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os
from pathlib import Path
from langgraph.graph import StateGraph, START, END

IMG_DIR = Path(__file__).resolve().parent / "img"
llm = ChatOpenAI(
    model="qwen-max",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
)


