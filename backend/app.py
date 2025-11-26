from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from rembg import remove
from PIL import Image
import io

app = FastAPI()

# Allow all origins for now (you can tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # or ["http://172.236.187.68:8080"] if you want strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "RemoveBG backend is running"}

@app.post("/remove-bg")
async def remove_bg(image: UploadFile = File(...)):
    # Basic validation
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = await image.read()
    input_bytes = io.BytesIO(contents)

    try:
        input_image = Image.open(input_bytes).convert("RGBA")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Remove background
    output_image = remove(input_image)

    out_bytes = io.BytesIO()
    output_image.save(out_bytes, format="PNG")
    out_bytes.seek(0)

    return StreamingResponse(out_bytes, media_type="image/png")

