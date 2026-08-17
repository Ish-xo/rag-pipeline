import gradio as gr
import asyncio
from src.analytics.timer import PipelineTimer
from src.stt.failover import FailoverSTTClient
from src.tts.failover import FailoverTTSClient
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
import numpy as np

# Load environment variables
load_dotenv()

# Initialize failover pipeline components for Frontend integration
stt_client = FailoverSTTClient()
tts_client = FailoverTTSClient()

def generate_core_wireframe():
    # Cybernetic Core Wireframe using Plotly
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x = 10 * np.outer(np.cos(u), np.sin(v))
    y = 10 * np.outer(np.sin(u), np.sin(v))
    z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
    
    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale='blues',
        showscale=False,
        opacity=0.2,
    )])
    # Add an inner core (Reality Stone red)
    x2 = 4 * np.outer(np.cos(u), np.sin(v))
    y2 = 4 * np.outer(np.sin(u), np.sin(v))
    z2 = 4 * np.outer(np.ones(np.size(u)), np.cos(v))
    fig.add_trace(go.Surface(
        x=x2, y=y2, z=z2,
        colorscale='reds',
        showscale=False,
        opacity=0.8,
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False, visible=False),
            yaxis=dict(showbackground=False, visible=False),
            zaxis=dict(showbackground=False, visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
    )
    return fig

async def process_interaction(audio_filepath, text_input, mode):
    from src.llm.provider_cascade import LLMProviderCascade
    from src.guardrails.input_guard import InputGuardrail
    from src.guardrails.retrieval_guard import RetrievalGuardrail
    from src.guardrails.output_guard import OutputGuardrail
    from src.retrieval.retriever import search
    from src.llm.schemas import SourceCitation
    
    timer = PipelineTimer()
    timer.record("T0") # Audio received
    
    # Initialize Workstream 1 components
    llm_cascade = LLMProviderCascade()
    input_guard = InputGuardrail()
    retrieval_guard = RetrievalGuardrail()
    output_guard = OutputGuardrail()
    
    # STT processing
    if audio_filepath and not text_input:
        try:
            with open(audio_filepath, "rb") as f:
                audio_bytes = f.read()
            text_input = await stt_client.transcribe(audio_bytes)
        except Exception as e:
            text_input = f"[STT Error: {e}]"
    
    timer.record("T1") # STT Complete
    
    # T1 -> T2: Input Guardrails
    guard_res = input_guard.validate(text_input or "")
    if not guard_res.is_safe:
        timer.record("T2")
        timer.record("T3")
        timer.record("T4")
        timer.record("T5")
        timer.record("T6")
        timer.record("T7")
        timer.record("T8")
        answer = guard_res.reason
        citations_str = "No citations."
    else:
        timer.record("T2") # Guardrails complete
        
        # T2 -> T3 -> T4: Embedding & Vector Search (Mock)
        # Using mock search for Workstream 2 until Phase 2 is done
        mock_resp = search(text_input) 
        timer.record("T3") # Embedding complete
        timer.record("T4") # Vector search complete
        
        # T4 -> T5: Reranking & Retrieval Guardrails
        mock_citations = [
            SourceCitation(id=1, text="गोवा भारत का एक सुंदर राज्य है और यह अपने समुद्र तटों के लिए जाना जाता है।", similarity=0.95),
            SourceCitation(id=2, text="Goa is a state in India, famous for its beaches and tourism.", similarity=0.88),
            SourceCitation(id=3, text="Irrelevant context about something else.", similarity=0.20)
        ]
        filtered_citations, ret_guard_res = retrieval_guard.filter_and_validate(mock_citations)
        timer.record("T5") # Reranking complete
        
        if not ret_guard_res.is_safe:
            timer.record("T6")
            timer.record("T7")
            timer.record("T8")
            answer = ret_guard_res.reason
            citations_str = "No citations passed threshold."
        else:
            # T5 -> T6 -> T7: Answer Generation
            # Measuring TTFT and full generation
            start_gen = asyncio.get_event_loop().time()
            answer, provider, exec_ms = await llm_cascade.generate_answer(text_input, filtered_citations)
            
            # Estimate TTFT (~20% of total generation time for non-streaming mock)
            await asyncio.sleep(exec_ms * 0.2 / 1000)
            timer.record("T6") # TTFT
            
            timer.record("T7") # Full text generation complete
            
            # T7 -> T8: Output Grounding complete
            out_guard_res = await output_guard.verify_grounding(answer, filtered_citations, cascade_provider=llm_cascade)
            if not out_guard_res.is_safe:
                answer = f"[GROUNDING FAILED] {out_guard_res.reason}\n\nOriginal Answer: {answer}"
            timer.record("T8") # Output grounding complete
            
            citations_str = "\n".join([f"{i+1}. [Doc ID: {c.id}] (Score: {c.similarity:.2f})\n   {c.text}" for i, c in enumerate(filtered_citations)])
    
    # TTS Synthesis
    audio_output = None
    if not os.environ.get("SKIP_TTS", "") and "GROUNDING FAILED" not in answer:
        output_file = "output.mp3"
        try:
            await tts_client.synthesize(answer, output_path=output_file)
            audio_output = output_file
        except Exception as e:
            print(f"TTS Error: {e}")
            
    timer.record("T9") # TTS complete
    
    waterfall = timer.get_waterfall()
    waterfall_str = "\n".join([f"{k}: {v:.1f}ms" for k, v in waterfall.items()])
    
    retrieval_lat = timer.get_latency("T2", "T5")
    e2e_lat = timer.get_latency("T1", "T8")
    
    metrics = f"[TIME STONE SYNC]\nRetrieval Latency: {retrieval_lat:.1f}ms\nPost-STT Latency: {e2e_lat:.1f}ms\n\nWaterfall Diagnostics:\n{waterfall_str}"
    
    return answer, citations_str, metrics, audio_output

# Define Custom Infinity Ultron Gradio Theme
theme = gr.themes.Base(
    primary_hue=gr.themes.colors.amber,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Orbitron"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill_dark="#0A0A0C",
    body_text_color_dark="#A8A9AD",
    body_background_fill="#0A0A0C",
    body_text_color="#A8A9AD",
    
    block_background_fill_dark="#1E1E24",
    block_border_width="1px",
    block_border_color_dark="#3F3F46",
    block_title_text_color_dark="#FFC72C",
    block_background_fill="#1E1E24",
    block_border_color="#3F3F46",
    block_title_text_color="#FFC72C",
    
    input_background_fill_dark="#121215",
    input_border_color_dark="#00D2FF",
    input_background_fill="#121215",
    input_border_color="#00D2FF",
)

custom_css = """
/* HUD and Glow Effects */
body {
    background: radial-gradient(circle at center, #1E1E24 0%, #0A0A0C 100%) !important;
}
.gradio-container {
    box-shadow: inset 0 0 100px rgba(138, 43, 226, 0.1) !important;
}
.gr-box, .gr-panel, div[class*="svelte-"] {
    border-radius: 0px !important;
}
/* Wrap inputs in chamfered borders */
.gr-box, .gr-form {
    background: rgba(18, 18, 21, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(138, 43, 226, 0.4) !important; /* Power Stone Purple */
    clip-path: polygon(10px 0, 10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px) !important;
    box-shadow: 0 0 15px rgba(138, 43, 226, 0.1), inset 0 0 15px rgba(138, 43, 226, 0.1) !important;
    transition: all 0.3s ease-in-out !important;
}
.gr-box:hover, .gr-form:focus-within {
    box-shadow: 0 0 20px rgba(0, 210, 255, 0.4), inset 0 0 20px rgba(0, 210, 255, 0.2) !important; /* Space Stone Blue */
    border-color: rgba(0, 210, 255, 0.8) !important;
}

/* Infinity Stone Accents for Headers */
h1#header { 
    text-align: center; 
    color: #FFC72C !important; /* Mind Stone */
    text-shadow: 0 0 20px rgba(255, 199, 44, 0.8), 0 0 40px rgba(255, 199, 44, 0.4); 
    margin-bottom: 20px; 
    letter-spacing: 4px;
    text-transform: uppercase;
}

/* Buttons */
button.primary {
    background: linear-gradient(45deg, #FFC72C, #FF8C00) !important; /* Mind to Soul Stone */
    color: #0A0A0C !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(255, 199, 44, 0.6) !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    clip-path: polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px) !important;
    font-weight: 800 !important;
    transition: all 0.2s !important;
}
button.primary:hover {
    box-shadow: 0 0 30px rgba(255, 199, 44, 1) !important;
    transform: scale(1.02) !important;
}

/* Time Stone Green for logs/metrics */
.monospace-text textarea { 
    font-family: 'Courier New', Courier, monospace !important; 
    color: #00FF7F !important; 
    text-shadow: 0 0 8px rgba(0, 255, 127, 0.5) !important; 
    background: rgba(0, 30, 10, 0.6) !important;
    border: 1px solid #00FF7F !important;
}

/* Reality Stone Red for Accordion (Citations) */
.gr-accordion {
    border-left: 4px solid #DC143C !important;
    background: rgba(220, 20, 60, 0.05) !important;
}

/* Space Stone Glow for Audio Players */
.gr-audio {
    box-shadow: inset 0 0 20px rgba(0, 210, 255, 0.2) !important;
    border-bottom: 2px solid #00D2FF !important;
}

/* Titles */
h3 {
    margin-top: 0 !important;
    text-transform: uppercase;
    font-family: 'Orbitron', sans-serif !important;
}
.mind-stone-text { color: #FFC72C !important; text-shadow: 0 0 10px rgba(255, 199, 44, 0.8); }
.power-stone-text { color: #8A2BE2 !important; text-shadow: 0 0 10px rgba(138, 43, 226, 0.8); }
.space-stone-text { color: #00D2FF !important; text-shadow: 0 0 10px rgba(0, 210, 255, 0.8); }
"""

with gr.Blocks(title="ULTRON-V Voice RAG", theme=theme, css=custom_css) as demo:
    gr.Markdown("# ⚡ INFINITY ULTRON COMMAND OVERRIDE", elem_id="header")
    
    with gr.Row():
        # Column 1: INPUTS (Space Stone Focused)
        with gr.Column(scale=1):
            gr.Markdown("<h3 class='space-stone-text'>🔵 INPUT SENSORS</h3>")
            audio_in = gr.Audio(sources=["microphone"], type="filepath", label="Voice Input")
            text_in = gr.Textbox(placeholder="Or type your override sequence...", label="Text Input (Fallback)")
            mode_toggle = gr.Radio(["Fast Path (Latency)", "Quality Path (Ensemble)"], value="Fast Path (Latency)", label="Processing Mode")
            submit_btn = gr.Button("EXECUTE OVERRIDE", variant="primary")
            
        # Column 2: 3D CYBERNETIC CORE (Reality/Space/Mind)
        with gr.Column(scale=2):
            gr.Markdown("<h3 class='mind-stone-text'>🧠 AI MATRIX CORE</h3>")
            core_plot = gr.Plot(value=generate_core_wireframe(), label="Core Uplink")
            
        # Column 3: OUTPUTS (Power Stone Focused)
        with gr.Column(scale=1):
            gr.Markdown("<h3 class='power-stone-text'>🟣 NEURAL RESPONSE</h3>")
            answer_out = gr.Textbox(label="Generated Response", lines=5)
            with gr.Accordion("Source Citations", open=False):
                citations_out = gr.Markdown()
            audio_out = gr.Audio(label="Synthesized Speech", interactive=False)
            
    with gr.Row():
        metrics_out = gr.Textbox(label="Diagnostics & Timeline", lines=8, elem_classes="monospace-text")

    submit_btn.click(
        fn=process_interaction,
        inputs=[audio_in, text_in, mode_toggle],
        outputs=[answer_out, citations_out, metrics_out, audio_out]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", theme=theme)
