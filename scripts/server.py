from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from scripts.main import generate_one

app = FastAPI()

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate(req: GenerateRequest):
    video_path = generate_one(req.prompt)
    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename="video.mp4"
    )
