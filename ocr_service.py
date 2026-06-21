from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

app = FastAPI(title="Handwritten OCR Service")

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
model.eval()
device = torch.device("cpu")   # oder "cuda" falls GPU verfügbar
model.to(device)

@app.post("/ocr")
async def ocr_handwritten(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        generated_ids = model.generate(pixel_values, max_length=512)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return JSONResponse(content={"text": text.strip()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))