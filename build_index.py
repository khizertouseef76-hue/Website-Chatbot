# src/build_index.py
import argparse, os, json
import numpy as np, faiss
from sentence_transformers import SentenceTransformer
from src.utils import read_jsonl, ensure_dir

def main():
    parser = argparse.ArgumentParser(description="Build FAISS index from chunks.jsonl")
    parser.add_argument("--infile", default="data/chunks.jsonl")
    parser.add_argument("--outdir", default="embeddings/faiss_index")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    args = parser.parse_args()

    data = read_jsonl(args.infile)
    if not data:
        raise SystemExit(f"No data in {args.infile}")

    print(f"[LOAD] Embedding model: {args.model}")
    embedder = SentenceTransformer(args.model)

    texts = [row["text"] for row in data]
    embs = embedder.encode(texts, batch_size=64, show_progress_bar=True)
    embs = np.asarray(embs, dtype="float32")

    index = faiss.IndexFlatIP(embs.shape[1])
    faiss.normalize_L2(embs)
    index.add(embs)

    ensure_dir(args.outdir)
    faiss.write_index(index, os.path.join(args.outdir, "index.faiss"))

    # metadata used by app.py for sources
    meta = [{"text": row["text"], "source": row["source"]} for row in data]
    with open(os.path.join(args.outdir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f"[DONE] vectors={embs.shape[0]} dim={embs.shape[1]} saved to {args.outdir}")

if __name__ == "__main__":
    main()
