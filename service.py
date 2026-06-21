from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import easyocr
import logging

# Logging aktivieren, damit wir sehen, wo er abstürzt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EasyOCR-Service")

logger.info("Lade EasyOCR Modelle (CPU)...")
# gpu=False zwingt ihn in den CPU-Modus, was RAM-Spitzen reduziert
reader = easyocr.Reader(['de', 'en'], gpu=False)
logger.info("Modelle geladen! Server ist bereit.")

# 🔥 WICHTIG: Normales 'def' (kein 'async def')
@app.post("/extract")
def extract_text(file: UploadFile = File(...)):
    logger.info(f"Empfange Datei: {file.filename}")
    
    try:
        # 🔥 WICHTIG: 'file.file.read()' (ohne await!)
        contents = file.file.read()
        logger.info(f"Datei gelesen ({len(contents)} Bytes). Starte OCR-Analyse...")
        
        # OCR Analyse
        results = reader.readtext(contents, detail=0, paragraph=True)
        logger.info("OCR-Analyse erfolgreich beendet!")
        
        extracted_string = "\n\n".join(results)
        return JSONResponse(content={"text": extracted_string})
        
    except Exception as exc:
        logger.error(f"Fehler bei der Analyse: {exc}")
        raise HTTPException(status_code=500, detail=f"OCR-Fehler: {exc}")