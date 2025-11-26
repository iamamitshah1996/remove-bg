from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from rembg import remove
from PIL import Image, ImageFilter
import io

app = FastAPI()

# CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/remove-bg")
async def remove_bg(image: UploadFile = File(...)):
    # Validate file type
    if image.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPG, PNG, WEBP supported")

    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    # Open as RGBA
    input_image = Image.open(io.BytesIO(data)).convert("RGBA")

    # High-quality background removal with alpha matting
    cutout = remove(
        input_image,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )

    # Feather edges by blurring ONLY the alpha channel
    if cutout.mode != "RGBA":
        cutout = cutout.convert("RGBA")

    r, g, b, a = cutout.split()
    # tweak radius 1.0–3.0 as you like
    a = a.filter(ImageFilter.GaussianBlur(radius=1.5))
    cutout = Image.merge("RGBA", (r, g, b, a))

    # Return as PNG
    buf = io.BytesIO()
    cutout.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

