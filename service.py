import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import easyocr

app = FastAPI(title="EasyOCR-Service")

# 🔥 Lade das Modell beim Serverstart in den RAM (gpu=False für CPU-Betrieb)
# 'de' und 'en' stehen für Deutsch und Englisch. Du kannst weitere Sprachen hinzufügen.
print("Lade EasyOCR Modelle...")
reader = easyocr.Reader(['de', 'en'], gpu=False)
print("Modelle geladen! Server ist bereit.")

@app.post("/extract")
async def extract_text(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # detail=0: Gibt uns nur den Text zurück, keine Box-Koordinaten
        # paragraph=True: Gruppiert zusammenhängende Zeilen intelligent zu Absätzen!
        results = reader.readtext(contents, detail=0, paragraph=True)
        
        # Fügt die erkannten Absätze mit doppelten Zeilenumbrüchen zusammen
        extracted_string = "\n\n".join(results)
        
        return JSONResponse(content={"text": extracted_string})
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR-Fehler: {exc}")