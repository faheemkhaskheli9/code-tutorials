"""RAG from scratch: chunk -> embed -> retrieve -> answer, with citations.

Runs on CPU with no API key. Two small Hugging Face models download on first run
(~400 MB total): MiniLM for the embeddings, Flan-T5-small for the answer text.
No vector database, no framework.

    python main.py                      # the built-in demo questions
    python main.py "your question"      # ask your own
    python main.py --hosted "..."       # same retrieval, hosted model writes the answer
"""

import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSeq2SeqLM, AutoTokenizer

DOCS = Path(__file__).parent / "docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL = "google/flan-t5-small"
CHUNK_CHARS, OVERLAP_CHARS, TOP_K = 600, 100, 3
MIN_SCORE = 0.25  # below this, treat it as "the docs don't cover this"

PROMPT = (
    "Answer the question using only the context below. If the context does not "
    "contain the answer, reply exactly: I don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\nAnswer:"
)

DEMO_QUESTIONS = [
    "How do I roll back a bad deploy?",
    "What port does the local dev server listen on?",
    "My deploy failed with E_LOCKED. What should I do?",
    "What is the capital of France?",
]


def chunk(text, size=CHUNK_CHARS, overlap=OVERLAP_CHARS):
    """Split into overlapping pieces, cutting at whitespace, always moving forward."""
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            snap = text.rfind(" ", start, end)
            if snap > start:
                end = snap
        if text[start:end].strip():
            pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


class Embedder:
    """MiniLM + mean pooling + L2 normalisation, so cosine similarity is a dot product."""

    def __init__(self, name=EMBED_MODEL):
        self.tok = AutoTokenizer.from_pretrained(name)
        self.model = AutoModel.from_pretrained(name).eval()

    def __call__(self, texts):
        batch = self.tok(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            hidden = self.model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1).float()
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
        return torch.nn.functional.normalize(pooled, dim=1).numpy()


def build_index(embed, docs=DOCS):
    if not docs.is_dir():
        raise SystemExit(f"No docs directory at {docs}")
    chunks, sources = [], []
    for path in sorted(docs.glob("*.md")):
        for i, piece in enumerate(chunk(path.read_text(encoding="utf-8"))):
            chunks.append(piece)
            sources.append((path.name, i))
    return {"vectors": embed(chunks), "chunks": chunks, "sources": sources}


def search(question, index, embed, top_k=TOP_K):
    scores = index["vectors"] @ embed([question])[0]
    order = np.argsort(-scores)[:top_k]
    return [(float(scores[i]), index["chunks"][i], index["sources"][i]) for i in order]


def answer(question, index, embed, generate):
    hits = search(question, index, embed)
    if not hits or hits[0][0] < MIN_SCORE:
        return "I don't know - nothing in the docs is close enough.", []
    context = "\n\n".join(text for _, text, _ in hits)
    return generate(PROMPT.format(context=context, question=question)), hits


def local_generator(name=GEN_MODEL):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(name).eval()

    def generate(prompt):
        batch = tok(prompt, return_tensors="pt", truncation=True, max_length=1024)
        with torch.no_grad():
            out = model.generate(**batch, max_new_tokens=64)
        return tok.decode(out[0], skip_special_tokens=True).strip()

    return generate


def hosted_generate(prompt):
    """Where a hosted model plugs in - same prompt, better answers. `pip install anthropic`."""
    import anthropic  # deliberately not in requirements.txt: the local path needs no key

    msg = anthropic.Anthropic().messages.create(
        model="claude-opus-5", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in msg.content if b.type == "text").strip()


def main():
    asked = [a for a in sys.argv[1:] if not a.startswith("--")]
    embed = Embedder()
    index = build_index(embed)
    print(f"Indexed {len(index['chunks'])} chunks from {len(set(s for s, _ in index['sources']))} files\n")
    generate = hosted_generate if "--hosted" in sys.argv else local_generator()
    for question in asked or DEMO_QUESTIONS:
        text, hits = answer(question, index, embed, generate)
        print(f"Q: {question}")
        print(f"A: {text}")
        for score, _, (name, i) in hits:
            print(f"   [{name} #{i}] {score:.3f}")
        print()


if __name__ == "__main__":
    main()
