import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def create_rag_chain(embeddings, llm):
    """Build RAG chain from pre-loaded components."""
    if not os.path.exists("chroma_db"):
        raise RuntimeError("Vector database not found! Run the ingestion script first.")
    
    vectordb = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    template = """
    You are an expert PharmD Residency Interview Coach and an ASHP-aligned Interviewer. 
    Use the context from the residency PDFs to evaluate the candidate.

    CONTEXT FROM DOCUMENTS:
    {context}

    CANDIDATE'S RESPONSE:
    {question}

    INSTRUCTIONS:
    1. ACT AS THE INTERVIEWER: Stay in your assigned persona.
    2. EVALUATE: Provide a brief "Coach's Critique" using the STAR method (Situation, Task, Action, Result). 
    - Was the clinical logic sound?
    - Did they mention specific details from the program brochure?
    3. SCORE: Give scores for 'Clarity', 'Depth', and 'STAR Compliance' out of 10.
    4. NEXT STEP: Ask the next interview question.

    FORMATTING:
    Use bold headers like **Coach's Feedback** and **Next Question**.
    End with:
    SCORE_CLARITY: X/10
    SCORE_DEPTH: X/10
    SCORE_STAR: X/10
    """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

rag_chain = create_rag_chain()

# Free Speech-to-Text (using local Whisper)
def speech_to_text(audio_buffer):
    # Note: Requires 'pip install openai-whisper'
    import whisper
    import tempfile
    
    model = whisper.load_model("base")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_buffer.read())
        result = model.transcribe(tmp.name)
    return result["text"]

# Free Text-to-Speech (using gTTS)
def text_to_speech(text):
    from gtts import gTTS
    import io
    
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()