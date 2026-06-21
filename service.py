from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import easyocr
import logging
import io
from PIL import Image # 🔥 Neu importieren

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EasyOCR-Service")

logger.info("Lade EasyOCR Modelle (CPU)...")
reader = easyocr.Reader(['de', 'en'], gpu=False)
logger.info("Modelle geladen! Server ist bereit.")

@app.post("/extract")
def extract_text(file: UploadFile = File(...)):
    logger.info(f"Empfange Datei: {file.filename}")
    
    try:
        contents = file.file.read()
        logger.info(f"Datei gelesen ({len(contents)} Bytes).")
        
        # 🔥 NEU: Bildgröße für den RAM optimieren
        image = Image.open(io.BytesIO(contents))
        
        # Wenn das Bild breiter oder höher als 1600 Pixel ist, skalieren wir es proportional herunter
        max_size = 1600
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            logger.info(f"Bild auf {image.width}x{image.height} verkleinert, um RAM zu sparen.")
            
            # Verkleinertes Bild zurück in Bytes wandeln
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format or 'JPEG')
            contents = img_byte_arr.getvalue()

        logger.info("Starte OCR-Analyse...")
        results = reader.readtext(contents, detail=0, paragraph=True)
        logger.info("OCR-Analyse erfolgreich beendet!")
        
        extracted_string = "\n\n".join(results)
        return JSONResponse(content={"text": extracted_string})
        
    except Exception as exc:
        logger.error(f"Fehler bei der Analyse: {exc}")
        raise HTTPException(status_code=500, detail=f"OCR-Fehler: {exc}")