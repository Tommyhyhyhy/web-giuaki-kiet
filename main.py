from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
VIDEO_FILE = BASE_DIR / "static" / "video" / "dothi.mp4"

app = FastAPI(title="Mo phong CLT")
app.mount(
	"/static",
	StaticFiles(directory=BASE_DIR / "static"),
	name="static",
)
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
	return templates.TemplateResponse(
		request=request,
		name="index.html",
		context={"video_available": VIDEO_FILE.is_file()},
	)


@app.get("/health")
async def health():
	return {"status": "ok"}
