# SIRA – AI Assistant for Sunbeam Institute

SIRA is a Streamlit-based RAG (Retrieval-Augmented Generation) AI assistant for the [Sunbeam Infotech Institute](https://www.sunbeaminfo.in/) website. It provides accurate, context-aware answers about courses, internships, and institute information.

## Features

- 🤖 Multi-model support: GROQ (Llama 3.3 70B), Gemini 2.5 Flash, LM Studio (local)
- 🔍 RAG pipeline using ChromaDB + `sentence-transformers/all-MiniLM-L6-v2`
- 💬 Chat history with multi-session support and prompt editing
- 🔐 User authentication (login / signup)
- 🎨 Modern glassmorphism UI with animated gradients

## Setup (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/Yuvraj220705/SIRA-AI-Assistant.git
cd SIRA-AI-Assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure secrets
Copy the template and fill in your API keys:
```bash
# Edit .streamlit/secrets.toml and add your keys:
GROQ_API_KEY = "your-groq-api-key"
GEMINI_API_KEY = "your-gemini-api-key"
```
> Get a free GROQ API key at https://console.groq.com  
> Get a free Gemini API key at https://aistudio.google.com

### 4. Run the app
```bash
streamlit run app.py
```

## Deployment (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select this repository, branch `main`, and set the entry point to `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
5. Click **Deploy**.

> **Note:** The ChromaDB vector store (`chroma_db/`) is pre-built and included in the repository. The app loads it directly — no website scraping occurs at runtime on Streamlit Cloud.

## Rebuilding the Vector Store (Local Only)

If you need to refresh the knowledge base from the website, run locally (requires Chrome):
```bash
python vector_store.py
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| LLM | GROQ / Gemini / LM Studio |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| Scraping | Selenium |
| Framework | LangChain |

## Project Structure

```
app.py                          # Streamlit entry point
AuthenticatedUserHome.py        # RAG chat interface (post-login)
UnauthenticatedUserHome.py      # Landing page with basic chat
login.py / signup.py            # Authentication
vector_store.py                 # ChromaDB create/load
chunking.py                     # Text splitting and normalization
scrape_*.py                     # Website scrapers (run locally only)
photos/                         # UI image assets
chroma_db/                      # Pre-built vector store
requirements.txt                # Python dependencies
```