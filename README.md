# PharmD Residency Interview Simulator

A locally run, privacy-first interview practice tool for pharmacy residents.  
This application simulates a residency interview panel that asks questions and gives feedback based on **your specific program’s documents**—all without sending data to the cloud.

Built by a fellow pharmacy professional who understands how stressful residency interviews can be—and how much preparation they require. 

---

## Why This Exists

Residency interviews increasingly focus on **program-specific knowledge**, **ASHP competencies**, and **structured storytelling (STAR method)**. Most practice tools are generic or require internet access.

This simulator:
- Reads **your program’s PDFs** (brochures, rotation guides, etc.)
- Asks relevant questions like: *"How would you contribute to our medication safety committee?"*
- Evaluates responses for clinical maturity, clarity, and structure
- Runs **entirely on your computer**—ideal for sensitive or offline practice

---

## For Residents: Getting Started (Windows)

### 1. Install Ollama
This app uses [Ollama](https://ollama.com) to run the AI model locally.
- Download: [https://ollama.com/download/OllamaSetup.exe](https://ollama.com/download/OllamaSetup.exe)
- Install it like any Windows program. It runs silently in the background.

> **Note**: On first use, Ollama will download the `llama3.1` model (~4.7 GB). This happens automatically when you start the simulator.

### 2. Download and Run
1. Go to the [Releases page](https://github.com/tikik/pharmD-residency-interview-simulation/releases)
2. Download **`PharmD-Interviewer-Package.zip`**
3. **Extract the full folder** (right-click → “Extract All…”)
4. Open the extracted folder and **double-click `Start_Interview.exe`**
   - A command window will appear—**leave it open**
   - Your browser will launch automatically at `http://localhost:8501`

### 3. (Optional) Add Your Program’s Materials
To get personalized questions:
- Place your residency program’s PDFs in the `data/` folder
- Restart the app—feedback will now reference your specific site

> First launch takes 1–2 minutes as models load. Subsequent sessions start in seconds.

---

## Technical Overview

This project combines:
- **Retrieval-Augmented Generation (RAG)** using Chroma and Hugging Face embeddings
- **Local LLM inference** via Ollama (`llama3.1`)
- **Voice input/output** using Whisper (local) and gTTS
- **Streamlit** for the web interface
- **PyInstaller** to package everything into a Windows executable

All components run offline. The only external dependency is Ollama, which is installed separately as a system service.

The build pipeline uses **GitHub Actions** to create a Windows `.exe` on release—so residents never need Python or the command line.

---

### Project Structure
```
├── app.py                  # Streamlit UI
├── rag_pipeline.py         # RAG chain, speech I/O
├── ingest_pdfs.py          # Builds Chroma DB from data/
├── data/                   # Place your residency PDFs here
├── chroma_db/              # Auto-generated vector database
├── instructions.txt        # End-user guide (included in ZIP)
├── requirements.txt        # Python dependencies
└── .github/workflows/      # Auto-builds Windows .exe on release
```
**Built with ❤️ to support future pharmacy leaders.**

### Project Journey

- **Git hygiene**: Learned from accidental 13k-file commit → now use strict `.gitignore`
- **Build strategy**: Switched from Linux (non-functional `.exe`) to Windows-native builds
- **Distribution**: Deliver via GitHub Releases — never commit binaries to source

### Acknowledgements

Ollama – Local LLM runtime (ollama.com)
Llama 3.1 – Meta’s open-weight language model
all-MiniLM-L6-v2 – Efficient sentence embeddings (Hugging Face)
Chroma – Lightweight vector database
Streamlit – Beautiful ML apps in minutes
