# RAG from scratch in ~100 lines

A complete retrieval-augmented generation pipeline - chunk, embed, retrieve,
answer with citations - in one file, on CPU, with no API key and no vector
database.

`docs/` is the corpus: four pages of documentation for a fictional deployment
CLI called Quokka. Fictional on purpose, so the language model cannot answer
from memory and every correct answer has to come from retrieval.

## Run it

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
.venv/Scripts/python main.py
```

First run downloads `all-MiniLM-L6-v2` (~90 MB) and `flan-t5-small` (~300 MB)
from Hugging Face - about 4 minutes on a normal connection. After that the whole
script takes ~15 seconds.

```bash
python main.py "How long does a rollback take?"   # your own question
python main.py --hosted "..."                     # same retrieval, hosted model answers
```

`--hosted` needs `pip install anthropic` and an `ANTHROPIC_API_KEY`. Everything
else runs locally.

`output.txt` is the real output of a warm run.
