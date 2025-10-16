import streamlit as st
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import faiss, numpy as np, json, os

# ------------------------- PAGE SETUP -------------------------
st.set_page_config(page_title="Meg.ai Chatbot", page_icon="💬", layout="centered")

# Custom theme CSS
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .stTextInput > div > div > input {
            background-color: #1c1f26;
            color: white;
            border-radius: 8px;
            border: 1px solid #5e2bff;
        }
        .stButton>button {
            background-color: #5e2bff;
            color: white;
            border-radius: 8px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #7749ff;
        }
        .stMarkdown {
            color: white;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ------------------------- HEADER -------------------------
# Display your logo (transparent background look)
st.image("mega.ai-logo-png-1.webp", width=250)
st.markdown("<h3 style='text-align:center;'>💬 Ask anything about the website!</h3>", unsafe_allow_html=True)
st.write("---")

# ------------------------- LOAD MODELS -------------------------
@st.cache_resource
def load_models():
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    return embedder, tokenizer, model

embedder, tokenizer, model = load_models()

# ------------------------- LOAD FAISS INDEX -------------------------
INDEX_PATH = "embeddings/faiss_index/index.faiss"
META_PATH = "embeddings/faiss_index/metadata.json"

if not os.path.exists(INDEX_PATH):
    st.error("⚠️ No FAISS index found. Please run `build_index.py` first.")
    st.stop()

index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# ------------------------- FUNCTIONS -------------------------
def retrieve_chunks(query, top_k=10):
    q_vec = embedder.encode([query])
    D, I = index.search(np.array(q_vec).astype('float32'), top_k)
    results = [(metadata[i]['text'], metadata[i]['source']) for i in I[0] if i < len(metadata)]
    return results

def generate_answer(context, query):
    # If context is empty, return fallback immediately
    if not context.strip():
        return "No reliable answer found, please refine your question."

    # --- Simplified and more direct prompt ---
    prompt = f"""
Use the information in the CONTEXT below to answer the QUESTION.
Write a clear, short factual answer. If the context truly has no information, say:
"No reliable answer found, please refine your question."

CONTEXT:
{context}

QUESTION: {query}
ANSWER:
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    outputs = model.generate(
        **inputs,
        max_new_tokens=180,
        temperature=0.2,     # less randomness
        do_sample=False,     # more deterministic answers
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # Clean up: remove repeated labels or prompt echoes
    if answer.lower().startswith("answer:"):
        answer = answer.split(":", 1)[1].strip()

    if not answer or len(answer.split()) < 3:
        return "No reliable answer found, please refine your question."

    return answer

# ------------------------- CHAT SECTION -------------------------
st.markdown("### 🧠 Chat with Meg.ai")
user_query = st.text_input("Ask your question:", placeholder="e.g. What services does this website offer?")

if user_query:
    with st.spinner("🔍 Searching knowledge base..."):
        retrieved = retrieve_chunks(user_query)
        if not retrieved:
            st.warning("No reliable answer found, please refine your question.")
        else:
            context_text = "\n".join([r[0] for r in retrieved])
            answer = generate_answer(context_text, user_query)

            st.markdown("#### 💡 Answer:")
            st.write(answer)
            st.write("---")
            st.markdown("#### 🔗 Sources:")
            for _, src in retrieved:
                st.markdown(f"- [{src}]({src})")

# ------------------------- FOOTER -------------------------
st.write("---")
st.markdown("<p style='text-align:center; color:gray;'>🤖 Meg.ai RAG Chatbot © 2025</p>", unsafe_allow_html=True)
