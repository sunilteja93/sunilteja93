#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

OWNER = "sunilteja93"
REPO = "llmrig"
OUT = Path("assets/research-pulse.svg")

FALLBACK = {
    "language": "Python",
    "release": "v0.3.0",
    "topics": ["local-llm", "ollama", "benchmarking"],
}


def github_json(path: str):
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "sunilteja93-profile-pulse",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def get_release() -> str:
    try:
        release = github_json(f"/repos/{OWNER}/{REPO}/releases/latest")
        tag = release.get("tag_name")
        if tag:
            return str(tag)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass

    try:
        tags = github_json(f"/repos/{OWNER}/{REPO}/tags?per_page=1")
        if tags and tags[0].get("name"):
            return str(tags[0]["name"])
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass

    return FALLBACK["release"]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def generate() -> str:
    try:
        repo = github_json(f"/repos/{OWNER}/{REPO}")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        repo = {}

    language = repo.get("language") or FALLBACK["language"]
    topics = repo.get("topics") or FALLBACK["topics"]

    preferred = [
        "local-llm",
        "ollama",
        "benchmarking",
        "llm-inference",
        "apple-silicon",
        "hardware-detection",
        "qwen",
    ]
    selected = [topic for topic in preferred if topic in topics][:3]
    if len(selected) < 3:
        selected.extend([t for t in topics if t not in selected][: 3 - len(selected)])
    signals = " / ".join(selected or FALLBACK["topics"])
    release = get_release()

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="265" viewBox="0 0 1200 265" role="img" aria-labelledby="title desc">
<title id="title">Live Research Pulse</title>
<desc id="desc">Current open-source and research signals.</desc>
<defs>
  <linearGradient id="pulseLine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#58a6ff"/>
    <stop offset=".5" stop-color="#7ee787"/>
    <stop offset="1" stop-color="#a371f7"/>
  </linearGradient>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<rect width="1200" height="265" rx="18" fill="#010409"/>
<rect x="16" y="16" width="1168" height="233" rx="14" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
<text x="42" y="52" fill="#8b949e" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="15">LIVE RESEARCH PULSE</text>
<circle cx="1130" cy="47" r="5" fill="#3fb950" filter="url(#glow)"/>
<text x="1050" y="52" fill="#7ee787" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">SIGNAL OK</text>
<line x1="42" y1="70" x2="1158" y2="70" stroke="#21262d"/>
<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
  <text x="42" y="104" fill="#8b949e" font-size="13">ACTIVE PROJECT</text>
  <text x="190" y="104" fill="#58a6ff" font-size="16" font-weight="700">LLMRig</text>
  <text x="42" y="134" fill="#8b949e" font-size="13">MODE</text>
  <text x="190" y="134" fill="#c9d1d9" font-size="15">BUILD / BENCHMARK / SHIP</text>
  <text x="42" y="164" fill="#8b949e" font-size="13">LANGUAGE</text>
  <text x="190" y="164" fill="#c9d1d9" font-size="15">{esc(language)}</text>
  <text x="42" y="194" fill="#8b949e" font-size="13">RELEASE</text>
  <text x="190" y="194" fill="#7ee787" font-size="15">{esc(release)}</text>
  <text x="42" y="224" fill="#8b949e" font-size="13">SIGNALS</text>
  <text x="190" y="224" fill="#c9d1d9" font-size="15">{esc(signals)}</text>
  <text x="665" y="104" fill="#8b949e" font-size="13">RESEARCH TRACK</text>
  <text x="825" y="104" fill="#a371f7" font-size="15">AI SECURITY</text>
  <text x="665" y="134" fill="#8b949e" font-size="13">PAPER</text>
  <text x="825" y="134" fill="#c9d1d9" font-size="15">IEEE Access / 2026</text>
  <text x="665" y="164" fill="#8b949e" font-size="13">FOCUS</text>
  <text x="825" y="164" fill="#c9d1d9" font-size="15">prompt injection + browser security</text>
  <text x="665" y="194" fill="#8b949e" font-size="13">PIPELINE</text>
  <text x="825" y="194" fill="#c9d1d9" font-size="15">observe &gt; attack &gt; measure &gt; harden</text>
</g>
<path d="M665 223 H718 L730 207 L744 237 L760 215 L774 223 H1155" fill="none" stroke="url(#pulseLine)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
</svg>
'''


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    previous = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if previous == content:
        print("research pulse already current")
        return 0
    OUT.write_text(content, encoding="utf-8")
    print(f"updated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
