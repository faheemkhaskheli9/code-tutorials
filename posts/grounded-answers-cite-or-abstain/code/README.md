# Cite the source or say "I don't know"

A retrieval-augmented question answerer with three gates between the language
model and the user: a retrieval gate, a per-sentence support gate and a number
gate. Citations are computed from the support gate, so they point at the chunk
that actually backs the sentence instead of at whatever the model typed.

CPU only, no API key, one file.

`docs/` is the corpus: the manual for a fictional weather station called the
Quill 2. Fictional on purpose - the model cannot answer from memory, so a
correct answer has to have come through retrieval. The manual also leaves some
obvious questions unanswered (battery life, wind speed, warranty), which is
where the gates earn their keep.

## Run it

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: .venv/bin/python
.venv/Scripts/python main.py
```

First run downloads `all-MiniLM-L6-v2` (~90 MB) and `flan-t5-small` (~300 MB)
from Hugging Face. After that a full run is about 13 seconds, and `--eval` takes 16.

```bash
python main.py "What voltage triggers E_BATT?"   # your own question
python main.py --raw "..."                       # gates 2 and 3 off, for comparison
python main.py --eval                            # 11 scored questions + self-checks
python main.py --hosted "..."                    # hosted model writes, gates unchanged
```

`--hosted` needs `pip install anthropic` and an `ANTHROPIC_API_KEY`. Everything
else runs locally.

`output.txt` is the real output of a warm run of `main.py` followed by
`main.py --eval`.

## The three gates

| Gate | Fires when | Knob |
|---|---|---|
| retrieval | best chunk cosine is below the threshold - the model is never called | `RETRIEVAL_MIN` |
| support | a sentence of the answer matches no retrieved chunk | `SUPPORT_MIN` |
| number | a number in a sentence is missing from the chunk that backs it | none |

Both thresholds were tuned on this corpus with `--eval`. Retune them on yours;
they are not universal constants.
