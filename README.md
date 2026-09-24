# Code Tutorials

Runnable code for the tutorials on my blog. Each post lives in
[`posts/<slug>/`](posts/): the article HTML, the full source under `code/`, and a
ZIP of it.

## How it's made

`run.ps1` asks Claude Code to write the next post from [`topics.md`](topics.md)
following [`WRITE_POST.md`](WRITE_POST.md). Claude builds the code, runs it, and
writes the post around the real output. [`publish.py`](publish.py) then zips the
code, pushes it here and creates the Blogger post (a draft by default).

## One-time setup

1. **GitHub repo** (public, so ZIP links work):
   `git remote add origin https://github.com/faheemkhaskheli9/code-tutorials.git`
   after creating it, or just `gh repo create code-tutorials --public --source . --push`.
2. **Google Cloud** (https://console.cloud.google.com):
   - Create a project and enable **Blogger API v3** (APIs & Services -> Library).
   - Google Auth Platform -> Branding: fill app name + your email.
     Audience: **External**, add yourself as a test user, then click
     **Publish app** (status "In production"). In "Testing" status the login
     expires every 7 days and the automation silently stops.
   - Clients -> Create client -> **Desktop app** -> download the JSON and save it
     here as `client_secret.json`.
3. `python publish.py auth` -> sign in with the Google account that owns the blog.
   Google shows "app isn't verified" - click Advanced -> Go to (your app). That's
   expected for a personal app. This writes `token.json`.
4. `python -m venv .venv` (posts install their dependencies here).

## Daily use

```powershell
.\run.ps1          # write + publish one post as a DRAFT (review it in Blogger)
.\run.ps1 -Live    # write + publish live
python publish.py  # retry publishing if a run failed after writing
```

Schedule it (Mon/Wed/Fri 9:00):

```powershell
schtasks /Create /TN "Blog post" /SC WEEKLY /D MON,WED,FRI /ST 09:00 /TR "powershell -NoProfile -ExecutionPolicy Bypass -File E:\Projects\code-tutorials\run.ps1"
```

Logs go to `logs/`. Never commit `client_secret.json` or `token.json`
(already in `.gitignore`).
