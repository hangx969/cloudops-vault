from fastapi import FastAPI

app = FastAPI()


@app.get("/api/chat")
async def chat(id: str = "", question: str = ""):
    return {
        "message": "OK",
        "data": {
            "answer": "chat demo"
        }
    }
