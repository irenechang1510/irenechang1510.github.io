#!/usr/bin/env python3
"""Rebuild on source changes and serve a draft-inclusive local preview."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import threading
import time
from build_notes import ROOT, OUT, build

def fingerprint():
    paths = [ROOT / 'index.html', * (ROOT / 'notes-src').rglob('*'),
             * (ROOT / 'assets').rglob('*'), ROOT / 'scripts' / 'build_notes.py']
    return [(str(p), p.stat().st_mtime_ns) for p in sorted(paths) if p.is_file()]

def watch():
    previous = fingerprint()
    while True:
        time.sleep(0.7)
        current = fingerprint()
        if current != previous:
            previous = current
            try:
                build(drafts=True)
            except Exception as exc:
                print(f'Build failed; keeping previous preview: {exc}', flush=True)

if __name__ == '__main__':
    build(drafts=True)
    threading.Thread(target=watch, daemon=True).start()
    print('Preview: http://localhost:8001 (drafts included). Save, then refresh your browser.', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8001), partial(SimpleHTTPRequestHandler, directory=str(OUT))).serve_forever()
