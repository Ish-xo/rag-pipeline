import os
import sys
from dotenv import load_dotenv

load_dotenv()

def print_status(name: str, has_key: bool):
    status = "✅ Configured" if has_key else "❌ Missing"
    print(f"{name.ljust(20)}: {status}")

def main():
    print("="*40)
    print("ULTRON-V: Environment Setup Verification")
    print("="*40)
    
    print("\n--- Speech-to-Text (STT) & Text-to-Speech (TTS) ---")
    print_status("Sarvam AI", bool(os.getenv("SARVAM_API_KEY")))
    print_status("ElevenLabs", bool(os.getenv("ELEVENLABS_API_KEY")))
    
    print("\n--- Core LLM Providers ---")
    print_status("Groq", bool(os.getenv("GROQ_API_KEY")))
    print_status("Cerebras", bool(os.getenv("CEREBRAS_API_KEY")))
    print_status("Google AI Studio", bool(os.getenv("GOOGLE_API_KEY")))
    
    print("\n--- Stretch LLM Providers ---")
    print_status("SambaNova", bool(os.getenv("SAMBANOVA_API_KEY")))
    print_status("Together AI", bool(os.getenv("TOGETHER_API_KEY")))
    print_status("OpenRouter", bool(os.getenv("OPENROUTER_API_KEY")))
    
    print("\n--- Embeddings ---")
    print_status("Voyage AI", bool(os.getenv("VOYAGE_API_KEY")))
    print_status("Jina AI (Optional)", bool(os.getenv("JINA_API_KEY")))
    
    print("\n--- Vector Databases ---")
    print_status("Qdrant", bool(os.getenv("QDRANT_URL") and os.getenv("QDRANT_API_KEY")))
    print_status("Pinecone", bool(os.getenv("PINECONE_API_KEY") and os.getenv("PINECONE_INDEX_HOST")))
    
    print("\n--- Deployment & Data ---")
    print_status("Hugging Face", bool(os.getenv("HF_TOKEN")))

if __name__ == "__main__":
    main()
