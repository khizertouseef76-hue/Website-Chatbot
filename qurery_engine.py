# src/query_engine.py
import os, json, faiss, numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class RAGEngine:
    def __init__(
        self,
        index_path="embeddings/faiss_index/index.faiss",
        meta_path="embeddings/faiss_index/metadata.json",
        embed_model="sentence-transformers/all-MiniLM-L6-v2",
        gen_model="google/flan-t5-base",
    ):
        if not os.path.exists(index_path):
            raise FileNotFoundError("FAISS index not found. Build it first.")
        self.index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.embedder = SentenceTransformer(embed_model)
        self.tokenizer = AutoTokenizer.from_pretrained(gen_model)
        self.generator = AutoModelForSeq2SeqLM.from_pretrained(gen_model)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[str, str]]:
        q = self.embedder.encode([query])
        D, I = self.index.search(np.array(q).astype("float32"), k)
        res = []
        for idx in I[0]:
            if 0 <= idx < len(self.metadata):
                m = self.metadata[idx]
                res.append((m["text"], m["source"]))
        return res

    def generate(self, context: str, query: str) -> str:
        prompt = (
            "You are Meg.ai, a concise and accurate assistant.\n"
            "Answer ONLY from the context. If unsure, say: "
            "\"No reliable answer found, please refine your question.\"\n\n"
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        out = self.generator.generate(**inputs, max_new_tokens=200)
        return self.tokenizer.decode(out[0], skip_special_tokens=True)

if __name__ == "__main__":
    engine = RAGEngine()
    q = input("Query: ")
    chunks = engine.retrieve(q)
    if not chunks:
        print("No reliable answer found, please refine your question.")
    else:
        ctx = "\n".join([c[0] for c in chunks])
        ans = engine.generate(ctx, q)
        print("\nAnswer:\n", ans)
        print("\nSources:")
        for _, s in chunks:
            print("-", s)
