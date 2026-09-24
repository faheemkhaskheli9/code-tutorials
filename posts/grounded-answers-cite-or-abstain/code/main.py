"""Grounded answers: cite the source sentence by sentence, or abstain.

Three gates sit between a question and an answer the user gets to read:

  1. retrieval gate - if nothing retrieved is close enough, abstain without
     ever calling the language model
  2. support gate   - every sentence of the answer has to match a retrieved
     chunk (embedding similarity + word overlap), or it is dropped
  3. number gate    - every number in a sentence has to appear in the chunk
     that supports it

Citations are computed from the support gate, not read out of the model's
text. Runs on CPU, no API key.

    python main.py                   # demo questions
    python main.py "your question"   # ask your own
    python main.py --raw "..."       # same pipeline, gates 2 and 3 off
    python main.py --eval            # the scored question set + self-checks
"""

import re
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSeq2SeqLM, AutoTokenizer

DOCS = Path(__file__).parent / "docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL = "google/flan-t5-small"
CHUNK_CHARS, TOP_K = 400, 3

RETRIEVAL_MIN = 0.25  # gate 1: best cosine below this means the manual is silent
SUPPORT_MIN = 0.42  # gate 2: 0.5*cosine + 0.5*word overlap, tuned on this corpus
ABSTAIN = "I don't know."

# No "cite your sources" instruction on purpose: flan-t5-small answers a
# question like "What does E_SD mean?" with the literal text "[1]" when you ask
# for citations. The citations come from verify(), not from the model.
PROMPT = (
    "Answer the question using only the context below. If the context does not "
    "contain the answer, reply exactly: I don't know.\n\n{context}\n\n"
    "Question: {question}\nAnswer:"
)

STOPWORDS = set(
    "a an and are as at be by can do does for from has have how i in is it its of on or "
    "that the to use used was what when where which who why will with you your".split()
)

DEMO_QUESTIONS = [
    "What does error E_SD mean?",
    "How far from the base station can the unit be?",
    "How long does the battery pack last?",
    "Can I update the firmware over the radio link?",
    "What is the capital of France?",
]


def chunk(text, size=CHUNK_CHARS):
    """One chunk per paragraph, gluing short ones together up to `size` chars."""
    pieces = []
    for para in re.split(r"\n\s*\n", text):
        para = " ".join(para.split())
        if not para:
            continue
        if pieces and len(pieces[-1]) + len(para) < size:
            pieces[-1] += " " + para
        else:
            pieces.append(para)
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
    chunks, sources = [], []
    for path in sorted(docs.glob("*.md")):
        for i, piece in enumerate(chunk(path.read_text(encoding="utf-8"))):
            chunks.append(piece)
            sources.append(f"{path.name} #{i}")
    if not chunks:
        raise SystemExit(f"No markdown found in {docs}")
    return {"vectors": embed(chunks), "chunks": chunks, "sources": sources}


def search(question, index, embed, top_k=TOP_K):
    """Return [(chunk_id, cosine)] for the top_k chunks, best first."""
    scores = index["vectors"] @ embed([question])[0]
    return [(int(i), float(scores[i])) for i in np.argsort(-scores)[:top_k]]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def words(text):
    # keep quill.cfg and 3.4 in one piece, but never swallow a sentence's full stop
    tokens = re.findall(r"[a-z0-9_]+(?:\.[a-z0-9_]+)*", text.lower())
    return {w for w in tokens if w not in STOPWORDS}


def numbers(text):
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def support(pair, pair_vec, chunk_text, chunk_vec):
    """Half embedding similarity, half word overlap. Either alone is easy to fool."""
    pair_words = words(pair)
    overlap = len(pair_words & words(chunk_text)) / max(len(pair_words), 1)
    return 0.5 * float(pair_vec @ chunk_vec) + 0.5 * overlap


def verify(question, answer, hits, index, embed):
    """Keep the sentences a retrieved chunk backs; return (kept, rejected)."""
    claims = sentences(re.sub(r"\[\d+\]", "", answer))  # the model's own markers go in the bin
    if not claims:
        return [], ["the model replied with citation markers and no text"]
    # score the question and the claim together: a chunk that backs "3 minutes"
    # is not the same as a chunk that backs "how long does the battery last? 3 minutes"
    vecs = embed([f"{question} {c}" for c in claims])
    kept, rejected = [], []
    for claim, vec in zip(claims, vecs):
        if len(words(claim)) < 2:
            rejected.append(f"{claim!r} - too short to check against a source")
            continue
        scored = [
            (support(f"{question} {claim}", vec, index["chunks"][cid], index["vectors"][cid]), rank, cid)
            for rank, (cid, _) in enumerate(hits, start=1)
        ]
        score, rank, cid = max(scored, key=lambda s: (s[0], -s[1]))  # ties go to the better hit
        if score < SUPPORT_MIN:
            rejected.append(f"{claim!r} - no chunk supports it (best {score:.2f})")
        elif not numbers(claim) <= numbers(index["chunks"][cid]):
            missing = ", ".join(sorted(numbers(claim) - numbers(index["chunks"][cid])))
            rejected.append(f"{claim!r} - number {missing} is not in [{rank}]")
        else:
            kept.append(f"{claim} [{rank}]")
    return kept, rejected


