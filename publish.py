"""Publish finished posts to Blogger, with their code zipped and pushed to GitHub.

    python publish.py auth      # one-time: sign in with Google, saves token.json
    python publish.py           # publish every posts/<slug>/ without published.json
    python publish.py --live    # same, but go live instead of saving as draft

Stdlib only. A post folder holds post.html, meta.json ({"title", "labels"}) and code/.
"""
import http.server
import json
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from pathlib import Path

BLOG_ID = "2065453767638002019"
GITHUB_REPO = "faheemkhaskheli9/code-tutorials"
SCOPE = "https://www.googleapis.com/auth/blogger"
ROOT = Path(__file__).parent
SECRET, TOKEN, POSTS = ROOT / "client_secret.json", ROOT / "token.json", ROOT / "posts"
REDIRECT = "http://127.0.0.1:8765"
SKIP = {".venv", "venv", "__pycache__", ".git", ".ipynb_checkpoints"}


def client():
    return json.loads(SECRET.read_text())["installed"]


def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    return json.load(urllib.request.urlopen(url, body))


def auth():
    c = client()
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent"})
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            got.update(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Done - you can close this tab.")

        def log_message(self, *a):
            pass

    print("Opening browser. If it doesn't open, visit:\n" + url)
    webbrowser.open(url)
    server = http.server.HTTPServer(("127.0.0.1", 8765), Handler)
    while "code" not in got and "error" not in got:  # ignore favicon etc.
        server.handle_request()
    if "error" in got:
        sys.exit(f"Google refused: {got['error'][0]}")
    tok = post_form(c["token_uri"], {
        "code": got["code"][0], "client_id": c["client_id"], "client_secret": c["client_secret"],
        "redirect_uri": REDIRECT, "grant_type": "authorization_code"})
    TOKEN.write_text(json.dumps({"refresh_token": tok["refresh_token"]}))
    print("Saved token.json")


def access_token():
    c = client()
    return post_form(c["token_uri"], {
        "client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": json.loads(TOKEN.read_text())["refresh_token"],
        "grant_type": "refresh_token"})["access_token"]


def zip_code(post: Path) -> Path:
    out = post / f"{post.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((post / "code").rglob("*")):
            rel = f.relative_to(post / "code")
            if f.is_file() and not SKIP & set(rel.parts):
                z.write(f, Path(post.name) / rel)
    return out


def fill_links(html: str, slug: str) -> str:
    base = f"https://github.com/{GITHUB_REPO}"
    return (html.replace("{{CODE_URL}}", f"{base}/tree/main/posts/{slug}/code")
                .replace("{{ZIP_URL}}", f"{base}/raw/main/posts/{slug}/{slug}.zip"))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True)


def push(slug):
    git("add", "-A", "posts", "topics.md")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode
    if staged:
        git("commit", "-m", f"post: {slug}")
    git("push", "origin", "HEAD")


def publish(post: Path, live: bool):
    meta = json.loads((post / "meta.json").read_text(encoding="utf-8"))
    zip_code(post)
    push(post.name)  # links in the post must resolve before it goes out
    body = json.dumps({
        "kind": "blogger#post", "title": meta["title"], "labels": meta.get("labels", []),
        "content": fill_links((post / "post.html").read_text(encoding="utf-8"), post.name),
    }).encode()
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?isDraft={str(not live).lower()}"
    req = urllib.request.Request(url, body, {
        "Authorization": f"Bearer {access_token()}", "Content-Type": "application/json"})
    res = json.load(urllib.request.urlopen(req))
    (post / "published.json").write_text(json.dumps(
        {"id": res["id"], "url": res.get("url"), "status": res.get("status")}, indent=2))
    print(f"{post.name}: {res.get('status')} {res.get('url', '(draft - see Blogger dashboard)')}")


def main():
    if sys.argv[1:] == ["auth"]:
        return auth()
    live = "--live" in sys.argv
    pending = [p for p in sorted(POSTS.iterdir())
               if p.is_dir() and (p / "post.html").exists() and not (p / "published.json").exists()]
    if not pending:
        print("Nothing to publish.")
    for post in pending:
        publish(post, live)
    if pending:
        push("record published ids")


if __name__ == "__main__":
    main()
