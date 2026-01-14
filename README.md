# AI Short Video Generator

A fully automated system that generates **vertical short-form videos** (TikTok / Reels style) using AI and n8n.

Each run produces **one complete video** with:

- One consistent background
- AI-generated voiceover
- Sentence-by-sentence subtitles
- Final MP4 ready to post

---

## How It Works

1. n8n generates a text prompt (AI-decided)
2. n8n calls a local FastAPI endpoint
3. Python:
   - Creates a background image
   - Generates AI voice (Edge Neural TTS)
   - Splits text into sentence-based subtitles
   - Renders the video using FFmpeg
4. One video is saved locally

---

## Tech Stack

- Python
- FastAPI
- FFmpeg
- ASS subtitles (libass)
- Microsoft Edge Neural TTS
- n8n (automation)

---

## n8n Workflow

![n8n Workflow](screenshots/screenshot.png)

---

## Run Locally

```bash
venv\Scripts\activate
uvicorn scripts.server:app --host 127.0.0.1 --port 8000
```
