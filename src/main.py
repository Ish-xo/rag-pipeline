from fastapi import FastAPI, UploadFile, File
import time
from .pipeline import VoiceRAGPipeline

app = FastAPI(title="Voice RAG Pipeline API")
pipeline = VoiceRAGPipeline()

@app.post("/api/ask")
async def ask_question(audio_file: UploadFile = File(...)):
    """
    Endpoint to receive audio, process it through the STT -> RAG -> Generation pipeline,
    and return the generated answer along with latency metrics.
    """
    start_time = time.time()
    
    # 1. Read the audio file
    audio_bytes = await audio_file.read()
    
    # 2. Process through the RAG pipeline
    try:
        result = await pipeline.process_audio(audio_bytes)
        status = "success"
    except Exception as e:
        result = str(e)
        status = "error"
    
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    
    return {
        "status": status,
        "answer": result,
        "latency_ms": round(latency_ms, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
