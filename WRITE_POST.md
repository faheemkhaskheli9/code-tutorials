# Write one blog post

You are writing ONE new tutorial for Faheem Khaskheli's programming blog on Blogger.
Faheem is a Python / AI engineer: LLMs, RAG, agents, computer vision, medical
imaging, time-series, reinforcement learning, Django and ML deployment. Readers
are working developers who want something they can run today.

## 1. Pick the topic

Take the FIRST unchecked `- [ ]` line in `topics.md`. Make a short kebab-case slug
from it (e.g. `rag-from-scratch-in-100-lines`). If `posts/<slug>/` already exists,
take the next one. Tick the line (`- [x]`) and append ` -> <slug>` when done.

## 2. Build and run the code FIRST

Create `posts/<slug>/code/` with a complete, small project:
- `main.py` (plus a module or two only if the tutorial needs it), `requirements.txt`
  with pinned versions, and a short `README.md` (what it does, how to run it).
- It must run on a CPU laptop in under 5 minutes with NO API keys and NO paid
  services. For LLM topics use a small local Hugging Face model or a
  deterministic fallback, and show where a hosted model would plug in.
- Datasets: public and small (sklearn/torchvision/HF datasets, or generated).
- Install deps into the shared venv: `.venv/Scripts/python -m pip install -r posts/<slug>/code/requirements.txt`
  and run with `.venv/Scripts/python`.
- Run it. Fix it until it works. Save the real terminal output to
  `posts/<slug>/code/output.txt`. Every output and number in the post must come
  from this real run - never invent results.

## 3. Write the post: `posts/<slug>/post.html`

Blogger post BODY only (no `<html>`, `<head>`, `<body>`, no `<h1>` - the title is separate).

Structure:
- Opening (2-4 short paragraphs): the concrete problem, why it bites, what the
  reader will have at the end. No throat-clearing.
- Build it step by step: `<h2>` sections, each with a snippet and the reasoning
  behind it (why this approach, what the alternative costs).
- "Running it" with the real output from `output.txt`.
- "Gotchas" - real things that broke or surprised you while building THIS code
  (you did just build it; describe those actual failures).
- "Where to go next" - 2-3 concrete extensions.
- Download box near the top AND at the end:
  `<p><b>Full code:</b> <a href="{{CODE_URL}}">browse on GitHub</a> | <a href="{{ZIP_URL}}">download ZIP</a></p>`
  (keep the `{{...}}` placeholders exactly - the publisher fills them in).

Code blocks: `<pre style="background:#f6f8fa;padding:12px;border-radius:6px;overflow-x:auto;font-size:14px"><code class="language-python">...</code></pre>`
with `<`, `>`, `&` HTML-escaped. Snippets must match the files in `code/` exactly.

Length: 1200-2000 words.

## Voice - it must read like a person wrote it

- First person, conversational, confident. Contractions. Mix short and long sentences.
- Have opinions: "I'd skip X here", "this is the part people get wrong".
- Specific over generic: real numbers, real error messages, real file names.
- NEVER use: "delve", "dive into", "in today's fast-paced world", "landscape",
  "leverage", "unlock", "seamless", "robust" (as filler), "game-changer",
  "it's important to note", "In conclusion", "Happy coding!", emoji headings,
  or a closing summary that repeats the post.
- Don't open with a dictionary definition or a rhetorical question.
- Don't invent jobs, clients, employers or past projects. Stories come from
  building this post's code or from general, clearly-framed experience.
- End with one genuine question to readers, not a recap.

## 4. Metadata: `posts/<slug>/meta.json`

`{"title": "...", "labels": ["Python", "..."]}` - title is outcome- or number-led
(e.g. "Build a RAG Pipeline in 100 Lines of Python (No API Key)"), not
"Understanding X". 3-5 labels.

## Rules

- Do NOT git commit, push, or call any publishing API - `publish.py` does that.
- Do NOT touch files outside this repo.
- If the code cannot be made to work, delete `posts/<slug>/`, leave the topic
  unchecked, add a note under it, and stop.
