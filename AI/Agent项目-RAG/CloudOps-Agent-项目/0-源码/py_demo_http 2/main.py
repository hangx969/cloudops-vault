from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

app = FastAPI()

llm = ChatOpenAI(
    api_key="sk-你的key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3-max",
)


@app.get("/api/chat")
async def chat(id: str = "", question: str = ""):
    if not question:
        return {"message": "question 不能为空", "data": None}

    response = llm.invoke([HumanMessage(content=question)])
    return {
        "message": "OK",
        "data": {
            "answer": response.content
        }
    }
