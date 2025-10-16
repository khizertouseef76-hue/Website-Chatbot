# 🌐 Universal Website Chatbot (RAG + Streamlit)

## 🧠 Overview
This project is a **Retrieval-Augmented Generation (RAG)** chatbot that answers user questions based on the content of *any website* — without training a new model.

It scrapes text from given URLs or sitemaps, builds a searchable FAISS vector index using embeddings, and generates answers using a pre-trained language model (Flan-T5).  
A Streamlit UI provides an elegant interface for chatting with the AI.

---

## ⚙️ Features
- ✅ Works with **any website**
- 🌍 Dynamic web scraping via **Playwright**
- 🧩 **FAISS** index for semantic retrieval
- 🤖 Uses **Flan-T5** for generation (no training needed)
- 💬 **Streamlit UI** with dark theme and custom logo
- 📁 Fully local — no API keys or internet calls required after setup

---

## 🧰 Tech Stack
| Component | Library / Tool |
|------------|----------------|
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Search | FAISS |
| Text Generation | `google/flan-t5-base` (or `flan-t5-large`) |
| Web Scraping | Playwright + Trafilatura |
| Frontend | Streamlit |
| Language | Python 3.11+ |

---

## 🧩 Project Structure
```
Chatbot For Website/
│
├── app.py                       # Streamlit UI
├── run_chatbot.py               # Orchestrator script
│
├── src/
│   ├── scraper_dynamic.py        # Website scraper
│   ├── build_index.py            # Embedding + FAISS builder
│   ├── query_engine.py           # Retrieval testing (CLI)
│   ├── utils.py                  # Helper functions
│   └── __init__.py
│
├── data/                         # Scraped text chunks (JSONL)
├── embeddings/                   # FAISS index and metadata
└── mega.ai-logo-png-1.webp       # Logo for UI
```

---

##  How It Works
1. **Scrape Website**  
   The scraper fetches and renders webpages (using Playwright), extracts readable text, and splits it into manageable chunks.  
   ```bash
   python -m src.scraper_dynamic --sitemap https://example.com/sitemap.xml
   ```

2. **Build FAISS Index**  
   Converts the chunks into embeddings for fast semantic search.  
   ```bash
   python -m src.build_index --infile data/chunks.jsonl
   ```

3. **Launch Chatbot UI**  
   Starts a Streamlit-based interface for question answering.  
   ```bash
   streamlit run app.py
   ```

4. **Chat!**  
   Enter questions in the chat box — the bot retrieves the most relevant text and answers naturally.

---

## 💻 Quick One-Line Run
Use the orchestrator to do everything automatically:
```bash
python run_chatbot.py --urls https://www.python.org/about/ https://www.python.org/downloads/
```
It will:
1. Scrape the site  
2. Build the FAISS index  
3. Launch the chatbot UI automatically

---

## 🧩 Requirements
Install dependencies inside your virtual environment:
```bash
pip install -U pip
pip install sentence-transformers faiss-cpu transformers trafilatura gradio pandas tqdm numpy playwright streamlit
playwright install
```

---

## ⚙️ Notes
- The project is modular: you can reuse the scraper, retriever, or UI independently.
- Works offline once models and pages are cached.

---

## 🧾 License
This project is open-source and intended for educational, research, and local business use.

---

© 2025 Meg.ai Universal Website Chatbot
