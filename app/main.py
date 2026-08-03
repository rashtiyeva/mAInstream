from fastapi import FastAPI

app = FastAPI(
    title="Mainstream",
    version="1.0.0"
)


@app.get("/")
async def health_check():
    return {"status": "running"}