def answer(question, index, embed, generate, gates=True):
    """Return (text, hits, rejected). hits is [] when the retrieval gate fires."""
    hits = search(question, index, embed)
    if hits[0][1] < RETRIEVAL_MIN:
        return f"{ABSTAIN} The manual does not cover this.", [], [
            f"retrieval gate: best chunk scored {hits[0][1]:.2f} < {RETRIEVAL_MIN}"
        ]
    context = "\n\n".join(
        f"[{rank}] ({index['sources'][cid]}) {index['chunks'][cid]}"
        for rank, (cid, _) in enumerate(hits, start=1)
    )
    raw = generate(PROMPT.format(context=context, question=question)).strip()
    if not raw:
        return f"{ABSTAIN} The model returned nothing.", [], ["empty completion"]
    if not gates:
        return raw, hits, []
    kept, rejected = verify(question, raw, hits, index, embed)
    if not kept:
        return f"{ABSTAIN} Nothing in the manual backs an answer.", [], rejected
    return " ".join(kept), hits, rejected


def local_generator(name=GEN_MODEL):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSeq2SeqLM.from_pretrained(name).eval()

    def generate(prompt):
        batch = tok(prompt, return_tensors="pt", truncation=True, max_length=1024)
        with torch.no_grad():
            out = model.generate(**batch, max_new_tokens=64)
        return tok.decode(out[0], skip_special_tokens=True)

    return generate


def hosted_generate(prompt):
    """Where a hosted model plugs in - the gates do not change. `pip install anthropic`."""
    import anthropic  # deliberately not in requirements.txt: the local path needs no key

    msg = anthropic.Anthropic().messages.create(
        model="claude-opus-5", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return next(b.text for b in msg.content if b.type == "text")


def show(question, index, embed, generate, gates=True):
    text, hits, rejected = answer(question, index, embed, generate, gates)
    print(f"Q: {question}")
    print(f"A: {text}")
    for rank, (cid, score) in enumerate(hits, start=1):
        print(f"   [{rank}] {index['sources'][cid]} (retrieval {score:.2f})")
    for note in rejected:
        print(f"   dropped: {note}")
    print()


# (question, answerable from docs/, a string the right answer must contain)
EVAL_CASES = [
    ("How often does the Quill 2 take a reading?", True, "90"),
    ("What does error E_SD mean?", True, "FAT32"),
    ("How high should I mount the unit?", True, "2.0"),
    ("How long does a firmware flash take?", True, "3 minutes"),
    ("How far from the base station can the unit be?", True, "400"),
    ("How many years of readings fit on the card?", True, "11"),
    ("How long does the battery pack last?", False, None),
    ("Can I update the firmware over the radio link?", False, None),
    ("What is the maximum wind speed the Quill 2 can measure?", False, None),
    ("What is the warranty period?", False, None),
    ("What is the capital of France?", False, None),
]


def score_cases(index, embed, generate, gates):
    results = []
    for question, answerable, needle in EVAL_CASES:
        text, _, _ = answer(question, index, embed, generate, gates)
        abstained = text.startswith(ABSTAIN)
        ok = (not abstained and needle.lower() in text.lower()) if answerable else abstained
        results.append((answerable, ok))
        print(f"  {'ok  ' if ok else 'FAIL'} {'answer' if answerable else 'abstain'}: {text[:70]}")
    return results


def summarise(label, results):
    answerable = [ok for wanted, ok in results if wanted]
    refusable = [ok for wanted, ok in results if not wanted]
    print(
        f"{label}: {sum(answerable)}/{len(answerable)} answered correctly, "
        f"{sum(refusable)}/{len(refusable)} correctly refused, "
        f"{sum(answerable) + sum(refusable)}/{len(results)} overall"
    )


def self_check():
    assert chunk("one\n\ntwo") == ["one two"], "short paragraphs glue together"
    assert len(chunk("word " * 100 + "\n\n" + "word " * 100)) == 2, "long paragraphs stay apart"
    assert sentences("One. Two!") == ["One.", "Two!"]
    assert numbers("3.4 V and 128 GB") == {"3.4", "128"}
    assert words("It lasts 15 minutes.") == {"lasts", "15", "minutes"}
    assert words("edit quill.cfg") == {"edit", "quill.cfg"}


def run_eval(index, embed, generate):
    self_check()
    print("Gates off (raw model output):")
    raw = score_cases(index, embed, generate, gates=False)
    print("\nGates on:")
    gated = score_cases(index, embed, generate, gates=True)
    print()
    summarise("Gates off", raw)
    summarise("Gates on ", gated)


def main():
    asked = [a for a in sys.argv[1:] if not a.startswith("--")]
    embed = Embedder()
    index = build_index(embed)
    print(f"Indexed {len(index['chunks'])} chunks\n")
    generate = hosted_generate if "--hosted" in sys.argv else local_generator()
    if "--eval" in sys.argv:
        run_eval(index, embed, generate)
        return
    for question in asked or DEMO_QUESTIONS:
        show(question, index, embed, generate, gates="--raw" not in sys.argv)


if __name__ == "__main__":
    main()
